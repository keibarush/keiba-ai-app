import streamlit as st

# タイトル
st.title("競馬AI 推奨買い目アプリ")

# 推奨買い目（仮データ、後でAIと接続）
tansho = 5
umaren = (3, 5)
sanrenpuku = (3, 5, 7)
sanrentan = (5, 3, 7)

# 表示
st.subheader("◎ AI推奨買い目")
st.write("◎ 単勝：", tansho)
st.write("◎ 馬連：", umaren)
st.write("◎ 三連複：", sanrenpuku)
st.write("◎ 三連単：", sanrentan)
