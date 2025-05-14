import streamlit as st
import pandas as pd
import json
import os
import glob

st.set_page_config(page_title="VibeCore", layout="wide")
st.title("VibeCore｜勝利の鼓動 × 勝ちの直感")

# 自動レース選択
win_files = sorted(glob.glob("win_*.json"))
race_ids = [f.replace("win_", "").replace(".json", "") for f in win_files]

if not race_ids:
    st.warning("勝率ファイルが見つかりません。")
else:
    selected_race = st.selectbox("レースを選択してください", race_ids)

    win_path = f"win_{selected_race}.json"
    odds_path = f"odds_{selected_race}.json"

    if not os.path.exists(odds_path):
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

        rows = []
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

            # ランク分類
            if score >= 50:
                rank = "本命圏（鉄板）"
            elif score >= 30:
                rank = "対抗圏（複勝）"
            elif score >= 10:
                rank = "爆発圏（穴）"
            else:
                rank = "買い控え圏"

            rows.append({
                "馬番": horse,
                "勝率（％）": round(prob * 100, 1) if prob is not None else None,
                "オッズ": odds,
                "勝利の鼓動 × 勝ちの直感（％）": score,
                "推し馬ランク": rank
            })

        df = pd.DataFrame(rows)
        df = df.sort_values("勝利の鼓動 × 勝ちの直感（％）", ascending=False).reset_index(drop=True)

        st.dataframe(df, use_container_width=True)

        # ランクごとの分布
        st.markdown("### 推し馬ランク別まとめ")
        for label in ["本命圏（鉄板）", "対抗圏（複勝）", "爆発圏（穴）", "買い控え圏"]:
            sub_df = df[df["推し馬ランク"] == label]
            if not sub_df.empty:
                st.markdown(f"#### {label}")
                st.dataframe(sub_df, use_container_width=True)
