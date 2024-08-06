import streamlit as st
import pandas as pd
import numpy as np
import time
 
# ページタイトルの設定
st.set_page_config(page_title="歴史問題")
 
# タイトルと説明
st.title('歴史問題')
 
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
# スライダーとガチャボタンの表示
ti = st.slider('時間制限を選択してください。小さいほど得点は高いです', min_value=5, max_value=30, value=15, step=5)
if ti==0:
    st.text('0は選択できません')
# 正解数と不正解数のカウンターをセッション状態で初期化
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0
 
if 'incorrect_answers' not in st.session_state:
    st.session_state.incorrect_answers = 0
 
# 正解数に応じて選択肢の数を決定
if st.session_state.correct_answers < 5:
    m = 3
elif st.session_state.correct_answers < 10:
    m = 5
else:
    m = 7
 
# 不正解数が5回を超えた場合の表示
if st.session_state.incorrect_answers >= 5:
    final_score = st.session_state.correct_answers * int(30/ti*10)
 
    st.markdown(
        f"""
        <div style="height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <h1 style="color: red; font-size: 50px; text-align: center;">終了</h1>
            <div style="background-color: #ADD8E6; padding: 20px; border-radius: 10px; margin-top: 20px;">
                <h2 style="color: black; text-align: center;">最終結果</h2>
                <p style="color: black; font-size: 24px; text-align: center;">正解数: {st.session_state.correct_answers}</p>
                <p style="color: black; font-size: 24px; text-align: center;">不正解数: {st.session_state.incorrect_answers}</p>
                <p style="color: black; font-size: 24px; text-align: center;">計算結果: {final_score}</p>
            </div>
        """,
        unsafe_allow_html=True
    )
   
    # 「もう一度」ボタンが押された場合の処理
    if st.button('もう一度', key='reset_button'):
        st.text('もう一度押してください')
        # セッション状態をリセット
        st.session_state.correct_answers = 0
        st.session_state.incorrect_answers = 0
        # RerunException を発生させてページを再読み込み
        st.runtime.scriptrunner.RerunException(None)
 
    st.stop()  # 以降の処理を停止
 
 
# ガチャ機能
if st.button('ガチャを引く！', key='gacha_button'):
    rarity_probs = {
        'N': 1.0,
    }
    chosen_rarity = np.random.choice(list(rarity_probs.keys()), p=list(rarity_probs.values()))
    subset_df = words_df[words_df['難易度'] == chosen_rarity]
    selected_word = subset_df.sample().iloc[0]
 
    # クイズ用の選択肢を生成
    other_words = words_df[words_df['問題'] != selected_word['問題']].sample(m)
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
    if not st.session_state.quiz_answered and st.session_state.timer_active:
        st.write("この問題の年号はどれでしょう？")
 
        # 4つずつ横に並べるための列を作成
        num_choices = len(st.session_state.choices)
        num_cols = 4
        num_rows = (num_choices + num_cols - 1) // num_cols  # 必要な行数を計算
 
        for row in range(num_rows):
            cols = st.columns(num_cols)
            for col in range(num_cols):
                choice_index = row * num_cols + col
                if choice_index < num_choices:
                    choice = st.session_state.choices[choice_index]
                    # 各ボタンに一意のキーを付与
                    if cols[col].button(str(choice), key=f'choice_{row}_{col}'):
                        st.session_state.selected_choice = choice
                        st.session_state.quiz_answered = True
 
                        # タイマーを終了する
                        st.session_state.timer_active = False
 
                        # 正解不正解にかかわらず正解数または不正解数を増やす
                        if choice == st.session_state.correct_answer:
                            st.session_state.correct_answers += 1
                            st.success("正解です！")
                        else:
                            st.session_state.incorrect_answers += 1
                            st.error(f"不正解です。正解は {st.session_state.correct_answer} でした。")
 
                        # 正しい意味を表示するフラグをセット
                        st.session_state.display_meaning = True
 
    elif st.session_state.quiz_answered or not st.session_state.timer_active:
        st.write("回答済みです。次の問題に進んでください。")
 
# タイマーの表示と制御
if 'timer_active' in st.session_state and st.session_state.timer_active:
    start_time = st.session_state.start_time
    elapsed_time = time.time() - start_time
    remaining_time = max(0, (ti) - elapsed_time)  # 残り時間の計算
 
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
        remaining_time = max(0, (ti) - elapsed_time)
        timer_placeholder.markdown(
            f'<h2 style="color: #20b2aa; font-size: 36px; text-align: center;">残り時間: {remaining_time:.1f} 秒</h2>',
            unsafe_allow_html=True
        )
        time.sleep(0.1)  # タイマーの更新
 
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
if st.button('正解数と不正解数をリセット', key='reset_counts'):
    st.session_state.correct_answers = 0
    st.session_state.incorrect_answers = 0
    st.text('もう一度押してください')