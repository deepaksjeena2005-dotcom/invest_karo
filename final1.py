import os
import json
import webbrowser
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from PIL import Image, ImageTk
import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
import pandas as pd


# ============================
# Constants & Configurations
# ============================
DB_FILE = "users.json"
REG_FILE = "registrations.json"
ADMIN_PASSWORD = "admin123"

AUTO_COMPANIES = {
    "Honda": "https://www.screener.in/company/522064/",
    "Hyundai": "https://www.screener.in/company/540005/",
    "Tata Motors": "https://www.screener.in/company/TATAMOTORS/",
    "Mahindra & Mahindra": "https://www.screener.in/company/M%26M/",
    "Maruti Suzuki": "https://www.screener.in/company/MARUTI/",
    "Ashok Leyland": "https://www.screener.in/company/ASHOKLEY/"
}
PETROLEUM_COMPANIES = {
    "Reliance Industries": "https://www.screener.in/company/RELIANCE/consolidated/",
    "Indian Oil Corporation": "https://www.screener.in/company/IOC/",
    "Bharat Petroleum": "https://www.screener.in/company/BPCL/",
    "Hindustan Petroleum": "https://www.screener.in/company/HINDPETRO/",
    "Oil India": "https://www.screener.in/company/OIL/"
}
STEEL_COMPANIES = {
    "Tata Steel": "https://www.screener.in/company/TATASTEEL/",
    "JSW Steel": "https://www.screener.in/company/JSWSTEEL/",
    "Steel Authority of India (SAIL)": "https://www.screener.in/company/SAIL/",
    "Jindal Steel & Power": "https://www.screener.in/company/JINDALSTEL/",
    "NMDC Steel": "https://www.screener.in/company/NMDCSTEEL/"
}
GOLD_COMPANIES = {
    "Titan": "https://www.screener.in/company/TITAN/",
    "Muthoot Finance": "https://www.screener.in/company/MUTHOOTFIN/",
    "Manappuram Finance": "https://www.screener.in/company/MANAPPURAM/",
    "Rajesh Exports": "https://www.screener.in/company/RAJESHEXPO/",
    "PC Jeweller": "https://www.screener.in/company/PCJEWELLER/"
}

PRICES = {
    **{c: 10 for c in AUTO_COMPANIES},
    **{c: 15 for c in PETROLEUM_COMPANIES},
    **{c: 20 for c in STEEL_COMPANIES},
    **{c: 30 for c in GOLD_COMPANIES}
}

CHART_PRICE_START = 100.0
CHART_MAX_POINTS = 200
CHART_STEP_STD = 0.5
CHART_UPDATE_INTERVAL = 800


# ============================
# JSON Helpers
# ============================
def safe_json_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            c = f.read().strip()
            return json.loads(c) if c else default
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_users():
    return safe_json_load(DB_FILE, {})

def save_users(users):
    save_json(DB_FILE, users)

def load_registrations():
    return safe_json_load(REG_FILE, [])

def save_registration(entry):
    regs = load_registrations()
    regs.append(entry)
    save_json(REG_FILE, regs)

def get_default_shares(companies):
    return {c: 0 for c in companies}

def open_link(url):
    webbrowser.open(url)

def load_image(path, size=None):
    try:
        if not os.path.exists(path):
            return None
        img = Image.open(path)
        if size:
            img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

def validate_email(email):
    return '@' in email and '.' in email.split('@')[-1]

def validate_password(pwd):
    return len(pwd) >= 6


# ============================
# Authentication Manager
# ============================
class AuthManager:
    def __init__(self, root):
        self.root = root

    def signup_user(self, name, email, password):
        if not (name and email and password):
            messagebox.showerror("Error", "All fields are required!")
            return False
        if not validate_email(email):
            messagebox.showerror("Error", "Invalid email address!")
            return False
        if not validate_password(password):
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return False
        users = load_users()
        if email in users:
            messagebox.showerror("Error", "Email already registered! Please login.")
            return False
        users[email] = {
            "name": name,
            "password": password,
            "balance": 100,
            "shares": get_default_shares(AUTO_COMPANIES),
            "petroleum_shares": get_default_shares(PETROLEUM_COMPANIES),
            "steel_shares": get_default_shares(STEEL_COMPANIES),
            "gold_shares": get_default_shares(GOLD_COMPANIES),
            "last_buy_price": {},
            "bonus": 100,
            "created": str(datetime.datetime.now())
        }
        save_users(users)
        save_registration({"name": name, "email": email, "bonus": 100})
        messagebox.showinfo("Success", f"Welcome {name}! Signup successful with ₹100 bonus.")
        return True

    def signin_user(self, email, password):
        users = load_users()
        if email not in users:
            messagebox.showerror("Error", "User not found! Please signup first.")
            return None
        if users[email]["password"] != password:
            messagebox.showerror("Error", "Incorrect password!")
            return None
        messagebox.showinfo("Welcome", f"Welcome back {users[email]['name']}! Balance: ₹{users[email]['balance']}")
        return email


# ============================
# Candlestick Chart
# ============================
def open_dummy_candlestick_chart(user_email, company, entry_price, title="Trading Chart"):
    ENTRY_PRICE = float(entry_price)
    users = load_users()
    user_data = users.get(user_email)
    if not user_data:
        messagebox.showerror("Error", "User not found!")
        return

    ohlc_data = []
    last_close = ENTRY_PRICE

    chart_win = tk.Toplevel()
    chart_win.title(title)
    chart_win.geometry("950x600")
    chart_win.configure(bg="black")

    fig = mpf.figure(style="charles", figsize=(9, 4.5), facecolor="black")
    ax = fig.add_subplot(1, 1, 1)
    fig.suptitle(title, color="white", fontsize=15)

    canvas = FigureCanvasTkAgg(fig, master=chart_win)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def simulate_next_ohlc(val):
        o = val
        c = max(0.1, o + np.random.normal(0, CHART_STEP_STD))
        h = max(o, c) + abs(np.random.normal(0, CHART_STEP_STD * 0.7))
        l = min(o, c) - abs(np.random.normal(0, CHART_STEP_STD * 0.7))
        l = max(l, 0.01)
        return [o, h, l, c]

    def redraw_chart():
        if len(ohlc_data) == 0:
            return
        df = pd.DataFrame(ohlc_data, columns=["Open", "High", "Low", "Close"])
        df["Volume"] = 1
        df.index = pd.date_range(start="2024-01-01", periods=len(ohlc_data), freq="T")
        ax.clear()
        mpf.plot(df, ax=ax, type="candle", style="charles", volume=False)
        current_price = df.iloc[-1]["Close"]
        ax.set_facecolor("black")
        ax.set_title(f"{title}\nCurrent ₹{current_price:.2f}", color="white")
        canvas.draw_idle()

    def update_chart():
        nonlocal last_close
        candle = simulate_next_ohlc(last_close)
        ohlc_data.append(candle)
        last_close = candle[3]
        if len(ohlc_data) > CHART_MAX_POINTS:
            ohlc_data.pop(0)
        redraw_chart()

    stop_flag = [False]

    def loop():
        if stop_flag[0]:
            return
        update_chart()
        chart_win.after(CHART_UPDATE_INTERVAL, loop)

    chart_win.protocol("WM_DELETE_WINDOW", lambda: (stop_flag.__setitem__(0, True), chart_win.destroy()))
    loop()


# ============================
# Trading / Portfolio Windows
# ============================
def show_portfolio_window(user_email, sector):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return
    user_data = users[user_email]
    if sector == "auto":
        portfolio = user_data.get("shares", {})
        comp = AUTO_COMPANIES
        title = "🚗 Automobile Portfolio"
    elif sector == "petroleum":
        portfolio = user_data.get("petroleum_shares", {})
        comp = PETROLEUM_COMPANIES
        title = "⛽ Petroleum Portfolio"
    elif sector == "steel":
        portfolio = user_data.get("steel_shares", {})
        comp = STEEL_COMPANIES
        title = "🏭 Steel Portfolio"
    elif sector == "gold":
        portfolio = user_data.get("gold_shares", {})
        comp = GOLD_COMPANIES
        title = "🥇 Gold Portfolio"
    else:
        return

    win = tk.Toplevel()
    win.title(f"{user_data['name']} - {title}")
    win.geometry("650x500")
    tk.Label(win, text=title, font=("Arial", 16, "bold"), bg="yellow").pack(pady=10, fill="x")

    frame = tk.Frame(win, bg="white")
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    headers = ["Company", "Shares", "Unit Price", "Total Value", "View"]
    for i, h in enumerate(headers):
        tk.Label(frame, text=h, font=("Arial", 12, "bold"), width=15, bg="lightgray", relief="ridge").grid(row=0, column=i)

    total_val = 0
    for i, (company, qty) in enumerate(portfolio.items(), start=1):
        price = PRICES.get(company, 0)
        val = qty * price
        total_val += val
        tk.Label(frame, text=company, width=15, bg="white").grid(row=i, column=0)
        tk.Label(frame, text=qty, width=15, bg="white").grid(row=i, column=1)
        tk.Label(frame, text=f"₹{price}", width=15, bg="white").grid(row=i, column=2)
        tk.Label(frame, text=f"₹{val}", width=15, bg="white").grid(row=i, column=3)
        tk.Button(frame, text="📊", command=lambda url=comp[company]: open_link(url)).grid(row=i, column=4)

    tk.Label(win, text=f"Total Portfolio Value: ₹{total_val}", font=("Arial", 14, "bold"),
             bg="lightblue").pack(fill="x", pady=8)


def load_company_logo(company_name):
    logo_path = f"logos/{company_name.lower().replace(' ', '_')}.png"
    try:
        img = Image.open(logo_path)
        img = img.resize((100, 100), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

def buy_sell_window(user_email):
    users = load_users()
    user_data = users[user_email]

    win = tk.Toplevel()
    win.title(f"Trade - {user_data['name']}")
    win.geometry("600x650")

    bal_var = tk.StringVar(value=f"Balance: ₹{user_data['balance']}")
    tk.Label(win, textvariable=bal_var, font=("Arial", 14, "bold"), fg="green").pack(pady=8)

    tk.Label(win, text="Select Sector:", font=("Arial", 12, "bold")).pack()
    sector_var = tk.StringVar()
    sector_cb = ttk.Combobox(win, textvariable=sector_var, state="readonly",
                             values=["Automobile", "Petroleum", "Steel", "Gold"])
    sector_cb.pack(pady=5)

    tk.Label(win, text="Select Company:", font=("Arial", 12, "bold")).pack()
    comp_var = tk.StringVar()
    comp_cb = ttk.Combobox(win, textvariable=comp_var, state="readonly")
    comp_cb.pack(pady=5)

    # Insert company logo label here
    logo_label = tk.Label(win, bg="white")
    logo_label.pack(pady=10)

    def update_companies(event=None):
        sec = sector_var.get()
        if sec == "Automobile": comp_cb["values"] = list(AUTO_COMPANIES.keys())
        elif sec == "Petroleum": comp_cb["values"] = list(PETROLEUM_COMPANIES.keys())
        elif sec == "Steel": comp_cb["values"] = list(STEEL_COMPANIES.keys())
        elif sec == "Gold": comp_cb["values"] = list(GOLD_COMPANIES.keys())

    sector_cb.bind("<<ComboboxSelected>>", update_companies)

    def update_logo(event=None):
        company = comp_var.get()
        img = load_company_logo(company)
        if img:
            logo_label.config(image=img, text="")
            logo_label.image = img  # Keep reference
        else:
            logo_label.config(image="C:\\Users\\neham\\Downloads\\IK.png.png", text="No logo available", font=("Arial", 10, "italic"), fg="red")

    comp_cb.bind("<<ComboboxSelected>>", update_logo)

    qty_entry = tk.Entry(win, font=("Arial", 12))
    qty_entry.pack(pady=6)

    def commit():
        save_users(users)
        bal_var.set(f"Balance: ₹{user_data['balance']}")

    def buy():
        c = comp_var.get()
        if not c:
            messagebox.showerror("Error", "Select a company.")
            return
        qty = qty_entry.get()
        if not qty.isdigit() or int(qty) <= 0:
            messagebox.showerror("Error", "Enter positive quantity.")
            return
        qty = int(qty)
        cost = PRICES[c] * qty
        if user_data["balance"] < cost:
            messagebox.showerror("Error", "Insufficient balance.")
            return
        user_data["balance"] -= cost
        if c in AUTO_COMPANIES:
            user_data["shares"][c] += qty
        elif c in PETROLEUM_COMPANIES:
            user_data["petroleum_shares"][c] += qty
        elif c in STEEL_COMPANIES:
            user_data["steel_shares"][c] += qty
        elif c in GOLD_COMPANIES:
            user_data["gold_shares"][c] += qty
        user_data["last_buy_price"][c] = PRICES[c]
        commit()
        messagebox.showinfo("Success", f"Bought {qty} shares of {c} for ₹{cost}.")
        qty_entry.delete(0, tk.END)

    def sell():
        c = comp_var.get()
        if not c:
            messagebox.showerror("Error", "Select a company.")
            return
        qty = qty_entry.get()
        if not qty.isdigit() or int(qty) <= 0:
            messagebox.showerror("Error", "Enter positive quantity.")
            return
        qty = int(qty)
        sh_dict = {}
        if c in AUTO_COMPANIES:
            sh_dict = user_data["shares"]
        elif c in PETROLEUM_COMPANIES:
            sh_dict = user_data["petroleum_shares"]
        elif c in STEEL_COMPANIES:
            sh_dict = user_data["steel_shares"]
        elif c in GOLD_COMPANIES:
            sh_dict = user_data["gold_shares"]
        if sh_dict.get(c, 0) < qty:
            messagebox.showerror("Error", "Not enough shares to sell.")
            return
        sh_dict[c] -= qty
        earnings = PRICES[c] * qty
        user_data["balance"] += earnings
        commit()
        messagebox.showinfo("Success", f"Sold {qty} shares of {c} for ₹{earnings}.")
        qty_entry.delete(0, tk.END)

    tk.Button(win, text="Buy", font=("Arial", 12, "bold"), bg="green", fg="white", command=buy).pack(pady=5)
    tk.Button(win, text="Sell", font=("Arial", 12, "bold"), bg="red", fg="white", command=sell).pack(pady=5)
    tk.Button(win, text="Open Chart", font=("Arial", 14),
              command=lambda: open_candlestick_chart(user_email, comp_var.get() or "Honda", PRICES.get(comp_var.get() or "Honda", 100))).pack(pady=12)

    # Portfolio buttons
    portfolio_frame = tk.Frame(win)
    portfolio_frame.pack(pady=10)
    tk.Button(portfolio_frame, text="🚗 Auto Portfolio", font=("Arial", 11), bg="lightblue",
              command=lambda: show_portfolio_window(user_email, "auto")).grid(row=0, column=0, padx=5)
    tk.Button(portfolio_frame, text="⛽ Petroleum Portfolio", font=("Arial", 11), bg="orange",
              command=lambda: show_portfolio_window(user_email, "petroleum")).grid(row=0, column=1, padx=5)
    tk.Button(portfolio_frame, text="🏭 Steel Portfolio", font=("Arial", 11), bg="lightgray",
              command=lambda: show_portfolio_window(user_email, "steel")).grid(row=0, column=2, padx=5)
    tk.Button(portfolio_frame, text="🥇 Gold Portfolio", font=("Arial", 11), bg="gold",
              command=lambda: show_portfolio_window(user_email, "gold")).grid(row=0, column=3, padx=5)

    tk.Button(win, text="Refresh Balance", font=("Arial", 11), bg="yellow", command=commit).pack(pady=5)
    tk.Button(win, text="Logout", font=("Arial", 11), bg="orange", command=win.destroy).pack(side="left", padx=10, pady=10)
    tk.Button(win, text="Exit App", font=("Arial", 11), bg="red", fg="white", command=win.quit).pack(side="right", padx=10, pady=10)

    # Portfolio buttons
    port_frame = tk.Frame(win)
    port_frame.pack(pady=10)
    tk.Button(port_frame, text="🚗 Auto Portfolio", command=lambda: show_portfolio_window(user_email, "auto")).grid(row=0, column=0, padx=5)
    tk.Button(port_frame, text="⛽ Petro Portfolio", command=lambda: show_portfolio_window(user_email, "petroleum")).grid(row=0, column=1, padx=5)
    tk.Button(port_frame, text="🏭 Steel Portfolio", command=lambda: show_portfolio_window(user_email, "steel")).grid(row=0, column=2, padx=5)
    tk.Button(port_frame, text="🥇 Gold Portfolio", command=lambda: show_portfolio_window(user_email, "gold")).grid(row=0, column=3, padx=5)

    tk.Button(win, text="Refresh Balance", bg="yellow", command=commit).pack(pady=5)
    tk.Button(win, text="Logout", bg="orange", command=win.destroy).pack(side="left", padx=10, pady=5)
    tk.Button(win, text="Exit App", bg="red", fg="white", command=win.quit).pack(side="right", padx=10, pady=5)


# ============================
# Admin Dashboard
# ============================
def check_admin_password():
    admin_win = tk.Toplevel()
    admin_win.title("Admin Login")
    admin_win.geometry("300x200")
    tk.Label(admin_win, text="🔐 Admin Password").pack(pady=10)
    pwd_entry = tk.Entry(admin_win, show="*")
    pwd_entry.pack(pady=10)

    def verify():
        if pwd_entry.get() == ADMIN_PASSWORD:
            admin_win.destroy()
            show_admin_dashboard()
        else:
            messagebox.showerror("Denied", "Wrong password!")

    tk.Button(admin_win, text="Login", command=verify).pack(pady=10)


def show_admin_dashboard():
    users = load_users()
    dash = tk.Toplevel()
    dash.title("Admin Dashboard")
    dash.geometry("1000x600")
    headers = ["Name", "Email", "Balance"]
    for i, h in enumerate(headers):
        tk.Label(dash, text=h, relief="ridge", width=20).grid(row=0, column=i)
    for r, (email, user) in enumerate(users.items(), 1):
        tk.Label(dash, text=user["name"]).grid(row=r, column=0)
        tk.Label(dash, text=email).grid(row=r, column=1)
        tk.Label(dash, text="₹" + str(user["balance"])).grid(row=r, column=2)


# ============================
# Main GUI
# ============================
def create_main_window():
    root = tk.Tk()
    root.title("InvestKaro - Stock Market Simulator")
    root.geometry("500x600")

    auth = AuthManager(root)
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # Signup
    frame1 = tk.Frame(notebook); notebook.add(frame1, text="Sign Up")
    tk.Label(frame1, text="Signup", font=("Arial", 18)).pack()
    e1, e2, e3 = tk.Entry(frame1), tk.Entry(frame1), tk.Entry(frame1, show="*")
    for w in [("Name", e1), ("Email", e2), ("Password", e3)]:
        tk.Label(frame1, text=w[0]).pack(); w[1].pack()
    def do_signup():
        if auth.signup_user(e1.get(), e2.get(), e3.get()):
            e1.delete(0, tk.END); e2.delete(0, tk.END); e3.delete(0, tk.END)
            notebook.select(1)
    tk.Button(frame1, text="Create Account", command=do_signup).pack(pady=10)

    # Login
    frame2 = tk.Frame(notebook); notebook.add(frame2, text="Login")
    tk.Label(frame2, text="Login", font=("Arial", 18)).pack()
    lemail, lpwd = tk.Entry(frame2), tk.Entry(frame2, show="*")
    for w in [("Email", lemail), ("Password", lpwd)]:
        tk.Label(frame2, text=w[0]).pack(); w[1].pack()
    def do_login():
        email = auth.signin_user(lemail.get(), lpwd.get())
        if email: buy_sell_window(email)
    tk.Button(frame2, text="Login", command=do_login).pack(pady=10)

    # Admin
    frame3 = tk.Frame(notebook); notebook.add(frame3, text="Admin")
    tk.Label(frame3, text="Admin Panel", font=("Arial", 18), fg="red").pack(pady=20)
    tk.Button(frame3, text="View Users", bg="red", fg="white", command=check_admin_password).pack(pady=10)

    return root


if __name__ == "__main__":
    root = create_main_window()
    root.mainloop()

