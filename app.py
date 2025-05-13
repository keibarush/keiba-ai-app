import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="VibeCore", layout="wide")
st.title("VibeCore｜AI競馬 勝率 × ケリー指数")

# ファイル読み込み（英数字に修正済）
with open("./vibecore/win_20250513_funa11.json", encoding="utf-8") as f:
    win_probs = json.load(f)

with open("./vibecore/odds_20250513_funa11.json", encoding="utf-8") as f:
    odds_data = json.load(f)

odds_dict = {item["horse"]: item["odds"] for item in odds_data}

kellies = []
for entry in win_probs:
    horse = entry["馬番"]
    prob = entry["勝率"]
    odds = odds_dict.get(horse, None)

    if odds and odds > 1.0:
        kelly = (prob * (odds - 1) - (1 - prob)) / (odds - 1)
        kelly = max(0, round(kelly * 100, 1))
    else:
        kelly = 0.0

    kellies.append({
        "馬番": horse,
        "勝率": round(prob * 100, 1),
        "オッズ": odds,
        "ケリー％": kelly
    })

df = pd.DataFrame(kellies)
df = df.sort_values("ケリー％", ascending=False).reset_index(drop=True)

st.dataframe(df, use_container_width=True)
