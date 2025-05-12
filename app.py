import streamlit as st
import os

# タイトル
st.title("AI競馬予想レポート（会員モード付き）")

# パスワード認証
st.sidebar.title("会員モードログイン")
devpass = st.sidebar.text_input("パスワードを入力してください", type="password")

if devpass != "gold123":
    st.error("※フル機能を使うにはゴールド会員または devpass が必要です。")
    st.stop()

# 入力フォーム
st.sidebar.header("レース選択")
race_date = st.sidebar.text_input("日付を入力（例：20250513）", max_chars=8)
race_place = st.sidebar.text_input("競馬場コード（例：funabashi）", max_chars=20)
race_no = st.sidebar.text_input("レース番号（例：11）", max_chars=2)

# ファイル名とパス
file_name = f"groq_result_{race_date}_{race_place}_{race_no}.txt"
groq_path = f"/content/drive/MyDrive/keiba-ai/{file_name}"

# ファイル読み込み
try:
    with open(groq_path, "r", encoding="utf-8") as f:
        groq_text = f.read()
        st.success("✅ 最新のAIレポートを読み込みました！")
        st.subheader("モバイル用ハイライト")
        st.text(groq_text)
except FileNotFoundError:
    st.error(f"❌ {file_name} が見つかりません。Colab で保存されているか確認してください。")
