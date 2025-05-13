import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="VibeCore", layout="wide")
st.title("VibeCore｜AI競馬 勝率 × ケリー指数")

# 勝率JSONの読み込み
with open("vibecore/勝率_20250513_funa11.json", encoding="utf-8") as f:
    win_probs = json.load(f)

# オッズJSONの読み込み
with open("vibecore/オッズ_20250513_funa11.json", encoding="utf-8") as f:
    odds_data = json.load(f)

# オッズを辞書化（馬番: オッズ）
odds_dict = {item["horse"]: item["odds"] for item in odds_data}

# ケリー計算（資金100円前提）
kellies = []
for entry in win_probs:
    horse = entry["馬番"]
    prob = entry["勝率"]
    odds = odds_dict.get(horse, None)
    
    if odds and odds > 1.0:
        kelly = (prob * (odds - 1) - (1 - prob)) / (odds - 1)
        kelly = max(0, round(kelly * 100, 1))  # パーセント表示
    else:
        kelly = 0.0

    kellies.append({
        "馬番": horse,
        "勝率": round(prob * 100, 1),
        "オッズ": odds,
        "ケリー％": kelly
    })

# DataFrame表示
df = pd.DataFrame(kellies)
df = df.sort_values("ケリー％", ascending=False).reset_index(drop=True)

st.dataframe(df, use_container_width=True)
