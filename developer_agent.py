import os
import re
import json
import time
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# Assuming local_ai is available from previous tasks
try:
    from local_ai import generate_content
except ImportError:
    # Fallback if run independently
    import requests
    def generate_content(prompt):
        payload = {"model": "llama3.1", "prompt": prompt, "stream": False}
        class R:
            def __init__(self, t): self.text = t
        try:
            return R(requests.post("http://localhost:11434/api/generate", json=payload).json().get("response", ""))
        except:
            return R("Error: Local AI not running.")

# Load config for Telegram Token
try:
    with open('mt5_backend/config.json', 'r') as f:
        config = json.load(f)
    TELEGRAM_TOKEN = config.get("telegram_bot_token", "")
except:
    TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

SYSTEM_PROMPT = """You are a Developer Agent. You can help the user write code, read files, and run commands.
You have access to the following tools via XML tags. You must use these EXACT tags.

1. To read a file:
<read_file>path/to/file</read_file>

2. To write or overwrite a file:
<write_file path="path/to/file">
file_content_here
</write_file>

3. To run a terminal command:
<run_command>command_here</run_command>

4. To reply to the user via Telegram (ends the conversation loop):
<reply>Your final answer or explanation here</reply>

Rules:
- IMPORTANT: You are running on a Windows Server (Powershell/CMD). Do NOT use Linux commands like 'ps', 'ls', or paths like '/proc'. Use Windows equivalents like 'tasklist', 'dir', etc.
- ALWAYS reply to the user in Thai language (<reply>ข้อความภาษาไทย...</reply>). Make your tone friendly, easy to understand, and helpful, like a general AI assistant.
- Think step by step.
- Use ONLY ONE tool per response.
- Wait for the system to provide the "Observation:" before continuing.
- Once you have completed the task or found the information, use <reply> to talk to the user IMMEDIATELY. Do not loop endlessly.
"""

def execute_tool(response_text):
    """Parses the LLM response for tools and executes them."""
    
    # 1. Read File
    read_match = re.search(r'<read_file>(.*?)</read_file>', response_text, re.DOTALL)
    if read_match:
        path = read_match.group(1).strip()
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"Observation: Content of {path}:\n{content[:2000]}" # Limit to avoid context overflow
        except Exception as e:
            return f"Observation: Error reading file: {e}"

    # 2. Write File
    write_match = re.search(r'<write_file path="(.*?)">(.*?)</write_file>', response_text, re.DOTALL)
    if write_match:
        path = write_match.group(1).strip()
        content = write_match.group(2)
        try:
            # Ensure dir exists
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Observation: Successfully wrote to {path}"
        except Exception as e:
            return f"Observation: Error writing file: {e}"

    # 3. Run Command
    cmd_match = re.search(r'<run_command>(.*?)</run_command>', response_text, re.DOTALL)
    if cmd_match:
        cmd = cmd_match.group(1).strip()
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            out = result.stdout + result.stderr
            return f"Observation: Command exited with {result.returncode}. Output:\n{out[:2000]}"
        except subprocess.TimeoutExpired:
            return "Observation: Command timed out after 10 seconds."
        except Exception as e:
            return f"Observation: Error running command: {e}"

    # 4. Reply
    reply_match = re.search(r'<reply>(.*?)</reply>', response_text, re.DOTALL)
    if reply_match:
        return f"REPLY:{reply_match.group(1).strip()}"

    # If no tool was used, assume it's just trying to reply
    return f"REPLY:{response_text.strip()}"

async def handle_dev_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = " ".join(context.args)
    if not user_msg:
        await update.message.reply_text("Please provide a task. Example: /dev read the mt5_gateway.py file")
        return

    await update.message.reply_text(f"🚀 Developer Agent started task: {user_msg}\nWorking...")

    # Initialize conversation
    conversation = SYSTEM_PROMPT + f"\n\nUser Request: {user_msg}\n\nThought:"
    
    max_loops = 5
    loop_count = 0
    
    while loop_count < max_loops:
        loop_count += 1
        
        # 1. Call LLM
        res = generate_content(conversation)
        ai_response = res.text
        
        # Log to conversation
        conversation += ai_response + "\n"
        
        # 2. Execute Tool
        tool_result = execute_tool(ai_response)
        
        if tool_result.startswith("REPLY:"):
            final_msg = tool_result.replace("REPLY:", "").strip()
            await update.message.reply_text(f"✅ Task Completed:\n\n{final_msg}")
            break
        else:
            # It's an observation, feed it back
            await update.message.reply_text(f"🔧 Tool Used:\n{tool_result[:500]}...")
            conversation += tool_result + "\n\nThought:"
            
    if loop_count >= max_loops:
        await update.message.reply_text("⚠️ Reached maximum loop count (5). Halting to prevent infinite loop.")

if __name__ == '__main__':
    print("Starting Developer Agent Listener...")
    if TELEGRAM_TOKEN and TELEGRAM_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN":
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("dev", handle_dev_command))
        print("Bot is listening for /dev commands!")
        while True:
            try:
                app.run_polling(read_timeout=30, connect_timeout=30, pool_timeout=30)
            except Exception as e:
                import time
                print(f"Network error in polling: {e}. Retrying in 10 seconds...")
                time.sleep(10)
    else:
        print("Error: Invalid TELEGRAM_TOKEN in config.json")
