import streamlit as st
import pandas as pd
import numpy as np

# Excelファイルのパス
EXCEL_FILE_PATH = "国.xlsx"

# Excelファイルの読み込み
@st.cache
def load_data(file_path):
    data = pd.read_excel(file_path)
    return data

# 国の情報と画像を表示
def show_country_info(country_data):
    if not country_data.empty:
        country_name = country_data.iloc[0]['国']
        st.write(f"国名: {country_name}")
        country_description = country_data.iloc[0]['人口']
        st.write(f"説明: {country_description}")  # 説明を表示
        country_image_url = country_data.iloc[0]['画像']
        if country_image_url:
            st.image(country_image_url, caption='国の画像', use_column_width=True)
    else:
        st.write('入力された国の情報が見つかりませんでした。')

# メインのStreamlitアプリケーション
def main():
    st.title('国の情報と画像表示アプリ')

    # Excelファイルを読み込む
    try:
        data = load_data(EXCEL_FILE_PATH)
    except:
        st.write('Excelファイルを読み込めませんでした。')
        return

    # テキスト入力フィールド
    country_name = st.text_input('国名を入力してください')

    # ユーザーが国名を入力した場合の処理
    if country_name:
        # 入力された国名に応じてデータをフィルタリング
        country_data = data[data['国'] == country_name]
        show_country_info(country_data)

if __name__ == '__main__':
    main()
