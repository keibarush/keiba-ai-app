import streamlit as st
import pandas as pd
from datetime import datetime

# ミッションCSV（ソロフリーランス向け）
missions_df = pd.DataFrame([
    {"id": "M1", "label": "3日連続ログイン", "points": 10, "premium_reward": "プレミアム称号「ログインスター」", "category": "無料"},
    {"id": "M2", "label": "推し馬に10HEART投票", "points": 15, "premium_reward": "限定演出（背景：応援ペンライト＋金ハート）", "category": "無料"},
    {"id": "M3", "label": "コメント5回投稿", "points": 10, "premium_reward": "「応援マスター」バッジ（銀＋虹）", "category": "無料"},
    {"id": "M10", "label": "ガチャでウルトラレア獲得", "points": 30, "premium_reward": "ウルトラSSR NFT（特別AR演出付き）", "category": "無料"},
    {"id": "M15", "label": "レース的中（3回以上）", "points": 20, "premium_reward": "限定ボイス（声優ナレーション）", "category": "無料"},
    {"id": "M20", "label": "コミュニティで1000HEART投票達成", "points": 50, "premium_reward": "コミュニティ限定NFT（団結の証）", "category": "プレミアム"},
    {"id": "M30", "label": "連勝応援（5連勝）", "points": 100, "premium_reward": "プレミアム専用ガチャチケット（SSR確定）", "category": "プレミアム"}
])

# バトルパス状態管理
if "battle_pass" not in st.session_state:
    st.session_state.battle_pass = {
        "points": 0,
        "missions": {row["id"]: {"done": False, "label": row["label"], "pt": row["points"], "premium_reward": row["premium_reward"], "category": row["category"]} for _, row in missions_df.iterrows()},
        "premium": False,
        "rewards": []
    }

# プレミアム加入チェック
st.session_state.battle_pass["premium"] = st.checkbox("プレミアムパス加入者（500円/月）")

# タイトル
st.title("【VibeCore】バトルパス")

# ミッション表示
for key, mission in st.session_state.battle_pass["missions"].items():
    if not mission["done"] and (mission["category"] == "無料" or st.session_state.battle_pass["premium"]):
        if st.button(f"ミッション達成：{mission['label']}（{mission['pt']}pt）", key=key):
            st.session_state.battle_pass["missions"][key]["done"] = True
            st.session_state.battle_pass["points"] += mission["pt"]
            if st.session_state.battle_pass["premium"]:
                st.session_state.battle_pass["rewards"].append(mission["premium_reward"])
            st.markdown(f"""
            <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
                <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 ミッション達成！ 🎉</h4>
                <div style='width: 50px; height: 50px; background: #FF69B4; border-radius: 50%; margin: 0 auto; animation: pulse 2s infinite;'></div>
                <p style='color: white;'>+{mission['pt']}ポイント獲得！</p>
            </div>
            """, unsafe_allow_html=True)

# 進行状況ゲージ表示
progress = min(st.session_state.battle_pass["points"] / 500 * 100, 100)
gauge_color = "linear-gradient(#FFD700, #FF69B4)" if st.session_state.battle_pass["premium"] else "#FF69B4"
st.markdown(f"### 現在のバトルパスポイント：{st.session_state.battle_pass['points']}pt")
st.markdown(f"""
<div style='width: 100%; height: 20px; background: #E0E0E0; border-radius: 10px; overflow: hidden;'>
    <div style='width: {progress}%; height: 100%; background: {gauge_color}; animation: grow 1s ease;'></div>
</div>
<style>
@keyframes grow {{
    0% {{ width: 0%; }}
    100% {{ width: {progress}%; }}
}}
@keyframes pulse {{
    0% {{ transform: scale(1); box-shadow: 0 0 5px #FF69B4; }}
    50% {{ transform: scale(1.05); box-shadow: 0 0 15px #FFD700; }}
    100% {{ transform: scale(1); box-shadow: 0 0 5px #FF69B4; }}
}}
</style>
""", unsafe_allow_html=True)

# 報酬表示
if st.session_state.battle_pass["points"] >= 100:
    if "背景NFT（虹）" not in st.session_state.battle_pass["rewards"]:
        st.session_state.battle_pass["rewards"].append("背景NFT（虹）")
    st.markdown("**✅ 報酬：背景NFT（虹）獲得！**")
if st.session_state.battle_pass["points"] >= 300 and st.session_state.battle_pass["premium"]:
    if "SSR NFT + 限定ボイス + 演出" not in st.session_state.battle_pass["rewards"]:
        st.session_state.battle_pass["rewards"].append("SSR NFT + 限定ボイス + 演出")
    st.markdown("**✅ プレミアム報酬：SSR NFT + 限定ボイス + 演出 開放！**")

# 獲得報酬一覧
st.markdown("### 獲得報酬")
for reward in st.session_state.battle_pass["rewards"]:
    st.markdown(f"- {reward}")
