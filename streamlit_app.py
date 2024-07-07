import streamlit as st
import pandas as pd
import numpy as np
import time
# ページタイトルの設定
st.set_page_config(page_title="歴史問題")

# 画像のURL
image_url = "https://th.bing.com/th/id/OIP.j1smnJA5KPDPCuPmZ6hAigHaHu?w=158&h=180&c=7&r=0&o=5&pid=1.7"

# 画像を表示
st.image(image_url, caption='', width=50)  # 幅を調整してタイトルの近くに表示する

# タイトルと説明
st.title('歴史問題')
st.write('歴史をランダムに表示して、勉強をサポートします！')
st.write('がんばってください')

# CSSを適用して背景色を設定
st.write(
    f"""
    <style>
        .stApp {{
            background-color: #f8f8ff;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# データの読み込み
@st.cache_data
def load_data():
    return pd.read_excel("rekisi.xlsx")

words_df = load_data()

# 正解数と不正解数のカウンターをセッション状態で初期化
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0

if 'incorrect_answers' not in st.session_state:
    st.session_state.incorrect_answers = 0

# ガチャ機能
if st.button('ガチャを引く！'):
    rarity_probs = {
        'N': 1.0,
    }
    chosen_rarity = np.random.choice(list(rarity_probs.keys()), p=list(rarity_probs.values()))
    subset_df = words_df[words_df['難易度'] == chosen_rarity]
    selected_word = subset_df.sample().iloc[0]
    
    # クイズ用の選択肢を生成
    other_words = words_df[words_df['問題'] != selected_word['問題']].sample(2)
    choices = other_words['回答'].tolist() + [selected_word['回答']]
    np.random.shuffle(choices)
    
    # 選択された単語とクイズ選択肢をセッション状態に保存
    st.session_state.selected_word = selected_word
    st.session_state.choices = choices
    st.session_state.correct_answer = selected_word['回答']
    st.session_state.display_meaning = False  # 初期化
    st.session_state.quiz_answered = False
    st.session_state.start_time = time.time()  # タイマーの開始時刻

    # タイマーをリセットして再開
    st.session_state.timer_active = True

# 選択された単語とクイズを表示
if 'selected_word' in st.session_state:
    st.header(f"問題: {st.session_state.selected_word['問題']}")
    st.subheader(f"難易度: {st.session_state.selected_word['難易度']}")

    # クイズ選択肢を表示
    st.write("この問題の年号はどれでしょう？")
    quiz_answer = st.radio("選択肢", st.session_state.choices)
    
    if not st.session_state.quiz_answered:
        if st.button('回答する'):
            st.session_state.quiz_answered = True
            st.session_state.selected_choice = quiz_answer
            
            # タイマーを終了する
            st.session_state.timer_active = False
            
            # 正解不正解にかかわらず正解数または不正解数を増やす
            if quiz_answer == st.session_state.correct_answer:
                st.session_state.correct_answers += 1
                st.success("正解です！")
            else:
                st.session_state.incorrect_answers += 1
                st.error(f"不正解です。正解は {st.session_state.correct_answer} でした。")
            
            # 正しい意味を表示するフラグをセット
            st.session_state.display_meaning = True
    else:
        st.write("回答済みです。次の問題に進んでください。")

# タイマーの表示と制御
if 'timer_active' in st.session_state and st.session_state.timer_active:
    start_time = st.session_state.start_time
    elapsed_time = time.time() - start_time
    remaining_time = max(0, 10 - elapsed_time)  # 10秒タイマーの残り時間
    timer_style = (
        
        f'<div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px;'
        f' box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);">'
        f'<h2 style="color: #333; font-size: 36px; text-align: center;">残り時間: {remaining_time:.1f} 秒</h2>'
        f'</div>'
    )
    
    timer_placeholder = st.empty()
    timer_placeholder.markdown(timer_style, unsafe_allow_html=True)
    while remaining_time > 0:
        elapsed_time = time.time() - start_time
        remaining_time = max(0, 10 - elapsed_time)
        timer_placeholder.markdown(
            f'<h2 style="color: #20b2aa; font-size: 36px; text-align: center;">残り時間: {remaining_time:.1f} 秒</h2>',
            unsafe_allow_html=True
        )
        time.sleep(1)  # 1秒ごとに更新



    # 時間切れ時も不正解としてカウント
    if not st.session_state.quiz_answered:
        st.session_state.incorrect_answers += 1
        st.error(f"時間切れです。正解は {st.session_state.correct_answer} でした。")

# 正解数と不正解数を四角で囲んで色を淡い水色にして表示
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        f'<div style="background-color: #ADD8E6; padding: 5px; border-radius: 3px;">'
        f'<h3 style="color: black;">正解した数</h3>'
        f'<p style="color: black; font-size: 24px; text-align: center;">{st.session_state.correct_answers}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
with col2:
    st.markdown(
        f'<div style="background-color: #ADD8E6; padding: 5px; border-radius: 3px;">'
        f'<h3 style="color: black;">不正解した数</h3>'
        f'<p style="color: black; font-size: 24px; text-align: center;">{st.session_state.incorrect_answers}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

# 正解数と不正解数をリセットするボタン
if st.button('正解数と不正解数をリセット'):
    st.session_state.correct_answers = 0
    st.session_state.incorrect_answers = 0
    st.text('もう一度押して下さい')
