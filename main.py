# main_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """ Create the items table if it doesn't exist """
    try:
        sql_create_items_table = """ CREATE TABLE IF NOT EXISTS items (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        price real NOT NULL,
                                        quantity integer NOT NULL
                                    ); """
        cursor = conn.cursor()
        cursor.execute(sql_create_items_table)
    except sqlite3.Error as e:
        print(e)

def add_item(conn, item):
    """ Add a new item into the items table """
    sql = ''' INSERT INTO items(name,price,quantity) VALUES(?,?,?) '''
    cursor = conn.cursor()
    cursor.execute(sql, item)
    conn.commit()
    return cursor.lastrowid

def view_all_items(conn):
    """ Query all rows in the items table """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    return rows

def update_item(conn, item_data):
    """ Update price and quantity of an item """
    sql = ''' UPDATE items SET price = ?, quantity = ? WHERE id = ?'''
    cursor = conn.cursor()
    cursor.execute(sql, item_data)
    conn.commit()

def remove_item(conn, item_id):
    """ Remove an item by item id """
    sql = 'DELETE FROM items WHERE id=?'
    cursor = conn.cursor()
    cursor.execute(sql, (item_id,))
    conn.commit()

# --- GUI Application Class ---

class ShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shop Management System")
        self.root.geometry("700x500")

        # Database connection
        self.db_file = "shop.db"
        self.conn = create_connection(self.db_file)
        create_table(self.conn)

        # --- Widgets ---
        self.create_widgets()
        self.populate_list()

    def create_widgets(self):
        # Frame for input fields
        input_frame = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        input_frame.pack(pady=10, padx=10, fill="x")

        # Labels and Entry fields
        tk.Label(input_frame, text="Item Name:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = tk.Entry(input_frame, font=('Arial', 10))
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Price:", font=('Arial', 10)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.price_entry = tk.Entry(input_frame, font=('Arial', 10))
        self.price_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Quantity:", font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = tk.Entry(input_frame, font=('Arial', 10))
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        # Frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        # Buttons
        tk.Button(button_frame, text="Add Item", command=self.add_item_gui, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update Item", command=self.update_item_gui, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remove Item", command=self.remove_item_gui, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Fields", command=self.clear_fields, width=12).pack(side=tk.LEFT, padx=5)

        # Treeview for displaying items
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Price", "Quantity"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Quantity", text="Quantity")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=200)
        self.tree.column("Price", width=100, anchor="center")
        self.tree.column("Quantity", width=100, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind select event
        self.tree.bind('<<TreeviewSelect>>', self.select_item)
        
        # Selected item ID
        self.selected_item_id = None

    def populate_list(self):
        # Clear existing items in the tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Fetch items from DB and insert into tree
        for row in view_all_items(self.conn):
            self.tree.insert("", "end", values=row)

    def add_item_gui(self):
        name = self.name_entry.get()
        price_str = self.price_entry.get()
        quantity_str = self.quantity_entry.get()

        if not name or not price_str or not quantity_str:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            price = float(price_str)
            quantity = int(quantity_str)
        except ValueError:
            messagebox.showerror("Error", "Price and Quantity must be numbers.")
            return

        add_item(self.conn, (name, price, quantity))
        messagebox.showinfo("Success", "Item added successfully.")
        self.clear_fields()
        self.populate_list()

    def select_item(self, event):
        try:
            selected = self.tree.selection()[0]
            item = self.tree.item(selected, 'values')
            
            self.selected_item_id = item[0]
            
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, item[1])
            
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, item[2])
            
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, item[3])
        except IndexError:
            # This can happen if the list is empty or selection is cleared
            pass

    def update_item_gui(self):
        if not self.selected_item_id:
            messagebox.showerror("Error", "Please select an item to update.")
            return

        price_str = self.price_entry.get()
        quantity_str = self.quantity_entry.get()

        if not price_str or not quantity_str:
            messagebox.showerror("Error", "Price and Quantity fields are required.")
            return

        try:
            price = float(price_str)
            quantity = int(quantity_str)
        except ValueError:
            messagebox.showerror("Error", "Price and Quantity must be numbers.")
            return

        update_item(self.conn, (price, quantity, self.selected_item_id))
        messagebox.showinfo("Success", "Item updated successfully.")
        self.clear_fields()
        self.populate_list()

    def remove_item_gui(self):
        if not self.selected_item_id:
            messagebox.showerror("Error", "Please select an item to remove.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this item?"):
            remove_item(self.conn, self.selected_item_id)
            messagebox.showinfo("Success", "Item removed successfully.")
            self.clear_fields()
            self.populate_list()

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.selected_item_id = None
        # Deselect item in treeview
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

if __name__ == '__main__': #main execution
    root = tk.Tk()
    app = ShopApp(root)
    root.mainloop()

