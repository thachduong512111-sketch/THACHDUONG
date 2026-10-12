import sqlite3
import streamlit as st

# Cấu hình giao diện rộng cho app
st.set_page_config(
    page_title="Hương Vị Việt - Ứng Dụng Gọi Món", page_icon="🥢", layout="wide"
)

# ================= 1. CẤU HÌNH DATABASE (Lưu dữ liệu không mất khi thoát trang) =================
conn = sqlite3.connect("quan_an.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS gio_hang (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ten_mon TEXT,
        gia REAL,
        so_luong INTEGER
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


# ================= 2. TRỢ LÝ ẢO Ở SIDEBAR (Giống mẫu N2 Assistant) =================
with st.sidebar:
  st.image(
      "https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=50
  )
  st.title("🤖 Trợ lý Quán Ăn")
  st.caption("Hỏi tui về món ăn, giá cả hoặc cách tính tiền nha!")

  if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Dạ chào bạn! Mình là trợ lý của quán. Bạn muốn chọn món gì ạ?"
        ),
    }]

  for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
      st.markdown(msg["content"])

  if prompt := st.chat_input("Nhập câu hỏi cho trợ lý..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    # Phản hồi thông minh của bot
    if "phở" in prompt.lower():
      reply = "Quán có Phở bò đặc biệt nước dùng đậm đà, giá 65.000đ nhé!"
    elif "nước" in prompt.lower() or "uống" in prompt.lower():
      reply = "Quán phục vụ Trà đào cam sả và Cà phê sữa đá rất ngon ạ!"
    else:
      reply = (
          "Dạ, bạn có thể xem qua thực đơn ở màn hình chính để chọn món nha!"
      )

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
      st.markdown(reply)

# ================= 3. GIAO DIỆN CHÍNH (Banner + Thực đơn + Giỏ hàng) =================

# Banner phong cách chuyên nghiệp
st.markdown(
    """
    <div style="background-color: #B83227; padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px;">
        <h1 style="margin:0;">🥢 HƯƠNG VỊ VIỆT - APP TÍNH TIỀN & ĐẶT MÓN</h1><p style="margin:5px 0 0 0;">Thực đơn phong phú • Phục vụ tận tâm • Dữ liệu luôn được lưu tự động</p>
    </div>
""",
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["📋 Thực đơn (Gọi món)", "🛒 Giỏ hàng & Thanh toán"])

# --- TAB 1: THỰC ĐƠN CÓ HÌNH ẢNH ---
with tab1:
  st.subheader("Danh sách Món ăn & Đồ uống")

  thuc_don = [
      {
          "ten": "Phở bò đặc biệt",
          "loai": "Đồ ăn",
          "gia": 65000,
          "hinh": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43",
      },
      {
          "ten": "Cơm tấm sườn nướng",
          "loai": "Đồ ăn",
          "gia": 70000,
          "hinh": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c",
      },
      {
          "ten": "Trà đào cam sả",
          "loai": "Đồ uống",
          "gia": 30000,
          "hinh": "https://images.unsplash.com/photo-1556679343-c7306c1976bc",
      },
      {
          "ten": "Cà phê sữa đá",
          "loai": "Đồ uống",
          "gia": 25000,
          "hinh": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd",
      },
  ]

  # Chia lưới hiển thị các món (2 cột)
  cols = st.columns(2)
  for index, mon in enumerate(thuc_don):
    with cols[index % 2]:
      with st.container(border=True):
        st.image(mon["hinh"], use_container_width=True)
        st.markdown(f"### {mon['ten']}")
        st.write(f"Phân loại: {mon['loai']}")
        st.markdown(f"Giá: **{mon['gia']:,} đ**")

        if st.button("➕ Thêm vào giỏ hàng", key=f"btn_{index}", use_container_width=True):
          them_vao_db(mon["ten"], mon["gia"])
          st.success(f"Đã thêm {mon['ten']} thành công!")
          st.rerun()

# --- TAB 2: GIỎ HÀNG & THANH TOÁN (Lấy từ SQLite) ---
with tab2:
  st.subheader("🛒 Giỏ hàng của bạn (Được lưu tự động vào Database)")

  cursor.execute("SELECT id, ten_mon, gia, so_luong FROM gio_hang")
  items = cursor.fetchall()

  if items:
    tong_tien = 0
    for item in items:
      item_id, ten, gia, sl = item
      thanh_tien = gia * sl
      tong_tien += thanh_tien

      col_a, col_b, col_c = st.columns([3, 2, 1])
      with col_a:
        st.write(f"**{ten}** ({gia:,}đ)")
      with col_b:
        st.write(f"Số lượng: {sl}")
      with col_c:
        if st.button("🗑️ Xóa", key=f"del_{item_id}"):
          cursor.execute("DELETE FROM gio_hang WHERE id = ?", (item_id,))
          conn.commit()
          st.rerun()

    st.divider()
    st.markdown(f"### Tổng thanh toán: **{tong_tien:,} đ**")

    if st.button("💳 Thanh toán hóa đơn", type="primary"):
      st.success("Thanh toán thành công! Hóa đơn đã được lưu.")
      cursor.execute("DELETE FROM gio_hang")  # Xóa giỏ hàng sau khi thanh toán
      conn.commit()
      st.rerun()
  else:st.info("Giỏ hàng đang trống. Hãy qua tab 'Thực đơn' để chọn món nhé!")
