import json
import os # Dosya var mı yok mu kontrol etmek için

# Dosya adını sabit olarak tanımlıyoruz
DATA_FILE = "inventory.json"
inventory = []

def save_data():
    """Saves the current inventory to a JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(inventory, file, indent=4)
    print("💾 Data saved to file.")

def load_data():
    """Loads inventory from a JSON file if it exists."""
    global inventory
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            inventory = json.load(file)
        print("📁 Data loaded from file.")
    else:
        inventory = []

def add_product():
    print("\n--- Add New Product ---")
    name = input("Enter product name: ")
    quantity = int(input("Enter quantity: "))
    price = float(input("Enter price: "))
    
    product = {
        "name": name,
        "quantity": quantity,
        "price": price
    }
    inventory.append(product)
    save_data() # Her eklemede kaydet!
    print(f"✅ {name} added successfully!")

def show_inventory():
    if not inventory:
        print("\n⚠️ Inventory is empty!")
        return

    print("\n" + "="*40)
    print(f"{'Product Name':<20} | {'Stock':<10} | {'Price':<10}")
    print("-" * 40)
    for item in inventory:
        print(f"{item['name']:<20} | {item['quantity']:<10} | ${item['price']:<10}")
    print("="*40 + "\n")

if __name__ == "__main__":
    load_data() # Program başlarken eski verileri çek
    while True:
        print("\n--- Inventory Management System ---")
        print("1. Add Product")
        print("2. Show Inventory")
        print("3. Exit")
        
        choice = input("Select an option (1-3): ")
        
        if choice == "1":
            add_product()
        elif choice == "2":
            show_inventory()
        elif choice == "3":
            print("Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice!")