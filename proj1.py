import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os
import webbrowser

DB_FILE = "users.json"

# Automobile companies & their share price links
AUTO_COMPANIES = {
    "Honda": "https://www.screener.in/company/522064/?order=desc",
    "Hyundai": "https://www.screener.in/company/HYUNDAI/",
    "Tata Motors": "https://www.screener.in/company/TATAMOTORS/consolidated/",
    "Beamer": "https://www.screener.in/company/542669/",
    "Mahindra": "https://www.screener.in/company/M&M/consolidated/",
    "Maruti Suzuki": "https://www.screener.in/company/MARUTI/consolidated/"
}

# Petroleum companies & their share price links
PETROLEUM_COMPANIES = {
    "Reliance Industries": "https://www.screener.in/company/RELIANCE/consolidated/",
    "Indian Oil Corporation": "https://www.screener.in/company/IOC/",
    "Bharat Petroleum": "https://www.screener.in/company/BPCL/",
    "Hindustan Petroleum": "https://www.screener.in/company/HINDPETRO/",
    "Oil India": "https://www.screener.in/company/OIL/"
}
# ----------------- Steel companies & their share price links ----------------- #
STEEL_COMPANIES = {
    "Tata Steel": "https://www.screener.in/company/TATASTEEL/",
    "JSW Steel": "https://www.screener.in/company/JSWSTEEL/",
    "Steel Authority of India (SAIL)": "https://www.screener.in/company/SAIL/",
    "Jindal Steel & Power": "https://www.screener.in/company/JINDALSTEL/",
    "NMDC Steel": "https://www.screener.in/company/NMDCSTEEL/"
}

# ----------------- Helper Functions ----------------- #

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(DB_FILE, "w") as file:
        json.dump(users, file, indent=4)

def get_default_shares(company_dict):
    return {company: 0 for company in company_dict.keys()}

def open_link(url):
    webbrowser.open(url)

# ----------------- Automobile Shares ----------------- #

def show_shares_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return

    user_data = users[user_email]
    shares_data = user_data.get("shares", {})

    share_win = tk.Toplevel(root)
    share_win.title(f"{user_data['name']}'s Automobile Shares")
    share_win.geometry("500x450")
    share_win.configure(bg="white")

    try:
        img1 = Image.open("C:\\Users\\neham\\Downloads\\auto.png")  # Automobile image
        img1 = img1.resize((1500, 400))
        photo1 = ImageTk.PhotoImage(img1)
        lbl_img1 = tk.Label(share_win, image=photo1, bg="white")
        lbl_img1.image = photo1
        lbl_img1.pack(pady=10)
    except:
        tk.Label(share_win, text="🚗 Automobile Shares", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

    frame = tk.Frame(share_win, bg="white")
    frame.pack(pady=10)

    tk.Label(frame, text="Company", font=("Arial", 12, "bold"), width=20, anchor="w", bg="white").grid(row=0, column=0)
    tk.Label(frame, text="Shares", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=1)
    tk.Label(frame, text="Live Price", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=2)

    for i, (company, shares) in enumerate(shares_data.items(), start=1):
        tk.Label(frame, text=company, font=("Arial", 11), width=20, anchor="w", bg="white").grid(row=i, column=0, pady=2)
        tk.Label(frame, text=str(shares), font=("Arial", 11), width=10, anchor="center", bg="white").grid(row=i, column=1, pady=2)
        tk.Button(frame, text="View", font=("Arial", 10, "bold"), fg="blue", cursor="hand2",
                  command=lambda url=AUTO_COMPANIES[company]: open_link(url)).grid(row=i, column=2, pady=2)

# ----------------- Petroleum Shares ----------------- #

def show_petroleum_shares_window(user_email):
    users = load_users()
    if user_email not in users:
        messagebox.showerror("Error", "User not found.")
        return

    user_data = users[user_email]
    petroleum_data = user_data.get("petroleum_shares", {})

    petro_win = tk.Toplevel(root)
    petro_win.title(f"{user_data['name']}'s Petroleum Shares")
    petro_win.geometry("500x450")
    petro_win.configure(bg="white")

    try:
        img2 = Image.open("C:\\Users\\neham\\Downloads\\oil.png")  # Petroleum image
        img2 = img2.resize((1500, 400))
        photo2 = ImageTk.PhotoImage(img2)
        lbl_img2 = tk.Label(petro_win, image=photo2, bg="white")
        lbl_img2.image = photo2
        lbl_img2.pack(pady=10)
    except:
        tk.Label(petro_win, text="🛢 Petroleum Shares", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

    frame = tk.Frame(petro_win, bg="white")
    frame.pack(pady=10)

    tk.Label(frame, text="Company", font=("Arial", 12, "bold"), width=20, anchor="w", bg="white").grid(row=0, column=0)
    tk.Label(frame, text="Shares", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=1)
    tk.Label(frame, text="Live Price", font=("Arial", 12, "bold"), width=10, anchor="center", bg="white").grid(row=0, column=2)

    for i, (company, shares) in enumerate(petroleum_data.items(), start=1):
        tk.Label(frame, text=company, font=("Arial", 11), width=20, anchor="w", bg="white").grid(row=i, column=0, pady=2)
        tk.Label(frame, text=str(shares), font=("Arial", 11), width=10, anchor="center", bg="white").grid(row=i, column=1, pady=2)
        tk.Button(frame, text="View", font=("Arial", 10, "bold"), fg="blue", cursor="hand2",
                  command=lambda url=PETROLEUM_COMPANIES[company]: open_link(url)).grid(row=i, column=2, pady=2)
         

# ----------------- Registration ----------------- #

def register_user():
    name = entry_name.get().strip()
    email = entry_email.get().strip().lower()
    password = entry_password.get().strip()

    if not (name and email and password):
        messagebox.showerror("Error", "Please fill all fields!")
        return

    users = load_users()
    if email in users:
        messagebox.showerror("Error", "This email is already registered.")
        return

    users[email] = {
        "name": name,
        "password": password,
        "balance": 20,
        "shares": get_default_shares(AUTO_COMPANIES),
        "petroleum_shares": get_default_shares(PETROLEUM_COMPANIES)
    }

    save_users(users)
    messagebox.showinfo("Success", f"Registration successful! ₹20 bonus credited to {name}.\nAutomobile & Petroleum shares initialized.")

    entry_name.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    entry_password.delete(0, tk.END)

    # Show both categories
    show_shares_window(email)
    show_petroleum_shares_window(email)
    

# ----------------- Main GUI ----------------- #

root = tk.Tk()
root.title("Stock Market - Registration")
root.geometry("400x500")
root.configure(bg="white")

try:
    img = Image.open("C:\\Users\\neham\\Downloads\\img.png")
    img = img.resize((500, 200))
    photo = ImageTk.PhotoImage(img)
    lbl_img = tk.Label(root, image=photo, bg="white")
    lbl_img.image = photo
    lbl_img.pack(pady=10)
except:
    tk.Label(root, text="📈 Stock Market", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

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

root.mainloop()
