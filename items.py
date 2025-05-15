# items.py
import streamlit as st

def display_items():
    st.markdown("### 商品一覧")
    items = [
        {"name": "100 HEARTパック", "price": 500, "description": "100 HEARTをチャージできます。"},
        {"name": "プレミアムパス", "price": 500, "description": "バトルパスのプレミアム報酬をアンロック！"},
        {"name": "限定NFT", "price": 1000, "description": "特別な背景NFTを獲得できます。"},
    ]
    for item in items:
        st.markdown(f"""
        <div style='padding: 12px; background: #FFFACD; border-radius: 12px; margin-bottom: 8px;'>
            <h5 style='margin-bottom: 4px;'>{item['name']}（{item['price']}円）</h5>
            <p style='color: #666;'>{item['description']}</p>
        </div>
        """, unsafe_allow_html=True)
