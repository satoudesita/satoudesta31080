import streamlit as st
import requests
import sqlite3

# データベースに接続する関数
def connect_db(db_name='products.db'):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    return conn, cur

# テーブル作成の関数
def create_table():
    conn, cur = connect_db()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product TEXT NOT NULL,
            jan_code TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# JANコード列を追加する関数
def add_jan_code_column():
    conn, cur = connect_db()
    try:
        cur.execute("ALTER TABLE products ADD COLUMN jan_code TEXT NOT NULL")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # 列がすでに存在している場合はエラーを無視する
    conn.close()

# 商品を挿入する関数
def insert_product(product_name, jan_code):
    conn, cur = connect_db()
    cur.execute("INSERT INTO products (product, jan_code) VALUES (?, ?)", (product_name, jan_code))
    conn.commit()
    conn.close()

# 商品を削除する関数（商品名で）
def delete_product_by_name(product_name):
    conn, cur = connect_db()
    cur.execute("DELETE FROM products WHERE product = ?", (product_name,))
    conn.commit()
    conn.close()

# 商品を削除する関数（JANコードで）
def delete_product_by_code(jan_code):
    conn, cur = connect_db()
    cur.execute("DELETE FROM products WHERE jan_code = ?", (jan_code,))
    conn.commit()
    conn.close()

# 全ての商品を取得する関数
def fetch_all_products():
    conn, cur = connect_db()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    conn.close()
    
    if rows: 
        for row in rows:
            st.text(f"商品名: {row[0]}, JANコード: {row[1]}")
    else:
        st.text("No products found.")

# テーブルを作成し、JANコード列を追加する
create_table()
add_jan_code_column()

API_URL = "https://api.jancodelookup.com/"
API_ID = "96385e12558d53c366efb3c187ef0440" 

def search_product_by_code(jan_code):
    params = {
        'appId': API_ID,
        'query': jan_code,
        'hits': 1,
        'page': 1,
        'type': 'code',
    }
    
    response = requests.get(API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if 'product' in data and len(data['product']) > 0:
            product = data['product'][0]
            return product
        else:
            st.warning("商品が見つかりませんでした")  
            return None
    else:
        st.error(f"APIリクエストに失敗しました: {response.status_code} - {response.text}")
        return None

st.subheader("JANコードで商品検索")
with st.form(key='my2_form', clear_on_submit=True):
    jan_code = st.text_input(label="JANコードを入力してください", key="search")           
        
    submit_button = st.form_submit_button(label='送信')

if jan_code:
    product = search_product_by_code(jan_code)
    if product:
        st.text("商品情報:")
        st.text(f"商品名: {product.get('itemName', '不明')}")
        st.text(f"ブランド名: {product.get('brandName', '不明')}")
        st.text(f"メーカー名: {product.get('makerName', '不明')}")
        st.text(f"詳細ページ: [商品ページ](https://www.jancodelookup.com/code/{product['codeNumber']})")
        st.image(product.get('itemImageUrl'))

        # 商品をデータベースに挿入（商品名とJANコード）
        insert_product(product.get('itemName', '不明'), jan_code) 
        
else:
    st.text("JANコードを入力してください")

st.subheader("冷蔵庫の中身")
    # 商品を表示
fetch_all_products()

    # 商品名で削除
delete_name = st.text_input("削除する商品名を入力してください")

if st.button("商品削除（名前）"):
    delete_product_by_name(delete_name)
    # 削除後に最新の商品リストを表示
    st.text("商品を削除しました。")
    st.rerun()  # アプリケーションを再実行してリストを更新
    

