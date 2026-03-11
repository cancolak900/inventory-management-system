import tkinter as tk
from tkinter import messagebox, ttk, simpledialog # simpledialog eklendi!
from main import InventoryManager, Product

class InventoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System - Pro (SQLite)")
        self.root.geometry("900x600")
        
        self.manager = InventoryManager()

        # --- SEARCH AREA ---
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="Search Product:").pack(side=tk.LEFT, padx=5)
        self.ent_search = tk.Entry(search_frame)
        self.ent_search.pack(side=tk.LEFT, padx=5)
        self.ent_search.bind("<KeyRelease>", lambda event: self.update_table())

        # --- INPUT AREA ---
        input_frame = tk.LabelFrame(self.root, text="Add New Item")
        input_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_name = tk.Entry(input_frame)
        self.ent_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Qty:").grid(row=0, column=2, padx=5, pady=5)
        self.ent_qty = tk.Entry(input_frame)
        self.ent_qty.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Price:").grid(row=0, column=4, padx=5, pady=5)
        self.ent_price = tk.Entry(input_frame)
        self.ent_price.grid(row=0, column=5, padx=5, pady=5)

        btn_add = tk.Button(input_frame, text="Add Product", command=self.add_product_ui, bg="#4CAF50", fg="white")
        btn_add.grid(row=0, column=6, padx=10, pady=5)

        # --- TABLE (Treeview) ---
        self.tree = ttk.Treeview(self.root, columns=("Name", "Stock", "Price"), show='headings')
        self.tree.heading("Name", text="Product Name")
        self.tree.heading("Stock", text="Stock Quantity")
        self.tree.heading("Price", text="Price ($)")
        
        self.tree.tag_configure('low_stock', background='#ffcccc')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20)

        # --- BUTTONS ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        # GÜNCELLEME BUTONU EKLENDİ
        tk.Button(btn_frame, text="Update Stock", command=self.update_ui, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_ui, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Refresh List", command=self.update_table).pack(side=tk.LEFT, padx=10)

        self.update_table()

    def clear_entries(self):
        self.ent_name.delete(0, tk.END)
        self.ent_qty.delete(0, tk.END)
        self.ent_price.delete(0, tk.END)

    def update_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        search_query = self.ent_search.get().lower()
        
        for p in self.manager.inventory:
            if search_query in p.name.lower():
                tag = 'low_stock' if p.quantity < 5 else ''
                self.tree.insert("", tk.END, values=(p.name, p.quantity, f"${p.price:.2f}"), tags=(tag,))

    def add_product_ui(self):
        try:
            name = self.ent_name.get()
            qty = int(self.ent_qty.get())
            prc = float(self.ent_price.get())
            
            if not name:
                messagebox.showwarning("Warning", "Product name cannot be empty!")
                return

            self.manager.add_item(name, qty, prc)
            self.update_table()
            self.clear_entries()
            messagebox.showinfo("Success", f"{name} added successfully!")
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer and Price must be a number.")

    # YENİ GÜNCELLEME FONKSİYONU
    def update_ui(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product from the list to update.")
            return

        item_values = self.tree.item(selected_item)['values']
        name_to_update = item_values[0]
        current_qty = item_values[1]

        # Kullanıcıya küçük bir pencerede yeni stoğu soruyoruz
        new_qty = simpledialog.askinteger("Update Stock", f"Enter new stock for {name_to_update}:", initialvalue=current_qty)

        # Eğer iptale basmazsa (None dönmezse) güncelle
        if new_qty is not None:
            self.manager.update_item(name_to_update, new_qty)
            self.update_table()
            messagebox.showinfo("Success", f"{name_to_update} stock updated to {new_qty}.")

    def delete_ui(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return

        item_values = self.tree.item(selected_item)['values']
        name_to_delete = item_values[0]

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {name_to_delete}?"):
            self.manager.delete_item(name_to_delete)
            self.update_table()
            messagebox.showinfo("Deleted", f"{name_to_delete} removed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryGUI(root)
    root.mainloop()