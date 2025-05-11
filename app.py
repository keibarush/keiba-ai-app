import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="AI競馬予想アプリ", layout="centered")

st.title("1レース・2モード AI競馬予想")

# --- モード選択 ---
mode = st.radio("モードを選んでください：", ["勝ち馬特化型（KEIBA RUSH）", "推し馬特化型（推し展開メーカー）"])

# --- ファイルアップロード共通処理 ---
uploaded_file = st.file_uploader("推奨JSONファイル（例：buy_20250511_東京_11R.json）をアップロード", type="json")

if uploaded_file:
    data = json.load(uploaded_file)

    if mode == "勝ち馬特化型（KEIBA RUSH）":
        st.subheader("【KEIBA RUSH突入】")
        st.markdown("**CHANCE ZONE → 展開完成 → RUSH発動！**")
        st.markdown("---")
        st.write("◎ 単勝：", data.get("tansho"))
        st.write("◎ 馬連：", data.get("umaren"))
        st.write("◎ 三連複：", data.get("sanrenpuku"))
        st.write("◎ 三連単：", data.get("sanrentan"))
        st.success("報酬期待値が最大になる組み合わせが自動表示されました！")

    elif mode == "推し馬特化型（推し展開メーカー）":
        st.subheader("【推し展開メーカー】")
        oshiuma = st.text_input("あなたの推し馬（馬名）を入力してください")

        if oshiuma:
            st.markdown(f"### 推し馬「{oshiuma}」")
            st.markdown("> if展開ストーリー：")
            st.info(f"{oshiuma}は道中内ラチ沿いを追走し、直線で一気の末脚！夢の勝利へ！")
            st.write("◎ 応援三連複：", data.get("sanrenpuku"))
            st.button("全力応援する！")
else:
    st.info("上からモードを選んで `.json` ファイルをアップロードしてください。")
