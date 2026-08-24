from local_ai import gemini_model
import json
import os
import time

from config import config

# --- Configuration ---
GEMINI_API_KEY = config.get("gemini_api_key", "")
DATABASE_PATH = "training_database.json"
OUTPUT_DATASET_PATH = "dataset.jsonl"

def setup_gemini():
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY is not set in config.json")
        return None
    
    # Use gemini-1.5-flash as the teacher model for speed and cost efficiency
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def generate_curated_output(model, trade):
    """
    Asks Gemini (Teacher) to look at the trade's outcome and the original prompt,
    and generate the IDEAL JSON response that the Local AI *should* have predicted.
    """
    profit = trade.get("profit", 0)
    symbol = trade.get("symbol", "Unknown")
    trade_type = trade.get("type", "Unknown")
    
    # We reconstruct the input context to tell Gemini what happened
    prompt = f"""
คุณคือ AI Teacher ผู้เชี่ยวชาญการเทรด Forex SMC
นี่คือบันทึกการเทรด (Trade Log) ของ Local AI:
- คู่เงิน: {symbol}
- ฝั่งที่เข้าเทรด: {trade_type}
- ผลกำไร/ขาดทุน: ${profit:.2f}

งานของคุณ:
จงเขียนผลลัพธ์ (Output) ในรูปแบบ JSON ที่สมบูรณ์แบบที่สุด ที่ Local AI *ควรจะ* ตอบกลับมาในสถานการณ์นี้ เพื่อใช้เป็นตัวอย่างฝึกสอน (Training Dataset)
- ถ้าไม้เดิม "กำไร": ให้หาเหตุผลสนับสนุนที่อิงตามหลัก SMC (Order Block, FVG) 
- ถ้าไม้เดิม "ขาดทุน": แปลว่า Local AI ตัดสินใจผิด ให้คุณปรับเปลี่ยนคำตอบเป็น "HOLD" หรือฝั่งที่ถูกต้องแทน พร้อมอธิบายเหตุผลว่าทำไมจึงไม่ควรเข้าเทรดฝั่งเดิม

ให้ตอบกลับเป็น JSON เพียวๆ ห้ามมีคำอธิบายอื่น ห้ามใส่ Markdown (```json) รูปแบบ JSON ต้องเป็นแบบนี้:
{{
    "market_analyst": {{
        "trend": "Bullish / Bearish / Ranging",
        "support": "...",
        "resistance": "...",
        "demand_zone": "...",
        "supply_zone": "...",
        "analysis": "..."
    }},
    "smc_strategist": {{
        "setup": "...",
        "decision": "BUY / SELL / HOLD",
        "confidence": "80-100"
    }}
}}
"""
    
    try:
        res = model.generate_content(prompt)
        text = res.text.strip()
        # Clean markdown if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        # Verify it's valid JSON
        json_data = json.loads(text.strip())
        return json.dumps(json_data, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Gemini Teacher Error: {e}")
        return None

def main():
    print("🎓 ------------------------------------------- 🎓")
    print("🎓 WEEKEND CURATOR: Local AI Training Pipeline 🎓")
    print("🎓 ------------------------------------------- 🎓")
    
    if not os.path.exists(DATABASE_PATH):
        print(f"⚠️ Database {DATABASE_PATH} not found. No trades to process.")
        return
        
    model = setup_gemini()
    if not model:
        return
        
    with open(DATABASE_PATH, "r", encoding="utf-8") as f:
        try:
            trades = json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Error reading {DATABASE_PATH}. Invalid JSON.")
            return

    print(f"📦 Found {len(trades)} trades in database.")
    
    curated_lines = []
    
    # Process each trade
    for i, trade in enumerate(trades):
        print(f"🔍 Curating Trade {i+1}/{len(trades)} (Ticket: {trade.get('ticket')}) ...")
        
        # In a real scenario, the 'training_database.json' must also store the EXACT input prompt 
        # that was given to the Local AI at the time, so we can pair it with the curated output.
        # For now, we simulate the structure.
        
        ideal_json_output = generate_curated_output(model, trade)
        
        if ideal_json_output:
            # Create ShareGPT format suitable for LLaMA-3 Fine-Tuning
            dataset_entry = {
                "messages": [
                    {
                        "role": "user", 
                        "content": f"Analyze {trade.get('symbol')} with SMC concepts based on recent OHLC data. Provide JSON output."
                    },
                    {
                        "role": "assistant",
                        "content": ideal_json_output
                    }
                ]
            }
            curated_lines.append(json.dumps(dataset_entry, ensure_ascii=False))
            print(f"✅ Trade {i+1} successfully curated.")
        else:
            print(f"❌ Failed to curate Trade {i+1}.")
            
        time.sleep(3) # Throttle Gemini API limits
        
    if curated_lines:
        # Append to jsonl file
        with open(OUTPUT_DATASET_PATH, "a", encoding="utf-8") as f:
            for line in curated_lines:
                f.write(line + "\n")
        print(f"\n🎉 Successfully added {len(curated_lines)} curated examples to {OUTPUT_DATASET_PATH}")
        print(f"🧠 Local AI is ready to be fine-tuned with this dataset!")
        
        # Optional: Clear the training database after successful curation
        # os.remove(DATABASE_PATH)
    else:
        print("\n⚠️ No data was curated.")

if __name__ == "__main__":
    main()
