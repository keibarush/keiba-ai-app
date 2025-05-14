import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="VibeCore", layout="wide")
st.title("VibeCore｜勝利の鼓動 × 勝ちの直感")

# レースID入力
race_id = st.text_input("レースIDを入力してください（例：20250513_funa11）", "")

# 入力がある場合のみ処理
if race_id:
    win_path = f"win_{race_id}.json"
    odds_path = f"odds_{race_id}.json"

    if not os.path.exists(win_path):
        st.error(f"勝率ファイルが見つかりません: {win_path}")
    elif not os.path.exists(odds_path):
        st.error(f"オッズファイルが見つかりません: {odds_path}")
    else:
        with open(win_path, encoding="utf-8") as f:
            win_probs = json.load(f)

        with open(odds_path, encoding="utf-8") as f:
            odds_data = json.load(f)

        def get(entry, *keys):
            for key in keys:
                if key in entry:
                    return entry[key]
            return None

        odds_dict = {get(item, "horse", "馬番"): item["odds"] for item in odds_data}

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

        df = pd.DataFrame(kellies)
        df = df.sort_values("勝利の鼓動 × 勝ちの直感（％）", ascending=False).reset_index(drop=True)

        st.dataframe(df, use_container_width=True)
