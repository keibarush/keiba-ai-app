import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# 商品情報（CSV読み込みまたは直書き）
try:
    products_df = pd.read_csv("products.csv")
except FileNotFoundError:
    products = [
        {"カテゴリ": "おすすめ", "プラン": "ライトプラン", "価格": "100円/月", "特典": "50HEART/月、ピンクペンライト演出", "リンク": "https://buy.stripe.com/test_sub_light", "人気度": 80, "おすすめ": True},
        {"カテゴリ": "サブスク", "プラン": "ライトプラン", "価格": "100円/月", "特典": "50HEART/月、ピンクペンライト演出", "リンク": "https://buy.stripe.com/test_sub_light", "人気度": 80, "おすすめ": True},
        {"カテゴリ": "サブスク", "プラン": "スタンダードプラン", "価格": "500円/月", "特典": "200HEART/月、虹色背景、限定ボイス", "リンク": "https://buy.stripe.com/test_sub_standard", "人気度": 90, "おすすめ": False},
        {"カテゴリ": "サブスク", "プラン": "VIPプラン", "価格": "1000円/月", "特典": "500HEART/月、AR応援、SSR NFT", "リンク": "https://buy.stripe.com/test_sub_vip", "人気度": 95, "おすすめ": True},
        {"カテゴリ": "HEART", "プラン": "100HEART", "価格": "500円", "特典": "+10HEARTボーナス", "リンク": "https://buy.stripe.com/test_heart_100", "人気度": 70, "おすすめ": False},
        {"カテゴリ": "HEART", "プラン": "500HEART", "価格": "2500円", "特典": "+50HEARTボーナス", "リンク": "https://buy.stripe.com/test_heart_500", "人気度": 85, "おすすめ": True},
        {"カテゴリ": "NFT", "プラン": "限定背景NFT", "価格": "1000円", "特典": "虹色背景/推し馬テーマ", "リンク": "https://buy.stripe.com/test_nft_single", "人気度": 75, "おすすめ": False},
        {"カテゴリ": "NFT", "プラン": "ガチャ10連", "価格": "1000円", "特典": "SSR確率10％/ウルトラ演出付き", "リンク": "https://buy.stripe.com/test_nft_gacha", "人気度": 90, "おすすめ": True},
        {"カテゴリ": "イベント", "プラン": "レース応援パック", "価格": "2000円（期間限定）", "特典": "500HEART＋限定NFT（レーステーマ）", "リンク": "https://buy.stripe.com/test_event_pack", "人気度": 95, "おすすめ": True, "限定": True}
    ]
    products_df = pd.DataFrame(products)

# ユーザー状態（ダミー）
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "push_horse": None,
        "purchases": [],
        "premium": False
    }

# 推し馬選択（パーソナライズ用）
if not st.session_state.user_data["push_horse"]:
    st.session_state.user_data["push_horse"] = st.selectbox("推し馬を選択（おすすめ商品用）", [f"馬番{i}" for i in range(1, 11)], key="push_horse_select")

# 期間限定キャンペーン
campaign_end = datetime(2025, 5, 20, 23, 59)
remaining_time = (campaign_end - datetime.now()).total_seconds()
if remaining_time > 0:
    hours, remainder = divmod(remaining_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    st.markdown(f"""
    <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
        <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 期間限定キャンペーン！ 🎉</h4>
        <p style='color: white;'>今だけHEART2倍！残り時間：{int(hours)}時間{int(minutes)}分{int(seconds)}秒</p>
    </div>
    """, unsafe_allow_html=True)

# UI表示
st.title("【VibeCore】商品一覧と購入ページ")

# おすすめ商品
st.markdown("## おすすめ商品")
recommended = products_df[products_df["おすすめ"] == True]
if st.session_state.user_data["push_horse"]:
    push_horse = st.session_state.user_data["push_horse"]
    recommended = recommended.append(pd.DataFrame([{
        "カテゴリ": "おすすめ",
        "プラン": f"{push_horse}限定背景NFT",
        "価格": "1000円",
        "特典": f"{push_horse}をテーマにした虹色背景",
        "リンク": "https://buy.stripe.com/test_nft_single",
        "人気度": 90,
        "おすすめ": True
    }]))
for _, row in recommended.iterrows():
    with st.container():
        st.markdown(f"""
        <div style='padding: 12px; background: #FFFACD; border-radius: 12px; margin-bottom: 8px;'>
            <p style='font-weight: bold; color: #333;'>{row['プラン']}</p>
            <p style='color: #666;'><b>価格：</b>{row['価格']}</p>
            <p style='color: #666;'><b>特典：</b>{row['特典']}</p>
            <p style='color: #FF69B4;'><b>人気度：</b>{row['人気度']}/100 {'⏳ 期間限定！' if '限定' in row and row['限定'] else ''}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("特典プレビュー", key=f"preview_{row['プラン']}"):
            st.markdown(f"""
            <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
                <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 特典プレビュー 🎉</h4>
                <div style='width: 100px; height: 100px; background: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet); border-radius: 50%; margin: 0 auto; animation: shine 2s infinite;'></div>
                <p style='color: white;'>{row['特典']}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"""
        <a href="{row['リンク']}" target="_blank">
            <button style='background: linear-gradient(#FFD700, #FF69B4); color: white; border: none; padding: 1em 2em; border-radius: 8px; font-size: 18px; animation: pulse 2s infinite;'>
                購入する！
            </button>
        </a>
        """, unsafe_allow_html=True)
        st.divider()

# カテゴリ選択（タブ形式）
st.markdown("## 全商品一覧")
tabs = st.tabs(["サブスク", "HEART", "NFT", "イベント"])
categories = ["サブスク", "HEART", "NFT", "イベント"]

for tab, category in zip(tabs, categories):
    with tab:
        # フィルター
        price_filter = st.selectbox(f"{category}の価格帯を選択", ["すべて", "500円以下", "500〜2000円", "2000円以上"], key=f"price_filter_{category}")
        filtered = products_df[products_df["カテゴリ"] == category]
        if price_filter != "すべて":
            if price_filter == "500円以下":
                filtered = filtered[filtered["価格"].str.replace("円.*", "", regex=True).astype(int) <= 500]
            elif price_filter == "500〜2000円":
                filtered = filtered[(filtered["価格"].str.replace("円.*", "", regex=True).astype(int) > 500) & (filtered["価格"].str.replace("円.*", "", regex=True).astype(int) <= 2000)]
            else:
                filtered = filtered[filtered["価格"].str.replace("円.*", "", regex=True).astype(int) > 2000]

        # 商品表示
        for _, row in filtered.iterrows():
            with st.container():
                st.markdown(f"""
                <div style='padding: 12px; background: #FFFACD; border-radius: 12px; margin-bottom: 8px;'>
                    <p style='font-weight: bold; color: #333;'>{row['プラン']}</p>
                    <p style='color: #666;'><b>価格：</b>{row['価格']}</p>
                    <p style='color: #666;'><b>特典：</b>{row['特典']}</p>
                    <p style='color: #FF69B4;'><b>人気度：</b>{row['人気度']}/100 {'⏳ 期間限定！' if '限定' in row and row['限定'] else ''}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("特典プレビュー", key=f"preview_{row['プラン']}_{category}"):
                    st.markdown(f"""
                    <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
                        <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 特典プレビュー 🎉</h4>
                        <div style='width: 100px; height: 100px; background: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet); border-radius: 50%; margin: 0 auto; animation: shine 2s infinite;'></div>
                        <p style='color: white;'>{row['特典']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"""
                <a href="{row['リンク']}" target="_blank">
                    <button style='background: linear-gradient(#FFD700, #FF69B4); color: white; border: none; padding: 1em 2em; border-radius: 8px; font-size: 18px; animation: pulse 2s infinite;'>
                        購入する！
                    </button>
                </a>
                """, unsafe_allow_html=True)
                st.divider()

# CSSアニメーション
st.markdown("""
<style>
@keyframes pulse {
    0% { transform: scale(1); box-shadow: 0 0 5px #FF69B4; }
    50% { transform: scale(1.05); box-shadow: 0 0 15px #FFD700; }
    100% { transform: scale(1); box-shadow: 0 0 5px #FF69B4; }
}
@keyframes shine {
    0% { box-shadow: 0 0 5px #FFF; }
    50% { box-shadow: 0 0 20px #FFF; }
    100% { box-shadow: 0 0 5px #FFF; }
}
button:hover {
    transform: scale(1.1);
    transition: transform 0.3s;
}
</style>
""", unsafe_allow_html=True)
