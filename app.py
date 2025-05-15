import streamlit as st
import pandas as pd
import json
import os
import glob
import random
from datetime import datetime
import sqlite3
import plotly.express as px
import logging
from dotenv import load_dotenv
import predictions
import payments
import 商品一覧 as items

# ログ設定
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# 環境変数
load_dotenv()
required_env = ["STRIPE_API_KEY", "WEBHOOK_SECRET", "SUCCESS_URL", "CANCEL_URL"]
for env_var in required_env:
    if not os.getenv(env_var):
        st.error(f"環境変数 {env_var} が設定されていません")
        st.stop()
SUCCESS_URL = os.getenv("SUCCESS_URL")
CANCEL_URL = os.getenv("CANCEL_URL")

# CSS
with open("styles.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ページ設定
st.set_page_config(page_title="VibeCore", layout="wide")

# ダークモード
theme = st.sidebar.selectbox("テーマ", ["ライト", "ダーク"], key="theme_select")
if theme == "ダーク":
    st.markdown('<script>document.body.classList.add("dark-mode");</script>', unsafe_allow_html=True)

# セッション状態初期化
def init_session_state():
    defaults = {
        "checked_horses": json.load(open("checked_horses.json", "r")) if os.path.exists("checked_horses.json") else [],
        "heart_balance": 200,
        "heart_history": [],
        "nft_inventory": [],
        "subscription_status": None,
        "payment_history": [],
        "battle_pass": {
            "points": 0,
            "missions": {},
            "premium": False,
            "rewards": [],
            "season": "2025-05",
            "push_horse": None
        },
        "forecasts": {},
        "votes": {},
        "user_settings": {"accuracy": 0.5, "emotion": 0.5, "style": "balanced"},
        "user_ratings": {},
        "purchases": [],
        "last_login": None,
        "user_goals": {"vote_goal": 0}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# データベース初期化
def init_db():
    conn = sqlite3.connect("vibecore.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS votes (horse TEXT, count INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS forecasts (id TEXT, user_id TEXT, comment TEXT, hearts INTEGER, timestamp TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS heart_history (action TEXT, amount INTEGER, timestamp TEXT)")
    conn.commit()
    conn.close()

init_db()

# ログインボーナス
today = datetime.now().date().isoformat()
if st.session_state.last_login != today:
    st.session_state.heart_balance += 1
    st.session_state.heart_history.append({
        "action": "ログインボーナス",
        "amount": 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    st.session_state.last_login = today

# サプライズ報酬
if random.random() < 0.05:
    st.session_state.heart_balance += 10
    st.session_state.heart_history.append({
        "action": "サプライズ報酬",
        "amount": 10,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    st.sidebar.markdown("🎉 サプライズ！10 HEART獲得！")

# サイドバー
st.sidebar.markdown(f"**HEART残高：{st.session_state.heart_balance} HEART**")
menu = st.sidebar.radio("機能を選択してください", [
    "AI競馬予測",
    "Stripe決済（サブスク／HEART／NFT）",
    "予想師コミュニティ",
    "バトルパスチャレンジ",
    "商品一覧",
    "HEART残高と履歴",
    "NFTコレクション",
    "管理ダッシュボード"
], key="menu_select_internal")

# ユーザーカスタム設定
st.sidebar.markdown("## ユーザーカスタム設定")
st.session_state.user_settings["accuracy"] = st.sidebar.slider("予測精度（的中重視/穴重視）", 0.0, 1.0, 0.5)
st.sidebar.markdown("""
<div class="tooltip">予測精度とは？
    <span class="tooltiptext">的中率を重視するか、穴馬を優先するか調整</span>
</div>
""", unsafe_allow_html=True)
st.session_state.user_settings["emotion"] = st.sidebar.slider("感情係数（推し指数重視）", 0.0, 1.0, 0.5)
style_options = ["保守的", "バランス", "攻撃的"]
st.session_state.user_settings["style"] = st.sidebar.selectbox("補正スタイル", style_options, index=style_options.index("バランス"))
st.sidebar.markdown("## 週間目標")
goal = st.sidebar.selectbox("今週の投票目標", [0, 5, 10], key="vote_goal")
st.session_state.user_goals = {"vote_goal": goal}
if len(st.session_state.votes) >= goal:
    st.sidebar.markdown("🎉 目標達成！")

# メニュー検索
search_query = st.sidebar.text_input("メニュー内検索", placeholder="機能名を入力（例：AI競馬予測）")
if search_query:
    filtered_menu = [m for m in ["AI競馬予測", "Stripe決済（サブスク／HEART／NFT）", "予想師コミュニティ", "バトルパスチャレンジ", "商品一覧", "HEART残高と履歴", "NFTコレクション", "管理ダッシュボード"] if search_query.lower() in m.lower()]
    if filtered_menu:
        st.session_state["menu_select_internal"] = filtered_menu[0]
        st.experimental_rerun()
    else:
        st.sidebar.warning("該当するメニューが見つかりません。")

# アクティビティ通知
st.sidebar.markdown("## アクティビティ通知")
if st.session_state.battle_pass["points"] >= 100:
    st.sidebar.markdown(f"🎉 バトルパスポイントが100pt達成！報酬を確認してください。")
if st.session_state.votes:
    total_votes = sum(st.session_state.votes.values())
    st.sidebar.markdown(f"📊 現在の総投票数：{total_votes}票")
if not st.session_state.battle_pass["premium"]:
    if st.sidebar.button("広告を見て10 HEART獲得"):
        st.session_state.heart_balance += 10
        st.session_state.heart_history.append({
            "action": "広告視聴",
            "amount": 10,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.sidebar.success("10 HEART獲得！")

# クイックアクセス
st.sidebar.markdown("## クイックアクセス")
with st.sidebar.expander("クイックアクセス"):
    if st.button("バトルパス進捗を確認", key="quick_battle_pass"):
        st.session_state["menu_select_internal"] = "バトルパスチャレンジ"
        st.experimental_rerun()
    if st.session_state.purchases:
        if st.button("最近の購入履歴を確認", key="quick_purchases"):
            st.session_state["menu_select_internal"] = "Stripe決済（サブスク／HEART／NFT）"
            st.experimental_rerun()

# 友達招待
st.sidebar.markdown("## 友達招待")
referral_code = st.sidebar.text_input("招待コードを入力", key="referral_code")
if referral_code:
    st.session_state.heart_balance += 50
    st.session_state.heart_history.append({
        "action": "招待ボーナス",
        "amount": 50,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    st.sidebar.success("50 HEART獲得！")

# メニュー選択演出
if menu:
    st.markdown(f"""
    <div style='text-align: center; padding: 8px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px; animation: fadeIn 0.5s;'>
        <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>選択中：{menu}</h4>
    </div>
    """, unsafe_allow_html=True)

# AI競馬予測
if menu == "AI競馬予測":
    st.markdown("**勝利の鼓動 × 勝ちの直感スコア**：勝率とオッズを基に、ユーザーの設定（精度/感情/スタイル）で調整された総合評価。スコアが高いほど期待値が高い馬です。")
    st.markdown("### 勝率またはオッズファイルをアップロード（JSON形式）")
    uploaded_file = st.file_uploader("アップロードしてください（例：win_20250515_monbetsu.json）", type=["json"])
    try:
        if uploaded_file is not None:
            filename = uploaded_file.name
            if filename.startswith(("win_", "odds_")) and filename.endswith(".json"):
                save_path = os.path.join(".", filename)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"{filename} をアップロードしました")
            else:
                raise ValueError("ファイル名が不正です")
    except Exception as e:
        logging.error(f"ファイルアップロードエラー: {str(e)}")
        st.error(f"アップロード中にエラーが発生しました：{str(e)}")

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
            try:
                with open(win_path, encoding="utf-8") as f:
                    win_probs = json.load(f)
                predictions.validate_json(win_probs, ["horse", "prob"])
                with open(odds_path, encoding="utf-8") as f:
                    odds_data = json.load(f)
                predictions.validate_json(odds_data, ["horse", "odds"])
            except Exception as e:
                st.error(f"JSONファイルの読み込みに失敗しました：{str(e)}")
                win_probs = odds_data = []

            def get(entry, *keys):
                for key in keys:
                    if key in entry:
                        return entry[key]
                return None

            odds_dict = predictions.fetch_real_time_odds(selected_race)
            if not odds_dict:
                odds_dict = {get(item, "horse", "馬番"): item["odds"] for item in odds_data}
            rows = []
            for entry in win_probs:
                horse = get(entry, "horse", "馬番")
                prob = get(entry, "prob", "勝率")
                odds = odds_dict.get(horse)

                adjusted_prob = 0
                if prob is not None:
                    prob = predictions.apply_weather_factor(prob, {"馬場": race_info["馬場"], "展開": pace})
                    prob = predictions.advanced_model_predict(horse, {"race_id": selected_race})
                    adjusted_prob = prob * (1 - st.session_state.user_settings["accuracy"]) + prob * st.session_state.user_settings["emotion"]
                    adjusted_prob += predictions.custom_model_adjustment(st.session_state.votes, horse)
                    if st.session_state.user_settings["style"] == "保守的":
                        adjusted_prob *= 0.9
                    elif st.session_state.user_settings["style"] == "攻撃的":
                        adjusted_prob *= 1.1

                if odds and adjusted_prob is not None:
                    if odds > 1.0:
                        score = predictions.calculate_score(adjusted_prob, odds, st.session_state.user_settings)
                    else:
                        score = 0.0
                else:
                    score = 0.0

                pace, track_bias, bias_score = predictions.get_pace_and_bias(horse)
                bias_color = "green" if bias_score >= 70 else "red" if bias_score < 30 else "yellow"
                push_index = random.uniform(50, 100)
                rank = "本命安定圏" if score >= 50 else "複勝安定圏" if score >= 30 else "オッズ妙味圏" if score >= 10 else "検討外・回避圏"

                rows.append({
                    "馬番": horse,
                    "勝率（％）": round(adjusted_prob * 100, 1) if adjusted_prob is not None else None,
                    "オッズ": odds,
                    "推し指数": push_index,
                    "勝利の鼓動 × 勝ちの直感（％）": score,
                    "推し馬ランク": rank,
                    "展開": pace,
                    "馬場バイアス": f"{track_bias} ({bias_score:.1f})",
                    "バイアス色": bias_color
                })

            df = pd.DataFrame(rows)
            df = df.sort_values("勝利の鼓動 × 勝ちの直感（％）", ascending=False).reset_index(drop=True)

            st.markdown("### レース基本情報")
            race_info = {
                "日時": "2025年5月15日 02:30",
                "距離": "1200m",
                "馬場": "良" if random.random() > 0.5 else "重",
                "出走馬": len(df)
            }
            st.markdown(f"""
            - **日時**：{race_info['日時']}
            - **距離**：{race_info['距離']}
            - **馬場**：{race_info['馬場']} {'🌧️' if race_info['馬場'] == '重' else '☀️'}
            - **出走馬**：{race_info['出走馬']}頭
            """)
            st.markdown(f"**今日の注目ポイント**：{random.choice(['内枠有利', '外枠有利', '差し馬優勢'])}")

            st.markdown("### モバイル用ハイライト")
            top_horses = df.head(3)
            for idx, horse in top_horses.iterrows():
                symbol = "◎" if idx == 0 else "◯" if idx == 1 else "▲"
                win_chance = "A" if horse["勝利の鼓動 × 勝ちの直感（％）"] >= 50 else "B" if horse["勝利の鼓動 × 勝ちの直感（％）"] >= 30 else "C"
                st.markdown(f"{symbol} 馬番{horse['馬番']}（オッズ: {horse['オッズ']}倍、勝負度: {win_chance}）")

            st.markdown("### 要点サマリー＋前回比較")
            previous_df = df.copy()
            previous_df["勝利の鼓動 × 勝ちの直感（％）"] *= 0.9
            for _, row in df.head(3).iterrows():
                prev_score = previous_df[previous_df["馬番"] == row["馬番"]]["勝利の鼓動 × 勝ちの直感（％）"].values[0] if not previous_df[previous_df["馬番"] == row["馬番"]].empty else row["勝利の鼓動 × 勝ちの直感（％）"]
                diff = row["勝利の鼓動 × 勝ちの直感（％）"] - prev_score
                st.markdown(f"馬番{row['馬番']}：スコア {row['勝利の鼓動 × 勝ちの直感（％）']:.1f}（前回比：<span style='color: {'green' if diff >= 0 else 'red'}'>{'+' if diff >= 0 else ''}{diff:.1f}</span>）", unsafe_allow_html=True)

            st.markdown("### 推し馬チェック")
            current_check = st.multiselect(
                "気になる馬を選んでください（保持されます）",
                options=df["馬番"].tolist(),
                default=st.session_state.checked_horses
            )
            st.session_state.checked_horses = current_check
            with open("checked_horses.json", "w") as f:
                json.dump(st.session_state.checked_horses, f)

            def highlight_top_row(s):
                return ['background-color: #FFFACD; border: 2px solid gold' if s.name == 0 else '' for _ in s]
            st.dataframe(df.style.apply(highlight_top_row, axis=1), use_container_width=True)
            fig = px.bar(df, x="馬番", y="勝利の鼓動 × 勝ちの直感（％）", title="馬別スコア")
            st.plotly_chart(fig)

            sim_results = predictions.simulate_race(win_probs)
            st.markdown("### レースシミュレーション（1000回）")
            for horse, prob in sim_results.items():
                st.markdown(f"馬番{horse}：勝率 {prob:.1f}%")

            st.markdown("### あなたの“推し馬カード”")
            selected_df = df[df["馬番"].isin(st.session_state.checked_horses)]
            if selected_df.empty:
                st.info("推し馬を上から選ぶと、ここにカードが出てきます。")
            else:
                for _, row in selected_df.iterrows():
                    light = {"本命安定圏": "#FFD700", "複勝安定圏": "#ADFF2F", "オッズ妙味圏": "#FF69B4", "検討外・回避圏": "#CCC"}.get(row["推し馬ランク"], "#FFF")
                    st.markdown(f"""
                    <div style="border-left: 8px solid {light}; padding: 12px; border-radius: 12px; background-color: #FFFACD;">
                        <h5 style='margin-bottom:4px;'>【馬番 {row['馬番']}｜{row['推し馬ランク']}】</h5>
                        <p><b>勝率：</b>{row['勝率（％）']}％<br>
                        <b>推し指数：</b>{row['推し指数']}<br>
                        <b>オッズ：</b>{row['オッズ']} 倍<br>
                        <b>スコア：</b>{row['勝利の鼓動 × 勝ちの直感（％）']}％<br>
                        <b>展開：</b>{row['展開']}<br>
                        <b>馬場バイアス：</b><span style='color:{row['バイアス色']};'>{row['馬場バイアス']}</span><br>
                        <p>信頼度：±5%</p>
                        <p style='color: #666;'>ストーリー：過去2戦で急成長中の期待馬！</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(row["馬場バイアス"].split("(")[1].split(")")[0] / 100)

                    st.markdown(f"この馬に{st.session_state.votes.get(row['馬番'], 0)}人が投票！")
                    if st.button(f"{row['馬番']}に10HEARTで応援投票", key=f"vote_{row['馬番']}"):
                        if st.session_state.heart_balance >= 10:
                            st.session_state.heart_balance -= 10
                            conn = sqlite3.connect("vibecore.db")
                            c = conn.cursor()
                            c.execute("INSERT OR REPLACE INTO votes (horse, count) VALUES (?, ?)",
                                      (row['馬番'], st.session_state.votes.get(row['馬番'], 0) + 1))
                            c.execute("INSERT INTO heart_history (action, amount, timestamp) VALUES (?, ?, ?)",
                                      (f"投票（馬番{row['馬番']}）", -10, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                            conn.commit()
                            conn.close()
                            st.session_state.votes[row['馬番']] = st.session_state.votes.get(row['馬番'], 0) + 1
                            st.session_state.heart_history.append({
                                "action": f"投票（馬番{row['馬番']}）",
                                "amount": -10,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            st.markdown(f"""
                            <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
                                <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 投票ありがとう！ 🎉</h4>
                                <p class="heart-animation">❤️ 10 HEART</p>
                                <p style='color: white;'>現在の投票数：{st.session_state.votes.get(row['馬番'], 0)}</p>
                                <p style='color: white;'>HEART残高：{st.session_state.heart_balance}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error("HEARTが不足しています。商品一覧からチャージしてください。")
                            if st.button("HEARTをチャージ", key=f"charge_{row['馬番']}"):
                                st.session_state["menu_select_internal"] = "商品一覧"
                                st.experimental_rerun()

                    win_chance = "A" if row["勝利の鼓動 × 勝ちの直感（％）"] >= 50 else "B" if row["勝利の鼓動 × 勝ちの直感（％）"] >= 30 else "C"
                    decision = "買い" if win_chance in ["A", "B"] else "見送り"
                    st.markdown(f"**結論**：勝負度 {win_chance} | {decision} | 狙い馬：馬番{row['馬番']}")
                    if win_chance in ["A", "B"]:
                        st.markdown(f"**賭け方提案**：馬番{row['馬番']}の単勝または馬連（馬番{row['馬番']}-馬番{df.iloc[1]['馬番']}）")

                    share_comment = f"馬番{row['馬番']}を信じて勝つ！🏆 #VibeCore"
                    if st.button(f"Xでシェア", key=f"share_{row['馬番']}"):
                        st.markdown(f"""
                        <div style='text-align: center; padding: 12px; background: #FFFACD; border-radius: 12px;'>
                            <p style='color: #333;'>{share_comment}</p>
                            <p style='color: #666; font-size: 0.9em;'>※このボタンはシェアのプレビューです。本番ではXの共有APIを利用します。</p>
                        </div>
                        """, unsafe_allow_html=True)

# Stripe決済
elif menu == "Stripe決済（サブスク／HEART／NFT）":
    st.markdown("## プレミアム応援プラン")
    st.markdown("""
    **VIPプラン特典**：
    - 早期レースデータアクセス
    - 限定NFTドロップ
    - プレミアムサポート
    """)
    plan = st.radio("プランを選択", ["ライト（100円/月）", "スタンダード（500円/月）", "VIP（1000円/月）"])
    price_ids = {
        "ライト（100円/月）": "price_xxx",
        "スタンダード（500円/月）": "price_xxx",
        "VIP（1000円/月）": "price_xxx"
    }

    if st.button("サブスクに加入"):
        session = payments.create_checkout_session(
            plan,
            price_ids[plan],
            "subscription",
            {"user_id": "user_123", "type": "subscription", "plan": plan},
            SUCCESS_URL,
            CANCEL_URL
        )
        st.session_state.purchases.append(f"サブスク：{plan}")
        st.markdown(f"""
        <a href="{session.url}" target="_blank">
            <button style='background: linear-gradient(#FFD700, #FF69B4); color: white; border: none; padding: 1em 2em; border-radius: 8px; font-size: 16px;'>
                今すぐ加入する！
            </button>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("## HEARTトークン購入")
    heart_plan = st.radio("HEARTを選択", ["100HEART（500円）", "500HEART（2500円）"])
    heart_prices = {
        "100HEART（500円）": "price_xxx",
        "500HEART（2500円）": "price_xxx"
    }

    if st.button("HEARTを購入"):
        session = payments.create_checkout_session(
            heart_plan,
            heart_prices[heart_plan],
            "payment",
            {"user_id": "user_123", "type": "heart", "amount": heart_plan.split("（")[0]},
            SUCCESS_URL,
            CANCEL_URL
        )
        st.session_state.purchases.append(f"HEART購入：{heart_plan}")
        amount = int(heart_plan.split("HEART")[0])
        st.session_state.heart_balance += amount
        if datetime.now().month == 5:
            st.session_state.heart_balance += amount
            st.session_state.heart_history.append({
                "action": "イベントブースト",
                "amount": amount,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.markdown("🎉 イベントブースト！HEARTが2倍！")
        st.session_state.heart_history.append({
            "action": f"HEART購入（{heart_plan}）",
            "amount": amount,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.markdown(f"""
        <a href="{session.url}" target="_blank">
            <button style='background: linear-gradient(#FFD700, #FF69B4); color: white; border: none; padding: 1em 2em; border-radius: 8px; font-size: 16px;'>
                HEARTを購入する！
            </button>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("## ギフトカード購入")
    gift_amount = st.radio("ギフトカードを選択", ["500HEART（2500円）"])
    gift_prices = {"500HEART（2500円）": "price_xxx"}
    if st.button("ギフトカードを購入"):
        session = payments.create_checkout_session(
            "ギフトカード",
            gift_prices[gift_amount],
            "payment",
            {"user_id": "user_123", "type": "gift", "amount": gift_amount.split("（")[0]},
            SUCCESS_URL,
            CANCEL_URL
        )
        st.session_state.purchases.append(f"ギフトカード：{gift_amount}")
        st.markdown(f"<a href='{session.url}' target='_blank'>購入する</a>", unsafe_allow_html=True)

    st.markdown("## NFT購入・ガチャ")
    if random.random() < 0.9:
        st.markdown("<p style='color: red;'>残り10個！今すぐ購入を！</p>", unsafe_allow_html=True)
    if datetime.now().month == 5:
        st.markdown("<p style='color: green;'>シーズンセール！NFT 10%オフ！</p>", unsafe_allow_html=True)
    st.markdown("""
    ### ガチャ確率
    - ウルトラレア: 1%
    - レア: 10%
    - ノーマル: 89%
    """)
    nft_plan = st.radio("NFTを選択", ["限定背景NFT（1000円）", "ガチャ10連（1000円）"])
    nft_prices = {
        "限定背景NFT（1000円）": "price_xxx",
        "ガチャ10連（1000円）": "price_xxx"
    }

    if st.button("NFTを購入"):
        session = payments.create_checkout_session(
            nft_plan,
            nft_prices[nft_plan],
            "payment",
            {"user_id": "user_123", "type": "nft", "item": nft_plan},
            SUCCESS_URL,
            CANCEL_URL
        )
        st.session_state.purchases.append(f"NFT購入：{nft_plan}")
        rarity = "ウルトラレア" if "ガチャ" in nft_plan and random.random() > 0.9 else "レア"
        nft_item = {"name": f"{nft_plan}（{rarity}）", "rarity": rarity, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        st.session_state.nft_inventory.append(nft_item)
        st.markdown(f"""
        <a href="{session.url}" target="_blank">
            <button style='background: linear-gradient(#FFD700, #FF69B4); color: white; border: none; padding: 1em 2em; border-radius: 8px; font-size: 16px;'>
                NFTを購入する！
            </button>
        </a>
        """, unsafe_allow_html=True)

    if st.session_state.subscription_status:
        if st.button("サブスクを解約"):
            stripe.Subscription.delete(st.session_state.subscription_status["subscription_id"])
            st.session_state.subscription_status = None
            st.markdown("サブスクを解約しました。継続特典を再検討してみませんか？")
            st.button("再加入する", key="rejoin")

    st.markdown("## 決済履歴")
    for entry in st.session_state.payment_history:
        st.markdown(f"<p style='color: #666;'>{entry['type']}：{entry.get('plan', '')}{entry.get('amount', '')}{entry.get('item', '')}（{entry.get('rarity', '')}）- {entry['timestamp']}</p>", unsafe_allow_html=True)

# 予想師コミュニティ
elif menu == "予想師コミュニティ":
    st.markdown("## 予想師コミュニティ")
    st.markdown("### 月間リーダーボード")
    conn = sqlite3.connect("vibecore.db")
    c = conn.cursor()
    c.execute("SELECT user_id, SUM(hearts) as total_hearts FROM forecasts WHERE timestamp LIKE ? GROUP BY user_id ORDER BY total_hearts DESC",
              (f"{datetime.now().year}-{datetime.now().month:02}%",))
    leaderboard_df = pd.DataFrame(c.fetchall(), columns=["ユーザー", "HEART獲得数"])
    conn.close()
    st.dataframe(leaderboard_df)

    user_id = "user_123"
    forecast_comment = st.text_input("あなたの予想を投稿", key="forecast_comment")
    if forecast_comment:
        st.markdown(f"**プレビュー**: {forecast_comment}")
        forecast_id = f"{user_id}_{len(st.session_state.forecasts)}"
        conn = sqlite3.connect("vibecore.db")
        c = conn.cursor()
        c.execute("INSERT INTO forecasts (id, user_id, comment, hearts, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (forecast_id, user_id, forecast_comment, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        st.session_state.forecasts[forecast_id] = {
            "user_id": user_id,
            "comment": forecast_comment,
            "hearts": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.success("予想が投稿されました！")

    for forecast_id, forecast in st.session_state.forecasts.items():
        st.markdown(f"""
        <div style='padding: 12px; background: #FFFACD; border-radius: 12px; margin-bottom: 8px;'>
            <p style='font-weight: bold; color: #333;'>ユーザー{forecast['user_id']}</p>
            <p style='color: #666;'>{forecast['comment']}<br>投稿：{forecast['timestamp']}</p>
            <p style='color: #FF69B4;'>応援：{forecast['hearts']} HEART</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("いいね", key=f"like_{forecast_id}"):
            st.session_state.user_ratings[forecast_id] = st.session_state.user_ratings.get(forecast_id, 0) + 1
        st.markdown(f"いいね数：{st.session_state.user_ratings.get(forecast_id, 0)}")
        points = st.selectbox("投げ銭ポイントを選択", [10, 50, 100], key=f"tip_points_{forecast_id}")
        if st.button(f"{points} HEARTで応援", key=f"tip_{forecast_id}"):
            if st.session_state.heart_balance >= points:
                st.session_state.heart_balance -= points
                st.session_state.forecasts[forecast_id]["hearts"] += points
                conn = sqlite3.connect("vibecore.db")
                c = conn.cursor()
                c.execute("UPDATE forecasts SET hearts = ? WHERE id = ?", (forecast["hearts"] + points, forecast_id))
                c.execute("INSERT INTO heart_history (action, amount, timestamp) VALUES (?, ?, ?)",
                          (f"投げ銭（ユーザー{forecast['user_id']}）", -points, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.session_state.heart_history.append({
                    "action": f"投げ銭（ユーザー{forecast['user_id']}）",
                    "amount": -points,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.markdown(f"""
                <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
                    <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 応援ありがとう！ 🎉</h4>
                    <p class="heart-animation">❤️ {points} HEART</p>
                    <p style='color: white;'>{points} HEARTを贈りました！</p>
                    <p style='color: white;'>HEART残高：{st.session_state.heart_balance}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("HEARTが不足しています。商品一覧からチャージしてください。")
                if st.button("HEARTをチャージ", key=f"charge_tip_{forecast_id}"):
                    st.session_state["menu_select_internal"] = "商品一覧"
                    st.experimental_rerun()

# バトルパスチャレンジ
elif menu == "バトルパスチャレンジ":
    missions_df = pd.DataFrame([
        {"id": "M1", "label": "3日連続ログイン", "points": 10, "premium_reward": "プレミアム称号「ログインスター」（金＋虹）", "category": "無料", "type": "daily"},
        {"id": "M2", "label": "推し馬に10HEART投票", "points": 15, "premium_reward": "限定演出（背景：応援ペンライト＋金ハート）", "category": "無料", "type": "cheer"},
        {"id": "M3", "label": "コメント5回投稿", "points": 10, "premium_reward": "「応援マスター」バッジ（銀＋虹）", "category": "無料", "type": "community"},
        {"id": "M10", "label": "ガチャでウルトラレア獲得", "points": 30, "premium_reward": "ウルトラSSR NFT（特別AR演出付き）", "category": "無料", "type": "gacha"},
        {"id": "M15", "label": "レース的中（3回以上）", "points": 20, "premium_reward": "限定ボイス（声優ナレーション）", "category": "無料", "type": "race"},
        {"id": "M20", "label": "コミュニティで全員500コメント達成", "points": 50, "premium_reward": "コミュニティ限定NFT（団結の証）", "category": "無料", "type": "community"},
        {"id": "M30", "label": "推し馬に50HEART投票（パーソナライズ）", "points": 80, "premium_reward": "パーソナライズ背景（推し馬テーマ）", "category": "プレミアム", "type": "cheer"},
        {"id": "M40", "label": "連勝応援（5連勝）", "points": 120, "premium_reward": "プレミアム専用ガチャチケット（SSR確定）＋限定AR", "category": "プレミアム", "type": "race"}
    ])

    if not st.session_state.battle_pass["missions"]:
        st.session_state.battle_pass["missions"] = {row["id"]: {"done": False, "label": row["label"], "pt": row["points"], "premium_reward": row["premium_reward"], "category": row["category"], "type": row["type"]} for _, row in missions_df.iterrows()}

    if not st.session_state.battle_pass["premium"]:
        st.markdown("""
        <div style='padding: 12px; background: #FFFACD; border-radius: 12px;'>
            <p>プレミアムパス（500円/月）で限定報酬をゲット！</p>
            <button onclick="window.location.href='#Stripe決済（サブスク／HEART／NFT）'">今すぐ加入</button>
        </div>
        """, unsafe_allow_html=True)
    st.session_state.battle_pass["premium"] = st.checkbox("プレミアムパス加入者（500円/月）")

    if not st.session_state.battle_pass["push_horse"]:
        st.session_state.battle_pass["push_horse"] = st.selectbox("推し馬を選択（パーソナライズミッション用）", [f"馬番{i}" for i in range(1, 11)], key="push_horse")
        if st.session_state.battle_pass["push_horse"]:
            for key, mission in st.session_state.battle_pass["missions"].items():
                if mission["type"] == "cheer" and "パーソナライズ" in mission["label"]:
                    mission["label"] = f"{st.session_state.battle_pass['push_horse']}に50HEART投票physics: 10.1103/PhysRevLett.76.2637
                    st.session_state.battle_pass["push_horse"] = st.selectbox("推し馬を選択（パーソナライズミッション用）", [f"馬番{i}" for i in range(1, 11)], key="push_horse")
                    if st.session_state.battle_pass["push_horse"]:
                        for key, mission in st.session_state.battle_pass["missions"].items():
                            if mission["type"] == "cheer" and "パーソナライズ" in mission["label"]:
                                mission["label"] = f"{st.session_state.battle_pass['push_horse']}に50HEART投票（パーソナライズ）"

    st.title("【VibeCore】バトルパス")
    st.markdown(f"**シーズン：{st.session_state.battle_pass['season']}**")
    if datetime.now().month == 5 and datetime.now().day >= 8:
        st.warning("シーズン終了まで1週間！報酬を今すぐ獲得！")
    total_comments = len(st.session_state.forecasts)
    st.markdown(f"**グループミッション進捗**：全員で500コメント（現在：{total_comments}/500）")
    st.progress(min(total_comments / 500, 1.0))
    if total_comments >= 1000:
        st.session_state.heart_balance += 50
        st.session_state.heart_history.append({
            "action": "グループ達成報酬",
            "amount": 50,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.markdown("🎉 全員で1000コメント達成！50 HEART獲得！")

    for key, mission in st.session_state.battle_pass["missions"].items():
        if not mission["done"] and (mission["category"] == "無料" or st.session_state.battle_pass["premium"]):
            if st.button(f"ミッション達成：{mission['label']}（{mission['pt']}pt）", key=key):
                st.session_state.battle_pass["missions"][key]["done"] = True
                st.session_state.battle_pass["points"] += mission["pt"]
                if st.session_state.battle_pass["premium"]:
                    st.session_state.battle_pass["rewards"].append(mission["premium_reward"])
                    if "NFT" in mission["premium_reward"]:
                        nft_item = {"name": mission["premium_reward"], "rarity": "SSR" if "SSR" in mission["premium_reward"] else "レア", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                        st.session_state.nft_inventory.append(nft_item)
                if st.session_state.battle_pass["points"] >= 100 and "背景NFT" in mission["premium_reward"]:
                    st.session_state.heart_balance += 100
                    st.session_state.heart_history.append({
                        "action": "バトルパス報酬（100pt達成）",
                        "amount": 100,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                st.markdown(f"""
                <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
                    <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 ミッション達成！ 🎉</h4>
                    <p class="heart-animation">❤️ {mission['pt']}ポイント</p>
                    <p style='color: white;'>+{mission['pt']}ポイント獲得！</p>
                    <audio src="fanfare.mp3" autoplay style="display: none;"></audio>
                </div>
                """, unsafe_allow_html=True)
                if st.session_state.battle_pass["points"] in [100, 250, 500]:
                    st.markdown(f"""
                    <div style='padding: 12px; background: #FFD700; border-radius: 12px;'>
                        🎉 {st.session_state.battle_pass["points"]}ポイント達成！報酬を確認！
                    </div>
                    """, unsafe_allow_html=True)

    progress = min(st.session_state.battle_pass["points"] / 500 * 100, 100)
    st.markdown(f"### 現在のバトルパスポイント：{st.session_state.battle_pass['points']}pt")
    st.markdown(f"""
    <div class="progress-circle" style="--progress: {progress};">
        {int(progress)}%
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 獲得報酬")
    for reward in st.session_state.b * 100:
        st.markdown(f"- {reward}")

# 商品一覧
elif menu == "商品一覧":
    if items is None:
        st.error("商品一覧.py が見つかりません。ファイルを確認してください。")
    else:
        try:
            items.display_items()
        except Exception as e:
            st.error(f"商品一覧ページの読み込み中にエラーが発生しました：{str(e)}")

# HEART残高と履歴
elif menu == "HEART残高と履歴":
    st.markdown("## HEART残高と利用履歴")
    st.markdown(f"**現在のHEART残高：{st.session_state.heart_balance} HEART**")
    st.markdown("### 利用履歴")
    if st.session_state.heart_history:
        for entry in st.session_state.heart_history:
            color = "green" if entry["amount"] > 0 else "red"
            st.markdown(f"""
            <div style='padding: 8px; background: #FFFACD; border-radius: 8px; margin-bottom: 4px;'>
                <p style='color: #666;'>{entry['action']}：<span style='color: {color};'>{entry['amount']} HEART</span>（{entry['timestamp']}）</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("まだ利用履歴はありません。")

# NFTコレクション
elif menu == "NFTコレクション":
    st.markdown("## あなたのNFTコレクション")
    if st.session_state.nft_inventory:
        for item in st.session_state.nft_inventory:
            card_color = "linear-gradient(#FFD700, #FF69B4)" if item["rarity"] == "ウルトラレア" else "#FF69B4"
            st.markdown(f"""
            <div style='padding: 12px; background: {card_color}; border-radius: 12px; margin-bottom: 8px; color: white;'>
                <h5 style='margin-bottom: 4px;'>{item['name']}</h5>
                <p style='color: white;'>レア度：{item['rarity']}<br>獲得日：{item['timestamp']}</p>
                <button style='background: white; color: #FF69B4; border: none; padding: 8px 16px; border-radius: 8px;'>Xでシェア</button>
                <p style='color: white; font-size: 0.9em;'>※このボタンはシェアのプレビューです。本番ではXの共有APIを利用します。</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("まだNFTはありません。商品一覧から購入してください。")

# 管理者ダッシュボード
elif menu == "管理ダッシュボード":
    st.markdown("## 管理者用ダッシュボード")
    if st.button("セッション状態をバックアップ"):
        with open("session_backup.json", "w") as f:
            json.dump(dict(st.session_state), f)
        st.success("バックアップ完了")
    if st.button("セッション状態を復元"):
        with open("session_backup.json", "r") as f:
            backup = json.load(f)
        for k, v in backup.items():
            st.session_state[k] = v
        st.success("復元完了")

    st.markdown("### 投票数")
    votes_df = pd.DataFrame(list(st.session_state.votes.items()), columns=["馬番", "投票数"])
    st.dataframe(votes_df)

    st.markdown("### 売上")
    total_revenue = sum(entry.get("amount", 0) for entry in st.session_state.payment_history if entry["type"] in ["HEART購入", "NFT購入"])
    st.markdown(f"総売上：{total_revenue}円")

    st.markdown("### ユーザー分析")
    conn = sqlite3.connect("vibecore.db")
    c = conn.cursor()
    c.execute("SELECT user_id, COUNT(*) as votes FROM forecasts GROUP BY user_id")
    user_activity = pd.DataFrame(c.fetchall(), columns=["ユーザー", "投稿数"])
    conn.close()
    st.dataframe(user_activity)

# エキサイトポップアップ
st.markdown("""
<script>
window.onbeforeunload = function() {
    return "今ならHEART 20%オフ！離れますか？";
};
</script>
""", unsafe_allow_html=True)
