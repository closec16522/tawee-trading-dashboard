import re

with open('mt5_backend/agent_orchestrator.py', 'r', encoding='utf-8') as f:
    content = f.read()

journal_func = """def send_summary_report():"""

new_journal_func = """def run_trade_journal():
    print("📔 TRADE JOURNAL: Checking for new closed trades to analyze...")
    journal_path = os.path.join(os.path.dirname(__file__), 'journal.json')
    journal_entries = []
    if os.path.exists(journal_path):
        try:
            with open(journal_path, 'r', encoding='utf-8') as f:
                journal_entries = json.load(f)
        except:
            pass

    analyzed_tickets = [entry.get("ticket") for entry in journal_entries]

    now = datetime.now()
    today_start = now - timedelta(days=30)
    deals = mt5.history_deals_get(today_start, now)
    
    new_entries = []
    
    if deals:
        sorted_deals = sorted(deals, key=lambda x: x.time, reverse=True)
        # We only want to analyze up to the last 15 closed deals to save API calls
        closed_deals = [d for d in sorted_deals if d.entry == 1][:15]
        
        for d in closed_deals:
            ticket = d.position_id
            if ticket in analyzed_tickets:
                continue
                
            # fetch entry price
            entry_price = 0.0
            pos_deals = mt5.history_deals_get(position=ticket)
            if pos_deals:
                for pd in pos_deals:
                    if pd.entry == 0:
                        entry_price = pd.price
                        break
                        
            symbol = d.symbol
            trade_type = "BUY" if d.type == 1 else "SELL"
            exit_price = d.price
            profit = d.profit
            close_time = datetime.fromtimestamp(d.time).strftime("%d %b %Y")

            # Analyze using Gemini
            if gemini_model:
                prompt = f"วิเคราะห์ผลการเทรด (Trade Insight) สั้นๆ 1-2 ประโยคสำหรับไม้นี้:\\nคู่เงิน: {symbol}\\nฝั่ง: {trade_type}\\nจุดเข้า: {entry_price}\\nจุดออก: {exit_price}\\nกำไร: ${profit:.2f}\\n\\nถ้ากำไร บอกว่าทำอะไรถูก (เช่น เข้าตามเทรน, ปิดได้ดี). ถ้าขาดทุน บอกว่าควรเรียนรู้อะไร (เช่น ผิดเทรน, SL สั้นไป). ตอบเป็นภาษาไทยสั้นๆ กระชับ ไม่ต้องเกริ่นนำ ไม่เกิน 20 คำ."
                insight = "ไม่มีข้อมูล"
                try:
                    res = gemini_model.generate_content(prompt)
                    insight = res.text.strip().replace('\\n', ' ')
                except Exception as e:
                    print("Error generating journal insight:", e)
                    insight = "ไม่สามารถวิเคราะห์ได้ในขณะนี้"
            else:
                insight = "รันตามระบบเทรด"
                
            entry = {
                "ticket": ticket,
                "symbol": symbol,
                "type": trade_type,
                "entry": entry_price,
                "exit": exit_price,
                "profit": profit,
                "date": close_time,
                "insight": insight
            }
            new_entries.append(entry)
            print(f"📔 JOURNAL: Analyzed trade #{ticket} ({symbol}) -> {insight}")

    if new_entries:
        # Prepend new entries
        journal_entries = new_entries + journal_entries
        # Limit to 50
        journal_entries = journal_entries[:50]
        
        with open(journal_path, 'w', encoding='utf-8') as f:
            json.dump(journal_entries, f, ensure_ascii=False, indent=4)
            
    # Always push the latest journal list to the gateway
    try:
        requests.post(f"{GATEWAY_URL}/api/journal_update", json={"entries": journal_entries}, timeout=5, proxies=LOCAL_PROXIES)
    except Exception as e:
        print("Error sending journal update to gateway:", e)

def send_summary_report():"""
content = content.replace(journal_func, new_journal_func)

main_loop_str = """            run_portfolio_manager()
            print("--- Cycle Complete ---")"""

new_main_loop_str = """            run_portfolio_manager()
            run_trade_journal()
            print("--- Cycle Complete ---")"""
content = content.replace(main_loop_str, new_main_loop_str)

with open('mt5_backend/agent_orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("agent_orchestrator.py patched")
