import streamlit as st

st.title("商品一覧｜VibeCoreショップ")

# 商品リスト（サンプル）
products = [
    {"カテゴリ": "サブスク", "商品名": "ライトプラン（100円/月）", "内容": "月50HEART＋限定演出", "リンク": "https://buy.stripe.com/test_lite"},
    {"カテゴリ": "サブスク", "商品名": "スタンダードプラン（500円/月）", "内容": "月200HEART＋背景＋限定ボイス", "リンク": "https://buy.stripe.com/test_std"},
    {"カテゴリ": "サブスク", "商品名": "VIPプラン（1000円/月）", "内容": "月500HEART＋AR演出＋プレミアムNFT", "リンク": "https://buy.stripe.com/test_vip"},
    {"カテゴリ": "HEART", "商品名": "100HEART（500円）", "内容": "初回＋10HEARTボーナス", "リンク": "https://buy.stripe.com/test_heart100"},
    {"カテゴリ": "HEART", "商品名": "500HEART（2500円）", "内容": "＋50HEARTボーナス", "リンク": "https://buy.stripe.com/test_heart500"},
    {"カテゴリ": "NFT", "商品名": "背景NFT（1000円）", "内容": "虹色演出の限定背景", "リンク": "https://buy.stripe.com/test_nft1"},
    {"カテゴリ": "ガチャ", "商品名": "ガチャ10連（1000円）", "内容": "SSR確率10％＋最低レア保証", "リンク": "https://buy.stripe.com/test_gacha10"}
]

# 表示
for p in products:
    st.markdown(f"### {p['商品名']}（{p['カテゴリ']}）")
    st.markdown(f"- 内容：{p['内容']}")
    st.link_button("今すぐ購入", p["リンク"], use_container_width=True)
    st.markdown("---")
