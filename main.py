import sqlite3

class Product:
    def __init__(self, name, quantity, price):
        self.name = name
        self.quantity = quantity
        self.price = price

class InventoryManager:
    def __init__(self, db_name="inventory.db"):
        self.db_name = db_name
        self.setup_database()
        self.load_data()

    def setup_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def load_data(self):
        self.inventory = []
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT name, quantity, price FROM products")
        rows = cursor.fetchall()
        for row in rows:
            self.inventory.append(Product(row[0], row[1], row[2]))
        conn.close()

    # ARTIK SADECE PARAMETRE ALIYOR (INPUT YOK)
    def add_item(self, name, qty, prc):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, qty, prc))
        conn.commit()
        conn.close()
        self.load_data()

    def update_item(self, name, new_qty):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET quantity = ? WHERE LOWER(name) = ?", (new_qty, name.lower()))
        conn.commit()
        conn.close()
        self.load_data()

    def delete_item(self, name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE LOWER(name) = ?", (name.lower(),))
        conn.commit()
        conn.close()
        self.load_data()

# ==========================================
# --- CLI KISMI (TERMINAL ARAYÜZÜ) ---
# ==========================================

def show_all_cli(manager):
    if not manager.inventory:
        print("\n⚠️ Inventory is empty!")
        return
    print("\n" + "="*50)
    print(f"{'Product Name':<20} | {'Stock':<10} | {'Price':<10}")
    print("-" * 50)
    low_stock = []
    for p in manager.inventory:
        status = "⚠️ LOW" if p.quantity < 5 else ""
        if p.quantity < 5: low_stock.append(p.name)
        print(f"{p.name:<20} | {p.quantity:<10} | ${p.price:<10.2f} {status}")
    print("="*50)
    if low_stock:
        print(f"📢 Restock needed: {', '.join(low_stock)}")

def main():
    manager = InventoryManager()
    while True:
        print("\n--- Professional Inventory System ---")
        print("1. Add Product   2. Show List   3. Update Stock")
        print("4. Delete Prod.  5. Search      6. Exit")
        choice = input("Select (1-6): ")

        if choice == "1":
            # GİRDİYİ BURADA ALIP MANAGER'A GÖNDERİYORUZ
            print("\n--- Add New Product ---")
            name = input("Enter product name: ")
            try:
                qty = int(input("Enter quantity: "))
                prc = float(input("Enter price: "))
                manager.add_item(name, qty, prc)
                print(f"✅ {name} added.")
            except ValueError:
                print("❌ Invalid input!")

        elif choice == "2":
            show_all_cli(manager)

        elif choice == "3":
            name = input("\nEnter product name to update: ")
            exists = any(p.name.lower() == name.lower() for p in manager.inventory)
            if not exists:
                print("❌ Product not found.")
                continue
            try:
                new_qty = int(input("Enter new stock: "))
                manager.update_item(name, new_qty)
                print(f"🔄 Stock updated.")
            except ValueError:
                print("❌ Invalid quantity!")

        elif choice == "4":
            name = input("\nEnter name to delete: ")
            exists = any(p.name.lower() == name.lower() for p in manager.inventory)
            if not exists:
                print("❌ Not found.")
                continue
            manager.delete_item(name)
            print(f"🗑️ {name} removed.")

        elif choice == "5":
            query = input("\nEnter product name to search: ").lower()
            results = [p for p in manager.inventory if query in p.name.lower()]
            if not results:
                print(f"❌ No products found matching '{query}'.")
            else:
                print(f"\n🔍 Results for '{query}':")
                for p in results:
                    print(f"- {p.name} (Stock: {p.quantity}, Price: ${p.price:.2f})")

        elif choice == "6": 
            print("System shutting down...")
            break
        else: 
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()