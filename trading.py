"""
merged_app_with_auto_chart.py

Merged Tkinter stock-market GUI + embedded dummy trading chart (matplotlib animation).
Behavior change: selecting a company (after selecting sector) will automatically open the dummy chart for that company.

Dependencies:
    pip install pillow numpy matplotlib
Run:
    python merged_app_with_auto_chart.py
"""

import os
import json
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

# Matplotlib imports for embedded chart
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------------------
# Config / Files / Data
# ----------------------------
DB_FILE = "users.json"
REG_FILE = "registrations.json"

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

PRICES = {
    **{c: 10 for c in AUTO_COMPANIES},
    **{c: 15 for c in PETROLEUM_COMPANIES},
    **{c: 20 for c in STEEL_COMPANIES}
}

IMAGE_PATHS = {
    "logo": "C:\\Users\\neham\\Downloads\\IK.png.png",
    "auto_bg": "C:\\Users\\neham\\Downloads\\auto.png",
    "petro_bg": "C:\\Users\\neham\\Downloads\\petro.png",
    "steel_bg": "C:\\Users\\neham\\Downloads\\steel1.png",
    "admin": "C:\\Users\\neham\\Downloads\\admin.png.png"
}

# Chart defaults
CHART_UPDATE_INTERVAL = 800  # ms
CHART_MAX_POINTS = 200
CHART_PRICE_START = 100.0
CHART_STEP_STD = 0.5

# ----------------------------
# Helper functions: JSON & images
# ----------------------------
def safe_json_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return default
        return json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError):
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
    data = load_registrations()
    data.append(entry)
    save_json(REG_FILE, data)

def load_image(path, size=None):
    try:
        if not os.path.exists(path):
            return None
        img = Image.open(path)
        if size:
            img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"load_image error ({path}):", e)
        return None

def open_link(url):
    webbrowser.open(url)

# ----------------------------
# Registration & User logic
# ----------------------------
def get_default_shares(company_dict):
    return {company: 0 for company in company_dict.keys()}

def register_user_callback(entry_name, entry_email, entry_password):
    name = entry_name.get().strip()
    email = entry_email.get().strip()
    password = entry_password.get().strip()

    if not name or not email or not password:
        messagebox.showerror("Error", "All fields are required!")
        return

    users = load_users()
    if email in users:
        messagebox.showerror("Error", "Email already registered!")
        return

    users[email] = {
        "name": name,
        "password": password,
        "balance": 100,
        "shares": get_default_shares(AUTO_COMPANIES),
        "petroleum_shares": get_default_shares(PETROLEUM_COMPANIES),
        "steel_shares": get_default_shares(STEEL_COMPANIES),
        "bonus": 100
    }
    save_users(users)
    save_registration({"name": name, "email": email, "bonus": 100})
    messagebox.showinfo("Success", "Registration successful! You received ₹100 bonus.")
    buy_sell_window(email)

# ----------------------------
# Dummy Trading Chart (matplotlib) - embedded into Tkinter
# ----------------------------
import mplfinance as mpf

def open_dummy_candlestick_chart(entry_price=None, side="BUY", title="Dummy Candlestick Chart"):
    ENTRY_PRICE = float(entry_price) if entry_price is not None else float(CHART_PRICE_START)
    SIDE = side.upper()
    import pandas as pd
    xs = []
    # We store OHLC data as dictionaries
    ohlc_data = []

    chart_win = tk.Toplevel(root)
    chart_win.title(title)
    chart_win.geometry("950x600")
    chart_win.configure(bg="black")
    
    # Figure
    fig = mpf.figure(style='charles', figsize=(9,4.5), facecolor='black')
    ax = fig.add_subplot(1,1,1)
    fig.suptitle(title, color='white', fontsize=16)
    
    canvas = FigureCanvasTkAgg(fig, master=chart_win)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    
    state = {
        "counter": 0,   # Tick counter, used as X index
        "ohlc": ohlc_data,
        "last_close": ENTRY_PRICE
    }
    
    # Simulate OHLC for next bar
    def simulate_next_ohlc(last_close):
        # Create random (small) OHLC variations
        open_ = last_close
        close = open_ + np.random.normal(0, CHART_STEP_STD)
        close = max(close, 0.1)
        high = max(open_, close) + abs(np.random.normal(0, CHART_STEP_STD * 0.7))
        low = min(open_, close) - abs(np.random.normal(0, CHART_STEP_STD * 0.7))
        high = max(high, open_, close)
        low = min(low, open_, close)
        low = max(low, 0.05)
        return [open_, high, low, close]
    
    def compute_pl(current_price):
        if SIDE == "BUY":
            abs_pl = current_price - ENTRY_PRICE
        else:
            abs_pl = ENTRY_PRICE - current_price
        pct = (abs_pl / ENTRY_PRICE) * 100.0
        return abs_pl, pct

    def redraw_chart():
        # Prepare DataFrame for mplfinance
        if len(state["ohlc"]) > 0:
            df = pd.DataFrame(state["ohlc"], columns=["Open","High","Low","Close"])
            df['Volume'] = 1
            df.index = pd.date_range(start="2024-01-01", periods=len(df), freq='T')
            ax.clear()
            mpf.plot(df, ax=ax, type='candle', style='charles',
                     datetime_format='%H:%M', xrotation=0,
                     ylabel='', ylabel_lower='', volume=False, warn_too_much_data=10000)
            # Formatting legend/title
            current_price = df.iloc[-1]['Close']
            abs_pl, pct = compute_pl(current_price)
            color = "lime" if abs_pl > 0 else ("red" if abs_pl < 0 else "white")
            ax.set_facecolor("black")
            ax.set_title(f"{title} | Current: {current_price:.2f} | P/L: {abs_pl:+.2f} ({pct:+.2f}%)", color='white')
            # Entry line
            ax.axhline(ENTRY_PRICE, color="yellow", linestyle="--", linewidth=1.2, label="Entry Price")
            # Legend
            ax.legend(facecolor="gray", edgecolor="white", labelcolor="white")
        canvas.draw()

    def update_chart(frame=None):
        last_close = state['last_close']
        o, h, l, c = simulate_next_ohlc(last_close)
        state['ohlc'].append([o,h,l,c])
        state['last_close'] = c
        state['counter'] += 1
        redraw_chart()
    
    def submit_manual_price():
        val = price_entry.get().strip()
        try:
            manual_close = float(val)
            if manual_close <= 0:
                messagebox.showerror("Error", "Enter a positive price.")
                return
            # Simulate Open/High/Low around this Close
            last_close = state['last_close']
            o, h, l, c = simulate_next_ohlc(last_close)
            state['ohlc'].append([o,h,l,manual_close])
            state['last_close'] = manual_close
            state['counter'] += 1
            redraw_chart()
            price_entry.delete(0, tk.END)
        except Exception:
            messagebox.showerror("Error", "Please enter a valid number.")

    def close_chart():
        try:
            chart_win.anim.event_source.stop()
        except Exception:
            pass
        chart_win.destroy()
    
    # Timer/Animation
    import threading
    stop_flag = [False]
    def run_anim():
        while not stop_flag[0]:
            chart_win.after(CHART_UPDATE_INTERVAL, update_chart)
            chart_win.update_idletasks()
            chart_win.after(CHART_UPDATE_INTERVAL)

    chart_win.anim_thread = threading.Thread(target=run_anim, daemon=True)
    chart_win.anim_thread.start()
    
    # --- UI For Custom Dummy Price ---
    control_frame = tk.Frame(chart_win, bg="black")
    control_frame.pack(fill=tk.X, pady=8)
    tk.Label(control_frame, text="Set Next Candlestick Close Price:", font=("Arial", 11),
             bg="black", fg="white").pack(side=tk.LEFT, padx=6)
    price_entry = tk.Entry(control_frame, font=("Arial", 11), width=10, bg="gray", fg="white", insertbackground="white")
    price_entry.pack(side=tk.LEFT, padx=6)
    tk.Button(control_frame, text="Submit", font=("Arial", 11, "bold"),
              bg="white", fg="black", command=submit_manual_price).pack(side=tk.LEFT, padx=6)
    tk.Button(control_frame, text="Close Chart", font=("Arial", 11, "bold"),
              bg="red", fg="white", command=lambda: [stop_flag.__setitem__(0, True), close_chart()]).pack(side=tk.RIGHT, padx=8)

# ----------------------------
# Buy/Sell Window
# ----------------------------
def buy_sell_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return
    user_data = users[user_email]

    trade_win = tk.Toplevel(root)
    trade_win.title(f"Buy/Sell Stocks - {user_data['name']}")
    trade_win.geometry("520x520")
    trade_win.configure(bg="white")

    bal_var = tk.StringVar(value=f"Balance: ₹{user_data['balance']}")
    tk.Label(trade_win, textvariable=bal_var, font=("Arial", 12, "bold"), bg="white").pack(pady=5)

    tk.Label(trade_win, text="Select Sector:", font=("Arial", 11), bg="white").pack()
    sector_var = tk.StringVar()
    sector_combo = ttk.Combobox(trade_win, textvariable=sector_var,
                                values=["Automobile", "Petroleum", "Steel"], state="readonly")
    sector_combo.pack(pady=5)

    tk.Label(trade_win, text="Select Company:", font=("Arial", 11), bg="white").pack()
    company_var = tk.StringVar()
    company_combo = ttk.Combobox(trade_win, textvariable=company_var, state="readonly")
    company_combo.pack(pady=5)

    price_var = tk.StringVar(value="Price: -")
    tk.Label(trade_win, textvariable=price_var, font=("Arial", 11, "italic"), bg="white").pack()

    def update_companies(event):
        if sector_var.get() == "Automobile":
            company_combo["values"] = list(AUTO_COMPANIES.keys())
        elif sector_var.get() == "Petroleum":
            company_combo["values"] = list(PETROLEUM_COMPANIES.keys())
        elif sector_var.get() == "Steel":
            company_combo["values"] = list(STEEL_COMPANIES.keys())
        company_var.set("")
        price_var.set("Price: -")

    def update_price_and_open_chart(event):
        comp = company_var.get()
        if comp:
            price_var.set(f"Price: ₹{PRICES.get(comp, '-')}")
            # Automatically open the dummy chart for this company (entry price = current unit price)
            entry = PRICES.get(comp, CHART_PRICE_START)
            # Open in BUY mode by default; change if you want SELL logic
            open_dummy_candlestick_chart(entry_price=entry, side="BUY", title=f"Dummy Chart - {comp}")

         
    sector_combo.bind("<<ComboboxSelected>>", update_companies)
    company_combo.bind("<<ComboboxSelected>>", update_price_and_open_chart)

    tk.Label(trade_win, text="Quantity:", font=("Arial", 11), bg="white").pack()
    qty_entry = tk.Entry(trade_win, font=("Arial", 11))
    qty_entry.pack(pady=5)

    def commit_and_refresh():
        save_users(users)
        bal_var.set(f"Balance: ₹{user_data['balance']}")

    def buy_stock():
        company = company_var.get()
        qty_txt = qty_entry.get().strip()
        if not company:
            messagebox.showerror("Error", "Please select a company.")
            return
        if not qty_txt.isdigit() or int(qty_txt) <= 0:
            messagebox.showerror("Error", "Enter a valid positive quantity.")
            return
        qty = int(qty_txt)
        unit = PRICES.get(company, 0)
        cost = unit * qty
        if user_data["balance"] < cost:
            messagebox.showerror("Error", f"Insufficient balance. Need ₹{cost}, have ₹{user_data['balance']}.")
            return
        user_data["balance"] -= cost
        if company in user_data["shares"]:
            user_data["shares"][company] += qty
        elif company in user_data["petroleum_shares"]:
            user_data["petroleum_shares"][company] += qty
        elif company in user_data["steel_shares"]:
            user_data["steel_shares"][company] += qty
        commit_and_refresh()
        messagebox.showinfo("Success", f"Bought {qty} shares of {company} for ₹{cost}.")

    def sell_stock():
        company = company_var.get()
        qty_txt = qty_entry.get().strip()
        if not company:
            messagebox.showerror("Error", "Please select a company.")
            return
        if not qty_txt.isdigit() or int(qty_txt) <= 0:
            messagebox.showerror("Error", "Enter a valid positive quantity.")
            return
        qty = int(qty_txt)

        portfolio_key = None
        if company in user_data["shares"]:
            portfolio_key = "shares"
        elif company in user_data["petroleum_shares"]:
            portfolio_key = "petroleum_shares"
        elif company in user_data["steel_shares"]:
            portfolio_key = "steel_shares"

        if portfolio_key is None:
            messagebox.showerror("Error", "Invalid company.")
            return

        if user_data[portfolio_key].get(company, 0) < qty:
            messagebox.showerror("Error", "Not enough shares to sell.")
            return

        user_data[portfolio_key][company] -= qty
        earnings = PRICES.get(company, 0) * qty
        user_data["balance"] += earnings
        commit_and_refresh()
        messagebox.showinfo("Success", f"Sold {qty} shares of {company} for ₹{earnings}.")

    tk.Button(trade_win, text="Buy", font=("Arial", 12, "bold"), bg="green", fg="white", command=buy_stock).pack(pady=5)
    tk.Button(trade_win, text="Sell", font=("Arial", 12, "bold"), bg="red", fg="white", command=sell_stock).pack(pady=5)

    btns = tk.Frame(trade_win, bg="white")
    btns.pack(pady=10)
    tk.Button(btns, text="Automobile Portfolio", command=lambda: show_auto_shares_window(user_email)).grid(row=0, column=0, padx=5)
    tk.Button(btns, text="Petroleum Portfolio", command=lambda: show_petroleum_shares_window(user_email)).grid(row=0, column=1, padx=5)
    tk.Button(btns, text="Steel Portfolio", command=lambda: show_steel_shares_window(user_email)).grid(row=0, column=2, padx=5)

# ----------------------------
# Shares display windows
# ----------------------------
def show_auto_shares_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return
    user_data = users[user_email]
    shares_data = user_data.get("shares", {})
    win = tk.Toplevel(root)
    win.title(f"{user_data['name']}'s Automobile Portfolio")
    for company, qty in shares_data.items():
        tk.Label(win, text=f"{company}: {qty} shares").pack()

def show_petroleum_shares_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return
    user_data = users[user_email]
    shares_data = user_data.get("petroleum_shares", {})
    win = tk.Toplevel(root)
    win.title(f"{user_data['name']}'s Petroleum Portfolio")
    for company, qty in shares_data.items():
        tk.Label(win, text=f"{company}: {qty} shares").pack()

def show_steel_shares_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return
    user_data = users[user_email]
    shares_data = user_data.get("steel_shares", {})
    win = tk.Toplevel(root)
    win.title(f"{user_data['name']}'s Steel Portfolio")
    win.geometry("520x500")
    win.configure(bg="white")
    frame = tk.Frame(win, bg="white")
    frame.pack(pady=10)
    tk.Label(frame, text="Company", font=("Arial", 12, "bold"), width=25, anchor="w", bg="white").grid(row=0, column=0)
    tk.Label(frame, text="Shares", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=1)
    tk.Label(frame, text="Price", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=2)
    tk.Label(frame, text="Link", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=3)
    for i, (company, shares) in enumerate(shares_data.items(), start=1):
        tk.Label(frame, text=company, font=("Arial", 11), width=25, anchor="w", bg="white").grid(row=i, column=0, pady=2)
        tk.Label(frame, text=str(shares), font=("Arial", 11), width=10, anchor="center", bg="white").grid(row=i, column=1, pady=2)
        tk.Label(frame, text=f"₹{PRICES.get(company, '-')}", font=("Arial", 11), width=10, anchor="center", bg="white").grid(row=i, column=2, pady=2)
        tk.Button(frame, text="View", font=("Arial", 10, "bold"), fg="blue", cursor="hand2",
                  command=lambda url=STEEL_COMPANIES.get(company, "#"): open_link(url)).grid(row=i, column=3, pady=2)

# ----------------------------
# Admin functions
# ----------------------------
ADMIN_PASSWORD = "admin123"

def check_admin_password():
    pass_win = tk.Toplevel(root)
    pass_win.title("Admin Login")
    pass_win.geometry("300x200")
    pass_win.configure(bg="white")
    admin_img = load_image(IMAGE_PATHS.get("admin",""), (80,80))
    if admin_img:
        admin_label = tk.Label(pass_win, image=admin_img, bg="white")
        admin_label.image = admin_img
        admin_label.pack(pady=5)
    tk.Label(pass_win, text="🔑 Enter Admin Password", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
    pwd_entry = tk.Entry(pass_win, font=("Arial", 12), show="*")
    pwd_entry.pack(pady=5)
    def verify():
        if pwd_entry.get().strip() == ADMIN_PASSWORD:
            pass_win.destroy()
            show_all_registrations()
        else:
            messagebox.showerror("Access Denied", "Incorrect password!")
    tk.Button(pass_win, text="Login", font=("Arial",12,"bold"), bg="blue", fg="white", command=verify).pack(pady=10)

def show_all_registrations():
    records = load_registrations()
    if not records:
        messagebox.showinfo("Info", "No registrations found.")
        return
    admin_win = tk.Toplevel(root)
    admin_win.title("Company Records - All Registrations")
    admin_win.geometry("650x450")
    admin_win.configure(bg="white")
    tk.Label(admin_win, text="All User Registrations", font=("Arial", 14, "bold"), bg="white").pack(pady=5)
    frame = tk.Frame(admin_win, bg="white")
    frame.pack(pady=10)
    tk.Label(frame, text="Name", font=("Arial",12,"bold"), width=20, anchor="w", bg="white").grid(row=0, column=0)
    tk.Label(frame, text="Email", font=("Arial",12,"bold"), width=30, anchor="w", bg="white").grid(row=0, column=1)
    tk.Label(frame, text="Bonus", font=("Arial",12,"bold"), width=10, anchor="center", bg="white").grid(row=0, column=2)
    for i, user in enumerate(records, start=1):
        tk.Label(frame, text=user.get("name",""), font=("Arial",11), width=20, anchor="w", bg="white").grid(row=i, column=0, pady=2)
        tk.Label(frame, text=user.get("email",""), font=("Arial",11), width=30, anchor="w", bg="white").grid(row=i, column=1, pady=2)
        tk.Label(frame, text=f"₹{user.get('bonus',0)}", font=("Arial",11), width=10, anchor="center", bg="white").grid(row=i, column=2, pady=2)

# ----------------------------
# Main GUI: registration form
# ----------------------------
root = tk.Tk()
root.title("Stock Market - Registration")
root.geometry("420x640")
root.configure(bg="white")

logo_img = load_image(IMAGE_PATHS.get("logo",""), (500, 320))
if logo_img:
    logo_label = tk.Label(root, image=logo_img, bg="white")
    logo_label.image = logo_img
    logo_label.pack(pady=8)

tk.Label(root, text="📈 Stock Market", font=("Arial", 20, "bold"), bg="white").pack(pady=6)

tk.Label(root, text="Name:", font=("Arial", 12), bg="white").pack()
entry_name = tk.Entry(root, font=("Arial", 12))
entry_name.pack(pady=5)

tk.Label(root, text="Email:", font=("Arial", 12), bg="white").pack()
entry_email = tk.Entry(root, font=("Arial", 12))
entry_email.pack(pady=5)

tk.Label(root, text="Password:", font=("Arial", 12), bg="white").pack()
entry_password = tk.Entry(root, font=("Arial", 12), show="*")
entry_password.pack(pady=5)

register_btn = tk.Button(root, text="Register", font=("Arial", 12, "bold"), bg="green", fg="white",
                         command=lambda: register_user_callback(entry_name, entry_email, entry_password))
register_btn.pack(pady=12)

quick = tk.Frame(root, bg="white")
quick.pack()
tk.Button(quick, text="Company Records (Admin)", font=("Arial", 12, "bold"), bg="blue", fg="white",
          command=check_admin_password).grid(row=0, column=0, padx=4, pady=4)

tk.Button(root, text="Open Dummy Trading Chart (Standalone)", bg="orange",
          command=lambda: open_dummy_candlestick_chart(entry_price=100.0, side="BUY", title="Standalone Dummy Chart")
)

root.mainloop()
