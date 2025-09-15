"""
streamlit_stock_app.py

Stock Market simulation with registration, buy/sell, portfolios, and dummy trading chart.
Run:
    streamlit run streamlit_stock_app.py
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# ----------------------------
# Config / Files / Data
# ----------------------------
DB_FILE = "users.json"
REG_FILE = "registrations.json"

AUTO_COMPANIES = {
    "Honda": 10,
    "Hyundai": 10,
    "Tata Motors": 10,
    "Mahindra & Mahindra": 10,
    "Maruti Suzuki": 10,
    "Ashok Leyland": 10
}
PETROLEUM_COMPANIES = {
    "Reliance Industries": 15,
    "Indian Oil Corporation": 15,
    "Bharat Petroleum": 15,
    "Hindustan Petroleum": 15,
    "Oil India": 15
}
STEEL_COMPANIES = {
    "Tata Steel": 20,
    "JSW Steel": 20,
    "Steel Authority of India (SAIL)": 20,
    "Jindal Steel & Power": 20,
    "NMDC Steel": 20
}

PRICES = {**AUTO_COMPANIES, **PETROLEUM_COMPANIES, **STEEL_COMPANIES}

# Chart defaults
CHART_PRICE_START = 100.0
CHART_STEP_STD = 0.5
CHART_POINTS = 200

# ----------------------------
# JSON helpers
# ----------------------------
def safe_json_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_users():
    return safe_json_load(DB_FILE, {})

def save_users(users):
    save_json(DB_FILE, users)

def load_registrations():
    return safe_json_load(REG_FILE, [])

def save_registration(entry):
    data = load_registrations()
    data.append(entry)
    save_json(REG_FILE, data)

# ----------------------------
# Dummy Trading Chart
# ----------------------------
def plot_dummy_chart(entry_price=CHART_PRICE_START, side="BUY"):
    xs = []
    ys = []
    last = entry_price
    for i in range(CHART_POINTS):
        step = np.random.normal(loc=0.0, scale=CHART_STEP_STD)
        last = max(1, last + step)
        xs.append(i)
        ys.append(last)

    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(xs, ys, label="Price")
    ax.axhline(entry_price, color="blue", linestyle="--", label="Entry")
    ax.set_title(f"Dummy Trading Chart ({side})")
    ax.set_xlabel("Ticks")
    ax.set_ylabel("Price")

    current = ys[-1]
    if side == "BUY":
        pl = current - entry_price
    else:
        pl = entry_price - current
    pct = (pl / entry_price) * 100

    st.write(f"📊 Current Price: {current:.2f}")
    st.write(f"💰 P/L: {pl:.2f} ({pct:.2f}%)")

    ax.legend()
    st.pyplot(fig)

# ----------------------------
# Streamlit App
# ----------------------------
st.title("📈 Stock Market Simulation")

menu = st.sidebar.selectbox("Menu", ["Register", "Login", "Admin", "Dummy Chart"])

if menu == "Register":
    st.subheader("New User Registration")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        users = load_users()
        if email in users:
            st.error("Email already registered!")
        else:
            users[email] = {
                "name": name,
                "password": password,
                "balance": 100,
                "shares": {c: 0 for c in AUTO_COMPANIES},
                "petroleum_shares": {c: 0 for c in PETROLEUM_COMPANIES},
                "steel_shares": {c: 0 for c in STEEL_COMPANIES},
                "bonus": 100
            }
            save_users(users)
            save_registration({"name": name, "email": email, "bonus": 100})
            st.success("✅ Registration successful! You got ₹100 bonus.")

elif menu == "Login":
    st.subheader("User Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_users()
        if email in users and users[email]["password"] == password:
            st.session_state["user"] = email
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

    if "user" in st.session_state:
        user_email = st.session_state["user"]
        user = load_users()[user_email]
        st.write(f"### Welcome {user['name']} 👋")
        st.write(f"💵 Balance: ₹{user['balance']}")

        sector = st.selectbox("Select Sector", ["Automobile", "Petroleum", "Steel"])
        if sector == "Automobile":
            companies = AUTO_COMPANIES
        elif sector == "Petroleum":
            companies = PETROLEUM_COMPANIES
        else:
            companies = STEEL_COMPANIES

        company = st.selectbox("Select Company", list(companies.keys()))
        qty = st.number_input("Quantity", min_value=1, value=1)
        price = PRICES.get(company, 0)
        st.write(f"💰 Price per share: ₹{price}")

        if st.button("Buy"):
            cost = price * qty
            if user["balance"] >= cost:
                user["balance"] -= cost
                if company in user["shares"]:
                    user["shares"][company] += qty
                elif company in user["petroleum_shares"]:
                    user["petroleum_shares"][company] += qty
                elif company in user["steel_shares"]:
                    user["steel_shares"][company] += qty
                users = load_users()
                users[user_email] = user
                save_users(users)
                st.success(f"Bought {qty} shares of {company} for ₹{cost}")
            else:
                st.error("Insufficient balance")

        if st.button("Sell"):
            if company in user["shares"] and user["shares"][company] >= qty:
                user["shares"][company] -= qty
                user["balance"] += price * qty
            elif company in user["petroleum_shares"] and user["petroleum_shares"][company] >= qty:
                user["petroleum_shares"][company] -= qty
                user["balance"] += price * qty
            elif company in user["steel_shares"] and user["steel_shares"][company] >= qty:
                user["steel_shares"][company] -= qty
                user["balance"] += price * qty
            else:
                st.error("Not enough shares to sell")
                st.stop()
            users = load_users()
            users[user_email] = user
            save_users(users)
            st.success(f"Sold {qty} shares of {company} for ₹{price*qty}")

        st.write("### Portfolio")
        st.json({
            "Automobile": user["shares"],
            "Petroleum": user["petroleum_shares"],
            "Steel": user["steel_shares"]
        })

        if st.button("📊 Open Dummy Trading Chart"):
            plot_dummy_chart(entry_price=price, side="BUY")

elif menu == "Admin":
    st.subheader("Admin Panel")
    pwd = st.text_input("Enter Admin Password", type="password")
    if st.button("Login as Admin"):
        if pwd == "admin123":
            st.success("Welcome, Admin")
            data = load_registrations()
            st.table(data)
        else:
            st.error("Wrong password")

elif menu == "Dummy Chart":
    st.subheader("Standalone Dummy Trading Chart")
    entry = st.number_input("Entry Price", min_value=1.0, value=100.0)
    side = st.selectbox("Side", ["BUY", "SELL"])
    if st.button("Generate Chart"):
        plot_dummy_chart(entry_price=entry, side=side)
