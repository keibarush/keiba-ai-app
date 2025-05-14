# バトルパスチャレンジ（ステップ㉓）
elif menu == "バトルパスチャレンジ":
    # ミッションCSV（ソロフリーランス向け）
    missions_df = pd.DataFrame([
        {"id": "M1", "label": "3日連続ログイン", "points": 10, "premium_reward": "プレミアム称号「ログインスター」（金＋虹）", "category": "無料", "type": "daily"},
        {"id": "M2", "label": "推し馬に10HEART投票", "points": 15, "premium_reward": "限定演出（背景：応援ペンライト＋金ハート）", "category": "無料", "type": "cheer"},
        {"id": "M3", "label": "コメント5回投稿", "points": 10, "premium_reward": "「応援マスター」バッジ（銀＋虹）", "category": "無料", "type": "community"},
        {"id": "M10", "label": "ガチャでウルトラレア獲得", "points": 30, "premium_reward": "ウルトラSSR NFT（特別AR演出付き）", "category": "無料", "type": "gacha"},
        {"id": "M15", "label": "レース的中（3回以上）", "points": 20, "premium_reward": "限定ボイス（声優ナレーション）", "category": "無料", "type": "race"},
        {"id": "M20", "label": "コミュニティで全員500コメント達成", "points": 50, "premium_reward": "コミュニティ限定NFT（団結の証）", "category": "無料", "type": "community"},
        {"id": "M30", "label": "推し馬に50HEART投票（パーソナライズ）", "points": 80, "premium_reward": "パーソナライズ背景（推し馬テーマ）", "category": "プレミアム", "type": "cheer"},
        {"id": "M40", "label": "連勝応援（5連勝）", "points": 120, "premium_reward": "プレミアム専用ガチャチケット（SSR確定）＋限定AR", "category": "プレミアム", "type": "race"},
        {"id": "M50", "label": "商品購入（1回以上）", "points": 50, "premium_reward": "限定演出（金色フラッシュ＋虹色ハート）", "category": "無料", "type": "purchase"}
    ])

    # バトルパス状態管理
    if "battle_pass" not in st.session_state:
        st.session_state.battle_pass = {
            "points": 0,
            "missions": {row["id"]: {"done": False, "label": row["label"], "pt": row["points"], "premium_reward": row["premium_reward"], "category": row["category"], "type": row["type"]} for _, row in missions_df.iterrows()},
            "premium": False,
            "rewards": [],
            "season": "2025-05",  # シーズン管理
            "push_horse": None,  # パーソナライズ用
            "notifications": []  # リアルタイム通知
        }

    # シーズンリセット（月末）
    current_month = datetime.now().strftime("%Y-%m")
    if st.session_state.battle_pass["season"] != current_month:
        st.session_state.battle_pass["points"] = 0
        st.session_state.battle_pass["missions"] = {row["id"]: {"done": False, "label": row["label"], "pt": row["points"], "premium_reward": row["premium_reward"], "category": row["category"], "type": row["type"]} for _, row in missions_df.iterrows()}
        st.session_state.battle_pass["rewards"].append("シーズン達成バッジ（無料）")
        if st.session_state.battle_pass["premium"]:
            st.session_state.battle_pass["rewards"].append("シーズン達成NFT（プレミアム）")
        st.session_state.battle_pass["season"] = current_month

    # プレミアム加入チェック
    st.session_state.battle_pass["premium"] = st.checkbox("プレミアムパス加入者（500円/月）")

    # パーソナライズミッション設定
    if not st.session_state.battle_pass["push_horse"]:
        st.session_state.battle_pass["push_horse"] = st.selectbox("推し馬を選択（パーソナライズミッション用）", [f"馬番{i}" for i in range(1, 11)], key="push_horse")
        if st.session_state.battle_pass["push_horse"]:
            for key, mission in st.session_state.battle_pass["missions"].items():
                if mission["type"] == "cheer" and "パーソナライズ" in mission["label"]:
                    mission["label"] = f"{st.session_state.battle_pass['push_horse']}に50HEART投票（パーソナライズ）"

    # ミッション表示
    st.title("【VibeCore】バトルパス")
    st.markdown(f"**シーズン：{st.session_state.battle_pass['season']}**")
    for key, mission in st.session_state.battle_pass["missions"].items():
        if not mission["done"] and (mission["category"] == "無料" or st.session_state.battle_pass["premium"]):
            if st.button(f"ミッション達成：{mission['label']}（{mission['pt']}pt）", key=key):
                st.session_state.battle_pass["missions"][key]["done"] = True
                st.session_state.battle_pass["points"] += mission["pt"]
                if st.session_state.battle_pass["premium"]:
                    st.session_state.battle_pass["rewards"].append(mission["premium_reward"])
                st.session_state.battle_pass["notifications"].append(f"ミッション達成：{mission['label']}（+{mission['pt']}pt）")
                st.markdown(f"""
                <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
                    <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 ミッション達成！ 🎉</h4>
                    <div style='width: 50px; height: 50px; background: #FF69B4; border-radius: 50%; margin: 0 auto; animation: pulse 2s infinite;'></div>
                    <p style='color: white;'>+{mission['pt']}ポイント獲得！</p>
                    <audio src="fanfare.mp3" autoplay style="display: none;"></audio>
                </div>
                """, unsafe_allow_html=True)

    # リアルタイム通知
    st.markdown("### 通知")
    for notification in st.session_state.battle_pass["notifications"][-3:]:
        st.markdown(f"- {notification}（{datetime.now().strftime('%H:%M:%S')}）")

    # 進行状況可視化
    progress = min(st.session_state.battle_pass["points"] / 500 * 100, 100)  # 最大500ptで100%
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
    </style>
    """, unsafe_allow_html=True)

    # 報酬表示（パーソナライズ対応）
    if st.session_state.battle_pass["points"] >= 100:
        reward = f"背景NFT（{st.session_state.battle_pass['push_horse']}テーマ）" if st.session_state.battle_pass["premium"] else "背景NFT（虹）"
        if reward not in st.session_state.battle_pass["rewards"]:
            st.session_state.battle_pass["rewards"].append(reward)
        st.markdown(f"**✅ 報酬：{reward}獲得！**")
    if st.session_state.battle_pass["points"] >= 300 and st.session_state.battle_pass["premium"]:
        reward = "SSR NFT + 限定ボイス + 演出"
        if reward not in st.session_state.battle_pass["rewards"]:
            st.session_state.battle_pass["rewards"].append(reward)
        st.markdown(f"**✅ プレミアム報酬：{reward} 開放！**")

    # 獲得報酬一覧
    st.markdown("### 獲得報酬")
    for reward in st.session_state.battle_pass["rewards"]:
        st.markdown(f"- {reward}")
