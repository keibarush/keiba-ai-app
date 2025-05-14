import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# セッション状態の初期化
if "push_horse" not in st.session_state:
    st.session_state.push_horse = None
if "purchases" not in st.session_state:
    st.session_state.purchases = []
if "user_ratings" not in st.session_state:
    st.session_state.user_ratings = {}

# 商品データ（CSV読み込みを想定）
products_df = pd.DataFrame([
    {"カテゴリ": "サブスク", "プラン": "ライトプラン", "価格": "100円/月", "特典": "50HEART/月、ピンクペンライト演出", "バッジ": "ライト加入バッジ（桃）", "演出": "ピンク演出、ミニハート", "リンク": "https://buy.stripe.com/test_sub_light", "人気度": 85},
    {"カテゴリ": "サブスク", "プラン": "スタンダードプラン", "価格": "500円/月", "特典": "200HEART/月、虹色背景、限定ボイス", "バッジ": "スタンダードバッジ（銀）", "演出": "虹背景、ボイス再生", "リンク": "https://buy.stripe.com/test_sub_standard", "人気度": 90},
    {"カテゴリ": "サブスク", "プラン": "VIPプラン", "価格": "1000円/月", "特典": "500HEART/月、AR演出、プレミアムNFT", "バッジ": "VIPバッジ（金＋虹）", "演出": "花冠AR、金スパーク", "リンク": "https://buy.stripe.com/test_sub_vip", "人気度": 95},
    {"カテゴリ": "HEART", "プラン": "100HEARTパック", "価格": "500円", "特典": "100HEART＋初回ボーナス10HEART", "バッジ": "初回購入バッジ（桃）", "演出": "金ハートが降る", "リンク": "https://buy.stripe.com/test_heart_100", "人気度": 80},
    {"カテゴリ": "HEART", "プラン": "500HEARTパック", "価格": "2500円", "特典": "500HEART＋ボーナス50HEART", "バッジ": "銀ハートバッジ", "演出": "ハートシャワー（中）", "リンク": "https://buy.stripe.com/test_heart_500", "人気度": 88},
    {"カテゴリ": "NFT", "プラン": "限定背景NFT", "価格": "1000円", "特典": "虹色背景、推し馬テーマ", "バッジ": "NFTコレクター（銀）", "演出": "獲得時に虹色フラッシュ", "リンク": "https://buy.stripe.com/test_nft_single", "人気度": 92},
    {"カテゴリ": "NFT", "プラン": "ガチャ10連", "価格": "1000円", "特典": "コモン～ウルトラレアNFT（レア以上1枚保証）", "バッジ": "ガチャ勇者（虹）", "演出": "スロット演出＋いななきSE", "リンク": "https://buy.stripe.com/test_nft_gacha", "人気度": 90},
    {"カテゴリ": "イベント", "プラン": "レース応援パック", "価格": "2000円（期間限定）", "特典": "500HEART＋限定NFT（レーステーマ）", "バッジ": "レースヒーロー（金＋虹）", "演出": "金色フラッシュ、馬の歓喜SE", "リンク": "https://buy.stripe.com/test_event_pack", "人気度": 87}
])

# UI表示
st.title("【VibeCore】商品一覧と購入ページ")

# 期間限定キャンペーン
campaign_end = datetime(2025, 5, 22, 23, 59)
time_left = campaign_end - datetime(2025, 5, 15, 1, 47)  # 現在の日時を固定
if time_left.total_seconds() > 0:
    st.markdown(f"""
    <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
        <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 今週限定キャンペーン！ 🎉</h4>
        <p style='color: white;'>HEART500パック購入で＋100HEARTボーナス！残り：<span style='color: red;'>{int(time_left.total_seconds() // 3600)}時間</span></p>
    </div>
    """, unsafe_allow_html=True)

# パーソナライズ推奨
if not st.session_state.push_horse:
    st.session_state.push_horse = st.selectbox("推し馬を選択（パーソナライズ推奨用）", [f"馬番{i}" for i in range(1, 11)], key="push_horse_select")

if st.session_state.push_horse:
    # recommended の初期化（空のDataFrame）
    recommended = pd.DataFrame(columns=["カテゴリ", "プラン", "価格", "特典", "バッジ", "演出", "リンク", "人気度", "おすすめ"])
    # パーソナライズ推奨商品を追加（append を pd.concat に変更）
    recommended = pd.concat([
        recommended,
        pd.DataFrame([{
            "カテゴリ": "おすすめ",
            "プラン": f"{st.session_state.push_horse}限定背景NFT",
            "価格": "1000円",
            "特典": f"{st.session_state.push_horse}をテーマにした虹色背景",
            "バッジ": "NFTコレクター（銀）",
            "演出": "獲得時に虹色フラッシュ",
            "リンク": "https://buy.stripe.com/test_nft_single",
            "人気度": 90,
            "おすすめ": True
        }])
    ], ignore_index=True)

    # リピート推奨（購入履歴に基づく）
    if st.session_state.purchases:
        last_purchase = st.session_state.purchases[-1]
        if "HEART" in last_purchase:
            recommended = pd.concat([
                recommended,
                pd.DataFrame([{
                    "カテゴリ": "おすすめ",
                    "プラン": "VIPプラン",
                    "価格": "1000円/月",
                    "特典": "500HEART/月、AR演出、プレミアムNFT、再購入特典：＋20HEART",
                    "バッジ": "VIPバッジ（金＋虹）",
                    "演出": "花冠AR、金スパーク",
                    "リンク": "https://buy.stripe.com/test_sub_vip",
                    "人気度": 95,
                    "おすすめ": True
                }])
            ], ignore_index=True)

    st.markdown("## あなたにおすすめの商品")
    for _, row in recommended.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div style='padding: 12px; background: #FFFACD; border: 2px solid #FFD700; border-radius: 12px; margin-bottom: 12px;'>
                    <h4 style='color: #333;'>{row['プラン']}（{row['価格']}）<span style='color: gold; font-size: 12px; margin-left: 8px;'>あなたにおすすめ</span></h4>
                    <p style='color: #666;'>{row['特典']}</p>
                    <p style='color: #666;'><b>バッジ：</b>{row['バッジ']}</p>
                    <p style='color: #666;'><b>演出：</b>{row['演出']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <a href="{row['リンク']}" target="_blank">
                    <button style='background: linear-gradient(#FFD700, #FF69B4); color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; animation: pulse 2s infinite; margin-top: 20px;'>
                        購入する
                    </button>
                </a>
                """, unsafe_allow_html=True)

# カテゴリ選択（タブ形式）
tabs = st.tabs(["サブスク", "HEART", "NFT", "イベント"])
for tab, category in zip(tabs, ["サブスク", "HEART", "NFT", "イベント"]):
    with tab:
        filtered = products_df[products_df["カテゴリ"] == category]
        for _, row in filtered.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    popularity = row["人気度"]
                    stars = "★" * int(popularity // 20) + "☆" * (5 - int(popularity // 20))
                    rating_key = f"rating_{row['プラン']}"
                    user_rating = st.session_state.user_ratings.get(rating_key, 0)
                    user_comment = st.session_state.user_ratings.get(f"comment_{row['プラン']}", "")
                    if user_rating == 0 and st.session_state.purchases and any(row['プラン'] in p for p in st.session_state.purchases):
                        user_rating = st.slider(f"{row['プラン']}の評価（星1〜5）", 1, 5, key=f"rate_{row['プラン']}")
                        user_comment = st.text_input(f"{row['プラン']}のコメント", key=f"comment_{row['プラン']}")
                        if st.button("評価を投稿", key=f"submit_{row['プラン']}"):
                            st.session_state.user_ratings[rating_key] = user_rating
                            st.session_state.user_ratings[f"comment_{row['プラン']}"] = user_comment
                            st.success("評価が投稿されました！")

                    st.markdown(f"""
                    <div style='padding: 12px; background: #FFFACD; border-radius: 12px; margin-bottom: 12px; transition: transform 0.3s;'>
                        <h4 style='color: #333;'>{row['プラン']}（{row['価格']}) {f'<span style="color: gold; font-size: 12px;">人気！</span>' if popularity >= 90 else ''}</h4>
                        <p style='color: #666;'>{row['特典']}</p>
                        <p style='color: #666;'><b>バッジ：</b>{row['バッジ']}</p>
                        <p style='color: #666;'><b>演出：</b>{row['演出']}</p>
                        <p style='color: #666;'><b>人気度：</b>{stars} ({popularity})</p>
                        <p style='color: #666;'><b>ユーザー評価：</b>{'★' * user_rating + '☆' * (5 - user_rating)} ({user_comment})</p>
                    </div>
                    <style>
                    div:hover {{
                        transform: scale(1.02);
                        box-shadow: 0 0 10px #FFD700;
                    }}
                    </style>
                    """, unsafe_allow_html=True)
                    if st.button("特典プレビュー", key=f"preview_{row['プラン']}"):
                        st.markdown(f"""
                        <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
                            <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>特典プレビュー</h4>
                            <div style='width: 100px; height: 100px; background: {'linear-gradient(#FFD700, #FF69B4)' if st.session_state.battle_pass['premium'] else '#FF69B4'}; border-radius: 50%; margin: 0 auto; animation: pulse 2s infinite;'></div>
                            <p style='color: white;'>{row['演出']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <a href="{row['リンク']}" target="_blank">
                        <button style='background: linear-gradient(#FFD700, #FF69B4); color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; animation: pulse 2s infinite; margin-top: 20px;'>
                            購入する
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                st.divider()

# 購入履歴とリピート推奨
st.markdown("## 購入履歴")
if st.session_state.purchases:
    for purchase in st.session_state.purchases:
        st.markdown(f"- {purchase}（{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）")
else:
    st.markdown("まだ購入履歴はありません。")

# CSSアニメーション（レスポンシブ対応）
st.markdown("""
<style>
@keyframes pulse {
    0% { transform: scale(1); box-shadow: 0 0 5px #FF69B4; }
    50% { transform: scale(1.05); box-shadow: 0 0 15px #FFD700; }
    100% { transform: scale(1); box-shadow: 0 0 5px #FF69B4; }
}
button:hover {
    transform: scale(1.1);
    transition: transform 0.3s;
}
@media (max-width: 600px) {
    button {
        padding: 12px 24px;
        font-size: 14px;
    }
    div[style*="padding: 12px"] {
        padding: 8px;
    }
}
</style>
""", unsafe_allow_html=True)
