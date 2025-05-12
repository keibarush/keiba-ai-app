import streamlit as st

# --- パスコード認証セクション ---
st.sidebar.title("会員モードログイン")
devpass = st.sidebar.text_input("パスコードを入力してください", type="password")

if devpass != "gold123":
    st.error("※フル機能を利用するにはゴールド会員または devpass が必要です。")
    st.stop()

# --- groq_result.txt の表示セクション ---
groq_path = "/content/drive/MyDrive/keiba-ai/groq_result.txt"

try:
    with open(groq_path, "r", encoding="utf-8") as f:
        groq_text = f.read()
        st.subheader("Groq AI予測レポート")
        st.text(groq_text)
except FileNotFoundError:
    st.error("groq_result.txt が見つかりません。Colab での保存を確認してください。")
