import streamlit as st
import pandas as pd

# Excelファイルの読み込み
@st.cache
def load_data(file_path):
    data = pd.read_excel(file_path)
    return data

# メインのStreamlitアプリケーション
def main():
    st.title('国のデータを取得するアプリ')

    # Excelファイルのパスを入力
    excel_file_path = st.text_input('Excelファイルのパスを入力してください')

    if excel_file_path:
        # Excelファイルを読み込む
        data = load_data(excel_file_path)

        # 国の選択
        country = st.text_input('国を入力してください')

        if country:
            # 国に関する情報を取得
            country_info = data[data['Country'] == country]

            if not country_info.empty:
                st.write('国の情報:')
                st.write(country_info)
            else:
                st.write('その国のデータはありません')

if __name__ == '__main__':
    main()
