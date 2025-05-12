import streamlit as st
import random
from datetime import datetime, timedelta
import requests

st.set_page_config(page_title="ランダム4コード", layout="centered")

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


if 'code' not in st.session_state or 'next_change' not in st.session_state:
    st.session_state.code = random.randint(1000, 9999)
    st.session_state.next_change = datetime.now() + timedelta(minutes=10)
    send_post_request("https://prod-01.japaneast.logic.azure.com:443/workflows/38f7b8c8d476411d8d4351e0638c6750/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=DQl_g5amg0IRCFIs1lRiIBvicQ1Z9JI9i7uNgWKKu2g", st.session_state.code)

now = datetime.now()
remaining = st.session_state.next_change - now

if remaining.total_seconds() <= 0:
    st.session_state.code = random.randint(1000, 9999)
    st.session_state.next_change = now + timedelta(minutes=10)
    send_post_request("https://prod-01.japaneast.logic.azure.com:443/workflows/38f7b8c8d476411d8d4351e0638c6750/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=DQl_g5amg0IRCFIs1lRiIBvicQ1Z9JI9i7uNgWKKu2g", st.session_state.code)
    remaining = st.session_state.next_change - now


seconds_left = int(remaining.total_seconds())
st.subheader("出席コード")
st.title(f" `{st.session_state.code}`")
st.text(f"コード更新: {seconds_left} 秒")


import time
time.sleep(1)
st.rerun()
