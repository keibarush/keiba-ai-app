import streamlit as st

groq_path = "/content/drive/MyDrive/keiba-ai/groq_result.txt"

try:
    with open(groq_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        st.subheader("AI展開別レポート")

        section = ""
        content = ""
        for line in lines:
            line = line.strip()
            if line.startswith("◎"):
                if section:
                    with st.expander(section):
                        st.markdown(content)
                section = line
                content = ""
            else:
                content += line + "\n"

        # 最後のセクション
        if section:
            with st.expander(section):
                st.markdown(content)

except FileNotFoundError:
    st.error("groq_result.txt が見つかりません。Colabで保存されているか確認してください。")
