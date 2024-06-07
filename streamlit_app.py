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

 

        # 出来事のリストをランダムにシャッフル 

        random.shuffle(events) 

 

        # 選択された出来事のリスト 

        selected_events = [] 

 

        # ボタンで出来事を選択 

        for event in events[4]: 

            if st.button(event): 

                selected_events.append(event) 

 

        # 選択された出来事を表示 

        st.write("選択された出来事:", selected_events) 

 

        # 全ての出来事が選択されたら、正しい順序かどうかをチェック 

        if len(selected_events) == 4: 

            correct_order = load_events_from_excel("events.xlsx") [:4]

            if selected_events == correct_order: 

                st.write("正解です！") 

                new_problem_button = True 

            else: 

                st.write("不正解です。もう一度トライしてください。") 

                st.write("正しい順序は以下の通りです:") 

                st.write(correct_order) 

 

if __name__ == "__main__": 

    event_sorting_game() 