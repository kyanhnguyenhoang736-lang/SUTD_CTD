# app.py
"I'm Anh"
import streamlit as st
from functions import (
    ensure_session, preset_combos, component_prices, drink_prices,
     apply_discounts, check_automatic_discounts,
    limit_selection, calculate_selected_total, calculate_waffle_price,
    validate_student_code, init_wordle, reset_wordle,
    feedback_for_guess,show_cart,show_order_summary
)
st.set_page_config(
    page_title = "Waffle World", page_icon = "🧇", layout = "wide", initial_sidebar_state = "expanded"
    )
ensure_session()

# -------------------------
# HOME PAGE
# -------------------------
def home_page():
    st.title("🧇 Waffle World")

    st.markdown("## Welcome!")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🍀 About Waffle World")
        st.markdown(
            """
            Welcome to **Waffle World**, the coziest spot for delicious, handcrafted waffles! 🧇  

            - We use only **fresh ingredients** to create sweet and savory waffles you'll love.  
            - Customize your waffle just the way you like it, or enjoy our preset combo meals for a quick delight.  

            Our mission is simple: **bring joy, one waffle at a time**. ✨
            """
        )
        st.markdown("---")
        st.subheader("💸 Discounts & Offers")
        st.markdown(
            "Maximize your waffle happiness with our special deals:"
            "- **Stack & Save:** buy multiple waffles and get increasing discounts (2 waffles = 5%, 3 waffles = 10%, 5+ = 15%).\n"
            "- **Student Discount:** valid 7-digit student code starting with 10X gives 5% off.\n"
            "- **Wordle Bonus:** win the mini-game for an extra 10% off your order!"
            "Combine discounts and enjoy the sweetest savings! 🍓🧇"
        )
    st.markdown("---")
    with col2:
        st.image("waffle_img1.jpg")
        st.markdown("what are you waiting for!")
        col3, col4 = st.columns(2)
        with col3:
            if st.button("Order Now"):
                st.session_state.page = "Order"
                st.rerun()
        with col4:
            if st.button("Play Wordle"):
                st.session_state.page = "Wordle"
                st.rerun()
    
    
    st.sidebar.markdown("Use the sidebar to navigate between pages.")
    show_order_summary()


# -------------------------
# ORDER PAGE
# -------------------------
def order_page():
    st.header("🍽 Order Now")
    st.info(
        "Discounts apply automatically:"
        " **Stack & Save** - the more waffles you buy, the more discounts you get" \
        " **Student Discount**, "
        " **Wordle Bonus**. "
    )


    # Presets
    st.subheader("Preset Combo Meals")
    for name, info in preset_combos.items():
        cols = st.columns([4, 1])
        with cols[0]:
            st.write(f"**{name}** - includes {', '.join(info['items'])}")
            st.caption(f"${info['price']:.2f}")
        with cols[1]:
            if st.button(f"Add {name}", key=f"add_{name}"):
                st.session_state.cart.append({
                    "name": name,
                    "details": ", ".join(info["items"]),
                    "unit_price": info["price"],
                    "qty": 1,
                    "price": info["price"]
                })
                check_automatic_discounts()
                st.success(f"{name} added to cart!")

    st.markdown("---")
    st.subheader("Build Your Own Waffle")
    qty = st.number_input("Number of waffles", 1, 4, 1)

    all_toppings = {**component_prices["Fruits"], **component_prices["Ice Creams"]}
    topping_raw = st.multiselect("Choose up to 3 toppings", [f"{t} (+${p:.2f})" for t, p in all_toppings.items()])
    toppings = [t.split(" (+")[0] for t in topping_raw]
    toppings = limit_selection(toppings, 3, "toppings")
    topping_total = calculate_selected_total(toppings, all_toppings)

    syrup_raw = st.multiselect("Choose up to 2 syrups", [f"{s} (+${p:.2f})" for s, p in component_prices["Syrups"].items()])
    syrups = [s.split(" (+")[0] for s in syrup_raw]
    syrups = limit_selection(syrups, 2, "syrups")
    syrup_total = calculate_selected_total(syrups, component_prices["Syrups"])

    drink_raw = st.selectbox("Choose a drink", [f"{d} (+${p:.2f})" for d, p in drink_prices.items()])
    drink_name = drink_raw.split(" (+")[0]
    drink_price = drink_prices[drink_name]

    unit_waffle_price = calculate_waffle_price(1, base=2.0, decay=0.2) + topping_total + syrup_total + drink_price
    total_waffles = calculate_waffle_price(qty, base=2.0, decay=0.2) + topping_total + syrup_total + drink_price

    st.markdown(f"### 💰 Total for {qty} waffles: ${round(total_waffles,2)}")

    if st.button("Add Custom Waffle to Cart"):
        details = f"{qty}x waffle with {', '.join(toppings or ['no toppings'])}, {', '.join(syrups or ['no syrup'])}, Drink: {drink_name}"
        st.session_state.cart.append({
            "name": "Custom Waffle",
            "details": details,
            "unit_price": round(unit_waffle_price, 2),
            "qty": int(qty),
            "price": round(unit_waffle_price * int(qty), 2)
        })
        check_automatic_discounts()
        st.success("Custom waffle added to cart!")

    st.markdown("---")
    st.subheader("Student Discount")
    code = st.text_input("Enter student code (optional)")
    if st.button("Apply Student Code"):
        if validate_student_code(code):
            st.session_state.discounts["student"] = 0.05
            st.success("Student discount applied (5%)")
        else:
            st.warning("Invalid student code.")

    st.markdown("---")
    show_order_summary()


# -------------------------
# WORDLE PAGE
# -------------------------
def wordle_page():
    st.header("🎮 Waffle Wordle")
    init_wordle()
    secret = st.session_state.wordle["secret"]
    attempt = st.session_state.wordle["attempt"]
    won = st.session_state.wordle["won"]

    if st.session_state.wordle.get("guesses"):
        st.markdown("**Previous guesses**")
        for g, fb in zip(st.session_state.wordle["guesses"], st.session_state.wordle["feedbacks"]):
            st.write(f"- {g.upper()} → {fb}")

    guess = st.text_input("Enter a 5-letter word").upper()
    if st.button("Submit Guess"):
        if won:
            st.info("Already solved this round.")
        elif not guess or len(guess) != len(secret):
            st.warning(f"Enter a {len(secret)}-letter word.")
        else:
            fb = feedback_for_guess(guess, secret)
            st.session_state.wordle["guesses"].append(guess)
            st.session_state.wordle["feedbacks"].append(fb)
            if guess == secret:
                st.success("🎉 Correct! 10% discount applied.")
                st.session_state.discounts["wordle"] = 0.10
                st.session_state.wordle["won"] = True
            else:
                st.write(fb)
                st.session_state.wordle["attempt"] += 1
                if st.session_state.wordle["attempt"] > 5:
                    st.error(f"Out of attempts! The word was {secret}.")
                    reset_wordle()

    if st.button("Back to Home"):
        st.session_state.page = "Home"
        st.rerun()

    st.markdown("---")
    show_order_summary()


# -------------------------
# CHECKOUT PAGE
# -------------------------
def checkout_page():
    st.header("🧾 Checkout")
    subtotal = show_cart()
    if subtotal == 0:
        return
    show_order_summary()
    if st.button("Complete Order"):
        st.success("✅ Order placed successfully!")
        for item in st.session_state.cart:
            st.write(f"- {item['name']} (${item['price']:.2f})")
        final = apply_discounts(subtotal)
        st.write(f"**Final Total:** ${round(final,2)}")
        st.session_state.cart = []
        st.session_state.discounts = {}
        reset_wordle()


# -------------------------
# SIDEBAR NAV
# -------------------------
st.sidebar.title("Navigation")
if st.sidebar.button("Home"):
    st.session_state.page = "Home"
if st.sidebar.button("Order Now"):
    st.session_state.page = "Order"
if st.sidebar.button("Wordle"):
    st.session_state.page = "Wordle"
if st.sidebar.button("Checkout"):
    st.session_state.page = "Checkout"
if st.sidebar.button("Reset App"):
    st.session_state.cart = []
    st.session_state.discounts = {}
    reset_wordle()
    st.session_state.page = "Home"
    st.sidebar.success("✅ App fully reset.")

# -------------------------
# ROUTING
# -------------------------
page = st.session_state.get("page", "Home")
if page == "Home":
    home_page()
elif page == "Order":
    order_page()
elif page == "Wordle":
    wordle_page()
elif page == "Checkout":
    checkout_page()
else:
    home_page()
