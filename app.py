import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="VibeCore 競馬予想", layout="wide")
st.title("VibeCore - AI競馬予想＋ケリー基準")

# === レース予想データの読み込み ===
json_path = '予想_20250513_funa11.json'

if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        prediction = json.load(f)

    st.subheader(f"レース情報：{prediction.get('レース', '不明')}")
    st.markdown("### ◎ 本命・対抗・穴")
    st.write(prediction.get("本命", "データなし"))

    st.markdown("### 買い目（ケリー基準）")
    for bet in prediction.get("ケリー買い目", []):
        st.write(f"- {bet}")
else:
    st.error("予想ファイルが見つかりません。")

# === ケリー基準：勝率ファイルから読み込み ===

st.markdown("---")
st.header("ケリー基準による推奨買い目")

win_prob_path = '勝率_20250513_funa11.json'  # ← Colabから保存・アップした勝率ファイル名

if os.path.exists(win_prob_path):
    with open(win_prob_path, 'r', encoding='utf-8') as f:
        win_probs = json.load(f)

    # 仮の単勝オッズ（後で自動化予定）
    win_odds = {
        "1番": 3.2,
        "2番": 7.5,
        "3番": 2.8,
        "4番": 11.0,
        "5番": 4.0,
    }

    # ケリー式計算
    def kelly(p, o):
        b = o - 1
        q = 1 - p
        return round((b * p - q) / b, 3) if (b * p - q) > 0 else 0

    # 表生成
    results = []
    for horse in win_probs:
        p = win_probs[horse]
        o = win_odds.get(horse, 0)
        k = kelly(p, o)
        results.append({"馬番": horse, "勝率": f"{p*100:.1f}%", "オッズ": o, "ケリースコア": k})

    df = pd.DataFrame(results).sort_values(by="ケリースコア", ascending=False)
    st.subheader("ケリースコア 一覧（高い順）")
    st.dataframe(df)

    total_score = df["ケリースコア"].sum()
    if total_score > 0:
        df["推奨金額"] = df["ケリースコア"].apply(lambda x: round(1000 * x / total_score))
        st.subheader("推奨購入金額（仮予算1000円）")
        st.dataframe(df[["馬番", "オッズ", "ケリースコア", "推奨金額"]])
else:
    st.error("勝率ファイルが見つかりません。")
