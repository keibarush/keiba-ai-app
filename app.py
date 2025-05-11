import streamlit as st
import json
from urllib.parse import parse_qs

st.set_page_config(page_title="AI競馬予想レポート", layout="wide")
st.title("AI競馬予想レポート｜0〜21構成")

# === あなた専用の全開放キー ===
query_params = st.experimental_get_query_params()
dev_mode = "dev_access" in query_params and query_params["dev_access"][0] == "yourpass123"

# === プラン分岐 ===
if dev_mode:
    plan = "プロ"
    st.success("開発者モード（全機能開放中）")
else:
    plan = st.selectbox("ご利用プランを選択してください", ["フリー", "スタンダード", "プロ"])

# === 表示許可セクション（プラン別）
plan_access = {
    "フリー": [1, 13, 19],
    "スタンダード": list(range(14)) + [19],
    "プロ": list(range(22))
}

# === ファイルアップロード
uploaded_file = st.file_uploader("AIレポートJSONファイルをアップロードしてください", type="json")

if uploaded_file:
    data = json.load(uploaded_file)
    allowed_sections = plan_access.get(plan, [])

    tabs = st.tabs([f"Sec.{i}" for i in allowed_sections])

    for idx, sec_id in enumerate(allowed_sections):
        with tabs[idx]:
            st.subheader(f"{sec_id}. セクション")

            if sec_id == 13:
                st.subheader("13. 馬別スペック評価")
                for horse in data.get("section_13", {}).get("馬別スペック評価", []):
                    st.markdown(
                        f"- 【{horse['馬番']}番】{horse['馬名']}（{horse['枠']}）｜評価：{horse['評価ランク']}｜支持率：{horse['支持率']}"
                    )

            elif sec_id == 15:
                st.subheader("15. 異常アラート")
                for alert in data.get("section_15", {}).get("異常アラート", []):
                    st.warning(alert)

            elif sec_id == 19:
                st.subheader("19. ベット構築（ケリー基準）")
                for bet in data.get("section_19", {}).get("ベット構築例", []):
                    st.markdown(
                        f"- **{bet['券種']}**｜{bet['買い目']}｜的中率：{bet['確率']}｜期待値：{bet['期待値']}｜"
                        f"Kelly比率：{bet['Kelly比率']}｜推奨金額：{bet['推奨金額']}"
                    )
            else:
                st.write(data.get(f"section_{sec_id}", "―"))

else:
    st.info("プランを選んでからAIレポートJSONをアップロードしてください。")
