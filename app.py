import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(
    page_title="競馬AI 推奨買い目アプリ",
    page_icon="horse:",
    layout="centered"
)

st.title("競馬AI 推奨買い目アプリ")
st.markdown("""
このアプリでは、AIが分析した**推奨買い目**を自動表示します。

- データはあなたがColabなどで作成した `.json` ファイルから読み込みます。
- 単勝・馬連・三連複・三連単を推奨します。
- **アップロードすればすぐに結果が見える**しくみです！
""")

# ファイルアップロード
uploaded_files = st.file_uploader("複数のJSONファイルをアップロード", type="json", accept_multiple_files=True)

if uploaded_files:
    data_list = []

    for file in uploaded_files:
        filename = file.name.replace(".json", "")
        parts = filename.split("_")
        if len(parts) == 4:
            _, date, place, race = parts
        else:
            st.warning(f"ファイル名が形式に合っていません: {filename}")
            continue

        buy = json.load(file)

        data_list.append({
            "日付": date,
            "競馬場": place,
            "レース": race,
            "単勝": buy.get("tansho"),
            "馬連": buy.get("umaren"),
            "三連複": buy.get("sanrenpuku"),
            "三連単": buy.get("sanrentan")
        })

    df = pd.DataFrame(data_list)
    df = df.sort_values(by=["日付", "競馬場", "レース"])
    st.dataframe(df)
else:
    st.info("左で複数の `buy_*.json` ファイルをアップロードしてください。")
