import streamlit as st
import pandas as pd

# Excelファイルのパス
EXCEL_FILE_PATH = "国.xlsx"

# Excelファイルの読み込み
@st.cache
def load_data(file_path):
    data = pd.read_excel(file_path)
    return data

# メインのStreamlitアプリケーション
def main():
    st.title('データ検索アプリ')

    # Excelファイルを読み込む
    try:
        data = load_data(EXCEL_FILE_PATH)
    except:
        st.write('Excelファイルを読み込めませんでした。')
        return

    # テキスト入力フィールド
    search_term = st.text_input('検索語を入力してください')

    # 検索語が入力された場合の処理
    if search_term:
        # 検索語に応じてデータを表示
        filtered_data = data[data['国'] == search_term]
        if not filtered_data.empty:
            st.write('検索語に関するデータ:')
            st.write(filtered_data)
        else:
            st.write('入力された検索語に関するデータは見つかりませんでした')

if __name__ == '__main__':
    main()
