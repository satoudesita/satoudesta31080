import streamlit as st
import pandas as pd
import numpy as np

# ページタイトルの設定
st.set_page_config(page_title="歴史ガチャ")

# タイトルと説明
st.title('歴史ガチャ')
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
    st.session_state.display_meaning = False
    st.session_state.quiz_answered = False

# 選択された単語とクイズを表示
if 'selected_word' in st.session_state:
    st.header(f"問題: {st.session_state.selected_word['問題']}")
    st.subheader(f"難易度: {st.session_state.selected_word['難易度']}")

    # クイズ選択肢を表示
    st.write("この問題の年号はどれでしょう？")
    quiz_answer = st.radio("選択肢", st.session_state.choices)
    
    if st.button('回答する'):
        st.session_state.quiz_answered = True
        st.session_state.selected_choice = quiz_answer
        
        # 正解不正解にかかわらず正解数または不正解数を増やす
        if quiz_answer == st.session_state.correct_answer:
            st.session_state.correct_answers += 1
        else:
            st.session_state.incorrect_answers += 1

    # 正誤フィードバックを表示
    if st.session_state.quiz_answered:
        if st.session_state.selected_choice == st.session_state.correct_answer:
            st.success("正解です！")
        else:
            st.error("不正解です。")
        st.write(f"正しい意味: {st.session_state.correct_answer}")

    # 正解を表示するボタン
    if st.button('年号を確認する'):
        st.session_state.display_meaning = True

    # 表示する場合は正解を表示
    if st.session_state.display_meaning:
        st.write(f"回答: {st.session_state.selected_word['回答']}")

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
