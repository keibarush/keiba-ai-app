import streamlit as st
import json

st.set_page_config(page_title="AI競馬予想アプリ", layout="wide")
st.title("1レース・2モード AI競馬予想")

# --- モード選択 ---
mode = st.radio("モードを選んでください：", ["勝ち馬特化型（KEIBA RUSH）", "推し馬特化型（推し展開メーカー）"])

# --- ファイルアップロード ---
uploaded_file = st.file_uploader("AIレポートJSON（例：buy_2025xxxxx_AI_report.json）をアップロード", type="json")

if uploaded_file:
    data = json.load(uploaded_file)

    # === モード①：勝ち馬特化型（ケリー基準） ===
    if mode == "勝ち馬特化型（KEIBA RUSH）":
        st.header("【KEIBA RUSH突入】")
        st.markdown("**CHANCE ZONE → 展開完成 → RUSH発動！**")
        st.write("◎ 単勝：", data.get("tansho", "―"))
        st.write("◎ 馬連：", data.get("umaren", "―"))
        st.write("◎ 三連複：", data.get("sanrenpuku", "―"))
        st.write("◎ 三連単：", data.get("sanrentan", "―"))

        st.markdown("---")
        st.subheader("セクション13：馬別スペック評価（全頭）")
        for horse in data["section_13"]["馬別スペック評価"]:
            st.write(f"【{horse['馬番']}番】{horse['馬名']}（{horse['枠']}）｜評価ランク：{horse['評価ランク']}｜支持率：{horse['支持率']}")

        st.subheader("セクション14：データ取得・品質ログ")
        st.info(data["section_14"]["データ取得ログ"])

        st.subheader("セクション15：異常アラート")
        for alert in data["section_15"]["異常アラート"]:
            st.warning(alert)

        st.subheader("セクション16：展開予測")
        st.write(data["section_16"]["展開予測"])

        st.subheader("セクション17：展開影響の深掘り")
        st.write(data["section_17"]["展開影響深掘り"])

        st.subheader("セクション18：推奨馬ピックアップ")
        st.success("推奨馬：" + "、".join(data["section_18"]["推奨馬ピックアップ"]))

        st.subheader("セクション19：ベット構築例（ケリー基準）")
        for bet in data["section_19"]["ベット構築例"]:
            st.markdown(
                f"- **{bet['券種']}**｜{bet['買い目']}｜的中率：{bet['確率']}｜期待値：{bet['期待値']}｜"
                f"Kelly比率：{bet['Kelly比率']}｜推奨金額：{bet['推奨金額']}"
            )

    # === モード②：推し馬特化型（if展開） ===
    elif mode == "推し馬特化型（推し展開メーカー）":
        st.header("【推し展開メーカー】")
        oshiuma = st.text_input("あなたの推し馬（馬名）を入力してください")

        if oshiuma:
            st.subheader(f"推し馬「{oshiuma}」ifストーリー")
            st.info(f"{oshiuma}は道中内ラチ沿いを追走し、直線で一気の末脚！夢の勝利へ！")
            st.write("◎ 応援三連複：", data.get("sanrenpuku", "―"))
            st.button("全力応援する！")

else:
    st.info("上からモードを選んで、AIレポートJSONをアップロードしてください。")
