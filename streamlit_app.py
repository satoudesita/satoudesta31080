import streamlit as st
import random
import time

# 設定
words = ["run", "went", "gone", "eat", "ate", "eaten"]
correct_answers = ["ran", "went", "gone", "ate", "ate", "eaten"]
maze_size = 5  # 迷路のサイズ

# ランダムに単語とその対応を選ぶ関数
def get_random_word():
    index = random.randint(0, len(words) - 1)
    return words[index], correct_answers[index]

# ゲームの状態を表示
def show_maze():
    # ランダムな単語とその正解を表示
    word, correct_answer = get_random_word()
    
    # スタート
    st.write("### 迷路が始まりました！")
    st.write("最初の単語：", word)
    
    # プレイヤーが選べる選択肢
    options = ["run", "ran", "went", "gone", "eat", "ate"]
    selected_option = st.radio("選んでください", options)
    
    # プレイヤーの選択を確認
    if selected_option == correct_answer:
        st.success("正解！次のマスに進みます。")
    else:
        st.error("間違えました。最初からやり直してください。")
        
    # ゲームの進行
    st.write("選択を終えたら、次のステップに進みましょう。")

# メインアプリケーション
def main():
    st.title("記憶迷路：ことばのダンジョン")
    
    # ゲーム開始ボタン
    start_button = st.button("ゲーム開始")
    
    if start_button:
        show_maze()

if __name__ == "__main__":
    main()
