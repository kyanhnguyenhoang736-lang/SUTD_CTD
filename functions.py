# functions.py
import random
from datetime import datetime
import streamlit as st

# -------------------------
# DATA
# -------------------------
preset_combos = {
    "Milo Meal": {"items": ["Classic Waffle", "Milo"], "price": 4.0},
    "Chocolate Heaven": {"items": ["Chocolate Chip Waffle", "Ice Cream"], "price": 4.5},
    "Berry Blast": {"items": ["Strawberry Waffle", "Milo"], "price": 4.5},
}

component_prices = {
    "Batters": {"Classic": 0, "Pandan": 0.5, "Whole Grain": 0.75},
    "Fruits": {"Banana": 1, "Strawberry": 1, "Blueberry": 1, "None": 0, "Cherry": 1},
    "Syrups": {"Maple": 0.5, "Chocolate": 0.75, "Honey": 0.5, "None": 0},
    "Ice Creams": {"Vanilla": 1.5, "Chocolate": 1.5, "Strawberry": 1.5, "None": 0, "Salted Caramel": 2, "Oreo": 2},
}

drink_prices = {"None": 0, "Water": 1.0, "Milo": 2.0, "Sprite": 1.5, "Coke": 1, "Coke Zero": 0.7, "Choc Milkshake": 2.0}

waffle_words = ["SYRUP", "FRUIT", "SWEET", "HONEY", "MAPLE", "CREAM", "BERRY", "DOUGH", "SUGAR", "JELLY", "ICING", "CRISP"]


# -------------------------
# SESSION INITIALIZER
# -------------------------
def ensure_session():
    if "cart" not in st.session_state:
        st.session_state.cart = []
    if "discounts" not in st.session_state:
        st.session_state.discounts = {}
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "wordle" not in st.session_state:
        st.session_state.wordle = {"secret": None, "attempt": 1, "won": False, "guesses": [], "feedbacks": []}


# -------------------------
# SHOW CART - goes into check out page
# -------------------------
def show_cart():
    st.subheader("🛒 Your Cart")
    if not st.session_state.cart:
        st.info("Cart is empty.")
        return 0.0

    subtotal = 0.0
    for idx, item in enumerate(st.session_state.cart):
        name = item.get("name", "Item")
        details = item.get("details", "")
        unit_price = float(item.get("unit_price", item.get("price", 0.0)))
        qty = int(item.get("qty", 1))
        line_price = unit_price * qty

        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"**{idx+1}. {name}** — {qty} × ${unit_price:.2f}")
            st.caption(details)
        with col2:
            if st.button("Remove", key=f"remove_{idx}"):
                st.session_state.cart.pop(idx)
                st.rerun()

        subtotal += line_price
        st.divider()

    st.write(f"**Cart Subtotal: ${round(subtotal, 2)}**")
    return subtotal


# -------------------------
# ORDER SUMMARY
# -------------------------
def show_order_summary():
    subtotal = calculate_cart_total()
    check_automatic_discounts()
    final = apply_discounts(subtotal)
    discount_total = sum(st.session_state.discounts.values())
    discount_amount = subtotal - final

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Subtotal", f"${round(subtotal, 2)}")
    with col2:
        st.metric(f"Final ({int(discount_total*100)}% off)", f"${round(final,2)}",
                  delta=f"-${round(discount_amount,2)}" if discount_amount > 0 else None)
    if st.session_state.discounts:
        st.markdown("**Active discounts:**")
        for k, v in st.session_state.discounts.items():
            if v > 0:
                st.write(f"- {k.replace('_', ' ').title()}: {int(v*100)}%")
    return subtotal, discount_total, final


# -------------------------
# CART HELPERS
# -------------------------
def calculate_cart_total():
    ensure_session()
    total = 0.0
    for it in st.session_state.cart:
        if "unit_price" in it and "qty" in it:
            total += float(it["unit_price"]) * int(it["qty"])
        else:
            total += float(it.get("price", 0.0))
    return total

def apply_discounts(total):
    ensure_session()
    discount_total = sum(st.session_state.discounts.values())
    return total * (1 - discount_total)


# -------------------------------------
# BUILD YOUR OWN WAFFLE HELPERS
# -------------------------------------

def limit_selection(selected, max_items, label="items"):
    if len(selected) > max_items:
        st.warning(f"⚠️ You can only select up to {max_items} {label}.")
        return selected[:max_items]
    return selected

def calculate_selected_total(selected_items, price_dict):
    return sum(price_dict.get(item, 0.0) for item in selected_items if item in price_dict)

def calculate_waffle_price(qty, base=2.0, decay=0.2):
    total = 0.0
    for i in range(qty):
        price = max(0.0, base - i * decay)
        total += price
    return total


# -------------------------
# DISCOUNT RULES
# -------------------------
def check_automatic_discounts():
    ensure_session()
    #calculates total waffles 
    waffle_count = 0
    for it in st.session_state.cart:
        name = it.get("name", "").lower()
        details = str(it.get("details", "")).lower()
        qty = int(it.get("qty", 1))
        if "waffle" in name or "waffle" in details:
            waffle_count += qty
    # applies discount for number of waffles 
    if waffle_count > 4:
        st.session_state.discounts["stack_n_save"] = 0.15
    elif waffle_count >= 3:
        st.session_state.discounts["stack_n_save"] = 0.10
    elif waffle_count == 2:
        st.session_state.discounts["stack_n_save"] = 0.05

# -------------------------
# STUDENT CODE VALIDATION
# -------------------------
def validate_student_code(code: str) -> bool:
    if not isinstance(code, str):
        return False
    code = code.strip()
    if len(code) != 7 or not code.isdigit():
        return False
    if not code.startswith("10"):
        return False
    else:
        return True 


# -------------------------
# WORDLE HELPERS
# -------------------------
def init_wordle():
    ensure_session()
    if not st.session_state.wordle.get("secret"):
        st.session_state.wordle["secret"] = random.choice(waffle_words)
        st.session_state.wordle["attempt"] = 1
        st.session_state.wordle["won"] = False
        st.session_state.wordle["guesses"] = []
        st.session_state.wordle["feedbacks"] = []

def reset_wordle():
    st.session_state.wordle = {
        "secret": None, "attempt": 1,
        "won": False, "guesses": [], "feedbacks": []
        }
    init_wordle()
    
def feedback_for_guess(guess, secret):
    feedback = ""
    for i, ch in enumerate(guess):
        if i < len(secret) and ch == secret[i]:
            feedback += f"{ch} : 🟩 "
        elif ch in secret:
            feedback += f"{ch} : 🟨 "
        else:
            feedback += f"{ch} : ⬜ "
    return feedback
