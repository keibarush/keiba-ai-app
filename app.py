import streamlit as st
import pandas as pd
import json
import os
import glob

# ページ設定
st.set_page_config(page_title="VibeCore", layout="wide")
st.title("VibeCore｜勝利の鼓動 × 勝ちの直感")

# SessionStateでチェック状態を保存
if "checked_horses" not in st.session_state:
    st.session_state.checked_horses = []

# ファイルアップロード（win_ / odds_ のjson）
st.markdown("### 勝率またはオッズファイルをアップロード（JSON形式）")
uploaded_file = st.file_uploader("アップロードしてください（例：win_20250514_funa11.json）", type=["json"])
if uploaded_file is not None:
    filename = uploaded_file.name
    if filename.startswith(("win_", "odds_")) and filename.endswith(".json"):
        save_path = os.path.join(".", filename)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"{filename} をアップロードしました")
    else:
        st.error("ファイル名が win_ または odds_ で始まる必要があります")

# 勝率ファイル一覧を自動取得
win_files = sorted(glob.glob("win_*.json"))
race_ids = [f.replace("win_", "").replace(".json", "") for f in win_files]

if not race_ids:
    st.warning("勝率ファイルが見つかりません。上からアップロードしてください。")
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

            if score >= 50:
                rank = "本命安定圏"
            elif score >= 30:
                rank = "複勝安定圏"
            elif score >= 10:
                rank = "オッズ妙味圏"
            else:
                rank = "検討外・回避圏"

            rows.append({
                "馬番": horse,
                "勝率（％）": round(prob * 100, 1) if prob is not None else None,
                "オッズ": odds,
                "勝利の鼓動 × 勝ちの直感（％）": score,
                "推し馬ランク": rank
            })

        df = pd.DataFrame(rows)
        df = df.sort_values("勝利の鼓動 × 勝ちの直感（％）", ascending=False).reset_index(drop=True)

        # 推し馬チェック（保持）
        st.markdown("### 推し馬チェック")
        current_check = st.multiselect(
            "気になる馬を選んでください（保持されます）",
            options=df["馬番"].tolist(),
            default=st.session_state.checked_horses
        )
        st.session_state.checked_horses = current_check

        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.markdown("### あなたの“推し馬カード”")

        selected_df = df[df["馬番"].isin(st.session_state.checked_horses)]
        if selected_df.empty:
            st.info("推し馬を上から選ぶと、ここにカードが出てきます。")
        else:
            for _, row in selected_df.iterrows():
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.image("https://cdn.pixabay.com/photo/2016/04/01/09/48/horse-1290171_960_720.png", width=60)
                with col2:
                    st.markdown(f"**馬番 {row['馬番']}｜{row['推し馬ランク']}**")
                    st.markdown(f"- 勝率：{row['勝率（％）']}％")
                    st.markdown(f"- オッズ：{row['オッズ']} 倍")
                    st.markdown(f"- スコア：{row['勝利の鼓動 × 勝ちの直感（％）']}％")
                    st.link_button("netkeiba戦績をみる", f"https://db.netkeiba.com/horse/{str(row['馬番']).zfill(10)}", use_container_width=True)
