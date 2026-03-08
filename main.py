# main.py

inventory = []

def add_product():
    """Gets product details from user and adds to inventory."""
    print("\n--- Add New Product ---")
    name = input("Enter product name: ")
    # int() ve float() kullanarak metni sayıya çeviriyoruz
    quantity = int(input("Enter quantity: "))
    price = float(input("Enter price: "))
    
    product = {
        "name": name,
        "quantity": quantity,
        "price": price
    }
    inventory.append(product)
    print(f"✅ {name} added successfully!")

def show_inventory():
    """Lists all products in the inventory."""
    if not inventory:
        print("\n⚠️ Inventory is empty!")
        return

    print("\n" + "="*40)
    print(f"{'Product Name':<20} | {'Stock':<10} | {'Price':<10}")
    print("-" * 40)
    for item in inventory:
        print(f"{item['name']:<20} | {item['quantity']:<10} | ${item['price']:<10}")
    print("="*40 + "\n")

# --- MAIN PROGRAM LOOP ---
if __name__ == "__main__":
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
            break # Döngüyü kırar ve programı bitirir
        else:
            print("❌ Invalid choice! Please try again.")