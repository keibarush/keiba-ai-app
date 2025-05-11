import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(
    page_title="競馬AI 推奨買い目アプリ",
    page_icon=":horse:",
    layout="centered"
)

st.title("競馬AI 推奨買い目アプリ")
st.markdown("""
このアプリでは、AIが分析した**推奨買い目**を自動表示します。

- データはあなたがColabなどで作成した `.json` ファイルから読み込みます。
- 単勝・馬連・三連複・三連単を推奨します。
- **アップロードすればすぐに結果が見える**仕組みです！

---
""")
