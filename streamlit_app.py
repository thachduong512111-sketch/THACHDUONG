import streamlit as st
import sqlite3
import google.generativeai as genai
# Cấu hình API Key cho Google Gemini
# Cấu hình API Key cho Google Gemini
genai.configure(api_key="AQ.Ab8RN6LPg96Rs8b6DIwvIHy8b2xKkvis_N1tUyrOrU7Nc_oUFA")
# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hương Vị Việt - Ứng Dụng Gọi Món & Chia Bill",
    page_icon="🍲",
    layout="wide",
)

# ==================== 1. CẤU HÌNH DATABASE (LƯU DỮ LIỆU BỀN VỮNG) ====================
conn = sqlite3.connect("quan_an.db", check_same_thread=False)
cursor = conn.cursor()

# Bảng Giỏ hàng
cursor.execute("""
CREATE TABLE IF NOT EXISTS gio_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_mon TEXT,
    gia REAL,
    so_luong INTEGER,
    loai TEXT
)
""")

# Bảng Lịch sử giao dịch & Doanh thu
cursor.execute("""
CREATE TABLE IF NOT EXISTS lich_su (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thoi_gian TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tong_tien REAL,
    so_nguoi INTEGER,
    tien_moi_nguoi REAL,
    hinh_thuc TEXT
)
""")
conn.commit()


# ==================== 2. BANNER GIAO DIỆN CHÍNH ====================
st.markdown("""
    <div style="background: linear-gradient(135deg, #B83227 0%, #E74C3C 100%); padding: 22px; border-radius: 16px; color: white; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(184, 50, 39, 0.3);">
        <div style="display: inline-flex; align-items: center; justify-content: center; background: white; width: 60px; height: 60px; border-radius: 50%; margin-bottom: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); overflow: hidden;">
            <img src="https://flagcdn.com/w80/vn.png" style="width: 100%; height: 100%; object-fit: cover;" />
        </div>
        <h1 style="margin: 0; font-size: 26px; letter-spacing: 1px;">HƯƠNG VỊ VIỆT</h1>
        <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Tinh hoa ẩm thực truyền thống • Chia bill thông minh • Quản lý doanh thu tự động</p>
    </div>
""", unsafe_allow_html=True)


# ==================== 3. DANH SÁCH MÓN ĂN & NƯỚC UỐNG ====================
DANH_SACH_DO_AN = [
    {"ten": "Cơm Tấm Sườn Bì Chả", "gia": 55000, "anh": "https://i.pinimg.com/736x/cb/7d/ba/cb7dba9f46946ba781e7bccb04317b12.jpg"},
    {"ten": "Phở Bò", "gia": 50000, "anh": "https://i.pinimg.com/1200x/35/6b/7a/356b7a29a52e3ae7cbf02597cbae488f.jpg"},
    {"ten": "Bò Kho", "gia": 55000, "anh": "https://i.pinimg.com/1200x/d3/ca/2a/d3ca2a8251574451353bab15a74cb973.jpg"},
    {"ten": "Bún Bò Huế", "gia": 55000, "anh": "https://i.pinimg.com/736x/aa/a6/b7/aaa6b7fc86c996451e593875ef83e2ce.jpg"},
    {"ten": "Bún Chả Hà Nội", "gia": 50000, "anh": "https://i.pinimg.com/736x/50/c2/c6/50c2c657c9fdeeedafccbce1c05a1f01.jpg"},
    {"ten": "Xôi Thập Cẩm", "gia": 35000, "anh": "https://i.pinimg.com/736x/20/cc/1f/20cc1fd5e526e51c296406ec3b466535.jpg"},
    {"ten": "Mì Xào Bò", "gia": 45000, "anh": "https://i.pinimg.com/1200x/f8/74/46/f874462062b32b8772f1661a48da8589.jpg"}
]

DANH_SACH_NUOC_UONG = [
    {"ten": "Cà Phê Sữa", "gia": 25000, "anh": "https://i.pinimg.com/1200x/a0/ee/d8/a0eed8b52ffdae7f3f89af1bfe0fc4dc.jpg"},{"ten": "Trà Đào Cam Sả", "gia": 32000, "anh": "https://i.pinimg.com/1200x/c1/15/be/c115be82743ce981b5f74df1d2e981ba.jpg"},
    {"ten": "Nước Ép Cam", "gia": 30000, "anh": "https://i.pinimg.com/736x/2e/8c/23/2e8c2342f2c28d6ff61e02e97f7d4997.jpg"},
    {"ten": "Sữa Đậu Nành", "gia": 18000, "anh": "https://i.pinimg.com/736x/0a/bc/8c/0abc8c6f5c966820c51ac8f68d6ccd21.jpg"}
]


# ==================== 4. MENU ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR) ====================
with st.sidebar:
    st.image("https://flagcdn.com/w80/vn.png", width=40)
    st.title("📌 Danh Mục Quản Lý")
    
    chuc_nang = st.radio(
        "Chọn chức năng:",
        [
            "📜 Menu Thực Đơn",
            "🧮 Chia Tiền Nhóm & QR",
            "📜 Lịch Sử Giao Dịch",
            "📊 Thống Kê Doanh Thu",
            "🤖 Trợ Lý AI Tư Vấn"
        ]
    )
    st.divider()
    
    # Hiển thị tóm tắt Giỏ Hàng ở Sidebar
    cursor.execute("SELECT SUM(gia * so_luong) FROM gio_hang")
    tong_tien_gh = cursor.fetchone()[0] or 0
    st.metric(label="🛒 Tổng giỏ hàng hiện tại", value=f"{tong_tien_gh:,.0f} VNĐ")


# ==================== 5. XỬ LÝ GIAO DIỆN THEO CHỨC NĂNG ====================

# --- CHỨC NĂNG 1: MENU THỰC ĐƠN ---
if chuc_nang == "📜 Menu Thực Đơn":
    col_menu, col_gio = st.columns([2.5, 1.2])
    
    with col_menu:
        st.header("🍽️ Thực Đơn Quán")
        
        # Tab Phân loại Đồ Ăn & Nước Uống riêng rõ ràng
        tab_do_an, tab_nuoc = st.tabs(["🍛 ĐỒ ĂN", "🥤 NƯỚC UỐNG"])
        
        # Hiển thị Đồ Ăn
        with tab_do_an:
            cols = st.columns(3)
            for idx, item in enumerate(DANH_SACH_DO_AN):
                with cols[idx % 3]:
                    st.image(item["anh"], use_container_width=True)
                    st.markdown(f"**{item['ten']}**")
                    st.write(f"Giá: :red[**{item['gia']:,} VNĐ**]")
                    sl = st.number_input("Số lượng", min_value=1, max_value=20, value=1, key=f"food_sl_{idx}")
                    if st.button("➕ Thêm vào giỏ", key=f"btn_food_{idx}"):
                        cursor.execute("INSERT INTO gio_hang (ten_mon, gia, so_luong, loai) VALUES (?, ?, ?, ?)",
                                       (item['ten'], item['gia'], sl, "Đồ ăn"))
                        conn.commit()
                        st.success(f"Đã thêm {sl} {item['ten']}")
                        st.rerun()

        # Hiển thị Nước Uống
        with tab_nuoc:
            cols_n = st.columns(3)
            for idx, item in enumerate(DANH_SACH_NUOC_UONG):
                with cols_n[idx % 3]:
                    st.image(item["anh"], use_container_width=True)
                    st.markdown(f"**{item['ten']}**")
                    st.write(f"Giá: :red[**{item['gia']:,} VNĐ**]")
                    sl = st.number_input("Số lượng", min_value=1, max_value=20, value=1, key=f"drink_sl_{idx}")
                    if st.button("➕ Thêm vào giỏ", key=f"btn_drink_{idx}"):
                        cursor.execute("INSERT INTO gio_hang (ten_mon, gia, so_luong, loai) VALUES (?, ?, ?, ?)",
                                       (item['ten'], item['gia'], sl, "Nước uống"))
                        conn.commit()
                        st.success(f"Đã thêm {sl} {item['ten']}")
                        st.rerun()

    with col_gio:
        st.header("🛒 Giỏ Hàng")
        cursor.execute("SELECT id, ten_mon, gia, so_luong, loai FROM gio_hang")
        items = cursor.fetchall()
        
        if items:
            for item in items:
                tt = item[2] * item[3]
                st.write(f"• **{item[1]}** (x{item[3]}) - :red[{tt:,.0f} VNĐ]")
            
            st.divider()
            st.markdown(f"### Tổng cộng: :red[{tong_tien_gh:,.0f} VNĐ]")
            
            if st.button("🗑️ Xóa sạch giỏ hàng", type="secondary"):
                cursor.execute("DELETE FROM gio_hang")
                conn.commit()
                st.rerun()
        else:
            st.info("Giỏ hàng chưa có món nào.")


# --- CHỨC NĂNG 2: CHIA TIỀN NHÓM & TẠO QR CHUYỂN KHỎAN ---
elif chuc_nang == "🧮 Chia Tiền Nhóm & QR":
    st.header("🧮 Chia Bill Thông Minh & Mã QR Chuyển Khoản")
    
    if tong_tien_gh > 0:
        col_calc, col_qr = st.columns([1.5, 1])
        
        with col_calc:
            st.subheader("1. Tính toán chia bill")
            st.write(f"Tổng hóa đơn trong giỏ: **{tong_tien_gh:,.0f} VNĐ**")
            so_nguoi = st.number_input("Nhập số người chia bill:", min_value=1, value=2)
            
            tien_moi_nguoi = tong_tien_gh / so_nguoi if so_nguoi > 0 else tong_tien_gh
            st.success(f"👉 Mỗi người cần chuyển: **{tien_moi_nguoi:,.0f} VNĐ**")
            
            if st.button("✅ Xác nhận thanh toán & Lưu lịch sử"):
                cursor.execute("INSERT INTO lich_su (tong_tien, so_nguoi, tien_moi_nguoi, hinh_thuc) VALUES (?, ?, ?, ?)",
                               (tong_tien_gh, so_nguoi, tien_moi_nguoi, "Chuyển khoản / Tiền mặt"))
                cursor.execute("DELETE FROM gio_hang")
                conn.commit()
                st.balloons()
                st.success("Đã thanh toán thành công và lưu vào Lịch sử!")
                st.rerun()

        with col_qr:
            st.subheader("2. Mã QR Thanh Toán VietQR")
            # Tạo mã VietQR động theo tổng tiền
            nganhang = "MB" # Ngân hàng MBBank
            stk = "0900000000" # Bạn có thể thay bằng STK của bạn
            tentk = "HUONG VI VIET"
            qr_url = f"https://img.vietqr.io/image/{nganhang}-{stk}-compact2.png?amount={int(tien_moi_nguoi)}&addInfo=Thanh%20toan%20Huong%20Vi%20Viet&accountName={tentk}"
            st.image(qr_url, caption=f"Quét QR để chuyển {tien_moi_nguoi:,.0f} VNĐ", use_container_width=True)
    else:
        st.warning("Giỏ hàng hiện đang trống! Vui lòng chọn món ở Menu trước.")


# --- CHỨC NĂNG 3: LỊCH SỬ GIAO DỊCH ---
elif chuc_nang == "📜 Lịch Sử Giao Dịch":
    st.header("📜 Lịch Sử Thanh Toán Giao Dịch")
    cursor.execute("SELECT id, thoi_gian, tong_tien, so_nguoi, tien_moi_nguoi FROM lich_su ORDER BY id DESC")
    rows = cursor.fetchall()
    
    if rows:
        st.dataframe(
            rows,
            column_config={
                "0": "Mã HD",
                "1": "Thời Gian",
                "2": "Tổng Hóa Đơn (VNĐ)",
                "3": "Số Người",
                "4": "Tiền/Người (VNĐ)"
            },
            use_container_width=True
        )
    else:
        st.info("Chưa có lịch sử giao dịch nào được lưu.")


# --- CHỨC NĂNG 4: THỐNG KÊ DOANH THU ---
elif chuc_nang == "📊 Thống Kê Doanh Thu":
    st.header("📊 Thống Kê Doanh Thu Quán")
    
    cursor.execute("SELECT SUM(tong_tien), COUNT(id) FROM lich_su")
    res = cursor.fetchone()
    tong_doanh_thu = res[0] or 0
    tong_don = res[1] or 0
    
    c1, c2 = st.columns(2)
    c1.metric("💰 Tổng Doanh Thu", f"{tong_doanh_thu:,.0f} VNĐ")
    c2.metric("🧾 Tổng Số Đơn Đã Thanh Toán", f"{tong_don} đơn")

# --- CHỨC NĂNG 5: TRỢ LÝ AI TƯ VẤN ---
elif chuc_nang == "🤖 Trợ Lý AI Tư Vấn":
    st.header("🤖 Trợ Lý AI Hương Vị Việt")
    st.write("Hỏi trợ lý về tư vấn món ăn, tính toán giá cả...")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hỏi trợ lý về tư vấn món ăn..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

            # Gọi AI Gemini tự động trả lời thông minh
          # Gọi AI Gemini tự động trả lời thông minh
    system_instruction = (
        "Bạn là trợ lý tư vấn món ăn thân thiện của nhà hàng Hương Vị Việt. "
        "Hãy tư vấn chi tiết các món ăn, đồ uống, hương vị, giá cả và hỗ trợ tính tiền bill cho khách hàng một cách sinh động, hấp dẫn. "
        "Tuyệt đối không lặp lại một câu trả lời mẫu cố định."
    )

  try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )

            prompt = str(prompt).strip()
            response = model.generate_content(prompt)
            reply = response.text or "Xin lỗi, AI chưa có câu trả lời."

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })

   except Exception as e:
            reply = f"Đã xảy ra lỗi kết nối AI: {e}"
            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })
