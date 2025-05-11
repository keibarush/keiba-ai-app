import streamlit as st
import json

st.set_page_config(page_title="AI競馬レポート", layout="wide")
st.title("AI競馬予想レポート｜0〜21構成")

# モード選択（UI用途）
mode = st.radio("表示モードを選んでください", ["KEIBA RUSH（勝ち馬）", "推し展開メーカー"], horizontal=True)

# JSONファイルアップロード
uploaded_file = st.file_uploader("AIレポートJSONファイルをアップロードしてください", type="json")

if uploaded_file:
    data = json.load(uploaded_file)

    # --- UI：タブ表示でセクション0〜21を整理 ---
    tabs = st.tabs([f"Sec.{i}" for i in range(22)])

    # セクション0
    with tabs[0]:
        st.subheader("0. ユーザーカスタム設定")
        st.json(data.get("section_0", {}))

    # セクション1
    with tabs[1]:
        st.subheader("1. モバイル用ハイライト")
        st.json(data.get("section_1", {}))

    # セクション2〜12
    for i in range(2, 13):
        with tabs[i]:
            st.subheader(f"{i}. セクション内容")
            st.write(data.get(f"section_{i}", "―"))

    # セクション13（馬別評価）
    with tabs[13]:
        st.subheader("13. 馬別スペック評価")
        for horse in data["section_13"]["馬別スペック評価"]:
            st.markdown(f"- 【{horse['馬番']}番】{horse['馬名']}（{horse['枠']}）｜評価：{horse['評価ランク']}｜支持率：{horse['支持率']}")

    # セクション14（ログ）
    with tabs[14]:
        st.subheader("14. データ取得ログ")
        st.info(data["section_14"]["データ取得ログ"])

    # セクション15（アラート）
    with tabs[15]:
        st.subheader("15. 異常アラート")
        for alert in data["section_15"]["異常アラート"]:
            st.warning(alert)

    # セクション16（展開予測）
    with tabs[16]:
        st.subheader("16. 展開予測")
        st.write(data["section_16"]["展開予測"])

    # セクション17（展開深掘り）
    with tabs[17]:
        st.subheader("17. 展開影響の深掘り")
        st.write(data["section_17"]["展開影響深掘り"])

    # セクション18（推奨馬）
    with tabs[18]:
        st.subheader("18. 推奨馬ピックアップ")
        st.success("推奨馬：" + "、".join(data["section_18"]["推奨馬ピックアップ"]))

    # セクション19（ケリーベット）
    with tabs[19]:
        st.subheader("19. ベット構築（ケリー基準）")
        for bet in data["section_19"]["ベット構築例"]:
            st.markdown(
                f"- **{bet['券種']}**｜{bet['買い目']}｜的中率：{bet['確率']}｜期待値：{bet['期待値']}｜"
                f"Kelly比率：{bet['Kelly比率']}｜推奨金額：{bet['推奨金額']}"
            )

    # セクション20
    with tabs[20]:
        st.subheader("20. バックテスト記録")
        st.write(data.get("section_20", {}))

    # セクション21
    with tabs[21]:
        st.subheader("21. 次回改善アクション")
        st.write(data.get("section_21", {}))
else:
    st.info("モード選択後、AIレポートJSONをアップロードしてください。")
