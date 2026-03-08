import tkinter as tk
from tkinter import messagebox, ttk
from main import InventoryManager, Product # Mevcut mantığımızı içe aktarıyoruz

class InventoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("800x500")
        
        self.manager = InventoryManager() # Arka plandaki beyin

        # --- GİRİŞ ALANLARI (Input Fields) ---
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5)
        self.ent_name = tk.Entry(input_frame)
        self.ent_name.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Qty:").grid(row=0, column=2, padx=5)
        self.ent_qty = tk.Entry(input_frame)
        self.ent_qty.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Price:").grid(row=0, column=4, padx=5)
        self.ent_price = tk.Entry(input_frame)
        self.ent_price.grid(row=0, column=5, padx=5)

        btn_add = tk.Button(input_frame, text="Add Product", command=self.add_product_ui)
        btn_add.grid(row=0, column=6, padx=10)

        # --- TABLO (Treeview) ---
        self.tree = ttk.Treeview(self.root, columns=("Name", "Stock", "Price"), show='headings')
        self.tree.heading("Name", text="Product Name")
        self.tree.heading("Stock", text="Stock Quantity")
        self.tree.heading("Price", text="Price ($)")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20)

        # --- BUTONLAR ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Delete Selected", command=self.delete_ui, bg="red", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Refresh List", command=self.update_table).pack(side=tk.LEFT, padx=10)

        self.update_table()

    def update_table(self):
        # Tabloyu temizle ve yeniden doldur
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for p in self.manager.inventory:
            self.tree.insert("", tk.END, values=(p.name, p.quantity, f"${p.price:.2f}"))

    def add_product_ui(self):
        try:
            name = self.ent_name.get()
            qty = int(self.ent_qty.get())
            prc = float(self.ent_price.get())
            
            # Arka plandaki manager'a ekletiyoruz
            self.manager.inventory.append(Product(name, qty, prc))
            self.manager.save_data()
            self.update_table()
            messagebox.showinfo("Success", f"{name} added successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for Quantity and Price.")

    def delete_ui(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return

        item_values = self.tree.item(selected_item)['values']
        name_to_delete = item_values[0]

        # Manager üzerinden silme
        self.manager.inventory = [p for p in self.manager.inventory if p.name != name_to_delete]
        self.manager.save_data()
        self.update_table()
        messagebox.showinfo("Deleted", f"{name_to_delete} removed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryGUI(root)
    root.mainloop()