import mysql.connector as conn
import tkinter as tk
from tkinter import ttk, messagebox

# Database Connection
db = conn.connect(host="localhost", user="root", password="asdfghjkl", database="harshap")
cur = db.cursor()

# GUI App
root = tk.Tk()
root.title("ShopSmart")
root.geometry("700x500")

# Labels & Entry for Searching
tk.Label(root, text="Enter Product Name:", font=("Arial", 12)).pack(pady=10)
search_entry = tk.Entry(root, font=("Arial", 12))
search_entry.pack()

# Table for Displaying Name, Price, and Quantity
columns = ["Product ID", "Name", "Price", "Quantity"]
tree = ttk.Treeview(root, columns=columns, show="headings")

tree.heading("Product ID", text="ID")  # Hidden column
tree.heading("Name", text="Name")
tree.heading("Price", text="Price", command=lambda: sort_by_price())  # Clickable for sorting
tree.heading("Quantity", text="Quantity")

tree.column("Product ID", width=0, stretch=False)  # Hide Product ID
tree.column("Name", width=200)
tree.column("Price", width=100)
tree.column("Quantity", width=100)

tree.pack(pady=10, fill="both", expand=True)

# Cart Data
cart = {}

# Store sorted data
product_data = []
sort_ascending = True  # Flag for sorting order


# Function to Show Product Details
def show_details(product_id):
    cur.execute(f"SELECT * FROM products WHERE product_id = {product_id}")
    result = cur.fetchone()

    if result:
        details = f"""
        ID: {result[0]}
        Name: {result[1]}
        Brand: {result[2]}
        Category: {result[3]}
        Price: {result[4]} {result[5]}
        Weight: {result[6]} {result[7]}
        Ingredients: {result[8]}
        Allergens: {result[9]}
        Calories: {result[10]}
        Protein: {result[11]}
        Carbohydrates: {result[12]}
        Fats: {result[13]}
        Sugar: {result[14]}
        Fiber: {result[15]}
        Sodium: {result[16]}
        Availability: {result[17]}
        """
        messagebox.showinfo("Product Details", details)
    else:
        messagebox.showinfo("Info", f"No product found with ID {product_id}")


# Function to Search Products by Name
def search_product():
    global product_data
    product_name = search_entry.get()

    cur.execute(f"SELECT product_id, name, price FROM products WHERE name LIKE '%{product_name}%'")
    product_data = cur.fetchall()
    
    update_table(product_data)


# Function to Update the Treeview
def update_table(data):
    tree.delete(*tree.get_children())  # Clear previous entries
    for row in data:
        tree.insert("", "end", values=(row[0], row[1], row[2], "1"))  # Default quantity 1


# Function to Sort by Price
def sort_by_price():
    global product_data, sort_ascending
    product_data.sort(key=lambda x: x[2], reverse=not sort_ascending)  # Sort by price
    sort_ascending = not sort_ascending  # Toggle order
    update_table(product_data)  # Refresh table


# Event Binding to Show Details on Double Click
def on_item_click(event):
    selected_item = tree.selection()
    if selected_item:
        product_id = tree.item(selected_item[0], "values")[0]  # Get Product ID
        show_details(product_id)

tree.bind("<Double-1>", on_item_click)  # Double-click to view details


# Function to Add to Cart
def add_to_cart():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a product!")
        return

    product_values = tree.item(selected_item[0], "values")
    product_id, name, price, quantity = product_values

    try:
        quantity = int(quantity)  # Ensure quantity is numeric
        if quantity <= 0:
            messagebox.showerror("Error", "Quantity must be at least 1!")
            return
    except ValueError:
        messagebox.showerror("Error", "Invalid quantity!")
        return

    # Add to cart dictionary
    if product_id in cart:
        cart[product_id]["quantity"] += quantity
    else:
        cart[product_id] = {"name": name, "price": float(price), "quantity": quantity}

    messagebox.showinfo("Success", f"{name} added to cart!")


# Function to View Cart
def view_cart():
    if not cart:
        messagebox.showinfo("Cart", "Your cart is empty!")
        return

    cart_window = tk.Toplevel(root)
    cart_window.title("Shopping Cart")
    cart_window.geometry("400x300")

    cart_tree = ttk.Treeview(cart_window, columns=["Name", "Price", "Quantity", "Total"], show="headings")

    cart_tree.heading("Name", text="Name")
    cart_tree.heading("Price", text="Price")
    cart_tree.heading("Quantity", text="Quantity")
    cart_tree.heading("Total", text="Total")

    cart_tree.column("Name", width=150)
    cart_tree.column("Price", width=80)
    cart_tree.column("Quantity", width=80)
    cart_tree.column("Total", width=80)

    cart_tree.pack(pady=10, fill="both", expand=True)

    total_cost = 0
    for item in cart.values():
        total_price = item["price"] * item["quantity"]
        cart_tree.insert("", "end", values=(item["name"], item["price"], item["quantity"], total_price))
        total_cost += total_price

    tk.Label(cart_window, text=f"Total Cost: {total_cost:.2f}", font=("Arial", 14, "bold")).pack(pady=10)


# Function to Open Add Product Window
def open_add_product_window():
    add_window = tk.Toplevel(root)
    add_window.title("Add New Product")
    add_window.geometry("400x500")

    tk.Label(add_window, text="Enter New Product Details", font=("Arial", 14, "bold")).pack(pady=10)

    entry_labels = [
        "ID", "Name", "Brand", "Category", "Price", "Currency", "Weight", "Unit",
        "Ingredients", "Allergens", "Calories", "Protein", "Carbohydrates", "Fats",
        "Sugar", "Fiber", "Sodium", "Availability"
    ]

    entries = []
    for label in entry_labels:
        frame = tk.Frame(add_window)
        frame.pack(fill="x", padx=20, pady=2)
        tk.Label(frame, text=label, width=15, anchor="w").pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(fill="x", expand=True)
        entries.append(entry)

    # Function to Insert Product
    def insert_product():
        values = [entry.get() for entry in entries]
        
        if not values[0].isdigit():  # Check if ID is numeric
            messagebox.showerror("Error", "Product ID must be numeric!")
            return

        try:
            cur.execute("INSERT INTO products VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
            db.commit()
            messagebox.showinfo("Success", "Product inserted successfully!")
            add_window.destroy()  # Close window after success
        except conn.errors.IntegrityError:
            messagebox.showerror("Error", "Product ID already exists!")

    tk.Button(add_window, text="Insert Product", font=("Arial", 12), command=insert_product).pack(pady=10)


tk.Button(root, text="Add to Cart", font=("Arial", 12), command=add_to_cart).pack(pady=5)
tk.Button(root, text="View Cart", font=("Arial", 12), command=view_cart).pack(pady=5)
tk.Button(root, text="Add New Product", font=("Arial", 12), command=open_add_product_window).pack(pady=5)
tk.Button(root, text="Search", font=("Arial", 12), command=search_product).pack(pady=5)

root.mainloop()