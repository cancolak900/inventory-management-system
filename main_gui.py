import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import requests

API_URL = "http://127.0.0.1:8000"

# ==========================================
# --- 1. GİRİŞ EKRANI (ENTER DESTEKLİ) ---
# ==========================================
class LoginWindow:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success = on_success_callback
        self.root.title("Sisteme Giriş - Pro Inventory")
        self.root.geometry("300x200")
        
        tk.Label(root, text="Kullanıcı Adı:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        self.ent_user = tk.Entry(root, font=("Arial", 12))
        self.ent_user.pack(pady=5)
        
        tk.Label(root, text="Şifre:", font=("Arial", 10, "bold")).pack(pady=5)
        self.ent_pass = tk.Entry(root, show="*", font=("Arial", 12))
        self.ent_pass.pack(pady=5)
        
        tk.Button(root, text="Giriş Yap", command=self.login, bg="#2196F3", fg="white", width=15).pack(pady=15)

        # 🚀 ENTER TUŞU ENTEGRASYONU 🚀
        # Pencerenin neresinde olursa olsun Enter'a basılınca login fonksiyonunu tetikle
        self.root.bind("<Return>", self.login)

    # event=None ekledik çünkü Enter tuşu buraya bir event parametresi gönderir
    def login(self, event=None):
        username = self.ent_user.get()
        password = self.ent_pass.get()
        if not username or not password:
            return messagebox.showwarning("Uyarı", "Boş alan bırakmayın!")
        
        try:
            response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                role = data.get("role")
                
                # Giriş başarılıysa Enter tuşu bağını koparıyoruz ki ana ekrana karışmasın
                self.root.unbind("<Return>") 
                self.on_success(token, role)
            else:
                messagebox.showerror("Hata", "Hatalı kullanıcı adı veya şifre!")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Bağlantı Hatası", "Sunucuya ulaşılamıyor.")


# ==========================================
# --- 2. ANA ENVANTER EKRANI ---
# ==========================================
class InventoryGUI:
    def __init__(self, root, token, role, on_logout_callback):
        self.root = root
        self.token = token
        self.role = role
        self.on_logout = on_logout_callback 
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        self.inventory_data = []
        self.root.title(f"Inventory System - Yetki: {self.role.upper()}")
        self.root.geometry("900x600")

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

        # 🚀 ÜRÜN EKLERKEN ENTER TUŞU ENTEGRASYONU 🚀
        # Bu 3 kutudan herhangi birindeyken Enter'a basılırsa ürünü ekler
        self.ent_name.bind("<Return>", self.add_product_api)
        self.ent_qty.bind("<Return>", self.add_product_api)
        self.ent_price.bind("<Return>", self.add_product_api)

        self.tree = ttk.Treeview(self.root, columns=("Name", "Stock", "Price"), show='headings')
        self.tree.heading("Name", text="Product Name")
        self.tree.heading("Stock", text="Stock Quantity")
        self.tree.heading("Price", text="Price ($)")
        self.tree.tag_configure('low_stock', background='#ffcccc')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20, fill="x", padx=20)
        
        tk.Button(btn_frame, text="Update Stock", command=self.update_api, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_api, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh List", command=self.fetch_products).pack(side=tk.LEFT, padx=5)
        
        if self.role == "admin":
            tk.Button(btn_frame, text="Sistem Logları", command=self.show_logs_window, bg="#9C27B0", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=15)
            tk.Button(btn_frame, text="➕ Personel Ekle", command=self.show_add_user_window, bg="#009688", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="🚪 Çıkış Yap", command=self.logout_ui, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=5)

        self.fetch_products()

    def fetch_products(self):
        try:
            response = requests.get(f"{API_URL}/products", headers=self.headers)
            if response.status_code == 200:
                self.inventory_data = response.json()
                self.filter_table()
            elif response.status_code == 401:
                messagebox.showerror("Hata", "Oturum süreniz dolmuş.")
                self.on_logout() 
        except requests.exceptions.RequestException:
            pass

    def filter_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        search_query = self.ent_search.get().lower()
        for p in self.inventory_data:
            if search_query in p["name"].lower():
                tag = 'low_stock' if p["quantity"] < 5 else ''
                self.tree.insert("", tk.END, values=(p["name"], p["quantity"], f"${p['price']:.2f}"), tags=(tag,))

    # event=None ekledik
    def add_product_api(self, event=None):
        name = self.ent_name.get()
        try:
            qty = int(self.ent_qty.get())
            prc = float(self.ent_price.get())
            if not name: return
            response = requests.post(f"{API_URL}/products", json={"name": name, "quantity": qty, "price": prc}, headers=self.headers)
            if response.status_code == 201:
                self.ent_name.delete(0, tk.END); self.ent_qty.delete(0, tk.END); self.ent_price.delete(0, tk.END)
                self.ent_name.focus() # İşlem bitince imleci tekrar 'Name' kutusuna al
                self.fetch_products()
        except ValueError:
            pass

    def update_api(self):
        selected_item = self.tree.selection()
        if not selected_item: return
        name_to_update = self.tree.item(selected_item)['values'][0]
        current_qty = self.tree.item(selected_item)['values'][1]
        new_qty = simpledialog.askinteger("Update", f"Yeni stok ({name_to_update}):", initialvalue=current_qty)
        if new_qty is not None:
            requests.put(f"{API_URL}/products/{name_to_update}", json={"quantity": new_qty}, headers=self.headers)
            self.fetch_products()

    def delete_api(self):
        selected_item = self.tree.selection()
        if not selected_item: return
        name_to_delete = self.tree.item(selected_item)['values'][0]
        if messagebox.askyesno("Onay", f"{name_to_delete} silinsin mi?"):
            requests.delete(f"{API_URL}/products/{name_to_delete}", headers=self.headers)
            self.fetch_products()

    def logout_ui(self):
        if messagebox.askyesno("Çıkış", "Çıkış yapmak istediğinize emin misiniz?"):
            self.on_logout()

    def show_logs_window(self):
        log_win = tk.Toplevel(self.root)
        log_win.title("Sistem Denetim Kayıtları")
        log_win.geometry("600x400")
        log_tree = ttk.Treeview(log_win, columns=("User", "Action", "Time"), show='headings')
        log_tree.heading("User", text="Kullanıcı")
        log_tree.heading("Action", text="Yapılan İşlem")
        log_tree.heading("Time", text="Tarih / Saat")
        log_tree.column("User", width=100); log_tree.column("Action", width=300); log_tree.column("Time", width=150)
        log_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        try:
            response = requests.get(f"{API_URL}/logs", headers=self.headers)
            if response.status_code == 200:
                for log in response.json():
                    log_tree.insert("", tk.END, values=(log["username"], log["action"], log["time"]))
        except requests.exceptions.RequestException:
            pass

    def show_add_user_window(self):
        user_win = tk.Toplevel(self.root)
        user_win.title("Yeni Personel Ekle")
        user_win.geometry("300x300")
        
        tk.Label(user_win, text="Kullanıcı Adı:", font=("Arial", 10, "bold")).pack(pady=(20,5))
        ent_u = tk.Entry(user_win, font=("Arial", 11))
        ent_u.pack(pady=5)
        
        tk.Label(user_win, text="Şifre:", font=("Arial", 10, "bold")).pack(pady=5)
        ent_p = tk.Entry(user_win, show="*", font=("Arial", 11))
        ent_p.pack(pady=5)
        
        tk.Label(user_win, text="Yetki:", font=("Arial", 10, "bold")).pack(pady=5)
        role_var = tk.StringVar(value="user")
        ttk.Combobox(user_win, textvariable=role_var, values=["user", "admin"], state="readonly", width=10).pack(pady=5)
        
        # event=None ekledik
        def save_new_user(event=None):
            u, p, r = ent_u.get(), ent_p.get(), role_var.get()
            if not u or not p:
                return messagebox.showwarning("Uyarı", "Boş alan bırakmayın!", parent=user_win)
            
            response = requests.post(f"{API_URL}/register", json={"username": u, "password": p, "role": r}, headers=self.headers)
            
            if response.status_code == 201:
                messagebox.showinfo("Başarılı", f"{u} kullanıcısı eklendi!", parent=user_win)
                user_win.destroy()
            else:
                messagebox.showerror("Hata", "Kullanıcı adı zaten var veya yetkiniz yok!", parent=user_win)

        tk.Button(user_win, text="Kaydet", command=save_new_user, bg="#4CAF50", fg="white", width=15).pack(pady=20)
        
        # 🚀 PERSONEL EKLERKEN ENTER TUŞU ENTEGRASYONU 🚀
        user_win.bind("<Return>", save_new_user)


def start_app():
    root = tk.Tk()
    root.withdraw() 
    
    def show_login():
        login_window = tk.Toplevel(root)
        login_window.protocol("WM_DELETE_WINDOW", root.destroy) 
        
        def on_login_success(token, role):
            login_window.destroy() 
            root.deiconify() 
            for widget in root.winfo_children(): widget.destroy()
            InventoryGUI(root, token, role, on_logout)

        LoginWindow(login_window, on_login_success)

    def on_logout():
        root.withdraw() 
        show_login()    

    show_login()
    root.mainloop()

if __name__ == "__main__":
    start_app()