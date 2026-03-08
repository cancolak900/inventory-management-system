import json
import os

DATA_FILE = "inventory.json"
inventory = []

# --- 1. Yardımcı Fonksiyonlar ---
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(inventory, file, indent=4)
    print("💾 Data saved to file.")

def load_data():
    global inventory
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            inventory = json.load(file)
        print("📁 Data loaded from file.")
    else:
        inventory = []

# --- 2. İşlem Fonksiyonları ---
def add_product():
    print("\n--- Add New Product ---")
    name = input("Enter product name: ")
    try:
        quantity = int(input("Enter quantity: "))
        price = float(input("Enter price: "))
    except ValueError:
        print("❌ Error: Quantity and Price must be numbers!")
        return
    
    product = {"name": name, "quantity": quantity, "price": price}
    inventory.append(product)
    save_data()
    print(f"✅ {name} added successfully!")

def show_inventory():
    if not inventory:
        print("\n⚠️ Inventory is empty!")
        return

    print("\n" + "="*45)
    print(f"{'Product Name':<20} | {'Stock':<10} | {'Price':<10}")
    print("-" * 45)
    
    low_stock_items = [] # Düşük stoklu ürünleri burada toplayacağız

    for item in inventory:
        # Ürün bilgilerini yazdır
        status = ""
        if item['quantity'] < 5:
            status = "⚠️ LOW STOCK"
            low_stock_items.append(item['name'])
            
        print(f"{item['name']:<20} | {item['quantity']:<10} | ${item['price']:<10} {status}")
    
    print("="*45)

    # Eğer düşük stoklu ürün varsa, listenin sonunda toplu bir uyarı geçelim
    if low_stock_items:
        print(f"\n📢 ALERT: You need to restock: {', '.join(low_stock_items)}")
    print("\n")

def delete_product():
    name = input("Enter the name of the product to delete: ")
    global inventory
    original_count = len(inventory)
    inventory = [item for item in inventory if item['name'].lower() != name.lower()]
    if len(inventory) < original_count:
        save_data()
        print(f"🗑️ {name} has been removed.")
    else:
        print(f"❌ Product '{name}' not found.")

def update_stock():
    name = input("Enter product name to update stock: ")
    for item in inventory:
        if item['name'].lower() == name.lower():
            try:
                new_qty = int(input(f"Current stock is {item['quantity']}. Enter new stock: "))
                item['quantity'] = new_qty
                save_data()
                print(f"🔄 {name} stock updated to {new_qty}.")
                return
            except ValueError:
                print("❌ Invalid input!")
                return
    print(f"❌ Product '{name}' not found.")


def search_product():
    """Searches for products by name (partial matches allowed)."""
    query = input("\nEnter product name to search: ").lower()
    
    # İsmi içinde arama terimi geçenleri bulalım
    results = [item for item in inventory if query in item['name'].lower()]
    
    if not results:
        print(f"❌ No products found matching '{query}'.")
        return

    print("\n" + "-"*45)
    print(f"🔍 SEARCH RESULTS for '{query}':")
    print("-" * 45)
    print(f"{'Product Name':<20} | {'Stock':<10} | {'Price':<10}")
    print("-" * 45)
    
    for item in results:
        status = "⚠️ LOW" if item['quantity'] < 5 else ""
        print(f"{item['name']:<20} | {item['quantity']:<10} | ${item['price']:<10} {status}")
    
    print("-" * 45 + "\n")


# --- 3. Ana Döngü (EN ALTTA OLMALI) ---
if __name__ == "__main__":
    load_data()
    while True:
        print("1. Add Product")
        print("2. Show Inventory")
        print("3. Update Stock") 
        print("4. Delete Product") 
        print("5. Search Product") 
        print("6. Exit")
        
        choice = input("Select an option (1-6): ")
        
        if choice == "1":
            add_product()
        elif choice == "2":
            show_inventory()
        elif choice == "3":
            update_stock()
        elif choice == "4":
            delete_product()
        elif choice == "5": 
            search_product()
        elif choice == "6":
            print("Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice!")