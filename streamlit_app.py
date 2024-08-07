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
    """
    <style>
        .stApp {
            background-color: #f8f8ff;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# データの読み込み
@st.cache_data
def load_data():
    return pd.read_excel("rekisi.xlsx")

words_df = load_data()

# タブの選択（サイドバーに配置）
tabs = st.sidebar.radio("選択してください", ['使い方','難易度１', '難易度２', '難易度３'])

# 正解数と不正解数のカウンターをセッション状態で初期化
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0

if 'incorrect_answers' not in st.session_state:
    st.session_state.incorrect_answers = 0

# タイマーの設定
def start_timer(ti):
    st.session_state.start_time = time.time()
    st.session_state.timer_active = True

def update_timer(ti):
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, ti - elapsed_time)
    return remaining_time

# 不正解数が制限に達したときの処理
def end_game():
    # 難易度によってスコアの倍率を変更
    multiplier = 1
    if tabs == '難易度２':
        multiplier = 1.5
    elif tabs == '難易度３':
        multiplier = 2

    final_score = st.session_state.correct_answers * int(30 / ti * 10) * multiplier

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
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button('もう一度', key='reset_button'):
        st.session_state.correct_answers = 0
        st.session_state.incorrect_answers = 0
        st.experimental_rerun()  # ページのリロード
    st.stop()

def display_timer(ti):
    remaining_time = update_timer(ti)
    timer_placeholder = st.empty()
    while remaining_time > 0:
        remaining_time = update_timer(ti)
        timer_placeholder.markdown(
            f'<h2 style="color: #20b2aa; font-size: 36px; text-align: center;">残り時間: {remaining_time:.1f} 秒</h2>',
            unsafe_allow_html=True
        )
        time.sleep(0.1)
    if not st.session_state.quiz_answered:
        st.session_state.incorrect_answers += 1
        st.error(f"時間切れです。正解は {st.session_state.correct_answer} でした。")

if tabs in ['使い方']:
    st.text("ガチャについて")
    st.text("1. 問題を解く制限時間を設定する（短いほど得点の倍率が高い）")
    st.text("2. ガチャを引くボタンを押す")
    st.text("3. 出てきた問題に対応する年号を4つの年号が書かれている選択肢ボタンから選ぶ")
    st.text("注意（時間制限を過ぎると不正解扱いになります）")
    st.text("4. もう一度ガチャを引くボタンを押し、再度問題を解く")
    st.text("5. 不正解数が5(難易度1の時)を超えると終了となり、それまでの正解数、得点が出ます。")

if tabs in ['難易度１', '難易度２', '難易度３']:
    # スライダーとガチャボタンの表示
    ti = st.slider('時間制限を選択してください。小さいほど得点は高いです', min_value=5, max_value=30, value=15, step=5)
    if ti == 0:
        st.text('0は選択できません')
        st.stop()

    if st.session_state.correct_answers < 5:
        m = 3
    elif st.session_state.correct_answers < 10:
        m = 5
    else:
        m = 7

    # 不正解数が制限に達した場合のゲーム終了
    incorrect_limit = 5 if tabs == '難易度１' else (3 if tabs == '難易度２' else 1)
    if st.session_state.incorrect_answers >= incorrect_limit:
        end_game()

    # ガチャ機能
    if st.button('ガチャを引く！', key='gacha_button'):
        rarity_probs = {'N': 1.0}
        chosen_rarity = np.random.choice(list(rarity_probs.keys()), p=list(rarity_probs.values()))
        subset_df = words_df[words_df['難易度'] == chosen_rarity]
        selected_word = subset_df.sample().iloc[0]

        other_words = words_df[words_df['問題'] != selected_word['問題']].sample(m)
        choices = other_words['回答'].tolist() + [selected_word['回答']]
        np.random.shuffle(choices)

        st.session_state.selected_word = selected_word
        st.session_state.choices = choices
        st.session_state.correct_answer = selected_word['回答']
        st.session_state.display_meaning = False
        st.session_state.quiz_answered = False
        start_timer(ti)

    if 'selected_word' in st.session_state:
        st.header(f"問題: {st.session_state.selected_word['問題']}")
        st.subheader(f"難易度: {st.session_state.selected_word['難易度']}")

        if not st.session_state.quiz_answered and st.session_state.timer_active:
            st.write("この問題の年号はどれでしょう？")

            num_choices = len(st.session_state.choices)
            num_cols = 4
            num_rows = (num_choices + num_cols - 1) // num_cols

            for row in range(num_rows):
                cols = st.columns(num_cols)
                for col in range(num_cols):
                    choice_index = row * num_cols + col
                    if choice_index < num_choices:
                        choice = st.session_state.choices[choice_index]
                        if cols[col].button(str(choice), key=f'choice_{row}_{col}'):
                            st.session_state.selected_choice = choice
                            st.session_state.quiz_answered = True
                            st.session_state.timer_active = False

                            if choice == st.session_state.correct_answer:
                                st.session_state.correct_answers += 1
                                st.success("正解です！")
                            else:
                                st.session_state.incorrect_answers += 1
                                st.error(f"不正解です。正解は {st.session_state.correct_answer} でした。")

                            st.session_state.display_meaning = True
        elif st.session_state.quiz_answered or not st.session_state.timer_active:
            st.write("回答済みです。次の問題に進んでください。")

    if 'timer_active' in st.session_state and st.session_state.timer_active:
        display_timer(ti)

    # 正解数と不正解数を表示
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
