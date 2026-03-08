import tkinter as tk
from tkinter import messagebox, ttk
from main import InventoryManager, Product

class InventoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System - Pro")
        self.root.geometry("900x600")
        
        self.manager = InventoryManager()

        # --- SEARCH AREA ---
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="Search Product:").pack(side=tk.LEFT, padx=5)
        self.ent_search = tk.Entry(search_frame)
        self.ent_search.pack(side=tk.LEFT, padx=5)
        self.ent_search.bind("<KeyRelease>", lambda event: self.update_table()) # Yazdıkça ara

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
        
        # Renklendirme (Tag) ayarı
        self.tree.tag_configure('low_stock', background='#ffcccc') # Açık kırmızı
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20)

        # --- BUTTONS ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Delete Selected", command=self.delete_ui, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Refresh List", command=self.update_table).pack(side=tk.LEFT, padx=10)

        self.update_table()

    def clear_entries(self):
        """Kutuları temizler."""
        self.ent_name.delete(0, tk.END)
        self.ent_qty.delete(0, tk.END)
        self.ent_price.delete(0, tk.END)

    def update_table(self):
        """Tabloyu temizler, arama kriterine göre yeniden doldurur ve stok uyarısı yapar."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        search_query = self.ent_search.get().lower()
        
        for p in self.manager.inventory:
            # Arama filtresi
            if search_query in p.name.lower():
                # Düşük stok kontrolü
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

            self.manager.inventory.append(Product(name, qty, prc))
            self.manager.save_data()
            self.update_table()
            self.clear_entries() # EKLEDİKTEN SONRA TEMİZLE
            messagebox.showinfo("Success", f"{name} added successfully!")
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer and Price must be a number.")

    def delete_ui(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return

        item_values = self.tree.item(selected_item)['values']
        name_to_delete = item_values[0]

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {name_to_delete}?"):
            self.manager.inventory = [p for p in self.manager.inventory if p.name != name_to_delete]
            self.manager.save_data()
            self.update_table()


if __name__ == "__main__":
    print("🚀 GUI başlatılıyor...") # Test mesajı 1
    root = tk.Tk()
    app = InventoryGUI(root)
    print("✅ Pencere döngüsü (mainloop) giriliyor...") # Test mesajı 2
    root.mainloop()