import streamlit as st
import random
from datetime import datetime, timedelta
import requests

st.set_page_config(page_title="ランダム4桁コード", layout="centered")

def send_post_request(url, code):
    if code:  # 空白でないか確認
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

# 初期化
if 'code' not in st.session_state or 'next_change' not in st.session_state:
    st.session_state.code = random.randint(1000, 9999)
    st.session_state.next_change = datetime.now() + timedelta(minutes=4)
    send_post_request("https://prod-08.japaneast.logic.azure.com:443/workflows/...", st.session_state.code)

# 残り時間の計算
now = datetime.now()
remaining = st.session_state.next_change - now

# 4分経過したら更新
if remaining.total_seconds() <= 0:
    st.session_state.code = random.randint(1000, 9999)
    st.session_state.next_change = now + timedelta(minutes=4)
    send_post_request("https://prod-08.japaneast.logic.azure.com:443/workflows/...", st.session_state.code)
    remaining = st.session_state.next_change - now

# 表示
seconds_left = int(remaining.total_seconds())
st.title("出席コード")
st.markdown(f"### 現在のコード: `{st.session_state.code}`")
st.markdown(f"次のコード更新まで: **{seconds_left} 秒**")

# 自動リフレッシュ（時間が来たら再実行）
import time
time.sleep(1)
st.rerun()
