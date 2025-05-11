import streamlit as st
import json
import os
import glob

# ==== 秘密モード（パスワード認証） ====
password = st.text_input("アクセスパスワードを入力してください", type="password")

if password != "mysecret123":  # ← 自由に変えてOK（例：keiba2025など）
    st.error("パスワードが違います")
    st.stop()

# ==== タイトル & モード選択 ====
st.set_page_config(page_title="AI競馬レポート", layout="wide")
st.title("AI競馬予想レポート｜折りたたみ形式＋色付きUI")

mode = st.radio("表示モードを選んでください", ["KEIBA RUSH（勝ち馬）", "推し展開メーカー"], horizontal=True)

# ==== JSONファイルアップロード ====
uploaded_file = st.file_uploader("AIレポートJSONファイルをアップロードしてください", type="json")

if uploaded_file:
    data = json.load(uploaded_file)

    for i in range(22):
        key = f"section_{i}"
        with st.expander(f"{i}. セクション内容", expanded=(i == 1)):
            section = data.get(key, "データなし")
            if isinstance(section, dict):
                st.json(section)
            elif isinstance(section, list):
                for item in section:
                    st.write(item)
            else:
                st.write(section)

    # セクション13だけ特別表示（馬別）
    horses = data.get("section_13", {}).get("馬別スペック評価", [])
    if horses:
        with st.expander("13. 馬別スペック評価", expanded=False):
            for horse in horses:
                st.markdown(
                    f"- **{horse['馬番']}番** {horse['馬名']}（{horse['枠']}）｜評価：{horse['評価ランク']}｜支持率：{horse['支持率']}"
                )
else:
    st.info("モード選択後、AIレポートJSONをアップロードしてください。")
