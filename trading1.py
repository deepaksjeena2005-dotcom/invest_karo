import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import json
import os
import random
import webbrowser

DB_FILE = "users.json"
REG_FILE = "registrations.json"


# Automobile companies & their share price links
AUTO_COMPANIES = {
    "Honda": "https://www.screener.in/company/522064/",
    "Hyundai": "https://www.screener.in/company/540005/",
    "Tata Motors": "https://www.screener.in/company/TATAMOTORS/",
    "Mahindra": "https://www.screener.in/company/M%26M/",
    "Maruti Suzuki": "https://www.screener.in/company/MARUTI/",
    "Ashok Leyland": "https://www.screener.in/company/ASHOKLEY/",
    "Beamer": "https://www.screener.in/company/542669/"
}

# Petroleum companies & their share price links
PETROLEUM_COMPANIES = {
    "Reliance Industries": "https://www.screener.in/company/RELIANCE/consolidated/",
    "Indian Oil Corporation": "https://www.screener.in/company/IOC/",
    "Bharat Petroleum": "https://www.screener.in/company/BPCL/",
    "Hindustan Petroleum": "https://www.screener.in/company/HINDPETRO/",
    "Oil India": "https://www.screener.in/company/OIL/"
}

# Steel companies & their share price links
STEEL_COMPANIES = {
    "Tata Steel": "https://www.screener.in/company/TATASTEEL/",
    "JSW Steel": "https://www.screener.in/company/JSWSTEEL/",
    "Steel Authority of India (SAIL)": "https://www.screener.in/company/SAIL/",
    "Jindal Steel & Power": "https://www.screener.in/company/JINDALSTEL/",
    "NMDC Steel": "https://www.screener.in/company/NMDCSTEEL/"
}

# Dummy stock prices (for buy/sell simulation)
PRICES = {
    **{c: 10 for c in AUTO_COMPANIES},        # ₹10 each in Automobile
    **{c: 15 for c in PETROLEUM_COMPANIES},   # ₹15 each in Petroleum
    **{c: 20 for c in STEEL_COMPANIES}        # ₹20 each in Steel
}

ADMIN_PASSWORD = "admin123"

# ----------------- Helper Functions ----------------- #

def load_image(path, size):
    """Load and resize image safely"""
    try:
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize(size)
            return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Image load error for {path}: {e}")
    return None

def open_link(url):
    """Open a company link in browser"""
    webbrowser.open(url)

def safe_json_load(path, default):
    """Safely load JSON file with error handling"""
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
    """Load users from JSON file"""
    return safe_json_load(DB_FILE, {})

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving users: {e}")

def save_registration(entry):
    """Save registration entry to separate file"""
    try:
        data = safe_json_load(REG_FILE, [])
        data.append(entry)
        with open(REG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving registration: {e}")

def get_default_shares(company_dict):
    """Get default share count (0) for all companies in a sector"""
    return {company: 0 for company in company_dict.keys()}

def validate_email(email):
    """Basic email validation"""
    return "@" in email and "." in email.split("@")[1]

def validate_password(password):
    """Basic password validation"""
    return len(password) >= 6


# ----------------- Authentication Module ----------------- #

class AuthManager:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def signup_user(self, name, email, password):
        """Handle user signup"""
        # Validation
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
        
        # Create new user
        new_user = {
            "name": name,
            "password": password,
            "balance": 100,  # Starting balance
            "shares": get_default_shares(AUTO_COMPANIES),
            "petroleum_shares": get_default_shares(PETROLEUM_COMPANIES),
            "steel_shares": get_default_shares(STEEL_COMPANIES),
            "bonus": 100,
            "signup_date": str(tk.datetime.datetime.now().date()) if hasattr(tk, 'datetime') else "2024-01-01"
        }
        
        users[email] = new_user
        save_users(users)
        save_registration(new_user)
        
        messagebox.showinfo("Success", f"Welcome {name}!\nSignup successful! You received ₹100 bonus.")
        return True
    
    def signin_user(self, email, password):
        """Handle user signin"""
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

# ----------------- Trading Module ----------------- #

def buy_sell_window(user_email):
    """Main trading interface"""
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return

    user_data = users[user_email]

    trade_win = tk.Toplevel()
    trade_win.title(f"InvestKaro - {user_data['name']}")
    trade_win.geometry("500x500")
    trade_win.configure(bg="white")

    # Balance display
    bal_var = tk.StringVar(value=f"Balance: ₹{user_data['balance']}")
    tk.Label(trade_win, textvariable=bal_var, font=("Arial", 14, "bold"), 
             bg="white", fg="green").pack(pady=10)

    # Sector selection
    tk.Label(trade_win, text="Select Sector:", font=("Arial", 12, "bold"), bg="white").pack()
    sector_var = tk.StringVar()
    sector_combo = ttk.Combobox(trade_win, textvariable=sector_var, 
                                values=["Automobile", "Petroleum", "Steel"], 
                                state="readonly", font=("Arial", 11))
    sector_combo.pack(pady=5)

    # Company selection
    tk.Label(trade_win, text="Select Company:", font=("Arial", 12, "bold"), bg="white").pack()
    company_var = tk.StringVar()
    company_combo = ttk.Combobox(trade_win, textvariable=company_var, 
                                state="readonly", font=("Arial", 11))
    company_combo.pack(pady=5)

    # Price display
    price_var = tk.StringVar(value="Price: -")
    tk.Label(trade_win, textvariable=price_var, font=("Arial", 12, "italic"), 
             bg="white", fg="blue").pack(pady=5)

    def update_companies(event):
        """Update company dropdown based on sector selection"""
        sector = sector_var.get()
        if sector == "Automobile":
            company_combo["values"] = list(AUTO_COMPANIES.keys())
        elif sector == "Petroleum":
            company_combo["values"] = list(PETROLEUM_COMPANIES.keys())
        elif sector == "Steel":
            company_combo["values"] = list(STEEL_COMPANIES.keys())
        company_var.set("")
        price_var.set("Price: -")

    def update_price(event):
        """Update price display when company is selected"""
        comp = company_var.get()
        if comp:
            price_var.set(f"Price: ₹{PRICES.get(comp, '-')}")

    sector_combo.bind("<<ComboboxSelected>>", update_companies)
    company_combo.bind("<<ComboboxSelected>>", update_price)

    # Quantity input
    tk.Label(trade_win, text="Quantity:", font=("Arial", 12, "bold"), bg="white").pack()
    qty_entry = tk.Entry(trade_win, font=("Arial", 12))
    qty_entry.pack(pady=5)

    def commit_and_refresh():
        """Save changes and refresh display"""
        save_users(users)
        bal_var.set(f"Balance: ₹{user_data['balance']}")

    def buy_stock():
        """Handle stock purchase"""
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
        
        # Deduct balance and add shares
        user_data["balance"] -= cost
        
        if company in AUTO_COMPANIES:
            user_data["shares"][company] += qty
        elif company in PETROLEUM_COMPANIES:
            user_data["petroleum_shares"][company] += qty
        elif company in STEEL_COMPANIES:
            user_data["steel_shares"][company] += qty
            
        commit_and_refresh()
        messagebox.showinfo("Success", f"✅ Bought {qty} shares of {company}\nCost: ₹{cost}")
        qty_entry.delete(0, tk.END)

    def sell_stock():
        """Handle stock sale"""
        company = company_var.get()
        qty_txt = qty_entry.get().strip()
        
        if not company:
            messagebox.showerror("Error", "Please select a company.")
            return
        if not qty_txt.isdigit() or int(qty_txt) <= 0:
            messagebox.showerror("Error", "Enter a valid positive quantity.")
            return
            
        qty = int(qty_txt)
        
        # Check which portfolio the company belongs to
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
        
        # Sell shares and add money
        user_data[portfolio_key][company] -= qty
        earnings = PRICES[company] * qty
        user_data["balance"] += earnings
        
        commit_and_refresh()
        messagebox.showinfo("Success", f"✅ Sold {qty} shares of {company}\nEarned: ₹{earnings}")
        qty_entry.delete(0, tk.END)

    # Trading buttons
    btn_frame = tk.Frame(trade_win, bg="white")
    btn_frame.pack(pady=20)
    
    tk.Button(btn_frame, text="🔶 BUY", font=("Arial", 14, "bold"), 
             bg="green", fg="white", command=buy_stock, width=10).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="🔻 SELL", font=("Arial", 14, "bold"), 
             bg="red", fg="white", command=sell_stock, width=10).grid(row=0, column=1, padx=10)

    # Portfolio buttons
    portfolio_frame = tk.Frame(trade_win, bg="white")
    portfolio_frame.pack(pady=10)
    
    tk.Button(portfolio_frame, text="🚗 Auto Portfolio", font=("Arial", 11), bg="lightblue", 
             command=lambda: show_portfolio_window(user_email, "auto")).grid(row=0, column=0, padx=5)
    tk.Button(portfolio_frame, text="⛽ Petroleum Portfolio", font=("Arial", 11), bg="orange", 
             command=lambda: show_portfolio_window(user_email, "petroleum")).grid(row=0, column=1, padx=5)
    tk.Button(portfolio_frame, text="🏭 Steel Portfolio", font=("Arial", 11), bg="gray", 
             command=lambda: show_portfolio_window(user_email, "steel")).grid(row=0, column=2, padx=5)
    tk.Button(portfolio_frame, text="Refresh Balance", font=("Arial", 11), bg="yellow",
             command=commit_and_refresh).grid(row=0, column=3, padx=5)
    tk.Button(portfolio_frame, text="logout", font=("arial",11), bg="pink",
                command=trade_win.destroy).grid(row=0, column=4, padx=5)
    tk.Button(portfolio_frame, text="Exit app", font=("arial",11), bg="red",
                command=trade_win.quit).grid(row=0, column=5, padx=5)
        
# ----------------- Portfolio Display Module ----------------- #

def show_portfolio_window(user_email, sector):
    """Display user's portfolio for a specific sector"""
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return

    user_data = users[user_email]
    
    # Select portfolio data, links, title, bg, and image based on sector
    if sector == "auto":
        portfolio_data = user_data.get("shares", {})
        company_links = AUTO_COMPANIES
        title = "🚗 Automobile Portfolio"
        bg_color = "steelblue"
        sector_img_path = "sectors/auto.png"
        def load_image(path, size):
            try:
                img = Image.open("C:\\Users\\neham\\Downloads\\auto.png.png")
                img = img.resize((400, 250), Image.LANCZOS)   # 👈 this line resizes
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print("Image load error:", e)
                return None
    elif sector == "petroleum":
        portfolio_data = user_data.get("petroleum_shares", {})
        company_links = PETROLEUM_COMPANIES
        title = "⛽ Petroleum Portfolio"
        bg_color = "orange"
        sector_img_path = "sectors/petro.png"
        def load_image(path, size):
            try:
                img = Image.open("C:\\Users\\neham\\Downloads\\petro.png.png")
                img = img.resize((400, 250), Image.LANCZOS)   # 👈 this line resizes
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print("Image load error:", e)
                return None
    else:
        sector == "steel"
        portfolio_data = user_data.get("steel_shares", {})
        company_links = STEEL_COMPANIES
        title = "🏭 Steel Portfolio"
        bg_color = "lightgray"
        sector_img_path = "sectors/steel1.png"

        def load_image(path, size):
            try:
                img = Image.open("C:\\Users\\neham\\Downloads\\steel1.png.png")
                img = img.resize((400, 250), Image.LANCZOS)   # 👈 this line resizes
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print("Image load error:", e)
                return None

    # Create new window
    portfolio_win = tk.Toplevel()
    portfolio_win.title(f"{user_data['name']}'s {title}")
    portfolio_win.geometry("650x500")
    portfolio_win.configure(bg="lime green")

    # Title Label
    tk.Label(portfolio_win, text=title, font=("Arial", 16, "bold"), 
             bg=bg_color, fg="black").pack(pady=10, fill="x")

    # Sector Image
    try:
        sector_img = load_image(sector_img_path, (100, 100))
        tk.Label(portfolio_win, image=sector_img, bg="lime green").pack()
        portfolio_win.sector_img_ref = sector_img  # prevent garbage collection
    except:
        tk.Label(portfolio_win, text="[Sector Image Missing]", bg="lime green", fg="red").pack()

    # Portfolio Table Frame
    frame = tk.Frame(portfolio_win, bg="white")
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Headers
    headers = ["Company", "Shares", "Unit Price", "Total Value", "View Link"]
    for i, header in enumerate(headers):
        tk.Label(frame, text=header, font=("Arial", 12, "bold"), 
                width=15, bg="lightgray", relief="ridge").grid(row=0, column=i, padx=1, pady=1)

    # Portfolio Data
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

    # Total Value Display
    tk.Label(portfolio_win, text=f"Total Portfolio Value: ₹{total_portfolio_value}", 
             font=("Arial", 14, "bold"), bg="yellow", fg="black").pack(pady=10, fill="x")


# ----------------- Admin Module ----------------- #

def check_admin_password():
    """Admin login verification"""
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
    """Admin dashboard showing all user data"""
    users = load_users()
    if not users:
        messagebox.showinfo("Info", "No users found in database.")
        return

    admin_dash = tk.Toplevel()
    admin_dash.title("Admin Dashboard - All Users")
    admin_dash.geometry("900x600")
    admin_dash.configure(bg="white")

    tk.Label(admin_dash, text="📊 Admin Dashboard - User Records", 
             font=("Arial", 16, "bold"), bg="red", fg="white").pack(fill="x", pady=5)

    # Scrollable frame
    canvas = tk.Canvas(admin_dash, bg="white")
    scrollbar = ttk.Scrollbar(admin_dash, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Headers
    headers = ["Name", "Email", "Balance", "Auto Stocks", "Petro Stocks", "Steel Stocks", "Total Portfolio"]
    for i, header in enumerate(headers):
        tk.Label(scrollable_frame, text=header, font=("Arial", 11, "bold"), 
                width=15, bg="lightgray", relief="ridge").grid(row=0, column=i, padx=1, pady=1)

    # User data
    for row, (email, user) in enumerate(users.items(), start=1):
        auto_total = sum(user.get("shares", {}).values())
        petro_total = sum(user.get("petroleum_shares", {}).values())
        steel_total = sum(user.get("steel_shares", {}).values())
        
        # Calculate portfolio values
        auto_value = sum(shares * PRICES.get(company, 0) for company, shares in user.get("shares", {}).items())
        petro_value = sum(shares * PRICES.get(company, 0) for company, shares in user.get("petroleum_shares", {}).items())
        steel_value = sum(shares * PRICES.get(company, 0) for company, shares in user.get("steel_shares", {}).items())
        total_portfolio = auto_value + petro_value + steel_value

        data = [
            user.get("name", ""),
            email,
            f"₹{user.get('balance', 0)}",
            f"{auto_total} (₹{auto_value})",
            f"{petro_total} (₹{petro_value})",
            f"{steel_total} (₹{steel_value})",
            f"₹{total_portfolio}"
        ]

        for col, value in enumerate(data):
            tk.Label(scrollable_frame, text=str(value), font=("Arial", 10), 
                    width=15, bg="white", relief="ridge").grid(row=row, column=col, padx=1, pady=1)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# ----------------- Main Application GUI ----------------- #

def create_main_window():
    """Create the main login/signup window"""
    global root
    root = tk.Tk()
    root.title("InvestKaro - Stock Market Simulator")
    root.geometry("500x700")
    root.configure(bg="white")
    
    # Try to load logo
    logo_img = load_image("C:\\Users\\neham\\Downloads\\IK.png.png", (300, 200))
    if logo_img:
        logo_label = tk.Label(root, image=logo_img, bg="white")
        logo_label.image = logo_img  # Keep reference
        logo_label.pack(pady=10)
    else:
        # Fallback if image not found
        tk.Label(root, text="📈 InvestKaro", font=("Arial", 24, "bold"), 
                bg="white", fg="green").pack(pady=20)

    tk.Label(root, text="Stock Market Simulator", font=("Arial", 16), 
             bg="white", fg="gray").pack()

    # Create notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(pady=20, expand=True, fill="both", padx=20)

    # Initialize auth manager
    auth_manager = AuthManager(root)

    # ========== Signup Tab ==========
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
            # Clear fields
            signup_name_entry.delete(0, tk.END)
            signup_email_entry.delete(0, tk.END)
            signup_password_entry.delete(0, tk.END)
            # Switch to login tab
            notebook.select(1)

    tk.Button(signup_frame, text="Create Account", font=("Arial", 14, "bold"), 
             bg="green", fg="white", command=handle_signup, width=15).pack(pady=20)

    tk.Label(signup_frame, text="🎁 Get ₹100 signup bonus!", font=("Arial", 12, "italic"), 
             bg="white", fg="orange").pack()

    # ========== Login Tab ==========
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
            # Clear fields
            login_email_entry.delete(0, tk.END)
            login_password_entry.delete(0, tk.END)
            # Open trading window
            buy_sell_window(user_email)

    tk.Button(login_frame, text="Login", font=("Arial", 14, "bold"), 
             bg="blue", fg="white", command=handle_login, width=15).pack(pady=20)

    # ========== Admin Tab ==========
    admin_frame = tk.Frame(notebook, bg="white")
    notebook.add(admin_frame, text="👨‍💼 Admin")

    tk.Label(admin_frame, text="Administrator Panel", font=("Arial", 18, "bold"), 
             bg="white", fg="red").pack(pady=40)

    tk.Button(admin_frame, text="View All Users", font=("Arial", 14, "bold"), 
             bg="red", fg="white", command=check_admin_password, width=15).pack(pady=20)

    tk.Label(admin_frame, text="⚠️ Admin access required", font=("Arial", 12, "italic"), 
             bg="white", fg="gray").pack()

    return root

# ----------------- Application Entry Point ----------------- #

if __name__ == "__main__":
    # Create and run the main application
    try:
        import datetime
        tk.datetime = datetime  # Add datetime to tk for date functionality
    except ImportError:
        pass
    
    root = create_main_window()
    root.mainloop()