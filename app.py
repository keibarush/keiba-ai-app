import streamlit as st
import json
import requests
from urllib.parse import parse_qs

st.set_page_config(page_title="AI競馬レポート", layout="wide")
st.title("AI競馬予想レポート（会員モード付き）")

# === アクセス制御 ===
query = st.experimental_get_query_params()
access_key = parse_qs(str(query)).get("access", [""])[0]

is_full_access = access_key == "devpass"  # ← あなた専用パスワード

# === GitHubから最新JSONを取得 ===
def get_latest_json_from_github():
    url = "https://api.github.com/repos/keibarush/keiba-ai-app/contents/json"
    res = requests.get(url).json()
    json_files = [f for f in res if f["name"].endswith(".json")]
    latest = max(json_files, key=lambda f: f["name"])
    return requests.get(latest["download_url"]).json()

try:
    data = get_latest_json_from_github()
    st.success("✅ 最新のAIレポートを読み込みました！")

    # === ハイライト表示（本命◎のみ or フル） ===
    with st.expander("1. モバイル用ハイライト", expanded=True):
        hl = data.get("section_1", {}).get("モバイル用ハイライト", {})
        st.metric("本命", hl.get("本命", "―"))

        if is_full_access:
            col1, col2 = st.columns(2)
            col1.metric("ROI", hl.get("ROI", "―"))
            col2.metric("Hit率", hl.get("Hit率", "―"))
            st.markdown(f"○ 対抗：{hl.get('対抗', '―')}　▲ 穴：{hl.get('穴', '―')}")
        else:
            st.warning("※フル機能を利用するにはゴールド会員または devpass が必要です。")

    # === ケリーベット構築（制限あり） ===
    with st.expander("19. ベット構築（ケリー基準）", expanded=False):
        bets = data.get("section_19", {}).get("ベット構築例", [])
        if is_full_access:
            for bet in sorted(bets, key=lambda x: float(x["Kelly比率"]), reverse=True):
                st.markdown(
                    f"- **{bet['券種']}**｜{bet['買い目']}｜的中率：{bet['確率']}｜期待値：{bet['期待値']}｜"
                    f"Kelly：{bet['Kelly比率']}｜推奨金額：{bet['推奨金額']}"
                )
        else:
            st.error("このセクションはゴールド会員専用です。")

    # === その他セクション（フルアクセスのみ展開） ===
    if is_full_access:
        for i in range(0, 22):
            if i in [1, 19]: continue
            key = f"section_{i}"
            content = data.get(key, {})
            with st.expander(f"{i}. セクション", expanded=False):
                st.json(content)
    else:
        st.info("※一部セクションは非表示です。全機能解放にはパスコードが必要です。")

except Exception as e:
    st.error(f"GitHubからの読み込みに失敗しました：{e}")
