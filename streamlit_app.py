import streamlit as st
import random
import time
from datetime import datetime, timedelta


st.set_page_config(page_title="ランダム4桁コード", layout="centered")


if 'next_change' not in st.session_state:
    st.session_state.next_change = datetime.now() + timedelta(minutes=4)
    st.session_state.code = random.randint(1000, 9999)

now = datetime.now()


remaining = st.session_state.next_change - now

if remaining.total_seconds() <= 0:
    st.session_state.code = random.randint(1000, 9999)
    st.session_state.next_change = now + timedelta(minutes=4)
    remaining = st.session_state.next_change - now


seconds_left = int(remaining.total_seconds())


st.title("出席コード")
st.markdown(f"### 現在のコード: `{st.session_state.code}`")
st.markdown(f"次のコード更新まで: **{seconds_left} 秒**")


time.sleep(1)
st.rerun()
