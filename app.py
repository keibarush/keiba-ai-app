import streamlit as st
import pandas as pd
import json
import os
import glob

# ページ設定
st.set_page_config(page_title="VibeCore", layout="wide")

# カスタムCSSの追加
st.markdown("""
    <style>
    /* フォントと背景 */
    body {
        font-family: 'Noto Sans JP', sans-serif;
        background-color: #F5F5F5;
        color: #333;
    }

    /* ヘッダー */
    .main h1 {
        font-size: 28px;
        font-weight: 700;
        background-color: #FFFACD;
        padding: 10px;
        border-radius: 8px;
        border-bottom: 2px solid #FFD700;
    }

    /* セクション見出し */
    h3 {
        color: #FF69B4;
        font-size: 24px;
        margin-bottom: 16px;
    }

    /* 表のスタイル */
    .dataframe {
        font-size: 14px;
        border: 1px solid #DDD;
        border-collapse: collapse;
        width: 100%;
        overflow-x: auto;
    }
    .dataframe th {
        background-color: #FFD700;
        color: #FFF;
        position: sticky;
        top: 0;
    }
    .dataframe td, .dataframe th {
        padding: 8px;
        text-align: left;
        border: 1px solid #DDD;
    }
    .dataframe tr:nth-child(even) {
        background-color: #FFF;
    }
    .dataframe tr:nth-child(odd) {
        background-color: #F5F5F5;
    }

    /* カードスタイル */
    .card {
        background: linear-gradient(#FFD700, #FFFACD);
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        padding: 16px;
        margin-bottom: 16px;
    }
    .card h5 {
        color: #FF69B4;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .card ul {
        list-style-type: none;
        padding-left: 0;
    }
    .card ul li {
        margin-bottom: 4px;
    }

    /* ボタンスタイル */
    .stButton>button {
        background-color: #FFD700;
        color: #FFF;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.1s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(#FFD700, #FF69B4);
        transform: scale(0.95);
    }

    /* メディアクエリでスマホ対応 */
    @media (max-width: 768px) {
        .main h1 {
            font-size: 24px;
        }
        h3 {
            font-size: 20px;
        }
        .stButton>button {
            width: 100%;
        }
    }
    </style>
""", unsafe_allow_html=True)

# タイトル
st.title("VibeCore｜勝利の鼓動 × 勝ちの直感")

# SessionStateでチェック状態を保存
if "checked_horses" not in st.session_state:
    st.session_state.checked_horses = []

# レース選択
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

        # 推し馬チェック（SessionState保持）
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
                with st.container():
                    st.markdown(f"""
                        <div class="card">
                            <h5>馬番 {row['馬番']}｜<span>{row['推し馬ランク']}</span></h5>
                            <ul>
                                <li><b>勝率：</b><span style='color:#0074D9'>{row['勝率（％）']}%</span></li>
                                <li><b>オッズ：</b>{row['オッズ']} 倍</li>
                                <li><b>スコア：</b>{row['勝利の鼓動 × 勝ちの直感（％）']}%</li>
                            </ul>
                            <a href="https://db.netkeiba.com/horse/{str(row['馬番']).zfill(10)}" target="_blank">
                                <button style="margin-top:10px;">netkeiba戦績をみる</button>
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
