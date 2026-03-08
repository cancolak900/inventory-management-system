import json
import os

class Product:
    def __init__(self, name, quantity, price):
        self.name = name
        self.quantity = quantity
        self.price = price

    def to_dict(self):
        return {"name": self.name, "quantity": self.quantity, "price": self.price}

class InventoryManager:
    def __init__(self, filename="inventory.json"):
        self.filename = filename
        self.inventory = []
        self.load_data()

    def save_data(self):
        with open(self.filename, "w") as file:
            json_data = [p.to_dict() for p in self.inventory]
            json.dump(json_data, file, indent=4)
        print("💾 Changes saved to disk.")

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                data = json.load(file)
                self.inventory = [Product(item['name'], item['quantity'], item['price']) for item in data]
            print(f"📁 Loaded {len(self.inventory)} products.")

    def add_item(self):
        print("\n--- Add New Product ---")
        name = input("Enter product name: ")
        try:
            qty = int(input("Enter quantity: "))
            prc = float(input("Enter price: "))
            self.inventory.append(Product(name, qty, prc))
            self.save_data()
            print(f"✅ {name} added.")
        except ValueError:
            print("❌ Invalid input! Numbers required.")

    def show_all(self):
        if not self.inventory:
            print("\n⚠️ Inventory is empty!")
            return
        print("\n" + "="*55)
        print(f"{'Product Name':<20} | {'Stock':<10} | {'Price':<10}")
        print("-" * 55)
        low_stock = []
        for p in self.inventory:
            status = "⚠️  LOW STOCK" if p.quantity < 5 else ""
            if p.quantity < 5: low_stock.append(p.name)
            print(f"{p.name:<20} | {p.quantity:<10} | ${p.price:<10.2f} {status}")
        print("="*55)
        if low_stock:
            print(f"📢 Restock needed: {', '.join(low_stock)}")

    # --- GERİ GELEN ÖZELLİK: ARAMA ---
    def search_item(self):
        query = input("\nEnter product name to search: ").lower()
        results = [p for p in self.inventory if query in p.name.lower()]
        
        if not results:
            print(f"❌ No products found matching '{query}'.")
            return

        print(f"\n🔍 Results for '{query}':")
        for p in results:
            print(f"- {p.name} (Stock: {p.quantity}, Price: ${p.price:.2f})")

    # --- GERİ GELEN ÖZELLİK: GÜNCELLEME ---
    def update_item(self):
        name = input("\nEnter product name to update: ").lower()
        for p in self.inventory:
            if p.name.lower() == name:
                try:
                    new_qty = int(input(f"Current stock: {p.quantity}. New stock: "))
                    p.quantity = new_qty
                    self.save_data()
                    print(f"🔄 {p.name} updated.")
                    return
                except ValueError:
                    print("❌ Invalid quantity!")
                    return
        print("❌ Product not found.")

    def delete_item(self):
        name = input("\nEnter name to delete: ").lower()
        original_len = len(self.inventory)
        self.inventory = [p for p in self.inventory if p.name.lower() != name]
        if len(self.inventory) < original_len:
            self.save_data()
            print(f"🗑️ {name} removed.")
        else:
            print("❌ Not found.")

def main():
    manager = InventoryManager()
    while True:
        print("\n--- Professional Inventory System ---")
        print("1. Add Product   2. Show List   3. Update Stock")
        print("4. Delete Prod.  5. Search      6. Exit")
        choice = input("Select (1-6): ")

        if choice == "1": manager.add_item()
        elif choice == "2": manager.show_all()
        elif choice == "3": manager.update_item()
        elif choice == "4": manager.delete_item()
        elif choice == "5": manager.search_item()
        elif choice == "6": 
            print("System shutting down...")
            break
        else: print("❌ Invalid choice.")

if __name__ == "__main__":
    main()