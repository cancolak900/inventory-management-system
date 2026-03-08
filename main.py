# main.py

# Our storage list (List of Dictionaries)
inventory = []

def add_product(name, quantity, price):
    """Adds a new product to the inventory."""
    product = {
        "name": name,
        "quantity": quantity,
        "price": price
    }
    inventory.append(product)
    print(f"✅ Success: {name} added to inventory.")

def show_inventory():
    """Prints all products in a clean format."""
    print("\n" + "="*30)
    print("CURRENT INVENTORY STATUS")
    print("="*30)
    
    for item in inventory:
        print(f"Product: {item['name']} | Stock: {item['quantity']} | Price: ${item['price']}")
    
    print("="*30 + "\n")

# Entry point of the program
if __name__ == "__main__":
    print("--- Welcome to the Inventory Management System ---")
    
    # Adding sample data
    add_product("MacBook Pro", 5, 2500)
    add_product("Wireless Mouse", 20, 45)
    
    # Show the results
    show_inventory()