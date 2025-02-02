import streamlit as st
import requests
import sqlite3

# データベースに接続する関数
def connect_db(db_name='products.db'):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    return conn, cur

# 商品がすでに存在するかをチェックする関数
def check_if_product_exists(jan_code):
    conn, cur = connect_db()
    cur.execute("SELECT * FROM products WHERE jan_code = ?", (jan_code,))
    existing_product = cur.fetchone()  # JANコードで既存の商品を探す
    conn.close()
    return existing_product is not None  # 商品があればTrueを返す

# 商品を挿入する関数
def insert_product(product_name, jan_code):
    if not check_if_product_exists(jan_code):  # 商品が存在しない場合のみ追加
        conn, cur = connect_db()
        cur.execute("INSERT INTO products (product, jan_code) VALUES (?, ?)", (product_name, jan_code))
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
    return rows

# テーブルを作成し、JANコード列を追加する
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

def add_jan_code_column():
    conn, cur = connect_db()
    try:
        cur.execute("ALTER TABLE products ADD COLUMN jan_code TEXT NOT NULL")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # 列がすでに存在している場合はエラーを無視する
    conn.close()

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

if submit_button and jan_code:
    product = search_product_by_code(jan_code)
    if product:
        st.text("商品情報:")
        st.text(f"商品名: {product.get('itemName', '不明')}")
        st.text(f"ブランド名: {product.get('brandName', '不明')}")
        st.text(f"メーカー名: {product.get('makerName', '不明')}")
        st.text(f"詳細ページ: [商品ページ](https://www.jancodelookup.com/code/{product['codeNumber']})")
        st.image(product.get('itemImageUrl'))

        # 商品をデータベースに挿入（商品名とJANコード） 既存商品がない場合のみ
        if not check_if_product_exists(jan_code):
            insert_product(product.get('itemName', '不明'), jan_code)
            st.success(f"{product.get('itemName', '不明')} が冷蔵庫に追加されました。")
else:
    if submit_button:
        st.text("JANコードを入力してください")

# 「冷蔵庫の中身」のセクションだけ細くて水色の背景
st.markdown("""
    <style>
        .refrigerator-container {
            background-color: #c1e4e9;  /* 水色の背景 */
            padding: 5px;
            width: 100%;  /* 幅を60%に設定（細くする） */
            margin: 0 auto;  /* 中央に配置 */
            border-radius: 5px;  /* 角を丸くする */
        }
    </style>
""", unsafe_allow_html=True)

st.subheader("冷蔵庫の中身")
st.markdown('<div class="refrigerator-container">', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 商品を取得し、リストとして表示
if 'products' not in st.session_state:
    st.session_state.products = fetch_all_products()

# 商品名と削除ボタンを列に分ける
for product in st.session_state.products:
    product_name, jan_code = product
    cols = st.columns([3, 1])  # 商品名とボタンを3:1の比率で分ける

    with cols[0]:  # 商品名を左のカラムに表示
        st.text(f"商品名: {product_name}, JANコード: {jan_code}")

    with cols[1]:  # 削除ボタンを右のカラムに表示
        try:
            # 削除ボタンのkeyを一意に設定する
            delete_button = st.button(f"削除", key=f"delete_{jan_code}_{product_name}")
            if delete_button:
                delete_product_by_code(jan_code)
                # 削除後にリストを即座に更新する
                st.session_state.products = fetch_all_products()  # 商品リストを即座に更新
                st.success(f"{product_name} が削除されました。")
        except Exception as e:
            st.error(f"削除中にエラーが発生しました: {str(e)}")

# 更新ボタンの追加
if st.button("冷蔵庫の中身を更新"):
    # 最新の商品リストを手動で更新
    st.session_state.products = fetch_all_products()  # 商品リストを再取得

st.markdown('<div class="refrigerator-container">', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
