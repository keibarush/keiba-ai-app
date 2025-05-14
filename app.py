import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="VibeCore", layout="wide")
st.title("VibeCore｜勝利の鼓動 × 勝ちの直感")

# JSONファイル読み込み
with open("win_20250513_funa11.json", encoding="utf-8") as f:
    win_probs = json.load(f)

with open("odds_20250513_funa11.json", encoding="utf-8") as f:
    odds_data = json.load(f)

# オッズ辞書作成
odds_dict = {item["horse"]: item["odds"] for item in odds_data}

# スコア計算（ケリーの代替名）
kellies = []
for entry in win_probs:
    horse = entry["馬番"]
    prob = entry["勝率"]
    odds = odds_dict.get(horse)

    if odds and odds > 1.0:
        score = (prob * (odds - 1) - (1 - prob)) / (odds - 1)
        score = max(0, round(score * 100, 1))
    else:
        score = 0.0

    kellies.append({
        "馬番": horse,
        "勝率（％）": round(prob * 100, 1),
        "オッズ": odds,
        "勝利の鼓動 × 勝ちの直感（％）": score
    })

# 表示
df = pd.DataFrame(kellies)
df = df.sort_values("勝利の鼓動 × 勝ちの直感（％）", ascending=False).reset_index(drop=True)

st.dataframe(df, use_container_width=True)
