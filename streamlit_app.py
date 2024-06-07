import streamlit as st
import pandas as pd

# 固定のExcelファイルのパス
EXCEL_FILE_PATH = "国.xlsx"

# Excelファイルの読み込み
@st.cache
def load_data(file_path):
    data = pd.read_excel(file_path)
    return data

# 画像を表示
def show_image(image_path):
    if image_path:
        st.image(image_path, caption='画像', use_column_width=True)

# メインのStreamlitアプリケーション
def main():
    st.title('画像表示アプリ')

    # Excelファイルを読み込む
    try:
        data = load_data(EXCEL_FILE_PATH)
    except:
        st.write('Excelファイルを読み込めませんでした。')
        return

    # 画像の列が含まれていることを確認
    if 'Image' not in data.columns:
        st.write('Excelファイルに画像の列が含まれていません。')
        return

    # 画像を表示する行を選択
    selected_row = st.selectbox('画像を表示する行を選択してください', data.index)

    # 選択された行の画像を表示
    selected_image_path = data.loc[selected_row, 'Image']
    show_image(selected_image_path)

if __name__ == '__main__':
    main()
