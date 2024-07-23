import streamlit as st
import pandas as pd
import numpy as np
import time

# ページタイトルの設定
st.set_page_config(page_title="歴史問題")

# タイトルと説明
st.title('歴史問題')
st.write('歴史をランダムに表示して、勉強をサポートします！')
st.write('がんばってください')

# CSSを適用して背景色と選択肢ボタンの色を設定
st.write(
    f"""
    <style>
        .stApp {{
            background-color: #f8f8ff;
        }}
        .stButton button {{
            background-color: #f0ffff;  /* ボタンの背景色 */
            color: black;  /* ボタンの文字色 */
            border-radius: 30px;  /* ボタンの角を丸くする */
            padding: 10px 20px;  /* ボタンの内側の余白 */
            font-size: 18px;  /* ボタンの文字のサイズ */
            font-weight: bold;  /* ボタンの文字を太字にする */
        }}
        .stButton button:hover {{
            background-color: #a4b0c6;  /* ボタンのホバー時の背景色 */
        }}
        .stButton button:active {{
            background-color: #5f9ea0;  /* ボタンのアクティブ時の背景色 */
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

if 'num_choices' not in st.session_state:
    st.session_state.num_choices = 3  # 初期は選択肢3つ

ti = st.slider('制限時間を入力してください', 0, 30, 15)

# 正解数が2を超えた場合に選択肢の数を増やす
if 5 <= st.session_state.correct_answers <= 10:
    st.session_state.num_choices = 5
elif st.session_state.correct_answers >= 11:
    st.session_state.num_choices = 7
else:
    st.session_state.num_choices = 3  # 正解数が2以下の場合は選択肢を3つに設定

# ガチャ機能
if st.button('ガチャを引く！'):
    rarity_probs = {
        'N': 1.0,
    }
    chosen_rarity = np.random.choice(list(rarity_probs.keys()), p=list(rarity_probs.values()))
    subset_df = words_df[words_df['難易度'] == chosen_rarity]
    selected_word = subset_df.sample().iloc[0]
    
    # クイズ用の選択肢を生成
    other_words = words_df[words_df['問題'] != selected_word['問題']].sample(st.session_state.num_choices - 1)
    choices = other_words['回答'].tolist() + [selected_word['回答']]
    np.random.shuffle(choices)
    
    # 選択された単語とクイズ選択肢をセッション状態に保存
    st.session_state.selected_word = selected_word
    st.session_state.choices = choices
    st.session_state.correct_answer = str(selected_word['回答'])  # 正しい答えを文字列として保存
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

        # 4列に並べるための列の設定
        num_cols = 4  # 一行に表示する選択肢の数
        cols = st.columns(num_cols)
        
        # 各選択肢をボタンとして表示
        for i, choice in enumerate(st.session_state.choices):
            # choiceがint型の場合、文字列に変換する
            if isinstance(choice, (int, np.int64)):
                choice = str(choice)
            
            with cols[i % num_cols]:
                if st.button(choice, key=f'choice_{i}'):
                    st.session_state.quiz_answered = True
                    st.session_state.selected_choice = choice

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

        # 不正解時の正しい答えを表示
        if st.session_state.correct_answer:
            st.write("正しい答えは次の通りです:")
            # 正しい答えも含めて選択肢を4列に並べる
            num_cols = 4
            cols = st.columns(num_cols)
            correct_choices = [st.session_state.correct_answer]  # 正しい答えのリスト
            
            for i in range(num_cols):
                with cols[i]:
                    if i < len(correct_choices):
                        st.write(f"- {correct_choices[i]}")
                    else:
                        st.write("")

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
if st.button('正解数と不正解数をリセット'):
    st.session_state.correct_answers = 0
    st.session_state.incorrect_answers = 0
    st.session_state.num_choices = 3  # リセット時に選択肢の数を3つに戻す
    st.text('もう一度押して下さい')
