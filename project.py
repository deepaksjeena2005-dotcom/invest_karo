import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import json
import os
import webbrowser

DB_FILE = "users.json"
REG_FILE = "registrations.json"

AUTO_COMPANIES = {
    "Honda": "https://www.screener.in/company/522064/",
    "Hyundai": "https://www.screener.in/company/540005/",
    "Tata Motors": "https://www.screener.in/company/TATAMOTORS/",
    "Mahindra": "https://www.screener.in/company/M%26M/",
    "Maruti Suzuki": "https://www.screener.in/company/MARUTI/",
    "Ashok Leyland": "https://www.screener.in/company/ASHOKLEY/",
    "Beamer": "https://www.screener.in/company/542669/"
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

# GOLD SECTOR
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
    **{c: 50 for c in GOLD_COMPANIES}
}

ADMIN_PASSWORD = "admin123"

def load_image(path, size):
    try:
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize(size)
            return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Image load error for {path}: {e}")
    return None

def open_link(url):
    webbrowser.open(url)

def safe_json_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return default
        return json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"JSON load error for {path}: {e}")
        return default

def load_users():
    return safe_json_load(DB_FILE, {})

def save_users(users):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving users: {e}")

def save_registration(entry):
    try:
        data = safe_json_load(REG_FILE, [])
        data.append(entry)
        with open(REG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving registration: {e}")

def get_default_shares(company_dict):
    return {company: 0 for company in company_dict.keys()}

def validate_email(email):
    return "@" in email and "." in email.split("@")[1]

def validate_password(password):
    return len(password) >= 6

class AuthManager:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def signup_user(self, name, email, password):
        if not name or not email or not password:
            messagebox.showerror("Error", "All fields are required!")
            return False
        if not validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address!")
            return False
        if not validate_password(password):
            messagebox.showerror("Error", "Password must be at least 6 characters long!")
            return False
        users = load_users()
        if email in users:
            messagebox.showerror("Error", "Email already registered! Please use Login.")
            return False

        new_user = {
            "name": name,
            "password": password,
            "balance": 100,
            "shares": get_default_shares(AUTO_COMPANIES),
            "petroleum_shares": get_default_shares(PETROLEUM_COMPANIES),
            "steel_shares": get_default_shares(STEEL_COMPANIES),
            "gold_shares": get_default_shares(GOLD_COMPANIES),
            "bonus": 100,
            "signup_date": str(tk.datetime.datetime.now().date()) if hasattr(tk, 'datetime') else "2024-01-01"
        }
        users[email] = new_user
        save_users(users)
        save_registration(new_user)
        messagebox.showinfo("Success", f"Welcome {name}!\nSignup successful! You received ₹100 bonus.")
        return True
    
    def signin_user(self, email, password):
        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password!")
            return False
        users = load_users()
        if email not in users:
            messagebox.showerror("Error", "User not found! Please signup first.")
            return False
        if users[email]["password"] != password:
            messagebox.showerror("Error", "Incorrect password!")
            return False
        messagebox.showinfo("Welcome", f"Welcome back {users[email]['name']}!\nBalance: ₹{users[email]['balance']}")
        return email

def buy_sell_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return

    user_data = users[user_email]

    trade_win = tk.Toplevel()
    trade_win.title(f"InvestKaro - {user_data['name']}")
    trade_win.geometry("500x500")
    trade_win.configure(bg="white")

    bal_var = tk.StringVar(value=f"Balance: ₹{user_data['balance']}")
    tk.Label(trade_win, textvariable=bal_var, font=("Arial", 14, "bold"), 
             bg="white", fg="green").pack(pady=10)

    tk.Label(trade_win, text="Select Sector:", font=("Arial", 12, "bold"), bg="white").pack()
    sector_var = tk.StringVar()
    sector_combo = ttk.Combobox(trade_win, textvariable=sector_var, 
                                values=["Automobile", "Petroleum", "Steel", "Gold"], 
                                state="readonly", font=("Arial", 11))
    sector_combo.pack(pady=5)

    tk.Label(trade_win, text="Select Company:", font=("Arial", 12, "bold"), bg="white").pack()
    company_var = tk.StringVar()
    company_combo = ttk.Combobox(trade_win, textvariable=company_var, 
                                state="readonly", font=("Arial", 11))
    company_combo.pack(pady=5)

    price_var = tk.StringVar(value="Price: -")
    tk.Label(trade_win, textvariable=price_var, font=("Arial", 12, "italic"), 
             bg="white", fg="blue").pack(pady=5)

    def update_companies(event):
        sector = sector_var.get()
        if sector == "Automobile":
            company_combo["values"] = list(AUTO_COMPANIES.keys())
        elif sector == "Petroleum":
            company_combo["values"] = list(PETROLEUM_COMPANIES.keys())
        elif sector == "Steel":
            company_combo["values"] = list(STEEL_COMPANIES.keys())
        elif sector == "Gold":
            company_combo["values"] = list(GOLD_COMPANIES.keys())
        company_var.set("")
        price_var.set("Price: -")

    def update_price(event):
        comp = company_var.get()
        if comp:
            price_var.set(f"Price: ₹{PRICES.get(comp, '-')}")

    sector_combo.bind("<<ComboboxSelected>>", update_companies)
    company_combo.bind("<<ComboboxSelected>>", update_price)

    tk.Label(trade_win, text="Quantity:", font=("Arial", 12, "bold"), bg="white").pack()
    qty_entry = tk.Entry(trade_win, font=("Arial", 12))
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
        unit_price = PRICES.get(company)
        cost = unit_price * qty
        if user_data["balance"] < cost:
            messagebox.showerror("Error", f"Insufficient balance!\nNeed: ₹{cost}\nHave: ₹{user_data['balance']}")
            return
        user_data["balance"] -= cost
        if company in AUTO_COMPANIES:
            user_data["shares"][company] += qty
             
        elif company in PETROLEUM_COMPANIES:
            user_data["petroleum_shares"][company] += qty
        elif company in STEEL_COMPANIES:
            user_data["steel_shares"][company] += qty
        elif company in GOLD_COMPANIES:
            user_data["gold_shares"][company] += qty
        commit_and_refresh()
        messagebox.showinfo("Success", f"✅ Bought {qty} shares of {company}\nCost: ₹{cost}")
        qty_entry.delete(0, tk.END)

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
        current_shares = 0
        if company in AUTO_COMPANIES:
            portfolio_key = "shares"
            current_shares = user_data["shares"].get(company, 0)
        elif company in PETROLEUM_COMPANIES:
            portfolio_key = "petroleum_shares"
            current_shares = user_data["petroleum_shares"].get(company, 0)
        elif company in STEEL_COMPANIES:
            portfolio_key = "steel_shares"
            current_shares = user_data["steel_shares"].get(company, 0)
        elif company in GOLD_COMPANIES:
            portfolio_key = "gold_shares"
            current_shares = user_data["gold_shares"].get(company, 0)
        user_data[portfolio_key][company] -= qty
        earnings = PRICES[company] * qty
        user_data["balance"] += earnings
        commit_and_refresh()
        messagebox.showinfo("Success", f"✅ Sold {qty} shares of {company}\nEarned: ₹{earnings}")
        qty_entry.delete(0, tk.END)

    btn_frame = tk.Frame(trade_win, bg="white")
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="🔶 BUY", font=("Arial", 14, "bold"), 
             bg="green", fg="white", command=buy_stock, width=10).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="🔻 SELL", font=("Arial", 14, "bold"), 
             bg="red", fg="white", command=sell_stock, width=10).grid(row=0, column=1, padx=10)

    portfolio_frame = tk.Frame(trade_win, bg="white")
    portfolio_frame.pack(pady=10)
    tk.Button(portfolio_frame, text="🚗 Auto Portfolio", font=("Arial", 11), bg="lightblue", 
             command=lambda: show_portfolio_window(user_email, "auto")).grid(row=0, column=0, padx=5)
    tk.Button(portfolio_frame, text="⛽ Petroleum Portfolio", font=("Arial", 11), bg="orange", 
             command=lambda: show_portfolio_window(user_email, "petroleum")).grid(row=0, column=1, padx=5)
    tk.Button(portfolio_frame, text="🏭 Steel Portfolio", font=("Arial", 11), bg="gray", 
             command=lambda: show_portfolio_window(user_email, "steel")).grid(row=0, column=2, padx=5)
    tk.Button(portfolio_frame, text="🥇 Gold Portfolio", font=("Arial", 11), bg="gold", 
             command=lambda: show_portfolio_window(user_email, "gold")).grid(row=0, column=3, padx=5)
    tk.Button(portfolio_frame, text="Refresh Balance", font=("Arial", 11), bg="yellow",
             command=commit_and_refresh).grid(row=0, column=4, padx=5)
    tk.Button(portfolio_frame, text="logout", font=("arial",11), bg="pink",
                command=trade_win.destroy).grid(row=0, column=5, padx=5)
    tk.Button(portfolio_frame, text="Exit app", font=("arial",11), bg="red",
                command=trade_win.quit).grid(row=0, column=6, padx=5)
        
def show_portfolio_window(user_email, sector):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return

    user_data = users[user_email]
    if sector == "auto":
        portfolio_data = user_data.get("shares", {})
        company_links = AUTO_COMPANIES
        title = "🚗 Automobile Portfolio"
        bg_color = "steelblue"
        sector_img_path = "sectors/auto.png"
        def load_image_local(path, size):
            try:
                img = Image.open("C:\\Users\\neham\\Downloads\\auto.png.png")
                img = img.resize((400, 250), Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print("Image load error:", e)
                return None
        img_loader = load_image_local
    elif sector == "petroleum":
        portfolio_data = user_data.get("petroleum_shares", {})
        company_links = PETROLEUM_COMPANIES
        title = "⛽ Petroleum Portfolio"
        bg_color = "orange"
        sector_img_path = "sectors/petro.png"
        def load_image_local(path, size):
            try:
                img = Image.open("C:\\Users\\neham\\Downloads\\petro.png.png")
                img = img.resize((400, 250), Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print("Image load error:", e)
                return None
        img_loader = load_image_local
    elif sector == "steel":
        portfolio_data = user_data.get("steel_shares", {})
        company_links = STEEL_COMPANIES
        title = "🏭 Steel Portfolio"
        bg_color = "lightgray"
        sector_img_path = "sectors/steel1.png"
        def load_image_local(path, size):
            try:
                img = Image.open("C:\\Users\\neham\\Downloads\\steel1.png.png")
                img = img.resize((400, 250), Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print("Image load error:", e)
                return None
        img_loader = load_image_local
    elif sector == "gold":
        portfolio_data = user_data.get("gold_shares", {})
        company_links = GOLD_COMPANIES
        title = "🥇 Gold Portfolio"
        bg_color = "gold"
        sector_img_path = "sectors/gold.png"
        def load_image_local(path, size):
            try:
                img = Image.open("C:\\Users\\neham\\Downloads\\gold.png.png")
                img = img.resize((400, 250), Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print("Image load error:", e)
                return None
        img_loader = load_image_local
    else:
        return

    portfolio_win = tk.Toplevel()
    portfolio_win.title(f"{user_data['name']}'s {title}")
    portfolio_win.geometry("650x500")
    portfolio_win.configure(bg="lime green")

    tk.Label(portfolio_win, text=title, font=("Arial", 16, "bold"), 
             bg=bg_color, fg="black").pack(pady=10, fill="x")

    try:
        sector_img = img_loader(sector_img_path, (100, 100))
        tk.Label(portfolio_win, image=sector_img, bg="lime green").pack()
        portfolio_win.sector_img_ref = sector_img
    except:
        tk.Label(portfolio_win, text="[Sector Image Missing]", bg="lime green", fg="red").pack()

    frame = tk.Frame(portfolio_win, bg="white")
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    headers = ["Company", "Shares", "Unit Price", "Total Value", "View Link"]
    for i, header in enumerate(headers):
        tk.Label(frame, text=header, font=("Arial", 12, "bold"), 
                width=15, bg="lightgray", relief="ridge").grid(row=0, column=i, padx=1, pady=1)

    total_portfolio_value = 0
    for i, (company, shares) in enumerate(portfolio_data.items(), start=1):
        unit_price = PRICES[company]
        total_value = shares * unit_price
        total_portfolio_value += total_value
        
        tk.Label(frame, text=company, font=("Arial", 10), width=15, 
                bg="yellow", relief="ridge").grid(row=i, column=0, padx=1, pady=1)
        tk.Label(frame, text=str(shares), font=("Arial", 10), width=15, 
                bg="yellow", relief="ridge").grid(row=i, column=1, padx=1, pady=1)
        tk.Label(frame, text=f"₹{unit_price}", font=("Arial", 10), width=15, 
                bg="yellow", relief="ridge").grid(row=i, column=2, padx=1, pady=1)
        tk.Label(frame, text=f"₹{total_value}", font=("Arial", 10), width=15, 
                bg="yellow", relief="ridge", fg="blue" if total_value > 0 else "gray").grid(row=i, column=3, padx=1, pady=1)
        
        if company in company_links:
            tk.Button(frame, text="View 📊", font=("Arial", 9), bg="blue", fg="white",
                     command=lambda url=company_links[company]: open_link(url)).grid(row=i, column=4, padx=1, pady=1)

    tk.Label(portfolio_win, text=f"Total Portfolio Value: ₹{total_portfolio_value}", 
             font=("Arial", 14, "bold"), bg="yellow", fg="black").pack(pady=10, fill="x")

def check_admin_password():
    admin_win = tk.Toplevel()
    admin_win.title("Admin Login")
    admin_win.geometry("300x250")
    admin_win.configure(bg="white")
    tk.Label(admin_win, text="🔐 Admin Access", font=("Arial", 16, "bold"), bg="white").pack(pady=20)
    tk.Label(admin_win, text="Enter Admin Password:", font=("Arial", 12), bg="white").pack()
    pwd_entry = tk.Entry(admin_win, font=("Arial", 12), show="*")
    pwd_entry.pack(pady=10)

    def verify():
        if pwd_entry.get().strip() == ADMIN_PASSWORD:
            admin_win.destroy()
            show_admin_dashboard()
        else:
            messagebox.showerror("Access Denied", "Incorrect admin password!")
            pwd_entry.delete(0, tk.END)

    tk.Button(admin_win, text="Login", font=("Arial", 12, "bold"), 
             bg="red", fg="white", command=verify).pack(pady=10)

def show_admin_dashboard():
    users = load_users()
    if not users:
        messagebox.showinfo("Info", "No users found in database.")
        return

    admin_dash = tk.Toplevel()
    admin_dash.title("Admin Dashboard - All Users")
    admin_dash.geometry("1100x600")
    admin_dash.configure(bg="white")

    tk.Label(admin_dash, text="📊 Admin Dashboard - User Records", 
             font=("Arial", 16, "bold"), bg="red", fg="white").pack(fill="x", pady=5)

    canvas = tk.Canvas(admin_dash, bg="white")
    scrollbar = ttk.Scrollbar(admin_dash, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    headers = ["Name", "Email", "Balance", "Auto Stocks", "Petro Stocks", "Steel Stocks", "Gold Stocks", "Total Portfolio"]
    for i, header in enumerate(headers):
        tk.Label(scrollable_frame, text=header, font=("Arial", 11, "bold"), 
                width=15, bg="lightgray", relief="ridge").grid(row=0, column=i, padx=1, pady=1)

    for row, (email, user) in enumerate(users.items(), start=1):
        auto_total = sum(user.get("shares", {}).values())
        petro_total = sum(user.get("petroleum_shares", {}).values())
        steel_total = sum(user.get("steel_shares", {}).values())
        gold_total = sum(user.get("gold_shares", {}).values())

        auto_value = sum(shares * PRICES.get(company, 0) for company, shares in user.get("shares", {}).items())
        petro_value = sum(shares * PRICES.get(company, 0) for company, shares in user.get("petroleum_shares", {}).items())
        steel_value = sum(shares * PRICES.get(company, 0) for company, shares in user.get("steel_shares", {}).items())
        gold_value = sum(shares * PRICES.get(company, 0) for company, shares in user.get("gold_shares", {}).items())
        total_portfolio = auto_value + petro_value + steel_value + gold_value

        data = [
            user.get("name", ""),
            email,
            f"₹{user.get('balance', 0)}",
            f"{auto_total} (₹{auto_value})",
            f"{petro_total} (₹{petro_value})",
            f"{steel_total} (₹{steel_value})",
            f"{gold_total} (₹{gold_value})",
            f"₹{total_portfolio}"
        ]

        for col, value in enumerate(data):
            tk.Label(scrollable_frame, text=str(value), font=("Arial", 10), 
                    width=15, bg="white", relief="ridge").grid(row=row, column=col, padx=1, pady=1)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def create_main_window():
    global root
    root = tk.Tk()
    root.title("InvestKaro - Stock Market Simulator")
    root.geometry("500x700")
    root.configure(bg="white")
    
    logo_img = load_image("C:\\Users\\neham\\Downloads\\IK.png.png", (300, 200))
    if logo_img:
        logo_label = tk.Label(root, image=logo_img, bg="white")
        logo_label.image = logo_img
        logo_label.pack(pady=10)
    else:
        tk.Label(root, text="📈 InvestKaro", font=("Arial", 24, "bold"), 
                bg="white", fg="green").pack(pady=20)

    tk.Label(root, text="Stock Market Simulator", font=("Arial", 16), 
             bg="white", fg="gray").pack()

    notebook = ttk.Notebook(root)
    notebook.pack(pady=20, expand=True, fill="both", padx=20)

    auth_manager = AuthManager(root)

    signup_frame = tk.Frame(notebook, bg="white")
    notebook.add(signup_frame, text="📝 Sign Up")

    tk.Label(signup_frame, text="Create New Account", font=("Arial", 18, "bold"), 
             bg="white", fg="green").pack(pady=20)

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

    tk.Button(signup_frame, text="Create Account", font=("Arial", 14, "bold"), 
             bg="green", fg="white", command=handle_signup, width=15).pack(pady=20)
    tk.Label(signup_frame, text="🎁 Get ₹100 signup bonus!", font=("Arial", 12, "italic"), 
             bg="white", fg="orange").pack()

    login_frame = tk.Frame(notebook, bg="white")
    notebook.add(login_frame, text="🔑 Login")

    tk.Label(login_frame, text="Welcome Back!", font=("Arial", 18, "bold"), 
             bg="white", fg="blue").pack(pady=20)

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

    tk.Button(login_frame, text="Login", font=("Arial", 14, "bold"), 
             bg="blue", fg="white", command=handle_login, width=15).pack(pady=20)

    admin_frame = tk.Frame(notebook, bg="white")
    notebook.add(admin_frame, text="👨‍💼 Admin")

    tk.Label(admin_frame, text="Administrator Panel", font=("Arial", 18, "bold"), 
             bg="white", fg="red").pack(pady=40)

    tk.Button(admin_frame, text="View All Users", font=("Arial", 14, "bold"), 
             bg="red", fg="white", command=check_admin_password, width=15).pack(pady=20)

    tk.Label(admin_frame, text="⚠️ Admin access required", font=("Arial", 12, "italic"), 
             bg="white", fg="gray").pack()

    return root

if __name__ == "__main__":
    try:
        import datetime
        tk.datetime = datetime
    except ImportError:
        pass
    root = create_main_window()
    root.mainloop()