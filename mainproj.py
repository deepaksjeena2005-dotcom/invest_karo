import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import json
import os
import webbrowser

# ---------- Config ----------
DB_FILE = "users.json"
REG_FILE = "registrations.json"  # Company record file

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

# Dummy stock prices (simulation)
PRICES = {
    **{c: 10 for c in AUTO_COMPANIES},
    **{c: 15 for c in PETROLEUM_COMPANIES},
    **{c: 20 for c in STEEL_COMPANIES}
}

# Image paths - optional. Missing images won't crash the app.
IMAGE_PATHS = {
    "logo": "C:\\Users\\neham\\Downloads\\investkaro.png.png",
    "auto_bg": "C:\\Users\\neham\\Downloads\\automobile.png.png",
    "petro_bg": "C:\\Users\\neham\\Downloads\\petro.png.png",
    "steel_bg": "C:\\Users\\neham\\Downloads\\steel1.py.png",
    "admin": "C:\\Users\\neham\\Downloads\\.png.png"
}

ADMIN_PASSWORD = "admin123"

# ---------- Helpers ----------
def load_image(path, size):
    try:
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        # Image not available or path incorrect: return None and continue
        # print("Image load error:", e)
        return None

def open_link(url):
    try:
        webbrowser.open(url)
    except Exception:
        messagebox.showerror("Error", "Failed to open link.")

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
        # Corrupted file — return default (do not crash)
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
    # entry should be a dict; include email so admin can display it
    data = load_registrations()
    data.append(entry)
    save_json(REG_FILE, data)

def get_default_shares(company_dict):
    return {company: 0 for company in company_dict.keys()}

# ---------- Registration ----------
def register_user():
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
        "email": email,
        "password": password,
        "balance": 100,
        "shares": get_default_shares(AUTO_COMPANIES),
        "petroleum_shares": get_default_shares(PETROLEUM_COMPANIES),
        "steel_shares": get_default_shares(STEEL_COMPANIES),
        "bonus": 100
    }

    save_users(users)
    # Save a compact registration record for admin listing
    reg_entry = {"name": name, "email": email, "bonus": 100}
    save_registration(reg_entry)

    messagebox.showinfo("Success", "Registration successful! You received ₹100 bonus.")
    buy_sell_window(email)

# ---------- Buy / Sell window ----------
def buy_sell_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return

    user_data = users[user_email]

    trade_win = tk.Toplevel(root)
    trade_win.title(f"Buy/Sell Stocks - {user_data['name']}")
    trade_win.geometry("480x460")
    trade_win.configure(bg="white")

    bal_var = tk.StringVar(value=f"Balance: ₹{user_data['balance']}")
    tk.Label(trade_win, textvariable=bal_var, font=("Arial", 12, "bold"), bg="white").pack(pady=6)

    # Sector selection
    tk.Label(trade_win, text="Select Sector:", font=("Arial", 11), bg="white").pack()
    sector_var = tk.StringVar()
    sector_combo = ttk.Combobox(trade_win, textvariable=sector_var,
                                values=["Automobile", "Petroleum", "Steel"], state="readonly")
    sector_combo.pack(pady=5)

    # Company selection
    tk.Label(trade_win, text="Select Company:", font=("Arial", 11), bg="white").pack()
    company_var = tk.StringVar()
    company_combo = ttk.Combobox(trade_win, textvariable=company_var, state="readonly")
    company_combo.pack(pady=5)

    price_var = tk.StringVar(value="Price: -")
    tk.Label(trade_win, textvariable=price_var, font=("Arial", 11, "italic"), bg="white").pack()

    def update_companies(event=None):
        sec = sector_var.get()
        if sec == "Automobile":
            company_combo["values"] = list(AUTO_COMPANIES.keys())
        elif sec == "Petroleum":
            company_combo["values"] = list(PETROLEUM_COMPANIES.keys())
        elif sec == "Steel":
            company_combo["values"] = list(STEEL_COMPANIES.keys())
        else:
            company_combo["values"] = []
        company_var.set("")
        price_var.set("Price: -")

    def update_price(event=None):
        comp = company_var.get()
        if comp:
            price_var.set(f"Price: ₹{PRICES.get(comp, '-')}")
        else:
            price_var.set("Price: -")

    sector_combo.bind("<<ComboboxSelected>>", update_companies)
    company_combo.bind("<<ComboboxSelected>>", update_price)

    tk.Label(trade_win, text="Quantity:", font=("Arial", 11), bg="white").pack()
    qty_entry = tk.Entry(trade_win, font=("Arial", 11))
    qty_entry.pack(pady=5)

    def commit_and_refresh():
        save_users(users)
        bal_var.set(f"Balance: ₹{user_data['balance']}")

    def portfolio_key_for_sector(sec):
        if sec == "Automobile":
            return "shares"
        elif sec == "Petroleum":
            return "petroleum_shares"
        elif sec == "Steel":
            return "steel_shares"
        return None

    def buy_stock():
        company = company_var.get()
        sec = sector_var.get()
        qty_txt = qty_entry.get().strip()
        if not sec:
            messagebox.showerror("Error", "Please select a sector.")
            return
        if not company:
            messagebox.showerror("Error", "Please select a company.")
            return
        if not qty_txt.isdigit() or int(qty_txt) <= 0:
            messagebox.showerror("Error", "Enter a valid positive quantity.")
            return
        qty = int(qty_txt)
        unit = PRICES.get(company)
        if unit is None:
            messagebox.showerror("Error", "Price not available for selected company.")
            return
        cost = unit * qty
        if user_data["balance"] < cost:
            messagebox.showerror("Error", f"Insufficient balance. Need ₹{cost}, have ₹{user_data['balance']}.")
            return
        pkey = portfolio_key_for_sector(sec)
        if pkey is None:
            messagebox.showerror("Error", "Invalid sector.")
            return
        user_data["balance"] -= cost
        # Ensure key exists
        if pkey not in user_data:
            user_data[pkey] = get_default_shares(AUTO_COMPANIES if pkey == "shares" else PETROLEUM_COMPANIES if pkey=="petroleum_shares" else STEEL_COMPANIES)
        user_data[pkey][company] = user_data[pkey].get(company, 0) + qty
        commit_and_refresh()
        messagebox.showinfo("Success", f"Bought {qty} shares of {company} for ₹{cost}.")

    def sell_stock():
        company = company_var.get()
        sec = sector_var.get()
        qty_txt = qty_entry.get().strip()
        if not sec:
            messagebox.showerror("Error", "Please select a sector.")
            return
        if not company:
            messagebox.showerror("Error", "Please select a company.")
            return
        if not qty_txt.isdigit() or int(qty_txt) <= 0:
            messagebox.showerror("Error", "Enter a valid positive quantity.")
            return
        qty = int(qty_txt)
        pkey = portfolio_key_for_sector(sec)
        if pkey is None:
            messagebox.showerror("Error", "Invalid sector.")
            return
        if user_data.get(pkey, {}).get(company, 0) < qty:
            messagebox.showerror("Error", "Not enough shares to sell.")
            return
        earnings = PRICES.get(company, 0) * qty
        user_data[pkey][company] -= qty
        user_data["balance"] += earnings
        commit_and_refresh()
        messagebox.showinfo("Success", f"Sold {qty} shares of {company} for ₹{earnings}.")

    tk.Button(trade_win, text="Buy", font=("Arial", 12, "bold"), bg="green", fg="white", command=buy_stock).pack(pady=6)
    tk.Button(trade_win, text="Sell", font=("Arial", 12, "bold"), bg="red", fg="white", command=sell_stock).pack(pady=6)

    # Quick links to portfolio windows
    btns = tk.Frame(trade_win, bg="white")
    btns.pack(pady=10)
    tk.Button(btns, text="Automobile Portfolio", command=lambda: show_auto_shares_window(user_email)).grid(row=0, column=0, padx=6)
    tk.Button(btns, text="Petroleum Portfolio", command=lambda: show_petroleum_shares_window(user_email)).grid(row=0, column=1, padx=6)
    tk.Button(btns, text="Steel Portfolio", command=lambda: show_steel_shares_window(user_email)).grid(row=0, column=2, padx=6)

# ---------- Portfolio display windows ----------
def show_auto_shares_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return
    user_data = users[user_email]
    auto_data = user_data.get("shares", {})

    auto_win = tk.Toplevel(root)
    auto_win.title(f"{user_data['name']}'s Automobile Shares")
    auto_win.geometry("520x450")
    auto_win.configure(bg="white")

    # optional image
    img = load_image(IMAGE_PATHS.get("auto_bg", ""), (800, 200))
    if img:
        tk.Label(auto_win, image=img, bg="white").pack(pady=8).image = img
    else:
        tk.Label(auto_win, text="🚗 Automobile Shares", font=("Arial", 14, "bold"), bg="white").pack(pady=8)

    frame = tk.Frame(auto_win, bg="white")
    frame.pack(pady=6)

    tk.Label(frame, text="Company", font=("Arial", 12, "bold"), width=30, anchor="w", bg="white").grid(row=0, column=0)
    tk.Label(frame, text="Shares", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=1)
    tk.Label(frame, text="Price", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=2)
    tk.Label(frame, text="Link", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=3)

    for i, (company, shares) in enumerate(auto_data.items(), start=1):
        tk.Label(frame, text=company, font=("Arial", 11), width=30, anchor="w", bg="white").grid(row=i, column=0, pady=2)
        tk.Label(frame, text=str(shares), font=("Arial", 11), width=10, anchor="center", bg="white").grid(row=i, column=1, pady=2)
        tk.Label(frame, text=f"₹{PRICES.get(company,'-')}", font=("Arial", 11), width=10, anchor="center", bg="white").grid(row=i, column=2, pady=2)
        tk.Button(frame, text="View", font=("Arial", 10, "bold"), fg="blue", cursor="hand2",
                  command=lambda url=AUTO_COMPANIES[company]: open_link(url)).grid(row=i, column=3, pady=2)

def show_petroleum_shares_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return
    user_data = users[user_email]
    petro_data = user_data.get("petroleum_shares", {})

    petro_win = tk.Toplevel(root)
    petro_win.title(f"{user_data['name']}'s Petroleum Shares")
    petro_win.geometry("520x500")
    petro_win.configure(bg="white")

    img = load_image(IMAGE_PATHS.get("petro_bg", ""), (800, 200))
    if img:
        tk.Label(petro_win, image=img, bg="white").pack(pady=8).image = img
    else:
        tk.Label(petro_win, text="🛢️ Petroleum Shares", font=("Arial", 14, "bold"), bg="white").pack(pady=8)

    frame = tk.Frame(petro_win, bg="white")
    frame.pack(pady=6)

    tk.Label(frame, text="Company", font=("Arial", 12, "bold"), width=30, anchor="w", bg="white").grid(row=0, column=0)
    tk.Label(frame, text="Shares", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=1)
    tk.Label(frame, text="Price", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=2)
    tk.Label(frame, text="Link", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=3)

    for i, (company, shares) in enumerate(petro_data.items(), start=1):
        tk.Label(frame, text=company, font=("Arial", 11), width=30, anchor="w", bg="white").grid(row=i, column=0, pady=2)
        tk.Label(frame, text=str(shares), font=("Arial", 11), width=10, anchor="center", bg="white").grid(row=i, column=1, pady=2)
        tk.Label(frame, text=f"₹{PRICES.get(company,'-')}", font=("Arial", 11), width=10, anchor="center", bg="white").grid(row=i, column=2, pady=2)
        tk.Button(frame, text="View", font=("Arial", 10, "bold"), fg="blue", cursor="hand2",
                  command=lambda url=PETROLEUM_COMPANIES[company]: open_link(url)).grid(row=i, column=3, pady=2)

def show_steel_shares_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return
    user_data = users[user_email]
    steel_data = user_data.get("steel_shares", {})

    steel_win = tk.Toplevel(root)
    steel_win.title(f"{user_data['name']}'s Steel Shares")

    steel_win.geometry("520x500")
    steel_win.configure(bg="white")

    img = load_image(IMAGE_PATHS.get("steel_bg", ""), (800, 200))
    if img:
        tk.Label(steel_win, image=img, bg="white").pack(pady=8).image = img
    else:
        tk.Label(steel_win, text="🛠️ Steel Shares", font=("Arial", 14, "bold"), bg="white").pack(pady=8)

    frame = tk.Frame(steel_win, bg="white")
    frame.pack(pady=6)

    tk.Label(frame, text="Company", font=("Arial", 12, "bold"), width=30, anchor="w", bg="white").grid(row=0, column=0)
    tk.Label(frame, text="Shares", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=1)
    tk.Label(frame, text="Price", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=2)
    tk.Label(frame, text="Link", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=3)

    for i, (company, shares) in enumerate(steel_data.items(), start=1):
        tk.Label(frame, text=company, font=("Arial", 11), width=30, anchor="w", bg="white").grid(row=i, column=0, pady=2)
        tk.Label(frame, text=str(shares), font=("Arial", 11), width=10, anchor="center", bg="white").grid(row=i, column=1, pady=2)
        tk.Label(frame, text=f"₹{PRICES.get(company,'-')}", font=("Arial", 11), width=10, anchor="center", bg="white").grid(row=i, column=2, pady=2)
        tk.Button(frame, text="View", font=("Arial", 10, "bold"), fg="blue", cursor="hand2",
                  command=lambda url=STEEL_COMPANIES[company]: open_link(url)).grid(row=i, column=3, pady=2)

# ---------- Admin ----------
def check_admin_password():
    pass_win = tk.Toplevel(root)
    pass_win.title("Admin Login")
    pass_win.geometry("300x220")
    pass_win.configure(bg="white")

    admin_img = load_image(IMAGE_PATHS.get("admin", ""), (80, 80))
    if admin_img:
        tk.Label(pass_win, image=admin_img, bg="white").pack(pady=5).image = admin_img

    tk.Label(pass_win, text="🔑 Enter Admin Password", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
    pwd_entry = tk.Entry(pass_win, font=("Arial", 12), show="*")
    pwd_entry.pack(pady=5)

    def verify():
        if pwd_entry.get().strip() == ADMIN_PASSWORD:
            pass_win.destroy()
            show_all_registrations()
        else:
            messagebox.showerror("Access Denied", "Incorrect password!")

    tk.Button(pass_win, text="Login", font=("Arial", 12, "bold"), bg="blue", fg="white", command=verify).pack(pady=10)

def show_all_registrations():
    records = load_registrations()
    if not records:
        messagebox.showinfo("Info", "No registrations found.")
        return

    admin_win = tk.Toplevel(root)
    admin_win.title("Company Records - All Registrations")
    admin_win.geometry("700x500")
    admin_win.configure(bg="white")

    tk.Label(admin_win, text="All User Registrations", font=("Arial", 14, "bold"), bg="white").pack(pady=5)

    frame = tk.Frame(admin_win, bg="white")
    frame.pack(pady=10)

    tk.Label(frame, text="Name", font=("Arial", 12, "bold"), width=30, anchor="w", bg="white").grid(row=0, column=0)
    tk.Label(frame, text="Email", font=("Arial", 12, "bold"), width=40, anchor="w", bg="white").grid(row=0, column=1)
    tk.Label(frame, text="Bonus", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=2)

    for i, user in enumerate(records, start=1):
        tk.Label(frame, text=user.get("name",""), font=("Arial", 11), width=30, anchor="w", bg="white").grid(row=i, column=0, pady=2)
        tk.Label(frame, text=user.get("email",""), font=("Arial", 11), width=40, anchor="w", bg="white").grid(row=i, column=1, pady=2)
        tk.Label(frame, text=f"₹{user.get('bonus',0)}", font=("Arial", 11), width=10, anchor="center", bg="white").grid(row=i, column=2, pady=2)

# ---------- Main GUI ----------
root = tk.Tk()
root.title("Stock Market - Registration")
root.geometry("420x600")
root.configure(bg="white")

logo_img = load_image(IMAGE_PATHS.get("logo",""), (380, 140))
if logo_img:
    logo_label = tk.Label(root, image=logo_img, bg="white")
    logo_label.image = logo_img
    logo_label.pack(pady=10)

tk.Label(root, text="📈 Stock Market", font=("Arial", 20, "bold"), bg="white").pack(pady=5)

tk.Label(root, text="Name:", font=("Arial", 12), bg="white").pack()
entry_name = tk.Entry(root, font=("Arial", 12))
entry_name.pack(pady=5)

tk.Label(root, text="Email:", font=("Arial", 12), bg="white").pack()
entry_email = tk.Entry(root, font=("Arial", 12))
entry_email.pack(pady=5)

tk.Label(root, text="Password:", font=("Arial", 12), bg="white").pack()
entry_password = tk.Entry(root, font=("Arial", 12), show="*")
entry_password.pack(pady=5)

tk.Button(root, text="Register", font=("Arial", 12, "bold"), bg="green", fg="white", command=register_user).pack(pady=15)

quick = tk.Frame(root, bg="white")
quick.pack()
tk.Button(quick, text="Company Records", font=("Arial", 12, "bold"), bg="blue", fg="white", command=check_admin_password).grid(row=0, column=0, padx=12)

root.mainloop()
