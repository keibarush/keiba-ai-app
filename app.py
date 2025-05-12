import streamlit as st

# タイトル
st.title("AI競馬予想レポート（会員モード付き）")

# groq_result.txt のパス
groq_path = "./groq_result.txt"

# ファイル読み込みと表示
try:
    with open(groq_path, "r", encoding="utf-8") as f:
        groq_text = f.read()
        st.success("✅ 最新のAIレポートを読み込みました！")
        st.subheader("モバイル用ハイライト")
        st.markdown(groq_text)
except FileNotFoundError:
    st.error("❌ groq_result.txt が見つかりません。Colabでの保存を確認してください。")
