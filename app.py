import streamlit as st
import json
import os
import glob

st.set_page_config(page_title="AI競馬レポート", layout="wide")
st.title("AI競馬予想レポート｜折りたたみ形式＋色付きUI")

# 表示モード選択（UIだけ）
mode = st.radio("表示モードを選んでください", ["KEIBA RUSH（勝ち馬）", "推し展開メーカー"], horizontal=True)

# JSONファイルアップロード
uploaded_file = st.file_uploader("AIレポートJSONファイルをアップロードしてください", type="json")

if uploaded_file:
    data = json.load(uploaded_file)

    for i in range(22):
        section_key = f"section_{i}"
        section_data = data.get(section_key, {})
        with st.expander(f"{i}. セクション内容", expanded=False):
            if isinstance(section_data, dict):
                for k, v in section_data.items():
                    st.markdown(f"**{k}**")
                    st.write(v)
            elif isinstance(section_data, list):
                for item in section_data:
                    st.write(item)
            else:
                st.write(section_data)

    # 特別表示：セクション13 馬別評価（あれば）
    if "section_13" in data and "馬別スペック評価" in data["section_13"]:
        with st.expander("13. 馬別スペック評価（整形表示）", expanded=False):
            for horse in data["section_13"]["馬別スペック評価"]:
                st.markdown(
                    f"- 【{horse['馬番']}番】{horse['馬名']}（{horse['枠']}）｜評価：{horse['評価ランク']}｜支持率：{horse['支持率']}"
                )
else:
    st.info("モード選択後、AIレポートJSONをアップロードしてください。")
