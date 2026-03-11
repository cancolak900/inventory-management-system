import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import requests

# API Sunucumuzun adresi
API_URL = "http://127.0.0.1:8000"

# ==========================================
# --- 1. GİRİŞ EKRANI (DEĞİŞMEDİ) ---
# ==========================================
class LoginWindow:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success = on_success_callback
        self.root.title("Sisteme Giriş - Pro Inventory")
        self.root.geometry("350x250")
        
        tk.Label(root, text="Kullanıcı Adı:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        self.ent_user = tk.Entry(root, font=("Arial", 12))
        self.ent_user.pack(pady=5)
        
        tk.Label(root, text="Şifre:", font=("Arial", 10, "bold")).pack(pady=5)
        self.ent_pass = tk.Entry(root, show="*", font=("Arial", 12))
        self.ent_pass.pack(pady=5)
        
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Giriş Yap", command=self.login, bg="#2196F3", fg="white", width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Kayıt Ol", command=self.register, bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT, padx=10)

    def login(self):
        username = self.ent_user.get()
        password = self.ent_pass.get()
        if not username or not password:
            messagebox.showwarning("Uyarı", "Kullanıcı adı ve şifre boş olamaz!")
            return
        try:
            response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            if response.status_code == 200:
                token = response.json().get("access_token")
                messagebox.showinfo("Başarılı", f"Hoş geldin, {username}!")
                self.on_success(token)
            else:
                messagebox.showerror("Hata", "Kullanıcı adı veya şifre hatalı!")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Bağlantı Hatası", "Sunucuya ulaşılamıyor. Backend açık mı?")

    def register(self):
        username = self.ent_user.get()
        password = self.ent_pass.get()
        if not username or not password:
            messagebox.showwarning("Uyarı", "Kullanıcı adı ve şifre boş olamaz!")
            return
        try:
            response = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
            if response.status_code == 201:
                messagebox.showinfo("Başarılı", "Kayıt işlemi başarılı! Şimdi giriş yapabilirsiniz.")
            elif response.status_code == 400:
                messagebox.showerror("Hata", "Bu kullanıcı adı zaten alınmış.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Bağlantı Hatası", "Sunucuya ulaşılamıyor.")


# ==========================================
# --- 2. ANA ENVANTER EKRANI (TAMAMEN API'YE BAĞLANDI) ---
# ==========================================
class InventoryGUI:
    def __init__(self, root, token):
        self.root = root
        self.token = token
        # API'ye yapacağımız tüm isteklerde bu "Bilet" başlığını kullanacağız
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        self.inventory_data = [] # Verileri RAM'de tutmak için
        
        self.root.title("Inventory Management System - Pro (API Connected)")
        self.root.geometry("900x600")

        # --- ARAYÜZ TASARIMI ---
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Search Product:").pack(side=tk.LEFT, padx=5)
        self.ent_search = tk.Entry(search_frame)
        self.ent_search.pack(side=tk.LEFT, padx=5)
        self.ent_search.bind("<KeyRelease>", lambda event: self.filter_table())

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
        tk.Button(input_frame, text="Add Product", command=self.add_product_api, bg="#4CAF50", fg="white").grid(row=0, column=6, padx=10, pady=5)

        self.tree = ttk.Treeview(self.root, columns=("Name", "Stock", "Price"), show='headings')
        self.tree.heading("Name", text="Product Name")
        self.tree.heading("Stock", text="Stock Quantity")
        self.tree.heading("Price", text="Price ($)")
        self.tree.tag_configure('low_stock', background='#ffcccc')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Update Stock", command=self.update_api, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_api, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Refresh List", command=self.fetch_products).pack(side=tk.LEFT, padx=10)

        # Program açılır açılmaz API'den verileri çek!
        self.fetch_products()

    # --- API İLE HABERLEŞEN METODLAR ---

    def fetch_products(self):
        """API'den ürünleri çeker ve tabloyu günceller."""
        try:
            response = requests.get(f"{API_URL}/products", headers=self.headers)
            if response.status_code == 200:
                self.inventory_data = response.json()
                self.filter_table() # Verileri tabloya bas
            elif response.status_code == 401:
                messagebox.showerror("Hata", "Oturum süreniz dolmuş, lütfen tekrar giriş yapın.")
                self.root.destroy()
        except requests.exceptions.RequestException:
            messagebox.showerror("Bağlantı Hatası", "Sunucudan veriler alınamadı.")

    def filter_table(self):
        """Arama kutusuna göre RAM'deki verileri filtreler ve tabloya yazar."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        search_query = self.ent_search.get().lower()
        for p in self.inventory_data:
            if search_query in p["name"].lower():
                tag = 'low_stock' if p["quantity"] < 5 else ''
                self.tree.insert("", tk.END, values=(p["name"], p["quantity"], f"${p['price']:.2f}"), tags=(tag,))

    def add_product_api(self):
        name = self.ent_name.get()
        try:
            qty = int(self.ent_qty.get())
            prc = float(self.ent_price.get())
            
            if not name:
                return messagebox.showwarning("Uyarı", "Ürün adı boş olamaz!")

            payload = {"name": name, "quantity": qty, "price": prc}
            # POST isteği atıyoruz ve bilet (header) gönderiyoruz
            response = requests.post(f"{API_URL}/products", json=payload, headers=self.headers)
            
            if response.status_code == 201:
                self.ent_name.delete(0, tk.END)
                self.ent_qty.delete(0, tk.END)
                self.ent_price.delete(0, tk.END)
                self.fetch_products() # Listeyi yenile
                messagebox.showinfo("Başarılı", f"{name} başarıyla eklendi!")
            else:
                messagebox.showerror("Hata", "Ürün eklenirken API hatası oluştu.")
        except ValueError:
            messagebox.showerror("Hata", "Sayısal değerleri doğru giriniz.")

    def update_api(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return messagebox.showwarning("Uyarı", "Güncellenecek ürünü seçin.")
        
        item_values = self.tree.item(selected_item)['values']
        name_to_update = item_values[0]
        current_qty = item_values[1]
        
        new_qty = simpledialog.askinteger("Update Stock", f"Yeni stok miktarını girin ({name_to_update}):", initialvalue=current_qty)
        if new_qty is not None:
            # PUT isteği atıyoruz
            response = requests.put(f"{API_URL}/products/{name_to_update}", json={"quantity": new_qty}, headers=self.headers)
            if response.status_code == 200:
                self.fetch_products()
                messagebox.showinfo("Başarılı", "Stok güncellendi.")

    def delete_api(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return messagebox.showwarning("Uyarı", "Silinecek ürünü seçin.")
            
        name_to_delete = self.tree.item(selected_item)['values'][0]
        
        if messagebox.askyesno("Onay", f"{name_to_delete} ürününü silmek istediğinize emin misiniz?"):
            # DELETE isteği atıyoruz
            response = requests.delete(f"{API_URL}/products/{name_to_delete}", headers=self.headers)
            if response.status_code == 200:
                self.fetch_products()
                messagebox.showinfo("Başarılı", "Ürün silindi.")

# ==========================================
# --- BAŞLATMA ---
# ==========================================
def start_app():
    root = tk.Tk()
    root.withdraw() 
    
    def on_login_success(token):
        login_window.destroy() 
        root.deiconify() 
        app = InventoryGUI(root, token)

    login_window = tk.Toplevel(root)
    login_window.protocol("WM_DELETE_WINDOW", root.destroy) 
    LoginWindow(login_window, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    start_app()