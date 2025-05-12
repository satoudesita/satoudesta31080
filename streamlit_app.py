import streamlit as st
import random
from datetime import datetime, timedelta
import requests
import time

st.set_page_config(page_title="ランダム4桁コード", layout="centered")

# POST送信関数
def send_post_request(url, code):
    if code:  
        try:
            request_data = {"code": str(code)}
            response = requests.post(url, json=request_data)
            if response.status_code == 200:
                st.write("成功: ", response.json())
            else:
                st.write("エラー: ", response.status_code)
                st.write("エラーメッセージ: ", response.text)
        except Exception as e:
            st.write(f"リクエストエラー: {e}")
    else:
        st.write("コードが空のため、送信をスキップしました。")

# セッションステート初期化
if 'code' not in st.session_state or 'next_change' not in st.session_state:
    st.session_state.code = random.randint(1000, 9999)
    st.session_state.next_change = datetime.now() + timedelta(minutes=10)
    send_post_request(
        "https://prod-01.japaneast.logic.azure.com:443/workflows/38f7b8c8d476411d8d4351e0638c6750/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=DQl_g5amg0IRCFIs1lRiIBvicQ1Z9JI9i7uNgWKKu2g",
        st.session_state.code
    )

# 残り時間
now = datetime.now()
remaining = st.session_state.next_change - now

if remaining.total_seconds() <= 0:
    st.session_state.code = random.randint(1000, 9999)
    st.session_state.next_change = now + timedelta(minutes=10)
    send_post_request(
        "https://prod-01.japaneast.logic.azure.com:443/workflows/38f7b8c8d476411d8d4351e0638c6750/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=DQl_g5amg0IRCFIs1lRiIBvicQ1Z9JI9i7uNgWKKu2g",
        st.session_state.code
    )
    remaining = st.session_state.next_change - now

seconds_left = int(remaining.total_seconds())


st.markdown(
    f"""
    <div style="text-align: center; padding-top: 120px;">
        <h2 style="font-size: 96px; color: #333;">出席コード</h2>
        <h1 style="font-size: 200px; color: #004080;">{st.session_state.code}</h1>
        <p style="font-size: 72px; color: #666;">次の更新まで: {seconds_left} 秒</p>
    </div>
    """,
    unsafe_allow_html=True
)


time.sleep(1)
st.rerun()
