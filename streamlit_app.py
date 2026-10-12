import sqlite3
import streamlit as st
# Cấu hình giao diện rộng cho app
st.set_page_config(
    page_title="Hương Vị Việt - Ứng Dụng Gọi Món & Chia Bill",
    page_icon="🥢",
    layout="wide",
)

# ================= 1. CẤU HÌNH DATABASE (Lưu dữ liệu không mất khi thoát trang) =================
conn = sqlite3.connect("quan_an.db", check_same_thread=False)
cursor = conn.cursor()

# Bảng giỏ hàng
cursor.execute("""
    CREATE TABLE IF NOT EXISTS gio_hang (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ten_mon TEXT,
        gia REAL,
        so_luong INTEGER
    )
""")
# Bảng lịch sử giao dịch / doanh thu
cursor.execute("""
    CREATE TABLE IF NOT EXISTS lich_su (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thoi_gian TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tong_tien REAL,
        chi_tiet TEXT
    )
""")
conn.commit()


def them_vao_db(ten_mon, gia):
  cursor.execute("SELECT so_luong FROM gio_hang WHERE ten_mon = ?", (ten_mon,))
  row = cursor.fetchone()
  if row:
    cursor.execute(
        "UPDATE gio_hang SET so_luong = so_luong + 1 WHERE ten_mon = ?",
        (ten_mon,),
    )
  else:
    cursor.execute(
        "INSERT INTO gio_hang (ten_mon, gia, so_luong) VALUES (?, ?, 1)",
        (ten_mon, gia),
    )
  conn.commit()


# ================= 2. TRỢ LÝ ẢO Ở SIDEBAR VỚI LOGO RIÊNG =================
with st.sidebar:
  # Logo thu nhỏ cho trợ lý
  st.markdown(
      """
        <div style="display: flex; align-items: center; gap: 10px; background: #2b2b2b; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
            <div style="background-color: #B83227; color: white; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: bold; font-size: 18px;">HV</div>
            <div>
                <h4 style="margin: 0; color: white; font-size: 15px;">Hương Vị Việt AI</h4>
                <p style="margin: 0; color: #aaa; font-size: 11px;">Trợ lý tư vấn quán</p>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  st.caption("Hỏi tui về món ăn, giá cả hoặc cách tính tiền nha!")

  if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Dạ chào bạn! Mình là trợ lý của quán Hương Vị Việt. Bạn cần giúp"
            " gì ạ?"
        ),
    }]

  for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
      st.markdown(msg["content"])

  if prompt := st.chat_input("Nhập câu hỏi cho trợ lý..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    p_lower = prompt.lower()
    if "phở" in p_lower:
      reply = "Quán có Phở bò đặc biệt thơm ngon đậm đà giá 65.000đ ạ!"
    elif "bún" in p_lower: reply = "Quán có Bún bò Huế (60.000đ) và Bún chả (55.000đ) rất ngon nha!"
    elif "cơm" in p_lower:
      reply = "Cơm tấm sườn nướng mật ong thơm lừng giá 65.000đ ạ!"
    elif "chia" in p_lower or "bill" in p_lower:
      reply = (
          "Bạn có thể vào tab 'Chia bill thông minh' để chia tiền cho nhóm"
          " nha!"
      )
    else:
      reply = (
          "Dạ, bạn có thể tham khảo thực đơn và các tab chức năng ở màn hình"
          " chính nhé!"
      )

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
      st.markdown(reply)

# ================= 3. GIAO DIỆN CHÍNH (LOGO THƯƠNG HIỆU ĐẸP MẮT) =================

st.markdown(...)
"""
    <div style="background: linear-gradient(135deg, #B83227 0%, #E74C3C 100%); padding: 25px; border-radius: 16px; color: white; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(184, 50, 39, 0.3);">
        <div style="display: inline-flex; align-items: center; justify-content: center; background: white; color: #B83227; width: 65px; height: 65px; border-radius: 50%; font-size: 32px; font-weight: bold; margin-bottom: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
            🥢
        </div>
        <h1 style="margin: 0; font-size: 28px; letter-spacing: 1px;">HƯƠNG VỊ VIỆT</h1>
        <p style="margin: 6px 0 0 0; font-size: 15px; opacity: 0.9;">Tinh hoa ẩm truyền thống • Chia bill thông minh • Quản lý doanh thu tự động</p>
    </div>
""",
unsafe
