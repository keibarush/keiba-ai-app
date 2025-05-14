import streamlit as st
import pandas as pd
import json
import os
import glob

st.set_page_config(page_title="VibeCore", layout="wide")
st.title("VibeCore｜勝利の鼓動 × 勝ちの直感")

# レースファイル読み込み（勝率JSON）
win_files = sorted(glob.glob("win_*.json"))
race_ids = [f.replace("win_", "").replace(".json", "") for f in win_files]

if not race_ids:
    st.warning("勝率ファイルが見つかりません。ファイルをアップロードしてください。")
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

        # キー抽出補助
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

            # ランク分類（旧表現 → 新表現）
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

        # 表現変更マッピング
        rank_label_map = {
            "本命圏（鉄板）": "本命安定圏",
            "対抗圏（複勝）": "複勝安定圏",
            "爆発圏（穴）": "オッズ妙味圏",
            "買い控え圏": "検討外・回避圏"
        }
        df["推し馬ランク"] = df["推し馬ランク"].map(rank_label_map)

        # 表全体表示
        st.dataframe(df, use_container_width=True)

        # ランク説明文
        explanation_dict = {
            "本命安定圏": "スコア50%以上。信頼できる本命候補。勝率とオッズのバランスが優秀。",
            "複勝安定圏": "スコア30〜49%。安定した複勝圏候補で連系にも使いやすい。",
            "オッズ妙味圏": "スコア10〜29%。勝率そこそこ＋高オッズで妙味ある狙い目。",
            "検討外・回避圏": "スコア10%未満。今回は回避候補。勝率・妙味ともに薄い可能性あり。"
        }

        st.markdown("### 推し馬ランク別まとめ")
        for label in ["本命安定圏", "複勝安定圏", "オッズ妙味圏", "検討外・回避圏"]:
            sub_df = df[df["推し馬ランク"] == label]
            if not sub_df.empty:
                with st.expander(f"【{label}】を表示"):
                    st.markdown(f"**{explanation_dict[label]}**")
                    st.dataframe(sub_df, use_container_width=True)

st.markdown("---")
st.markdown("### あなたの直感で選ぶ“推しプロフィール”")

for label in ["本命安定圏", "複勝安定圏", "オッズ妙味圏"]:
    sub_df = df[df["推し馬ランク"] == label]
    if not sub_df.empty:
        st.markdown(f"#### {label}")
        for _, row in sub_df.iterrows():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.image("https://cdn.pixabay.com/photo/2016/04/01/09/48/horse-1290171_960_720.png", width=60)  # 仮の馬アイコン
            with col2:
                st.markdown(f"**馬番 {row['馬番']}**")
                st.markdown(f"・勝率：{row['勝率（％）']}％")
                st.markdown(f"・オッズ：{row['オッズ']} 倍")
                st.markdown(f"・スコア：{row['勝利の鼓動 × 勝ちの直感（％）']}％")
                st.markdown(f"・ランク：{row['推し馬ランク']}")
                st.link_button("戦績をみる（netkeiba）", f"https://db.netkeiba.com/horse/{str(row['馬番']).zfill(10)}", use_container_width=True)
