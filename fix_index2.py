import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Open Positions title
bad_title = "posTitle.innerText = Open Positions ( ออเดอร์กำลังรัน);"
good_title = "posTitle.innerText = `Open Positions (${data.positions.length} ออเดอร์กำลังรัน)`;"
content = content.replace(bad_title, good_title)

# Fix empty positions
bad_empty_pos = 'html = <tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:20px;">ไม่มีออเดอร์ที่กำลังรัน</td></tr>;'
good_empty_pos = 'html = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:20px;">ไม่มีออเดอร์ที่กำลังรัน</td></tr>`;'
content = content.replace(bad_empty_pos, good_empty_pos)

# Fix empty recent trades
bad_empty_trades = 'html = <tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:20px;">ไม่มีประวัติการเทรดล่าสุด</td></tr>;'
good_empty_trades = 'html = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:20px;">ไม่มีประวัติการเทรดล่าสุด</td></tr>`;'
content = content.replace(bad_empty_trades, good_empty_trades)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("index.html remaining backticks fixed!")
