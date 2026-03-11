from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import bcrypt
import jwt
import sqlite3
import datetime

# --- GÜVENLİK AYARLARI ---
SECRET_KEY = "benim_cok_gizli_anahtarim_123!" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Güvenlik Görevlisi (Header'dan Bearer token'ı okur)
security = HTTPBearer()

app = FastAPI(title="Pro Inventory Backend API")

# --- VERİTABANI KURULUMU ---
def init_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    # Kullanıcılar Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Ürünler Tablosu (Artık veritabanının tek sahibi API)
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

@app.on_event("startup")
def startup_event():
    init_db()

# --- VERİ MODELLERİ (İstemciden Gelen Veri Yapıları) ---
class UserAuth(BaseModel):
    username: str
    password: str

class ProductCreate(BaseModel):
    name: str
    quantity: int
    price: float

class ProductUpdate(BaseModel):
    quantity: int

# --- GÜVENLİK FONKSİYONLARI ---
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

# Gelen biletin (Token) sahte olup olmadığını kontrol eden fonksiyon
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Şifreyi (SECRET_KEY) kullanarak bileti çözmeye çalış
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Geçersiz bilet")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Biletin süresi dolmuş, tekrar giriş yapın")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Geçersiz bilet veya imza")

# ==========================================
# --- 1. AÇIK UÇ NOKTALAR (Herkes Girebilir) ---
# ==========================================
@app.get("/")
def root():
    return {"message": "Inventory API Calisiyor."}

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserAuth):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Kullanıcı adı zaten alınmış")
    
    hashed_password = get_password_hash(user.password)
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (user.username, hashed_password))
    conn.commit()
    conn.close()
    return {"message": "Kayıt başarılı"}

@app.post("/login")
def login(user: UserAuth):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, password_hash FROM users WHERE username = ?", (user.username,))
    db_user = cursor.fetchone()
    conn.close()
    
    if not db_user or not verify_password(user.password, db_user[1]):
        raise HTTPException(status_code=401, detail="Hatalı kullanıcı adı veya şifre")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# --- 2. KORUMALI UÇ NOKTALAR (Sadece JWT ile Girilebilir) ---
# ==========================================

# Ürünleri Listele (Sadece giriş yapmış kullanıcı görebilir)
@app.get("/products")
def get_products(current_user: str = Depends(get_current_user)):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity, price FROM products")
    # Verileri Python sözlükleri (JSON) listesine çeviriyoruz
    products = [{"name": row[0], "quantity": row[1], "price": row[2]} for row in cursor.fetchall()]
    conn.close()
    return products

# Yeni Ürün Ekle
@app.post("/products", status_code=status.HTTP_201_CREATED)
def add_product(product: ProductCreate, current_user: str = Depends(get_current_user)):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (product.name, product.quantity, product.price))
    conn.commit()
    conn.close()
    return {"message": f"{product.name} başarıyla eklendi."}

# Ürün Stoğunu Güncelle
@app.put("/products/{product_name}")
def update_product(product_name: str, product: ProductUpdate, current_user: str = Depends(get_current_user)):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET quantity = ? WHERE LOWER(name) = ?", (product.quantity, product_name.lower()))
    conn.commit()
    conn.close()
    return {"message": f"{product_name} stoğu güncellendi."}

# Ürün Sil
@app.delete("/products/{product_name}")
def delete_product(product_name: str, current_user: str = Depends(get_current_user)):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE LOWER(name) = ?", (product_name.lower(),))
    conn.commit()
    conn.close()
    return {"message": f"{product_name} sistemden silindi."}