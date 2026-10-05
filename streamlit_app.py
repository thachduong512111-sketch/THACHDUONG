import streamlit as st
import pandas as pd
from datetime import datetime

# Cấu hình trang Streamlit
st.set_page_config(page_title="App Tính Tiền Quán & Chia Bill", page_icon="🧮", layout="wide")

# Khởi tạo dữ liệu trong Session State
if 'menu' not in st.session_state:
    st.session_state.menu = [
        {"id": 1, "name": "Phở bò đặc biệt", "category": "Món chính", "price": 65000, "desc": "Phở bò truyền thống với tái, nạm và bò viên."},
        {"id": 2, "name": "Cơm tấm sườn nướng", "category": "Món chính", "price": 70000, "desc": "Sườn nướng mật ong dùng kèm cơm tấm, bì và đồ chua."},
        {"id": 3, "name": "Trà đào cam sả", "category": "Nước uống", "price": 35000, "desc": "Giải nhiệt ngày hè với vị thanh ngọt."},
        {"id": 4, "name": "Cà phê sữa đá", "category": "Nước uống", "price": 25000, "desc": "Cà phê nguyên chất đậm đà."}
    ]

if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("🍽️ App Tính Tiền Quán & Chia Hóa Đơn Thông Minh")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🛒 1. Gọi món & Thanh toán", 
    "👥 2. Chia bill thông minh", 
    "📜 3. Lịch sử giao dịch", 
    "📊 4. Thống kê doanh thu"
])

# ---------------------------------------------------------
# TAB 1: GỌI MÓN & THANH TOÁN
# ---------------------------------------------------------
with tab1:
    col_menu, col_cart = st.columns([3, 2])

    with col_menu:
        st.subheader("📋 Thực đơn")
        
        # Bộ lọc danh mục
        categories = ["Tất cả"] + list(set(item['category'] for item in st.session_state.menu))
        selected_cat = st.selectbox("Lọc theo danh mục", categories)

        for item in st.session_state.menu:
            if selected_cat == "Tất cả" or item['category'] == selected_cat:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{item['name']}**")
                        st.caption(f"{item['category']} • {item['desc']}")
                        st.markdown(f"**:red[{item['price']:,} đ]**")
                    with c2:
                        if st.button("Thêm", key=f"add_{item['id']}"):
                            st.session_state.cart.append(item)
                            st.toast(f"Đã thêm {item['name']} vào giỏ!")

    with col_cart:
        st.subheader("🛒 Giỏ hàng")
        if not st.session_state.cart:
            st.info("Giỏ hàng đang trống. Hãy chọn món từ thực đơn.")
        else:
            df_cart = pd.DataFrame(st.session_state.cart)
            st.dataframe(df_cart[['name', 'price']], use_container_width=True)

            if st.button("❌ Xóa tất cả món"):
                st.session_state.cart = []
                st.rerun()

            st.divider()
            
            # Thông tin bàn & Ghi chú
            st.subheader("📋 Thông tin đơn hàng")
            table_num = st.selectbox("Chọn số bàn", [f"Bàn {i}" for i in range(1, 11)])
            note = st.text_input("Ghi chú cho bếp", placeholder="Ví dụ: Không hành, ít cay...")

            # Tính toán VAT & Giảm giá
            st.subheader("⚙️ Tính toán hóa đơn")
            discount_percent = st.number_input("Mức giảm giá (%)", min_value=0, max_value=100, value=0)
            vat_percent = st.number_input("Thuế VAT (%)", min_value=0, max_value=20, value=8)

            subtotal = sum(item['price'] for item in st.session_state.cart)
            discount_amount = subtotal * (discount_percent / 100)
            after_discount = subtotal - discount_amount
            vat_amount = after_discount * (vat_percent / 100)
            total_final = after_discount + vat_amount

            st.write(f"**Tạm tính:** {subtotal:,.0f} đ")
            st.write(f"**Giảm giá ({discount_percent}%):** -{discount_amount:,.0f} đ")
            st.write(f"**VAT ({vat_percent}%):** +{vat_amount:,.0f} đ")
            st.markdown(f"### **Tổng cộng: {total_final:,.0f} đ**")

            # Nút Lưu hóa đơn
            if st.button("✅ Hoàn tất & Gửi đơn hàng", type="primary"):
                order_info = {
                    "time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
                    "table": table_num,
                    "items": [i['name'] for i in st.session_state.cart],
                    "total": total_final,
                    "note": note
                }
                st.session_state.history.append(order_info)
                st.session_state.last_total = total_final
                st.session_state.cart = []
                st.success(f"Đã tạo hóa đơn cho {table_num} thành công!")

            # Mã QR giả lập demo
            st.divider()
            st.subheader("📱 QR Thanh toán (Demo)")
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=PAYMENT_TABLE_{table_num}_TOTAL_{int(total_final)}"
            st.image(qr_url, caption="Quét mã QR để thanh toán giả lập")

# ---------------------------------------------------------
# TAB 2: CHIA BILL THÔNG MINH
# ---------------------------------------------------------
with tab2:
    st.subheader("👥 Chia bill thông minh cho nhóm")
    
    num_people = st.number_input("Số người tham gia chia tiền", min_value=1, value=2, step=1)
    bill_amount = st.number_input(
        "Số tiền cần chia (đ)", 
        min_value=0.0, 
        value=float(st.session_state.get('last_total', 135000)), 
        step=5000.0
    )

    if bill_amount > 0 and num_people > 0:
        per_person = bill_amount / num_people
        st.success(f"👉 **Mỗi người cần thanh toán:** :red[{per_person:,.0f} VNĐ]")

# ---------------------------------------------------------
# TAB 3: LỊCH SỬ GIAO DỊCH
# ---------------------------------------------------------
with tab3:
    st.subheader("📜 Lịch sử các đơn hàng đã tạo")
    if not st.session_state.history:
        st.info("Chưa có lịch sử giao dịch nào.")
    else:
        df_history = pd.DataFrame(st.session_state.history)
        df_history['items'] = df_history['items'].apply(lambda x: ", ".join(x))
        df_history.columns = ["Thời gian", "Bàn", "Các món đã đặt", "Tổng tiền (đ)", "Ghi chú"]
        st.dataframe(df_history, use_container_width=True)

# ---------------------------------------------------------
# TAB 4: THỐNG KÊ DOANH THU
# ---------------------------------------------------------
with tab4:
    st.subheader("📊 Thống kê doanh thu đơn giản")
    if not st.session_state.history:
        st.info("Chưa có dữ liệu doanh thu.")
    else:
        total_revenue = sum(order['total'] for order in st.session_state.history)
        total_orders = len(st.session_state.history)

        col1, col2 = st.columns(2)
        col1.metric("Tổng số đơn hàng", f"{total_orders} đơn")
        col2.metric("Tổng doanh thu", f"{total_revenue:,.0f} đ")

        st.divider()
        st.markdown("**Biểu đồ doanh thu theo từng đơn:**")
        df_history = pd.DataFrame(st.session_state.history)
        st.bar_chart(data=df_history, y="total")
