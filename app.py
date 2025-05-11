（存在確認付きコード）

import streamlit as st
import json
import glob
import os

st.title("AI競馬予想レポート｜自動読込モード")

json_folder = "/content/drive/MyDrive/keiba-ai/json/"
file_list = glob.glob(f"{json_folder}/*.json")

if file_list:
    latest_file = max(file_list, key=os.path.getctime)
    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    st.json(data)
else:
    st.warning("JSONファイルが見つかりません。Colabで生成後、再試行してください。")
