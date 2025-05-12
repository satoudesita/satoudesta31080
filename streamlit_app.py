import streamlit as st
import random
import time
from datetime import datetime, timedelta
import requests

st.set_page_config(page_title="ランダム4桁コード", layout="centered")

def send_post_request(url, data):
        try:

            request_data = {
                "code": str(data)  # データを文字列として 'body' フィールドに格納
            }
           
            response = requests.post(url, json=request_data)  # json形式でPOSTリクエストを送信
            if response.status_code == 200:
                st.write("成功: ", response.json())
            else:
                st.write("エラー: ", response.status_code)
                st.write("エラーメッセージ: ", response.text)  # エラーメッセージを表示
        except Exception as e:
            st.write(f"リクエストエラー: {e}")


if 'next_change' not in st.session_state:
    st.session_state.next_change = datetime.now() + timedelta(minutes=4)
    st.session_state.code = random.randint(1000, 9999)
    send_post_request('https://prod-08.japaneast.logic.azure.com:443/workflows/2dad7268f2844042bae005c2ec7916f6/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=V-60f4bGMzshRcghrvSV7qt-WEgKqbgQGfGk2F8BQPk', st.session_state.code)

now = datetime.now()


remaining = st.session_state.next_change - now

if remaining.total_seconds() <= 0:
    st.session_state.code = random.randint(1000, 9999)
    st.session_state.next_change = now + timedelta(minutes=4)
    remaining = st.session_state.next_change - now
    send_post_request('https://prod-08.japaneast.logic.azure.com:443/workflows/2dad7268f2844042bae005c2ec7916f6/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=V-60f4bGMzshRcghrvSV7qt-WEgKqbgQGfGk2F8BQPk', st.session_state.code)


seconds_left = int(remaining.total_seconds())


st.title("出席コード")
st.markdown(f"### 現在のコード: `{st.session_state.code}`")
st.markdown(f"次のコード更新まで: **{seconds_left} 秒**")


time.sleep(1)
st.rerun()
