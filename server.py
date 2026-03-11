from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import bcrypt
import jwt
import sqlite3
import datetime

SECRET_KEY = "benim_cok_gizli_anahtarim_123!" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()
app = FastAPI(title="Pro Inventory - RBAC & Logging API")

# ==========================================
# --- VERİTABANI VE LOG SİSTEMİ ---
# ==========================================
def init_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    # 1. Kullanıcılar (Artık 'role' sütunu var)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')
    # 2. Ürünler
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')
    # 3. YENİ: Sistem Kayıtları (Audit Logs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

# Her hareketi veritabanına yazan casus fonksiyonumuz
def log_action(username: str, action: str):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (username, action) VALUES (?, ?)", (username, action))
    conn.commit()
    conn.close()

# --- VERİ MODELLERİ ---
class UserAuth(BaseModel):
    username: str
    password: str
    role: str = "user" # Kayıt olurken role belirtilmezse otomatik 'user' (çalışan) olur

class ProductCreate(BaseModel):
    name: str
    quantity: int
    price: float

class ProductUpdate(BaseModel):
    quantity: int

# --- GÜVENLİK ---
def get_password_hash(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Artık sadece username değil, dictionary olarak {"username": "Ali", "role": "admin"} dönüyor
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401, detail="Geçersiz bilet")
        return {"username": username, "role": role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Biletin süresi dolmuş")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Geçersiz bilet")

# ==========================================
# --- UÇ NOKTALAR ---
# ==========================================
# YENİ KORUMALI KAYIT UÇ NOKTASI (Sadece Admin Girebilir)
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserAuth, current_user: dict = Depends(get_current_user)):
    # GÜVENLİK DUVARI: Biletinde "admin" yazmıyorsa reddet!
    if current_user["role"] != "admin":
        log_action(current_user["username"], "YETKİSİZ ERİŞİM: Yeni kullanıcı açmaya çalıştı!")
        raise HTTPException(status_code=403, detail="Sadece adminler yeni kullanıcı açabilir!")
        
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Kullanıcı zaten var")
    
    hashed_password = get_password_hash(user.password)
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                   (user.username, hashed_password, user.role))
    conn.commit()
    conn.close()
    
    # Kimin kimi eklediğini logluyoruz
    log_action(current_user["username"], f"Yeni personel ekledi: {user.username} (Rol: {user.role})")
    return {"message": "Kayıt başarılı"}

@app.post("/login")
def login(user: UserAuth):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    # Şifreyle beraber rolü de (db_user[2]) çekiyoruz
    cursor.execute("SELECT username, password_hash, role FROM users WHERE username = ?", (user.username,))
    db_user = cursor.fetchone()
    conn.close()
    
    if not db_user or not verify_password(user.password, db_user[1]):
        raise HTTPException(status_code=401, detail="Hatalı giriş")
    
    # Bilete artık kişinin ROLÜNÜ de mühürlüyoruz
    access_token = create_access_token(data={"sub": user.username, "role": db_user[2]})
    
    log_action(user.username, "Sisteme giriş yaptı")
    return {"access_token": access_token, "token_type": "bearer", "role": db_user[2]}

# --- ENVANTER (LOGLU İŞLEMLER) ---
@app.get("/products")
def get_products(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity, price FROM products")
    products = [{"name": row[0], "quantity": row[1], "price": row[2]} for row in cursor.fetchall()]
    conn.close()
    return products

@app.post("/products", status_code=status.HTTP_201_CREATED)
def add_product(product: ProductCreate, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (product.name, product.quantity, product.price))
    conn.commit()
    conn.close()
    
    # KİMİN EKLEDİĞİNİ LOGLA
    log_action(current_user["username"], f"Yeni ürün ekledi: {product.name} ({product.quantity} adet)")
    return {"message": "Ürün eklendi"}

@app.put("/products/{product_name}")
def update_product(product_name: str, product: ProductUpdate, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET quantity = ? WHERE LOWER(name) = ?", (product.quantity, product_name.lower()))
    conn.commit()
    conn.close()
    
    # KİMİN GÜNCELLEDİĞİNİ LOGLA
    log_action(current_user["username"], f"Stok güncelledi: {product_name} -> Yeni Stok: {product.quantity}")
    return {"message": "Stok güncellendi"}

@app.delete("/products/{product_name}")
def delete_product(product_name: str, current_user: dict = Depends(get_current_user)):
    # İstersen silme işlemini SADECE ADMIN yapabilir diyebilirsin:
    # if current_user["role"] != "admin":
    #     raise HTTPException(status_code=403, detail="Sadece adminler ürün silebilir!")

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE LOWER(name) = ?", (product_name.lower(),))
    conn.commit()
    conn.close()
    
    # KİMİN SİLDİĞİNİ LOGLA
    log_action(current_user["username"], f"Ürün SİLDİ: {product_name}")
    return {"message": "Ürün silindi"}

# ==========================================
# --- YENİ: SADECE PATRONUN (ADMIN) GÖREBİLECEĞİ LOG EKRANI ---
# ==========================================
@app.get("/logs")
def get_logs(current_user: dict = Depends(get_current_user)):
    # GÜVENLİK DUVARI: Biletinde "admin" yazmıyorsa 403 (Yasak) hatası fırlat
    if current_user["role"] != "admin":
        # Dikkat çeksin diye bunu loglayalım :)
        log_action(current_user["username"], "YETKİSİZ ERİŞİM DENEMESİ: Logları görmeye çalıştı!")
        raise HTTPException(status_code=403, detail="Bu sayfayı sadece Patron (Admin) görebilir!")
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, action, timestamp FROM logs ORDER BY id DESC")
    logs = [{"username": row[0], "action": row[1], "time": row[2]} for row in cursor.fetchall()]
    conn.close()
    return logs