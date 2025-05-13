import streamlit as st
import json
import os

st.set_page_config(page_title="VibeCore 競馬予想", layout="wide")

st.title("VibeCore - AI競馬予想")

# ファイルパス（あなたのDriveのJSONファイルを手動DL or パス修正）
json_path = '予想_20250513_funa11.json'  # ← 同じフォルダに配置しておく前提

if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        prediction = json.load(f)
    
    st.subheader(f"レース情報：{prediction.get('レース', '不明')}")
    st.markdown("### ◎ 本命・対抗・穴")
    st.write(prediction.get("本命", "データなし"))

    st.markdown("### 買い目（ケリー基準）")
    for bet in prediction.get("ケリー買い目", []):
        st.write(f"- {bet}")
else:
    st.error("予想ファイルが見つかりません。")
