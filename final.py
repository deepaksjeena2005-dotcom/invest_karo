import os
import json
import webbrowser
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from PIL import Image, ImageTk
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# -------------------- Constants --------------------
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

# -------------------- JSON Helpers --------------------
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

# -------------------- Authentication Manager --------------------
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

# -------------------- Profit Helper --------------------
def add_profit_to_balance(user_data, profit_amount):
    if profit_amount > 0:
        user_data["balance"] += profit_amount

# -------------------- Candlestick Chart --------------------
def open_dummy_candlestick_chart(user_email, company, entry_price, side="BUY", title="Trading Chart"):
    # Function body omitted for brevity (use your existing chart simulation code)
    pass

# -------------------- Trading Window --------------------
def buy_sell_window(user_email):
    # Function body omitted for brevity (use your existing buy/sell UI code)
    pass

# -------------------- Portfolio Window --------------------
def show_portfolio_window(user_email, sector):
    # Function body omitted for brevity (use your existing portfolio UI code)
    pass

# -------------------- Admin --------------------
def check_admin_password():
    # Function body omitted for brevity (use your existing admin password check code)
    pass

def show_admin_dashboard():
    # Function body omitted for brevity (use your existing admin dashboard code)
    pass

# -------------------- Main Window --------------------
def create_main_window():
    global root
    root = tk.Tk()
    root.title("InvestKaro - Stock Market Simulator")
    root.geometry("500x700")
    root.configure(bg="white")

    # Logo
    logo_img = load_image("C:\\Users\\neham\\Downloads\\IK.png.png", (300, 200))
    if logo_img:
        logo_label = tk.Label(root, image=logo_img, bg="white")
        logo_label.image = logo_img
        logo_label.pack(pady=10)
    else:
        tk.Label(root, text="InvestKaro", font=("Arial", 24, "bold"), bg="white", fg="green").pack(pady=20)

    tk.Label(root, text="Stock Market Simulator", font=("Arial", 16), bg="white", fg="gray").pack()

    notebook = ttk.Notebook(root)
    notebook.pack(pady=20, expand=True, fill="both", padx=20)

    auth_manager = AuthManager(root)

    # -------------------- Signup Tab --------------------
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
        success = auth_manager.signup_user(
            signup_name_entry.get().strip(),
            signup_email_entry.get().strip(),
            signup_password_entry.get()
        )
        if success:
            signup_name_entry.delete(0, tk.END)
            signup_email_entry.delete(0, tk.END)
            signup_password_entry.delete(0, tk.END)
            notebook.select(1)

    tk.Button(signup_frame, text="Create Account", font=("Arial", 14, "bold"), bg="green", fg="white",
              command=handle_signup, width=15).pack(pady=20)
    tk.Label(signup_frame, text="🎁 Get ₹100 signup bonus!", font=("Arial", 12), bg="white", fg="orange").pack()

    # -------------------- Login Tab --------------------
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
        user_email = auth_manager.signin_user(
            login_email_entry.get().strip(),
            login_password_entry.get()
        )
        if user_email:
            login_email_entry.delete(0, tk.END)
            login_password_entry.delete(0, tk.END)
            buy_sell_window(user_email)

    tk.Button(login_frame, text="Login", font=("Arial", 14, "bold"), bg="blue", fg="white",
              command=handle_login, width=15).pack(pady=20)

    # -------------------- Admin Tab --------------------
    admin_frame = tk.Frame(notebook, bg="white")
    notebook.add(admin_frame, text="Admin")
    tk.Label(admin_frame, text="Administrator Panel", font=("Arial", 18, "bold"), bg="white", fg="red").pack(pady=40)
    tk.Button(admin_frame, text="View All Users", font=("Arial", 14, "bold"), bg="red", fg="white",
              command=check_admin_password, width=15).pack(pady=20)
    tk.Label(admin_frame, text="⚠️ Admin access required", font=("Arial", 12, "italic"), bg="white", fg="gray").pack()

    return root

# -------------------- Run App ----------------
# -------------------- Buy/Sell Window --------------------
def buy_sell_window(user_email):
    users = load_users()
    user_data = users[user_email]

    window = tk.Toplevel()
    window.title(f"Trading - {user_data['name']}")
    window.geometry("600x600")
    window.configure(bg="white")

    tk.Label(window, text=f"Welcome, {user_data['name']}", font=("Arial", 16, "bold"), bg="white", fg="green").pack(pady=10)
    tk.Label(window, text=f"Balance: ₹{user_data['balance']}", font=("Arial", 14), bg="white", fg="blue").pack(pady=5)

    # Company selection
    tk.Label(window, text="Select Sector:", font=("Arial", 12), bg="white").pack(pady=5)
    sector_var = tk.StringVar(value="Automobile")
    sector_options = ["Automobile", "Petroleum", "Steel", "Gold"]
    ttk.Combobox(window, values=sector_options, textvariable=sector_var, state="readonly").pack(pady=5)

    tk.Label(window, text="Select Company:", font=("Arial", 12), bg="white").pack(pady=5)
    company_var = tk.StringVar()
    company_combo = ttk.Combobox(window, values=list(AUTO_COMPANIES.keys()), textvariable=company_var, state="readonly")
    company_combo.pack(pady=5)

    def update_company_list(*args):
        sector = sector_var.get()
        if sector == "Automobile":
            company_combo.config(values=list(AUTO_COMPANIES.keys()))
        elif sector == "Petroleum":
            company_combo.config(values=list(PETROLEUM_COMPANIES.keys()))
        elif sector == "Steel":
            company_combo.config(values=list(STEEL_COMPANIES.keys()))
        elif sector == "Gold":
            company_combo.config(values=list(GOLD_COMPANIES.keys()))
        company_var.set("")

    sector_var.trace("w", update_company_list)

    # Buy/Sell quantity
    tk.Label(window, text="Quantity:", font=("Arial", 12), bg="white").pack(pady=5)
    quantity_entry = tk.Entry(window, font=("Arial", 12), width=10)
    quantity_entry.pack(pady=5)

    def perform_trade(side):
        company = company_var.get()
        if not company:
            messagebox.showerror("Error", "Please select a company.")
            return
        try:
            qty = int(quantity_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid quantity!")
            return

        price = PRICES.get(company, 10)
        total_cost = price * qty

        if side == "BUY":
            if user_data["balance"] < total_cost:
                messagebox.showerror("Error", "Insufficient balance!")
                return
            user_data["balance"] -= total_cost
            user_data["shares"][company] = user_data["shares"].get(company, 0) + qty
            user_data["last_buy_price"][company] = price
            messagebox.showinfo("Success", f"Bought {qty} shares of {company} at ₹{price} each.")
        else:  # SELL
            if user_data["shares"].get(company, 0) < qty:
                messagebox.showerror("Error", "Not enough shares to sell!")
                return
            user_data["shares"][company] -= qty
            profit = price * qty
            add_profit_to_balance(user_data, profit)
            messagebox.showinfo("Success", f"Sold {qty} shares of {company} at ₹{price} each.")

        save_users(users)
        tk.Label(window, text=f"Balance: ₹{user_data['balance']}", font=("Arial", 14), bg="white", fg="blue").pack(pady=5)

    tk.Button(window, text="Buy", font=("Arial", 12, "bold"), bg="green", fg="white",
              command=lambda: perform_trade("BUY")).pack(pady=5)
    tk.Button(window, text="Sell", font=("Arial", 12, "bold"), bg="red", fg="white",
              command=lambda: perform_trade("SELL")).pack(pady=5)

    # Open Screener link
    def open_company_link():
        company = company_var.get()
        if not company:
            messagebox.showerror("Error", "Select a company first!")
            return
        sector = sector_var.get()
        if sector == "Automobile":
            open_link(AUTO_COMPANIES[company])
        elif sector == "Petroleum":
            open_link(PETROLEUM_COMPANIES[company])
        elif sector == "Steel":
            open_link(STEEL_COMPANIES[company])
        elif sector == "Gold":
            open_link(GOLD_COMPANIES[company])

    tk.Button(window, text="Open Company Screener Page", font=("Arial", 12), bg="orange", fg="white",
              command=open_company_link).pack(pady=10)

# -------------------- Admin Password --------------------
def check_admin_password():
    pwd = simpledialog.askstring("Admin Login", "Enter admin password:", show="*")
    if pwd == ADMIN_PASSWORD:
        show_admin_dashboard()
    else:
        messagebox.showerror("Error", "Incorrect admin password!")

def show_admin_dashboard():
    regs = load_registrations()
    admin_window = tk.Toplevel()
    admin_window.title("Admin Dashboard")
    admin_window.geometry("500x500")
    tk.Label(admin_window, text="Registered Users", font=("Arial", 16, "bold")).pack(pady=10)

    for r in regs:
        tk.Label(admin_window, text=f"{r['name']} ({r['email']}) - Bonus: ₹{r['bonus']}").pack(pady=2)

# -------------------- Run App --------------------
if __name__ == "__main__":
    root = create_main_window()
    root.mainloop()

# -------------------- Candlestick Chart --------------------
def show_candlestick_chart():
    company = company_var.get()
    if not company:
        messagebox.showerror("Error", "Select a company first!")
        return

    # Simulate OHLC data for 10 days
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta
    import random

    days = 10
    base_price = PRICES.get(company, 10)
    dates = [datetime.now() - timedelta(days=i) for i in range(days)][::-1]
    ohlc_data = []

    last_close = base_price
    for _ in range(days):
        open_price = round(last_close + random.uniform(-2, 2), 2)
        high = round(open_price + random.uniform(0, 3), 2)
        low = round(open_price - random.uniform(0, 3), 2)
        close = round(low + random.uniform(0, high - low), 2)
        ohlc_data.append((open_price, high, low, close))
        last_close = close

    # Plot Candlestick chart
    fig, ax = plt.subplots()
    for i, (o, h, l, c) in enumerate(ohlc_data):
        color = "green" if c >= o else "red"
        ax.plot([dates[i], dates[i]], [l, h], color=color)
        ax.plot([dates[i]-timedelta(hours=0.2), dates[i]+timedelta(hours=0.2)], [o, o], color=color, linewidth=5)
        ax.plot([dates[i]-timedelta(hours=0.2), dates[i]+timedelta(hours=0.2)], [c, c], color=color, linewidth=5)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    plt.title(f"{company} - Last {days} Days")
    plt.xlabel("Date")
    plt.ylabel("Price (₹)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Button to open chart
tk.Button(window, text="Show Candlestick Chart", font=("Arial", 12), bg="purple", fg="white",
          command=show_candlestick_chart).pack(pady=10)

# Store OHLC history for each company
ohlc_history = {}

def update_ohlc(company, price):
    from datetime import datetime
    import random

    # Initialize if first time
    if company not in ohlc_history:
        ohlc_history[company] = []

    # Previous close
    last_close = ohlc_history[company][-1][3] if ohlc_history[company] else price

    # Generate random OHLC around the trade price
    open_price = round(last_close + random.uniform(-1, 1), 2)
    high = round(max(open_price, price) + random.uniform(0, 1), 2)
    low = round(min(open_price, price) - random.uniform(0, 1), 2)
    close = round(price, 2)

    ohlc_history[company].append((open_price, high, low, close))

    # Keep only last 10 entries
    if len(ohlc_history[company]) > 10:
        ohlc_history[company].pop(0)

def show_candlestick_chart():
    company = company_var.get()
    if not company:
        messagebox.showerror("Error", "Select a company first!")
        return

    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta

    if company not in ohlc_history or not ohlc_history[company]:
        messagebox.showinfo("Info", "No trade data yet for this company.")
        return

    ohlc_data = ohlc_history[company]
    days = len(ohlc_data)
    dates = [datetime.now() - timedelta(days=i) for i in range(days)][::-1]

    fig, ax = plt.subplots()
    for i, (o, h, l, c) in enumerate(ohlc_data):
        color = "green" if c >= o else "red"
        ax.plot([dates[i], dates[i]], [l, h], color=color)
        ax.plot([dates[i]-timedelta(hours=0.2), dates[i]+timedelta(hours=0.2)], [o, o], color=color, linewidth=5)
        ax.plot([dates[i]-timedelta(hours=0.2), dates[i]+timedelta(hours=0.2)], [c, c], color=color, linewidth=5)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    plt.title(f"{company} - Last {days} Trades")
    plt.xlabel("Date")
    plt.ylabel("Price (₹)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def draw_candlestick_chart(frame, company):
    frame.destroy()  # Remove previous canvas if any

    if company not in ohlc_history or not ohlc_history[company]:
        return tk.Label(root, text="No trade data yet for this company.").pack()

    ohlc_data = ohlc_history[company]
    days = len(ohlc_data)
    dates = [datetime.now() - timedelta(days=i) for i in range(days)][::-1]

    fig, ax = plt.subplots(figsize=(6,4))
    for i, (o, h, l, c) in enumerate(ohlc_data):
        color = "green" if c >= o else "red"
        ax.plot([dates[i], dates[i]], [l, h], color=color)
        ax.plot([dates[i]-timedelta(hours=0.2), dates[i]+timedelta(hours=0.2)], [o, o], color=color, linewidth=5)
        ax.plot([dates[i]-timedelta(hours=0.2), dates[i]+timedelta(hours=0.2)], [c, c], color=color, linewidth=5)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    ax.set_title(f"{company} - Last {days} Trades")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (₹)")
    ax.grid(True)
    plt.tight_layout()

    # Embed in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()
    return canvas.get_tk_widget()

# Clear previous chart and draw new one
if 'chart_frame' in globals():
    chart_frame.destroy()
chart_frame = draw_candlestick_chart(chart_frame if 'chart_frame' in globals() else tk.Frame(root), company)

chart_frame = tk.Frame(root)
chart_frame.pack()
