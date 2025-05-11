import streamlit as st
import json
import requests
from datetime import datetime

# === 設定 ===
repo_owner = "keibarush"
repo_name = "keiba-ai-app"
folder = "json"

st.set_page_config(page_title="AI競馬レポート | 自動表示モード", layout="wide")
st.title("AI競馬予想レポート ｜ 自動読込＆常時更新")

# GitHub API から最新のJSONファイルを取得
def get_latest_json_from_github(owner, repo, folder):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder}"
    response = requests.get(url)
    files = response.json()
    
    json_files = [f for f in files if f['name'].endswith('.json')]
    if not json_files:
        return None

    latest_file = max(json_files, key=lambda x: x['name'])
    json_url = latest_file['download_url']
    return requests.get(json_url).json()

# JSON取得と表示
data = get_latest_json_from_github(repo_owner, repo_name, folder)

if data:
    st.success("最新のAIレポートを読み込みました！")

    with st.expander("0. ユーザーカスタム設定", expanded=False):
        st.json(data.get("section_0", {}))

    with st.expander("1. モバイル用ハイライト", expanded=False):
        st.json(data.get("section_1", {}))

    for i in range(2, 13):
        with st.expander(f"{i}. セクション内容", expanded=False):
            st.write(data.get(f"section_{i}", "―"))

    with st.expander("13. 馬別スペック評価", expanded=False):
        horses = data.get("section_13", {}).get("馬別スペック評価", [])
        if horses:
            for horse in horses:
                st.markdown(f"- **{horse['馬番']}番** {horse['馬名']}（{horse['枠']}）｜評価：{horse['評価ランク']}｜支持率：{horse['支持率']}")
        else:
            st.info("馬別スペック評価が見つかりません")

    with st.expander("14. データ取得ログ", expanded=False):
        st.info(data.get("section_14", {}).get("データ取得ログ", "―"))

    with st.expander("15. 異常アラート", expanded=False):
        for alert in data.get("section_15", {}).get("異常アラート", []):
            st.warning(alert)

    with st.expander("16. 展開予測", expanded=False):
        st.write(data.get("section_16", {}).get("展開予測", "―"))

    with st.expander("17. 展開影響の深掘り", expanded=False):
        st.write(data.get("section_17", {}).get("展開影響深掘り", "―"))

    with st.expander("18. 推奨馬ピックアップ", expanded=False):
        st.success("推奨馬：" + "、".join(data.get("section_18", {}).get("推奨馬ピックアップ", [])))

    with st.expander("19. ベット構築（ケリー基準）", expanded=False):
        for bet in data.get("section_19", {}).get("ベット構築例", []):
            st.markdown(
                f"- **{bet['券種']}**｜{bet['買い目']}｜的中率：{bet['確率']}｜期待値：{bet['期待値']}｜"
                f"Kelly比率：{bet['Kelly比率']}｜推奨金額：{bet['推奨金額']}"
            )

    with st.expander("20. バックテスト記録", expanded=False):
        st.write(data.get("section_20", {}))

    with st.expander("21. 次回改善アクション", expanded=False):
        st.write(data.get("section_21", {}))

else:
    st.error("GitHubから最新のレポートが取得できませんでした。JSONファイルがアップロードされているか確認してください。")
