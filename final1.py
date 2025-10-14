import os
import json
import webbrowser
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from PIL import Image, ImageTk
import datetime
import numpy as np
import pandas as pd
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Constants and sample data ---
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

CHART_STEP_STD = 0.5
CHART_MAX_POINTS = 200
CHART_UPDATE_INTERVAL = 800

# --- JSON helpers ---
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

# Get default zero shares
def get_default_shares(companies):
    return {c: 0 for c in companies}

def open_link(url):
    webbrowser.open(url)

def validate_email(email):
    return '@' in email and '.' in email.split('@')[-1]

def validate_password(pwd):
    return len(pwd) >= 6

# --- Auth Manager ---
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

# --- Candlestick Trading Chart ---
def open_dummy_candlestick_chart(user_email, company, entry_price, side="BUY", title="Trading Chart", balance_update_callback=None):
    ENTRY_PRICE = float(entry_price)
    SIDE = side.upper()

    users = load_users()
    user_data = users.get(user_email)
    if not user_data:
        messagebox.showerror("Error", "User not found!")
        return

    invested_amount = simpledialog.askfloat("Investment", f"Enter amount invested in {company} shares:", minvalue=0.01)
    if invested_amount is None:
        return

    shares_owned = 0
    if company in AUTO_COMPANIES:
        shares_owned = user_data.get("shares", {}).get(company, 0)
    elif company in PETROLEUM_COMPANIES:
        shares_owned = user_data.get("petroleum_shares", {}).get(company, 0)
    elif company in STEEL_COMPANIES:
        shares_owned = user_data.get("steel_shares", {}).get(company, 0)
    elif company in GOLD_COMPANIES:
        shares_owned = user_data.get("gold_shares", {}).get(company, 0)

    if shares_owned == 0:
        messagebox.showinfo("No Shares", "You do not own any shares of this company.")
        return

    effective_entry_price = invested_amount / shares_owned if shares_owned > 0 else ENTRY_PRICE

    ohlc_data = []
    last_close = effective_entry_price

    chart_win = tk.Toplevel()
    chart_win.title(title)
    chart_win.geometry("950x600")
    chart_win.configure(bg="black")

    fig = None
    ax = None
    canvas = None

    def redraw_chart():
        nonlocal fig, ax, canvas
        if len(ohlc_data) == 0:
            return
        df = pd.DataFrame(ohlc_data, columns=["Open", "High", "Low", "Close"])
        df.index = pd.date_range(start="2024-01-01", periods=len(ohlc_data), freq='min')
        if fig is None or ax is None:
            fig, axlist = mpf.plot(df, type='candle', style='charles', volume=False, returnfig=True)
            ax = axlist[0]
            if canvas is not None:
                canvas.get_tk_widget().destroy()
            canvas = FigureCanvasTkAgg(fig, master=chart_win)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            ax.clear()
            mpf.plot(df, ax=ax, type='candle', style='charles', volume=False, warn_too_much_data=10000)
        current_price = df.iloc[-1]['Close']
        abs_pl = (current_price - effective_entry_price) * shares_owned if SIDE == "BUY" else (effective_entry_price - current_price) * shares_owned
        pct = (abs_pl / invested_amount) * 100 if invested_amount > 0 else 0
        ax.set_facecolor("black")
        ax.set_title(f"{title} | Current: ₹{current_price:.2f} | P/L: ₹{abs_pl:.2f} ({pct:.2f}%)", color='white')
        ax.axhline(effective_entry_price, color="yellow", linestyle="--", linewidth=1.2)
        canvas.draw_idle()

    def simulate_next_ohlc(last_close_val):
        o = last_close_val
        c = max(0.1, o + np.random.normal(0, CHART_STEP_STD))
        h = max(o, c) + abs(np.random.normal(0, CHART_STEP_STD * 0.7))
        l = min(o, c) - abs(np.random.normal(0, CHART_STEP_STD * 0.7))
        l = max(l, 0.01)
        return [o, h, l, c]

    def update_chart(_=None):
        nonlocal last_close
        candle = simulate_next_ohlc(last_close)
        ohlc_data.append(candle)
        last_close = candle[3]
        if len(ohlc_data) > CHART_MAX_POINTS:
            ohlc_data.pop(0)
        redraw_chart()

    def submit_manual_price():
        nonlocal last_close
        try:
            val = float(price_entry.get())
            if val <= 0:
                messagebox.showerror("Error", "Enter positive price!")
                return
            o = last_close
            c = val
            h = max(o, c) + abs(np.random.normal(0, CHART_STEP_STD * 0.7))
            l = min(o, c) - abs(np.random.normal(0, CHART_STEP_STD * 0.7))
            l = max(l, 0.05)
            ohlc_data.append([o, h, l, c])
            if len(ohlc_data) > CHART_MAX_POINTS:
                ohlc_data.pop(0)
            last_close = c
            redraw_chart()
            price_entry.delete(0, tk.END)
        except Exception:
            messagebox.showerror("Error", "Invalid price")

    def withdraw_all():
        latest_price = last_close
        break_even_price = effective_entry_price
        if SIDE == "BUY":
            can_withdraw = latest_price >= break_even_price
        else:
            can_withdraw = latest_price <= break_even_price
        if can_withdraw:
            current_total = latest_price * shares_owned
            user_data["balance"] += current_total
            users[user_email] = user_data
            save_users(users)
            messagebox.showinfo("Success", f"₹{current_total:.2f} (Invested + profit) credited to your trading balance.")
            withdraw_btn.config(state="disabled")
            if balance_update_callback:
                balance_update_callback(user_data["balance"])
        else:
            messagebox.showinfo("Info", "Current price not above invested amount, cannot withdraw yet.")

    stop_flag = [False]

    def animation_loop():
        if stop_flag[0]:
            return
        update_chart()
        chart_win.after(CHART_UPDATE_INTERVAL, animation_loop)

    chart_win.protocol("WM_DELETE_WINDOW", lambda: (stop_flag.__setitem__(0, True), chart_win.destroy()))

    control_frame = tk.Frame(chart_win, bg="black")
    control_frame.pack(fill=tk.X, pady=8)

    # tk.Label(control_frame, text="Set Next Price:", font=("Arial", 11), bg="black", fg="white").pack(side=tk.LEFT, padx=6)
    price_entry = tk.Entry(control_frame, font=("Arial", 11), width=10, bg="gray", fg="white", insertbackground="white")
    price_entry.pack(side=tk.LEFT, padx=6)
    tk.Button(control_frame, text="Submit", font=("Arial", 11, "bold"), bg="white", fg="black", command=submit_manual_price).pack(side=tk.LEFT, padx=6)

    withdraw_btn = tk.Button(control_frame, text="Withdraw Profit", font=("Arial", 11, "bold"), bg="green", fg="white", command=withdraw_all)
    withdraw_btn.pack(side=tk.LEFT, padx=6)

    tk.Button(control_frame, text="Close Chart", font=("Arial", 11, "bold"), bg="red", fg="white", command=lambda: (stop_flag.__setitem__(0, True), chart_win.destroy())).pack(side=tk.RIGHT, padx=8)

    animation_loop()

# --- Trading Window ---
def buy_sell_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return
    
    user_data = users[user_email]
    trade_win = tk.Toplevel()
    trade_win.title(f"Trade - {user_data['name']}")
    trade_win.geometry("600x600")
    trade_win.configure(bg="white")

    bal_var = tk.StringVar(value=f"Balance: ₹{user_data['balance']}")
    tk.Label(trade_win, textvariable=bal_var, font=("Arial", 14, "bold"), bg="white", fg="green").pack(pady=10)

    # Sector Selection
    tk.Label(trade_win, text="Select Sector:", font=("Arial", 12, "bold"), bg="white").pack()
    sector_var = tk.StringVar()
    sector_cb = ttk.Combobox(trade_win, textvariable=sector_var, state="readonly", values=["Automobile", "Petroleum", "Steel", "Gold"], font=("Arial", 11))
    sector_cb.pack(pady=6)

    # Company Selection
    tk.Label(trade_win, text="Select Company:", font=("Arial", 12, "bold"), bg="white").pack()
    company_var = tk.StringVar()
    company_cb = ttk.Combobox(trade_win, textvariable=company_var, state="readonly", font=("Arial", 11))
    company_cb.pack(pady=6)

    price_var = tk.StringVar(value="Price: -")
    tk.Label(trade_win, textvariable=price_var, font=("Arial", 12, "italic"), bg="white", fg="blue").pack()

    def update_companies(event):
        s = sector_var.get()
        if s == "Automobile":
            company_cb['values'] = list(AUTO_COMPANIES.keys())
        elif s == "Petroleum":
            company_cb['values'] = list(PETROLEUM_COMPANIES.keys())
        elif s == "Steel":
            company_cb['values'] = list(STEEL_COMPANIES.keys())
        elif s == "Gold":
            company_cb['values'] = list(GOLD_COMPANIES.keys())
        else:
            company_cb['values'] = []
        company_var.set("")
        price_var.set("Price: -")

    sector_cb.bind("<<ComboboxSelected>>", update_companies)

    def update_price(event):
        c = company_var.get()
        price_var.set(f"Price: ₹{PRICES.get(c, '-')}" if c else "Price: -")

    company_cb.bind("<<ComboboxSelected>>", update_price)

    qty_entry = tk.Entry(trade_win, font=("Arial", 12))
    qty_entry.pack(pady=8)

    def commit():
        save_users(users)
        bal_var.set(f"Balance: ₹{user_data['balance']}")

    def buy():
        c = company_var.get()
        if not c:
            messagebox.showerror("Error", "Select a company.")
            return
        qty = qty_entry.get()
        if not qty.isdigit() or int(qty) <= 0:
            messagebox.showerror("Error", "Enter positive quantity.")
            return
        qty = int(qty)
        price = PRICES.get(c)
        cost = price * qty
        if user_data["balance"] < cost:
            messagebox.showerror("Error", "Insufficient balance.")
            return
        user_data["balance"] -= cost
        sh_dict = None
        if c in AUTO_COMPANIES:
            sh_dict = user_data["shares"]
        elif c in PETROLEUM_COMPANIES:
            sh_dict = user_data["petroleum_shares"]
        elif c in STEEL_COMPANIES:
            sh_dict = user_data["steel_shares"]
        elif c in GOLD_COMPANIES:
            if "gold_shares" not in user_data:
                user_data["gold_shares"] = get_default_shares(GOLD_COMPANIES)
            sh_dict = user_data["gold_shares"]
        if sh_dict is not None:
            sh_dict[c] = sh_dict.get(c, 0) + qty
        if "last_buy_price" not in user_data:
            user_data["last_buy_price"] = {}
        user_data["last_buy_price"][c] = price
        commit()
        messagebox.showinfo("Success", f"Bought {qty} shares of {c} for ₹{cost}.")
        qty_entry.delete(0, tk.END)

    def sell():
        c = company_var.get()
        if not c:
            messagebox.showerror("Error", "Select a company.")
            return
        qty = qty_entry.get()
        if not qty.isdigit() or int(qty) <= 0:
            messagebox.showerror("Error", "Enter positive quantity.")
            return
        qty = int(qty)
        sh_dict = None
        if c in AUTO_COMPANIES:
            sh_dict = user_data["shares"]
        elif c in PETROLEUM_COMPANIES:
            sh_dict = user_data["petroleum_shares"]
        elif c in STEEL_COMPANIES:
            sh_dict = user_data["steel_shares"]
        elif c in GOLD_COMPANIES:
            sh_dict = user_data.get("gold_shares", {})
        else:
            messagebox.showerror("Error", "Invalid company.")
            return

        if sh_dict.get(c, 0) < qty:
            messagebox.showerror("Error", "Not enough shares to sell.")
            return

        sh_dict[c] -= qty
        earnings = PRICES[c] * qty
        user_data["balance"] += earnings
        commit()
        messagebox.showinfo("Success", f"Sold {qty} shares of {c} for ₹{earnings}.")
        qty_entry.delete(0, tk.END)

    tk.Button(trade_win, text="Buy", font=("Arial", 12, "bold"), bg="green", fg="white", command=buy).pack(pady=5)
    tk.Button(trade_win, text="Sell", font=("Arial", 12, "bold"), bg="red", fg="white", command=sell).pack(pady=5)

    def open_chart():
        c = company_var.get()
        if c:
            price = user_data.get("last_buy_price", {}).get(c, PRICES.get(c, 30))
            open_dummy_candlestick_chart(
                user_email, c, price, side="BUY", title=f"Chart - {c}",
                balance_update_callback=lambda new_bal: bal_var.set(f"Balance: ₹{new_bal:.2f}")
            )

    tk.Button(trade_win, text="Open Chart", font=("Arial", 14), command=open_chart).pack(pady=12)

    # Navigation and extras can be added here (portfolios, logout, exit, etc.)

# --- Main GUI Window Setup ---
def create_main_window():
    root = tk.Tk()
    root.title("InvestKaro - Stock Market Simulator")
    root.geometry("500x700")
    root.configure(bg="white")

    auth_manager = AuthManager(root)

    notebook = ttk.Notebook(root)
    notebook.pack(pady=20, expand=True, fill="both", padx=20)

    # Signup tab
    signup_frame = tk.Frame(notebook, bg="white")
    notebook.add(signup_frame, text="Sign Up")

    tk.Label(signup_frame, text="Create New Account", font=("Arial", 18, "bold"), bg="white", fg="green").pack(pady=20)
    tk.Label(signup_frame, text="Full Name:", font=("Arial", 12), bg="white").pack()
    signup_name_entry = tk.Entry(signup_frame, font=("Arial", 12), width=25)
    signup_name_entry.pack(pady=5)
    tk.Label(signup_frame, text="Email Address:", font=("Arial", 12), bg="white").pack()
    signup_email_entry = tk.Entry(signup_frame, font=("Arial", 12), width=25)
    signup_email_entry.pack(pady=5)
    tk.Label(signup_frame, text="Password:", font=("Arial", 12), bg="white").pack()
    signup_password_entry = tk.Entry(signup_frame, font=("Arial", 12), show="*", width=25)
    signup_password_entry.pack(pady=5)

    def handle_signup():
        success = auth_manager.signup_user(signup_name_entry.get().strip(), signup_email_entry.get().strip(), signup_password_entry.get())
        if success:
            signup_name_entry.delete(0, tk.END)
            signup_email_entry.delete(0, tk.END)
            signup_password_entry.delete(0, tk.END)
            notebook.select(1)

    tk.Button(signup_frame, text="Create Account", font=("Arial", 14, "bold"), bg="green", fg="white",
              command=handle_signup, width=15).pack(pady=20)

    # Login tab
    login_frame = tk.Frame(notebook, bg="white")
    notebook.add(login_frame, text="Login")

    tk.Label(login_frame, text="Welcome Back!", font=("Arial", 18, "bold"), bg="white", fg="blue").pack(pady=20)
    tk.Label(login_frame, text="Email Address:", font=("Arial", 12), bg="white").pack()
    login_email_entry = tk.Entry(login_frame, font=("Arial", 12), width=25)
    login_email_entry.pack(pady=5)
    tk.Label(login_frame, text="Password:", font=("Arial", 12), bg="white").pack()
    login_password_entry = tk.Entry(login_frame, font=("Arial", 12), show="*", width=25)
    login_password_entry.pack(pady=5)

    def handle_login():
        user_email = auth_manager.signin_user(login_email_entry.get().strip(), login_password_entry.get())
        if user_email:
            login_email_entry.delete(0, tk.END)
            login_password_entry.delete(0, tk.END)
            buy_sell_window(user_email)

    tk.Button(login_frame, text="Login", font=("Arial", 14, "bold"), bg="blue", fg="white",
              command=handle_login, width=15).pack(pady=20)

    return root

if __name__ == "__main__":
    root = create_main_window()
    root.mainloop()
