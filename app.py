import streamlit as st
import json
import glob
import os

st.set_page_config(page_title="AI競馬レポート", layout="wide")
st.title("AI競馬予想レポート｜自動読込モード")

# Google Driveマウント先のパスを指定
drive_path = "/content/drive/MyDrive/keiba-ai/json/"

# 最新ファイル取得
file_list = glob.glob(os.path.join(drive_path, '*.json'))
latest_file = max(file_list, key=os.path.getctime)

# 最新ファイルを自動読み込み
with open(latest_file, encoding="utf-8") as f:
    data = json.load(f)

st.success(f"最新ファイルを自動読込しました：{os.path.basename(latest_file)}")

# --- タブ表示 ---
tabs = st.tabs([f"Sec.{i}" for i in range(22)])

for i in range(22):
    with tabs[i]:
        section_key = f"section_{i}"
        st.subheader(f"{i}. セクション内容")
        section_data = data.get(section_key, "―")

        if isinstance(section_data, dict) or isinstance(section_data, list):
            st.json(section_data)
        else:
            st.write(section_data)
