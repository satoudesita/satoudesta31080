import streamlit as st 

import pandas as pd 

import random 

 

def load_events_from_excel(file_path): 

    # Excelファイルからデータを読み込む 

    df = pd.read_excel(file_path, engine='openpyxl') 

    # 1列目のデータをリストに変換して返す 

    events = df.iloc[:, 0].tolist() 

    return events 

 

def event_sorting_game(): 

    st.title("物事の順序を並べ替えるゲーム") 

 

    new_problem_button = st.button("新しい問題を表示") 

 

    if new_problem_button: 

        # Excelファイルから出来事のリストを読み込む 

        events = load_events_from_excel("events.xlsx") 

 

        # 4つの出来事をランダムに選択 

        selected_events = random.sample(events, 4) 

 

        # 出来事の順序をシャッフル 

        random.shuffle(selected_events) 

 

        # 出来事を表示 

        for event in selected_events: 

            st.write(event) 

 

        # 正しい順序を取得 

        correct_order = sorted(selected_events) 

 

        # 入力された順序を取得 

        user_order = [] 

        for event in selected_events: 

            user_order.append(st.text_input(f"{event} の順序を入力してください:", key=event)) 

 

        # 全ての順序が入力されている場合、正解かどうかを判定 

        if all(user_order): 

            if user_order == correct_order: 

                st.write("正解です！") 

            else: 

                st.write("不正解です。もう一度トライしてください。") 

                st.write("正しい順序は以下の通りです:") 

                st.write(", ".join(correct_order)) 

 

if __name__ == "__main__": 

    event_sorting_game() 