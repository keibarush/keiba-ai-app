import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="VibeCore", layout="wide")
st.title("VibeCore｜勝利の鼓動 × 勝ちの直感")

# JSON読み込み（ファイルはStreamlit Cloudにアップロード済とする）
with open("win_20250513_funa11.json", encoding="utf-8") as f:
    win_probs = json.load(f)

with open("odds_20250513_funa11.json", encoding="utf-8") as f:
    odds_data = json.load(f)

# キー名に対応（日本語 or 英語どちらでもOKにする）
def get(entry, *keys):
    for key in keys:
        if key in entry:
            return entry[key]
    return None

# オッズ辞書（horse 番号 → オッズ）
odds_dict = {get(item, "horse", "馬番"): item["odds"] for item in odds_data}

# 勝率 × オッズ → スコア計算
kellies = []
for entry in win_probs:
    horse = get(entry, "horse", "馬番")
    prob = get(entry, "prob", "勝率")
    odds = odds_dict.get(horse)

    if odds and prob is not None:
        if odds > 1.0:
            score = (prob * (odds - 1) - (1 - prob)) / (odds - 1)
            score = max(0, round(score * 100, 1))
        else:
            score = 0.0
    else:
        score = 0.0

    kellies.append({
        "馬番": horse,
        "勝率（％）": round(prob * 100, 1) if prob is not None else None,
        "オッズ": odds,
        "勝利の鼓動 × 勝ちの直感（％）": score
    })

# 表示
df = pd.DataFrame(kellies)
df = df.sort_values("勝利の鼓動 × 勝ちの直感（％）", ascending=False).reset_index(drop=True)

st.dataframe(df, use_container_width=True)
