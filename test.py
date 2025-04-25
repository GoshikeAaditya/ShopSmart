# Enhanced ShopSmart with Login, Recommendations, Payment, Subscription, Rewards, and Filters
import mysql.connector as conn
import tkinter as tk
from tkinter import ttk, messagebox

# Connect to database
db = conn.connect(host="localhost", user="root", password="asdfghjkl", database="harshap")
cur = db.cursor()

# Ensure users and subscriptions tables exist
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(100) PRIMARY KEY,
    password VARCHAR(100) NOT NULL,
    points INT DEFAULT 0,
    subscription VARCHAR(20) DEFAULT 'none'
);
""")
db.commit()

# ------------------------- LOGIN WINDOW -----------------------------
def open_login():
    login_win = tk.Tk()
    login_win.title("Login - ShopSmart")
    login_win.geometry("300x200")

    tk.Label(login_win, text="Username").pack(pady=5)
    user_entry = tk.Entry(login_win)
    user_entry.pack()

    tk.Label(login_win, text="Password").pack(pady=5)
    pass_entry = tk.Entry(login_win, show="*")
    pass_entry.pack()

    def login():
        username = user_entry.get()
        password = pass_entry.get()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cur.fetchone()
        if result:
            login_win.destroy()
            open_main_app(username)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials!")

    tk.Button(login_win, text="Login", command=login).pack(pady=10)
    tk.Button(login_win, text="Register", command=lambda: register(user_entry.get(), pass_entry.get())).pack()
    login_win.mainloop()

def register(username, password):
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        messagebox.showinfo("Success", "Registered successfully!")
    except:
        messagebox.showerror("Error", "User already exists")

# ------------------------- MAIN APP -----------------------------
def open_main_app(username):
    root = tk.Tk()
    root.title(f"ShopSmart - Welcome {username}")
    root.geometry("900x600")

    tk.Label(root, text="Search Product:").pack()
    search_entry = tk.Entry(root)
    search_entry.pack()

    filter_frame = tk.Frame(root)
    filter_frame.pack(pady=5)
    tk.Label(filter_frame, text="Category").pack(side="left")
    category_cb = ttk.Combobox(filter_frame)
    category_cb.pack(side="left")

    tk.Label(filter_frame, text="Brand").pack(side="left")
    brand_cb = ttk.Combobox(filter_frame)
    brand_cb.pack(side="left")

    tk.Label(filter_frame, text="Max Price").pack(side="left")
    max_price = tk.Entry(filter_frame, width=10)
    max_price.pack(side="left")

    columns = ["Product ID", "Name", "Price", "Quantity"]
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    cart = {}
    product_data = []
    sort_ascending = True

    def search():
        query = search_entry.get()
        cat = category_cb.get()
        brand = brand_cb.get()
        price = max_price.get()

        sql = "SELECT product_id, name, price FROM products WHERE name LIKE %s"
        vals = [f"%{query}%"]

        if cat:
            sql += " AND category=%s"
            vals.append(cat)
        if brand:
            sql += " AND brand=%s"
            vals.append(brand)
        if price:
            sql += " AND price<=%s"
            vals.append(price)

        cur.execute(sql, vals)
        nonlocal product_data
        product_data = cur.fetchall()
        update_table(product_data)

    def update_table(data):
        tree.delete(*tree.get_children())
        for row in data:
            tree.insert("", "end", values=(row[0], row[1], row[2], 1))

    def sort_by_price():
        nonlocal sort_ascending, product_data
        product_data.sort(key=lambda x: x[2], reverse=not sort_ascending)
        sort_ascending = not sort_ascending
        update_table(product_data)

    def show_details(product_id):
        cur.execute("SELECT * FROM products WHERE product_id=%s", (product_id,))
        result = cur.fetchone()
        if result:
            messagebox.showinfo("Details", f"Name: {result[1]}\nCategory: {result[3]}\nPrice: {result[4]}\nCalories: {result[10]}")

    def add_to_cart():
        selected = tree.selection()
        if not selected: return
        item = tree.item(selected[0])['values']
        pid, name, price, qty = item
        qty = int(qty)
        if pid in cart:
            cart[pid]['quantity'] += qty
        else:
            cart[pid] = {'name': name, 'price': float(price), 'quantity': qty}
        messagebox.showinfo("Cart", f"Added {name} to cart")

    def view_cart():
        if not cart:
            messagebox.showinfo("Cart", "Your cart is empty")
            return

        top = tk.Toplevel(root)
        top.title("Cart")

        tree_cart = ttk.Treeview(top, columns=["Name", "Price", "Qty", "Total"], show="headings")
        for c in ["Name", "Price", "Qty", "Total"]:
            tree_cart.heading(c, text=c)
        tree_cart.pack()

        total_cost = 0
        for item in cart.values():
            total = item['price'] * item['quantity']
            tree_cart.insert("", "end", values=(item['name'], item['price'], item['quantity'], total))
            total_cost += total

        tk.Label(top, text=f"Total: {total_cost:.2f}", font=("Arial", 12)).pack()
        tk.Button(top, text="Proceed to Pay", command=lambda: open_payment_window(username, total_cost)).pack(pady=5)

    def open_payment_window(user, amount):
        pay_win = tk.Toplevel(root)
        pay_win.title("Payment Gateway")
        tk.Label(pay_win, text=f"Amount to Pay: ₹{amount:.2f}").pack(pady=5)
        for field in ["Card Number", "Expiry Date", "CVV"]:
            tk.Label(pay_win, text=field).pack()
            tk.Entry(pay_win).pack()

        def confirm():
            points_earned = int(amount // 100)
            cur.execute("UPDATE users SET points = points + %s WHERE username=%s", (points_earned, user))
            db.commit()
            cart.clear()
            messagebox.showinfo("Success", f"Payment Successful! Earned {points_earned} points")
            pay_win.destroy()

        tk.Button(pay_win, text="Confirm Payment", command=confirm).pack(pady=10)

    def show_recommendations():
        print(list(map(str, cart.keys())))
        cur.execute("SELECT DISTINCT category FROM products WHERE product_id IN (""%s)" % ",".join(map(str, cart.keys())))
        cats = [row[0] for row in cur.fetchall()]
        if not cats:
            messagebox.showinfo("Rec", "Add items to cart to get recommendations")
            return
        cur.execute("SELECT name FROM products WHERE category IN (%s) LIMIT 5" % ",".join(["%s"]*len(cats)), cats)
        recs = [r[0] for r in cur.fetchall()]
        messagebox.showinfo("Recommended", "\n".join(recs))

    def manage_subscription():
        cur.execute("SELECT subscription, points FROM users WHERE username=%s", (username,))
        sub, pts = cur.fetchone()
        top = tk.Toplevel(root)
        top.title("Subscription")
        tk.Label(top, text=f"Current: {sub}\nPoints: {pts}").pack(pady=10)

        def subscribe(plan):
            def confirm_sub():
                cur.execute("UPDATE users SET subscription=%s WHERE username=%s", (plan, username))
                db.commit()
                messagebox.showinfo("Subscribed", f"Subscribed to {plan}!")
                pay_sub_win.destroy()

            pay_sub_win = tk.Toplevel(top)
            pay_sub_win.title("Payment - Subscription")
            tk.Label(pay_sub_win, text=f"Pay for {plan.title()} Subscription").pack()
            for field in ["Card Number", "Expiry Date", "CVV"]:
                tk.Label(pay_sub_win, text=field).pack()
                tk.Entry(pay_sub_win).pack()
            tk.Button(pay_sub_win, text="Confirm Payment", command=confirm_sub).pack(pady=10)

        tk.Button(top, text="Monthly", command=lambda: subscribe("monthly")).pack()
        tk.Button(top, text="Yearly", command=lambda: subscribe("yearly")).pack()

    # Load filter options
    cur.execute("SELECT DISTINCT category FROM products")
    category_cb['values'] = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT brand FROM products")
    brand_cb['values'] = [r[0] for r in cur.fetchall()]

    # Bindings & Buttons
    tree.bind("<Double-1>", lambda e: show_details(tree.item(tree.selection()[0])['values'][0]))
    tk.Button(root, text="Search", command=search).pack()
    tk.Button(root, text="Sort by Price", command=sort_by_price).pack()
    tk.Button(root, text="Add to Cart", command=add_to_cart).pack()
    tk.Button(root, text="View Cart", command=view_cart).pack()
    tk.Button(root, text="Recommendations", command=show_recommendations).pack()
    tk.Button(root, text="Subscription", command=manage_subscription).pack()

    root.mainloop()

open_login()
