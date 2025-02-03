import streamlit as st
import requests
import sqlite3
import hashlib

# データベースに接続する関数
def connect_db(db_name='products.db'):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    return conn, cur

# ユーザー情報管理のための関数
def create_users_table():
    conn, cur = connect_db()
    cur.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ユーザー名が既に存在するかを確認
def check_if_user_exists(username):
    conn, cur = connect_db()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    existing_user = cur.fetchone()
    conn.close()
    return existing_user is not None

# パスワードをハッシュ化して保存
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ユーザーをデータベースに追加
def insert_user(username, password):
    if not check_if_user_exists(username):  # ユーザーが存在しない場合に追加
        conn, cur = connect_db()
        hashed_password = hash_password(password)
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return True
    else:
        return False

# ユーザーを認証
def authenticate_user(username, password):
    conn, cur = connect_db()
    hashed_password = hash_password(password)
    cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cur.fetchone()
    conn.close()
    return user is not None

# 商品がすでに存在するかをチェックする関数（ユーザーごと）
def check_if_product_exists(jan_code, username):
    conn, cur = connect_db()
    cur.execute("SELECT * FROM products WHERE jan_code = ? AND username = ?", (jan_code, username))
    existing_product = cur.fetchone()  # JANコードで既存の商品を探す
    conn.close()
    return existing_product is not None  # 商品があればTrueを返す

# 商品を挿入する関数（ユーザーごと）
def insert_product(product_name, jan_code, username):
    if not check_if_product_exists(jan_code, username):  # 商品が存在しない場合のみ追加
        conn, cur = connect_db()
        cur.execute("INSERT INTO products (product, jan_code, username) VALUES (?, ?, ?)", (product_name, jan_code, username))
        conn.commit()
        conn.close()

# 商品を削除する関数（JANコードで、ユーザーごと）
def delete_product_by_code(jan_code, username):
    conn, cur = connect_db()
    cur.execute("DELETE FROM products WHERE jan_code = ? AND username = ?", (jan_code, username))
    conn.commit()
    conn.close()

# 全ての商品を取得する関数（ユーザーごと）
def fetch_all_products(username):
    conn, cur = connect_db()
    cur.execute("SELECT * FROM products WHERE username = ?", (username,))
    rows = cur.fetchall()
    conn.close()
    return rows

# 商品情報を取得するAPI
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

# 買い物リスト関連

# 買い物リストのテーブルを作成
def create_shopping_list_table():
    conn, cur = connect_db()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS shopping_list (
            item_name TEXT NOT NULL,
            username TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 買い物リストに商品を追加
def insert_shopping_item(item_name, username):
    conn, cur = connect_db()
    cur.execute("INSERT INTO shopping_list (item_name, username) VALUES (?, ?)", (item_name, username))
    conn.commit()
    conn.close()

# 買い物リストを削除
def delete_shopping_item(item_name, username):
    conn, cur = connect_db()
    cur.execute("DELETE FROM shopping_list WHERE item_name = ? AND username = ?", (item_name, username))
    conn.commit()
    conn.close()

# 買い物リストを取得
def fetch_shopping_list(username):
    conn, cur = connect_db()
    cur.execute("SELECT * FROM shopping_list WHERE username = ?", (username,))
    rows = cur.fetchall()
    conn.close()
    return rows

# サイドバーにログイン・サインアップを表示する
def show_sidebar():
    if 'username' not in st.session_state:
        login_signup_tab = st.sidebar.selectbox("ログイン / サインアップ", ["ログイン", "サインアップ"])

        if login_signup_tab == "ログイン":
            show_login()
        elif login_signup_tab == "サインアップ":
            show_signup()
    else:
        # ユーザーがログインしている場合
        st.sidebar.write(f"ログイン中: {st.session_state.username}")
        if st.sidebar.button("ログアウト"):
            del st.session_state.username
            st.sidebar.success("ログアウトしました。")
            st.rerun()  # ログアウト後、ページをリロードして再表示

# ログイン画面
def show_login():
    st.sidebar.subheader("ログイン")
    username = st.sidebar.text_input("ユーザー名")
    password = st.sidebar.text_input("パスワード", type="password")

    if st.sidebar.button("ログイン"):
        if authenticate_user(username, password):
            st.session_state.username = username
            st.sidebar.success("ログイン成功！")
            st.rerun()  # ログイン後、ページをリロードして再表示
        else:
            st.sidebar.error("ユーザー名かパスワードが間違っています。")

# サインアップ画面
def show_signup():
    st.sidebar.subheader("サインアップ")
    new_username = st.sidebar.text_input("新しいユーザー名")
    new_password = st.sidebar.text_input("新しいパスワード", type="password")

    if st.sidebar.button("アカウント作成"):
        if insert_user(new_username, new_password):
            st.sidebar.success("アカウント作成が成功しました！ログインしてください。")
            st.rerun()  # サインアップ後、ページをリロードして再表示
        else:
            st.sidebar.error("そのユーザー名はすでに使用されています。")

# 商品管理画面
def show_product_management():
    st.title("冷蔵庫管理")

    # JANコードを入力するフォーム
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

            # 商品をデータベースに挿入（ユーザー名も一緒に保存）
            if not check_if_product_exists(jan_code, st.session_state.username):
                insert_product(product.get('itemName', '不明'), jan_code, st.session_state.username)
                st.success(f"{product.get('itemName', '不明')} が冷蔵庫に追加されました。")

    # 冷蔵庫の中身
    st.subheader("冷蔵庫の中身")
    
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

    st.markdown('<div class="refrigerator-container">', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if 'username' in st.session_state:
        username = st.session_state.username
        products = fetch_all_products(username)

        if not products:
            st.write("冷蔵庫の中身は空です。商品を追加してください。")

        for product in products:
            product_name, jan_code, _ = product
            col1, col2 = st.columns([4, 1])

            with col1:
                st.text(product_name)
            with col2:
                delete_button = st.button(f"削除", key=f"delete_{jan_code}")
                if delete_button:
                    delete_product_by_code(jan_code, username)
                    st.success(f"{product_name} が冷蔵庫から削除されました。")
                    st.rerun()  # ページをリロードして再表示
    
    st.markdown('<div class="refrigerator-container">', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 買い物リスト管理画面
def show_shopping_list():

    if 'username' in st.session_state:
        username = st.session_state.username
        shopping_list = fetch_shopping_list(username)

        st.subheader("買い物リスト")

        if shopping_list:
            for item in shopping_list:
                item_name, username = item
                st.text(item_name)
                delete_button = st.button(f"削除", key=f"delete_shopping_{item_name}")
                if delete_button:
                    delete_shopping_item(item_name, username)
                    shopping_list = fetch_shopping_list(username)
                    st.success(f"{item_name} が買い物リストから削除されました。")
                    st.rerun()

        new_item = st.text_input("買い物リストに追加する商品名")
        if st.button("商品を追加"):
            if new_item:
                insert_shopping_item(new_item, username)
                shopping_list = fetch_shopping_list(username)
                st.success(f"{new_item} が買い物リストに追加されました。")
                st.rerun()

# メイン
def main():
    create_users_table()
    create_shopping_list_table()
    show_sidebar()

    if 'username' in st.session_state:
        tabs = st.tabs(["商品管理", "買い物リスト"])

        with tabs[0]:
            show_product_management()
        
        with tabs[1]:
            show_shopping_list()

if __name__ == "__main__":
    main()
