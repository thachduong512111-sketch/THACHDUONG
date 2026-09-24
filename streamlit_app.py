import streamlit as st


st.set_page_config(
    page_title="Đặt món nhà hàng",
    page_icon="🍽️",
    layout="wide",
)

# Dữ liệu mẫu của thực đơn. Có thể thay thế bằng dữ liệu từ database/API.
MENU = [
    {"name": "Phở bò đặc biệt", "category": "Món chính", "price": 65000, "description": "Phở bò truyền thống với tái, nạm và bò viên."},
    {"name": "Cơm tấm sườn nướng", "category": "Món chính", "price": 70000, "description": "Sườn nướng mật ong dùng kèm cơm tấm, bì và đồ chua."},
    {"name": "Mì xào hải sản", "category": "Món chính", "price": 85000, "description": "Mì xào cùng tôm, mực và rau củ tươi."},
    {"name": "Gỏi cuốn tôm thịt", "category": "Khai vị", "price": 45000, "description": "4 cuốn gỏi cuốn dùng kèm nước chấm đặc biệt."},
    {"name": "Khoai tây chiên", "category": "Khai vị", "price": 35000, "description": "Khoai tây chiên giòn, rắc phô mai."},
    {"name": "Salad rau trộn", "category": "Khai vị", "price": 40000, "description": "Rau xanh theo mùa với sốt mè rang."},
    {"name": "Trà đào cam sả", "category": "Đồ uống", "price": 35000, "description": "Trà đào thơm mát cùng cam tươi và sả."},
    {"name": "Nước ép dưa hấu", "category": "Đồ uống", "price": 30000, "description": "Nước ép dưa hấu nguyên chất."},
    {"name": "Cà phê sữa đá", "category": "Đồ uống", "price": 30000, "description": "Cà phê rang xay pha phin cùng sữa đặc."},
]


def money(value: int) -> str:
    """Định dạng số tiền theo kiểu hiển thị Việt Nam."""
    return f"{value:,.0f} ₫".replace(",", ".")


def add_to_cart(item: dict) -> None:
    cart = st.session_state.cart
    name = item["name"]
    if name in cart:
        cart[name]["quantity"] += 1
    else:
        cart[name] = {
            "name": name,
            "price": item["price"],
            "quantity": 1,
        }


if "cart" not in st.session_state:
    st.session_state.cart = {}
if "order_message" not in st.session_state:
    st.session_state.order_message = None

st.title("🍽️ Đặt món nhà hàng")
st.caption("Chọn món ăn, số lượng và gửi yêu cầu đến bếp một cách nhanh chóng.")

if st.session_state.order_message:
    st.success(st.session_state.order_message)
    st.session_state.order_message = None

menu_col, cart_col = st.columns([1.65, 1], gap="large")

with menu_col:
    st.subheader("📖 Thực đơn")
    categories = ["Tất cả"] + sorted({item["category"] for item in MENU})
    selected_category = st.selectbox("Lọc theo danh mục", categories)

    filtered_menu = [
        item for item in MENU
        if selected_category == "Tất cả" or item["category"] == selected_category
    ]

    for item in filtered_menu:
        with st.container(border=True):
            item_col, action_col = st.columns([4, 1])
            with item_col:
                st.markdown(f"**{item['name']}**  ")
                st.caption(f"{item['category']} · {item['description']}")
                st.markdown(f"### {money(item['price'])}")
            with action_col:
                st.write("")
                if st.button("Thêm", key=f"add_{item['name']}", use_container_width=True):
                    add_to_cart(item)
                    st.toast(f"Đã thêm {item['name']} vào giỏ hàng", icon="✅")
                    st.rerun()

with cart_col:
    st.subheader("🛒 Giỏ hàng")

    if not st.session_state.cart:
        st.info("Giỏ hàng đang trống. Hãy chọn món từ thực đơn.")
    else:
        for name, item in list(st.session_state.cart.items()):
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.caption(f"{money(item['price'])} / món")
                quantity_col, total_col = st.columns([1.2, 1])
                with quantity_col:
                    decrease, quantity, increase = st.columns([1, 1.2, 1])
                    with decrease:
                        if st.button("−", key=f"decrease_{name}", use_container_width=True):
                            item["quantity"] -= 1
                            if item["quantity"] <= 0:
                                del st.session_state.cart[name]
                            st.rerun()
                    with quantity:
                        st.markdown(
                            f"<div style='text-align:center;padding-top:5px'>{item['quantity']}</div>",
                            unsafe_allow_html=True,
                        )
                    with increase:
                        if st.button("+", key=f"increase_{name}", use_container_width=True):
                            item["quantity"] += 1
                            st.rerun()
                with total_col:
                    item_total = item["price"] * item["quantity"]
                    st.markdown(f"**{money(item_total)}**")
                if st.button("🗑️ Xóa món", key=f"remove_{name}"):
                    del st.session_state.cart[name]
                    st.rerun()

        subtotal = sum(item["price"] * item["quantity"] for item in st.session_state.cart.values())
        st.divider()
        st.markdown(f"## Tổng cộng: {money(subtotal)}")

    st.divider()
    st.subheader("📋 Thông tin đơn hàng")
    table_number = st.selectbox("Chọn số bàn", [f"Bàn {number}" for number in range(1, 21)])
    kitchen_note = st.text_area(
        "Ghi chú cho bếp",
        placeholder="Ví dụ: Không hành, ít cay, thêm nước chấm...",
        height=90,
    )

    submit_order = st.button(
        "📤 Gửi đơn hàng",
        type="primary",
        use_container_width=True,
        disabled=not bool(st.session_state.cart),
    )

    if submit_order:
        if not st.session_state.cart:
            st.warning("Vui lòng chọn ít nhất một món trước khi gửi đơn.")
        else:
            item_count = sum(item["quantity"] for item in st.session_state.cart.values())
            st.session_state.order_message = (
                f"Đã gửi đơn thành công cho {table_number} ({item_count} món). "
                "Bếp sẽ chuẩn bị món ngay!"
            )
            st.session_state.cart = {}
            st.rerun()

st.divider()
st.caption("© Nhà hàng · Hệ thống đặt món nội bộ")
