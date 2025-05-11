import streamlit as st
import json

st.set_page_config(page_title="AI競馬レポート", layout="wide")
st.title("AI競馬予想レポート｜折りたたみ形式＋色付きUI")

# 表示モード選択
mode = st.radio("表示モードを選んでください", ["KEIBA RUSH（勝ち馬）", "推し展開メーカー"], horizontal=True)

# JSONファイルアップロード
uploaded_file = st.file_uploader("AIレポートJSONファイルをアップロードしてください", type="json")

if uploaded_file:
    data = json.load(uploaded_file)

    # === 各セクション ===
    with st.expander("0. ユーザーカスタム設定", expanded=False):
        st.code(json.dumps(data.get("section_0", {}), indent=2, ensure_ascii=False))

    with st.expander("1. モバイル用ハイライト", expanded=True):
        sec1 = data.get("section_1", {})
        st.metric("本命", sec1.get("本命", "―"))
        st.metric("対抗", sec1.get("対抗", "―"))
        st.metric("穴馬", sec1.get("穴", "―"))
        st.success(f"勝負度：{sec1.get('勝負度', '―')}｜ROI：{sec1.get('ROI', '―')}｜Hit率：{sec1.get('Hit率', '―')}")

    for i in range(2, 13):
        with st.expander(f"{i}. セクション内容", expanded=False):
            st.write(data.get(f"section_{i}", "―"))

    with st.expander("13. 馬別スペック評価", expanded=True):
        for horse in data["section_13"]["馬別スペック評価"]:
            st.markdown(f"- **{horse['馬番']}番 {horse['馬名']}**（{horse['枠']}）｜評価：{horse['評価ランク']}｜支持率：{horse['支持率']}")

    with st.expander("14. データ取得ログ"):
        st.info(data["section_14"]["データ取得ログ"])

    with st.expander("15. 異常アラート"):
        for alert in data["section_15"]["異常アラート"]:
            st.warning(alert)

    with st.expander("16. 展開予測"):
        st.write(data["section_16"]["展開予測"])

    with st.expander("17. 展開影響の深掘り"):
        st.write(data["section_17"]["展開影響深掘り"])

    with st.expander("18. 推奨馬ピックアップ"):
        st.success("推奨馬：" + "、".join(data["section_18"]["推奨馬ピックアップ"]))

    with st.expander("19. ベット構築（ケリー基準）"):
        for bet in data["section_19"]["ベット構築例"]:
            st.markdown(
                f"- **{bet['券種']}**｜{bet['買い目']}｜的中率：{bet['確率']}｜期待値：{bet['期待値']}｜"
                f"Kelly比率：{bet['Kelly比率']}｜推奨金額：{bet['推奨金額']}"
            )

    with st.expander("20. バックテスト記録"):
        st.write(data.get("section_20", {}))

    with st.expander("21. 次回改善アクション"):
        st.write(data.get("section_21", {}))

else:
    st.info("モード選択後、AIレポートJSONをアップロードしてください。")
