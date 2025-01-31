import streamlit as st
import requests

API_URL = "https://api.jancodelookup.com/"
API_ID = "96385e12558d53c366efb3c187ef0440" 

def search_product_by_code(jan_code):
    params = {
        'appId': API_ID,     # アプリID（
        'query': jan_code,    # JANコード
        'hits': 1,            # 取得件数（1件だけ取得）
        'page': 1,            # 1ページ目を指定
        'type': 'code',       # コード番号検索
    }
    
    # APIにリクエストを送信
    response = requests.get(API_URL, params=params)
    
    # レスポンスのステータスコードを確認
    if response.status_code == 200:
        data = response.json()  # JSONレスポンスをパース
        
       
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
        jan_code = st.text_input(label="JANコードを入力してください",key="search")           
        
        submit_button = st.form_submit_button(label='送信')

if jan_code:
    # 商品を検索
    product = search_product_by_code(jan_code)
    if product:
        st.text("商品情報:")
        st.text(f"商品名: {product.get('itemName', '不明')}")
        st.text(f"品番: {product.get('itemModel', '不明')}")
        st.text(f"ブランド名: {product.get('brandName', '不明')}")
        st.text(f"メーカー名: {product.get('makerName', '不明')}")
        st.text(f"詳細ページ: [商品ページ](https://www.jancodelookup.com/code/{product['codeNumber']})")
        st.image(product.get('itemImageUrl')) 
else:
    st.text("JANコードを入力してください")
