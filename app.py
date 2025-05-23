import streamlit as st
import pandas as pd
import json
import os
import glob
import random
import sqlite3
from datetime import datetime
import stripe
from dotenv import load_dotenv
import logging

import logging

st.set_page_config(page_title="VibeCore", layout="wide")  # ✅ Streamlit設定は必ず最初に！

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLiteデータベースの初期化
try:
    conn = sqlite3.connect("vibecore.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS heart_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT,
            amount INTEGER,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS heart_balance (
            user_id TEXT PRIMARY KEY,
            balance INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nft_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            name TEXT,
            rarity TEXT,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS battle_pass (
            user_id TEXT PRIMARY KEY,
            points INTEGER,
            missions TEXT,
            premium INTEGER,
            rewards TEXT,
            season TEXT,
            push_horse TEXT
        )
    """)
    conn.commit()
except Exception as e:
    logger.error(f"データベースの初期化に失敗しました: {e}")
    st.error(f"データベースの初期化に失敗しました: {e}")
    conn = None
    cursor = None

# HEART残高の関数
def get_heart_balance(user_id="user_123"):
    if cursor is None:
        return 200
    try:
        cursor.execute("SELECT balance FROM heart_balance WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 200
    except Exception as e:
        logger.error(f"HEART残高の取得に失敗しました: {e}")
        return 200

def update_heart_balance(user_id, new_balance):
    if cursor is None:
        return
    try:
        cursor.execute("INSERT OR REPLACE INTO heart_balance (user_id, balance) VALUES (?, ?)", (user_id, new_balance))
        conn.commit()
    except Exception as e:
        logger.error(f"HEART残高の更新に失敗しました: {e}")

def add_heart_history(user_id, action, amount):
    if cursor is None:
        return
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO heart_history (user_id, action, amount, timestamp) VALUES (?, ?, ?, ?)",
                       (user_id, action, amount, timestamp))
        conn.commit()
    except Exception as e:
        logger.error(f"HEART履歴の追加に失敗しました: {e}")

def get_heart_history(user_id="user_123"):
    if cursor is None:
        return []
    try:
        cursor.execute("SELECT action, amount, timestamp FROM heart_history WHERE user_id = ?", (user_id,))
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"HEART履歴の取得に失敗しました: {e}")
        return []

# NFTインベントリの関数
def get_nft_inventory(user_id="user_123"):
    if cursor is None:
        return []
    try:
        cursor.execute("SELECT name, rarity, timestamp FROM nft_inventory WHERE user_id = ?", (user_id,))
        return [{"name": row[0], "rarity": row[1], "timestamp": row[2]} for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"NFTインベントリの取得に失敗しました: {e}")
        return []

def add_nft_inventory(user_id, name, rarity):
    if cursor is None:
        return
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO nft_inventory (user_id, name, rarity, timestamp) VALUES (?, ?, ?, ?)",
                       (user_id, name, rarity, timestamp))
        conn.commit()
    except Exception as e:
        logger.error(f"NFTインベントリの追加に失敗しました: {e}")

# バトルパスの関数
def get_battle_pass(user_id="user_123"):
    if cursor is None:
        return {
            "points": 0,
            "missions": {},
            "premium": False,
            "rewards": [],
            "season": "2025-05",
            "push_horse": None
        }
    try:
        cursor.execute("SELECT points, missions, premium, rewards, season, push_horse FROM battle_pass WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            return {
                "points": result[0],
                "missions": json.loads(result[1]) if result[1] else {},
                "premium": bool(result[2]),
                "rewards": json.loads(result[3]) if result[3] else [],
                "season": result[4],
                "push_horse": result[5]
            }
        return {
            "points": 0,
            "missions": {},
            "premium": False,
            "rewards": [],
            "season": "2025-05",
            "push_horse": None
        }
    except Exception as e:
        logger.error(f"バトルパスデータの取得に失敗しました: {e}")
        return {
            "points": 0,
            "missions": {},
            "premium": False,
            "rewards": [],
            "season": "2025-05",
            "push_horse": None
        }

def update_battle_pass(user_id, battle_pass_data):
    if cursor is None:
        return
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO battle_pass (user_id, points, missions, premium, rewards, season, push_horse)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            battle_pass_data["points"],
            json.dumps(battle_pass_data["missions"]),
            int(battle_pass_data["premium"]),
            json.dumps(battle_pass_data["rewards"]),
            battle_pass_data["season"],
            battle_pass_data["push_horse"]
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"バトルパスデータの更新に失敗しました: {e}")

# items.pyのフォールバック
class ItemsFallback:
    def display_items(self):
        st.markdown("## 商品一覧")
        st.write("商品データが見つかりません。以下はサンプル商品です：")
        st.write("- HEARTパック（100 HEART）：500円")
        st.write("- 限定NFTガチャ：1000円")
        st.write("- プレミアムパス：500円/月")

try:
    import items
except ImportError:
    items = ItemsFallback()
    logger.warning("items.pyが見つかりません。フォールバックを使用します。")

# 環境変数の読み込み
load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_xxx")
SUCCESS_URL = os.getenv("SUCCESS_URL", "https://your-app.streamlit.app/?session_id={CHECKOUT_SESSION_ID}")
CANCEL_URL = os.getenv("CANCEL_URL", "https://your-app.streamlit.app/")

if stripe.api_key == "sk_test_xxx":
    st.warning("Stripe APIキーが設定されていません。テストモードで動作します。")

# ページ設定

# セッション状態の初期化
if "checked_horses" not in st.session_state:
    st.session_state.checked_horses = []
if "heart_balance" not in st.session_state:
    st.session_state.heart_balance = get_heart_balance()
if "heart_history" not in st.session_state:
    st.session_state.heart_history = get_heart_history()
if "nft_inventory" not in st.session_state:
    st.session_state.nft_inventory = get_nft_inventory()
if "subscription_status" not in st.session_state:
    st.session_state.subscription_status = None
if "payment_history" not in st.session_state:
    st.session_state.payment_history = []
if "battle_pass" not in st.session_state:
    st.session_state.battle_pass = get_battle_pass()
if "forecasts" not in st.session_state:
    st.session_state.forecasts = {}
if "votes" not in st.session_state:
    st.session_state.votes = {}
if "user_settings" not in st.session_state:
    st.session_state.user_settings = {"accuracy": 0.5, "emotion": 0.5, "style": "balanced"}
if "user_ratings" not in st.session_state:
    st.session_state.user_ratings = {}
if "purchases" not in st.session_state:
    st.session_state.purchases = []
if "menu_select" not in st.session_state:
    st.session_state.menu_select = "AI競馬予測"

# サイドバーのメニュー
menu_options = [
    "AI競馬予測",
    "Stripe決済（サブスク／HEART／NFT）",
    "予想師コミュニティ",
    "バトルパスチャレンジ",
    "商品一覧",
    "HEART残高と履歴",
    "NFTコレクション",
    "管理ダッシュボード"
]
menu = st.sidebar.radio("機能を選択してください", menu_options, key="menu_select")

# ユーザー設定
st.sidebar.markdown("## ユーザーカスタム設定")
st.session_state.user_settings["accuracy"] = st.sidebar.slider("予測精度（的中重視/穴重視）", 0.0, 1.0, 0.5)
st.session_state.user_settings["emotion"] = st.sidebar.slider("感情係数（推し指数重視）", 0.0, 1.0, 0.5)
st.session_state.user_settings["style"] = st.sidebar.selectbox("補正スタイル", ["保守的", "バランス", "攻撃的"], index=1)

# メニュー内検索
search_query = st.sidebar.text_input("メニュー内検索", placeholder="機能名を入力（例：AI競馬予測）")
if search_query:
    filtered_menu = [m for m in menu_options if search_query.lower() in m.lower()]
    if filtered_menu:
        st.session_state.menu_select = filtered_menu[0]
    else:
        st.sidebar.warning("該当するメニューが見つかりません。")

# アクティビティ通知
st.sidebar.markdown("## アクティビティ通知")
if st.session_state.battle_pass["points"] >= 100:
    st.sidebar.markdown(f"🎉 バトルパスポイントが100pt達成！報酬を確認してください。")
if st.session_state.votes:
    total_votes = sum(st.session_state.votes.values())
    st.sidebar.markdown(f"📊 現在の総投票数：{total_votes}票")

# クイックアクセスボタン
st.sidebar.markdown("## クイックアクセス")
if st.button("バトルパス進捗を確認", key="quick_battle_pass"):
    st.session_state.menu_select = "バトルパスチャレンジ"
if st.session_state.purchases and st.button("最近の購入履歴を確認", key="quick_purchases"):
    st.session_state.menu_select = "Stripe決済（サブスク／HEART／NFT）"

# メニュー選択時の演出
if menu:
    st.markdown(f"""
    <div style='text-align: center; padding: 8px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px; animation: fadeIn 0.5s;'>
        <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>選択中：{menu}</h4>
    </div>
    <style>
    @keyframes fadeIn {{
        0% {{ opacity: 0; }}
        100% {{ opacity: 1; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# AI競馬予測セクション
if menu == "AI競馬予測":
    st.markdown("### 勝率またはオッズファイルをアップロード（JSON形式）")
    uploaded_file = st.file_uploader("アップロードしてください（例：win_20250515_monbetsu.json）", type=["json"])
    if uploaded_file:
        filename = uploaded_file.name
        if filename.startswith(("win_", "odds_")) and filename.endswith(".json"):
            save_path = os.path.join(".", filename)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"{filename} をアップロードしました")
        else:
            st.error("ファイル名が win_ または odds_ で始まる必要があります")

    win_files = sorted(glob.glob("win_*.json"))
    race_ids = [f.replace("win_", "").replace(".json", "") for f in win_files]

    if not race_ids:
        st.warning("勝率ファイルが見つかりません。上からアップロードしてください。")
    else:
        selected_race = st.selectbox("レースを選択してください", race_ids)
        win_path = f"win_{selected_race}.json"
        odds_path = f"odds_{selected_race}.json"

        if not os.path.exists(win_path) or not os.path.exists(odds_path):
            st.error(f"必要なファイルが見つかりません: {win_path}, {odds_path}")
        else:
            try:
                with open(win_path, encoding="utf-8") as f:
                    win_probs = json.load(f)
                with open(odds_path, encoding="utf-8") as f:
                    odds_data = json.load(f)
            except json.JSONDecodeError as e:
                st.error(f"JSONファイルの形式が不正です: {e}")
                win_probs, odds_data = [], []
            except Exception as e:
                st.error(f"ファイルの読み込みに失敗しました: {e}")
                win_probs, odds_data = [], []

            if not win_probs or not odds_data:
                st.error("データの読み込みに失敗しました。")
            else:
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

                    adjusted_prob = 0
                    if prob is not None:
                        adjusted_prob = prob * (1 - st.session_state.user_settings["accuracy"]) + prob * st.session_state.user_settings["emotion"]
                        if st.session_state.user_settings["style"] == "保守的":
                            adjusted_prob *= 0.9
                        elif st.session_state.user_settings["style"] == "攻撃的":
                            adjusted_prob *= 1.1

                    score = 0.0
                    if odds and adjusted_prob is not None and odds > 1.0:
                        score = (adjusted_prob * (odds - 1) - (1 - adjusted_prob)) / (odds - 1)
                        score = max(0, round(score * 100, 1))

                    pace = random.choice(["先行", "差し", "逃げ"])
                    track_bias = random.choice(["内有利", "外有利", "フラット"])
                    bias_score = random.uniform(0, 100)
                    if horse and horse.isdigit():
                        if track_bias == "内有利" and int(horse) <= 3:
                            bias_score += 20
                        elif track_bias == "外有利" and int(horse) > 3:
                            bias_score += 20
                    bias_score = min(bias_score, 100)
                    bias_color = "green" if bias_score >= 70 else "red" if bias_score < 30 else "yellow"

                    push_index = random.uniform(50, 100)
                    rank = ("本命安定圏" if score >= 50 else
                            "複勝安定圏" if score >= 30 else
                            "オッズ妙味圏" if score >= 10 else
                            "検討外・回避圏")

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

                if not rows:
                    st.error("データの処理に失敗しました。")
                else:
                    df = pd.DataFrame(rows).sort_values("勝利の鼓動 × 勝ちの直感（％）", ascending=False).reset_index(drop=True)

                    # レース情報
                    st.markdown("### レース基本情報")
                    race_info = {
                        "日時": "2025年5月15日 12:40",
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

                    # モバイル用ハイライト
                    st.markdown("### モバイル用ハイライト")
                    for _, horse in df.head(3).iterrows():
                        symbol = "◎" if horse.name == 0 else "◯" if horse.name == 1 else "▲"
                        win_chance = "A" if horse["勝利の鼓動 × 勝ちの直感（％）"] >= 50 else "B" if horse["勝利の鼓動 × 勝ちの直感（％）"] >= 30 else "C"
                        st.markdown(f"{symbol} 馬番{horse['馬番']}（勝負度：{win_chance}）")

                    # 要点サマリー＋前回比較
                    st.markdown("### 要点サマリー＋前回比較")
                    previous_df = df.copy()
                    previous_df["勝利の鼓動 × 勝ちの直感（％）"] *= 0.9
                    for _, row in df.head(3).iterrows():
                        prev_score = previous_df[previous_df["馬番"] == row["馬番"]]["勝利の鼓動 × 勝ちの直感（％）"].values[0] if not previous_df[previous_df["馬番"] == row["馬番"]].empty else row["勝利の鼓動 × 勝ちの直感（％）"]
                        diff = row["勝利の鼓動 × 勝ちの直感（％）"] - prev_score
                        st.markdown(f"馬番{row['馬番']}：スコア {row['勝利の鼓動 × 勝ちの直感（％）']}（前回比：{'+' if diff >= 0 else ''}{diff:.1f}）")

                    # 推し馬チェック
                    st.markdown("### 推し馬チェック")
                    current_check = st.multiselect(
                        "気になる馬を選んでください（保持されます）",
                        options=df["馬番"].tolist(),
                        default=st.session_state.checked_horses
                    )
                    st.session_state.checked_horses = current_check

                    # テーブル表示
                    st.dataframe(df, use_container_width=True)

                    # 推し馬カード
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
                                <b>馬場バイアス：</b><span style='color:{row['バイアス色']};'>{row['馬場バイアス']}</span></p>
                            </div>
                            """, unsafe_allow_html=True)

                            # HEART投票
                            if st.button(f"{row['馬番']}に10HEARTで応援投票", key=f"vote_{row['馬番']}"):
                                if st.session_state.heart_balance >= 10:
                                    st.session_state.heart_balance -= 10
                                    st.session_state.votes[row['馬番']] = st.session_state.votes.get(row['馬番'], 0) + 1
                                    st.session_state.heart_history.append({
                                        "action": f"投票（馬番{row['馬番']}）",
                                        "amount": -10,
                                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    })
                                    update_heart_balance("user_123", st.session_state.heart_balance)
                                    add_heart_history("user_123", f"投票（馬番{row['馬番']}）", -10)
                                    st.session_state.heart_history = get_heart_history()
                                    st.markdown(f"""
                                    <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
                                        <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 投票ありがとう！ 🎉</h4>
                                        <p style='color: white;'>現在の投票数：{st.session_state.votes.get(row['馬番'], 0)}</p>
                                        <p style='color: white;'>HEART残高：{st.session_state.heart_balance}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.error("HEARTが不足しています。商品一覧からチャージしてください。")

                            # シェアコメント
                            share_comment = f"馬番{row['馬番']}を信じて勝つ！🏆 #VibeCore"
                            if st.button(f"Xでシェア", key=f"share_{row['馬番']}"):
                                st.markdown(f"""
                                <div style='text-align: center; padding: 12px; background: #FFFACD; border-radius: 12px;'>
                                    <p style='color: #333;'>{share_comment}</p>
                                    <p style='color: #666; font-size: 0.9em;'>※このボタンはシェアのプレビューです。</p>
                                </div>
                                """, unsafe_allow_html=True)

# Stripe決済セクション
elif menu == "Stripe決済（サブスク／HEART／NFT）":
    st.markdown("## プレミアム応援プラン")
    plan = st.radio("プランを選択", ["ライト（100円/月）", "スタンダード（500円/月）", "VIP（1000円/月）"])
    price_ids = {
        "ライト（100円/月）": "price_python",
        "スタンダード（500円/月）": "price_xxx",
        "VIP（1000円/月）": "price_xxx"
    }

    if st.button("サブスクに加入"):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                subscription_data={"items": [{"price": price_ids[plan]}]},
                success_url=SUCCESS_URL,
                cancel_url=CANCEL_URL,
                metadata={"user_id": "user_123", "type": "subscription", "plan": plan}
            )
            st.session_state.purchases.append(f"サブスク：{plan}")
            st.markdown(f"""
            <a href="{session.url}" target="_blank">
                <button style='background: linear-gradient(#FFD700, #FF69B4); color: white; border: none; padding: 1em 2em; border-radius: 8px; font-size: 16px;'>
                    今すぐ加入する！
                </button>
            </a>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"サブスク加入に失敗しました: {e}")

    st.markdown("## HEARTトークン購入")
    heart_plan = st.radio("HEARTを選択", ["100HEART（500円）", "500HEART（2500円）"])
    heart_prices = {
        "100HEART（500円）": "price_xxx",
        "500HEART（2500円）": "price_xxx"
    }

    if st.button("HEARTを購入"):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": heart_prices[heart_plan], "quantity": 1}],
                mode="payment",
                success_url=SUCCESS_URL,
                cancel_url=CANCEL_URL,
                metadata={"user_id": "user_123", "type": "heart", "amount": heart_plan.split("（")[0]}
            )
            st.session_state.purchases.append(f"HEART購入：{heart_plan}")
            amount = int(heart_plan.split("HEART")[0])
            st.session_state.heart_balance += amount
            update_heart_balance("user_123", st.session_state.heart_balance)
            add_heart_history("user_123", f"HEART購入（{heart_plan}）", amount)
            st.session_state.heart_history = get_heart_history()
            st.markdown(f"""
            <a href="{session.url}" target="_blank">
                <button style='background: linear-gradient(#FFD700, #FF69B4); color: white; border: none; padding: 1em 2em; border-radius: 8px; font-size: 16px;'>
                    HEARTを購入する！
                </button>
            </a>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"HEART購入に失敗しました: {e}")

    st.markdown("## NFT購入・ガチャ")
    nft_plan = st.radio("NFTを選択", ["限定背景NFT（1000円）", "ガチャ10連（1000円）"])
    nft_prices = {
        "限定背景NFT（1000円）": "price_xxx",
        "ガチャ10連（1000円）": "price_xxx"
    }

    if st.button("NFTを購入"):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": nft_prices[nft_plan], "quantity": 1}],
                mode="payment",
                success_url=SUCCESS_URL,
                cancel_url=CANCEL_URL,
                metadata={"user_id": "user_123", "type": "nft", "item": nft_plan}
            )
            st.session_state.purchases.append(f"NFT購入：{nft_plan}")
            rarity = "ウルトラレア" if "ガチャ" in nft_plan and random.random() > 0.9 else "レア"
            nft_item = {"name": f"{nft_plan}（{rarity}）", "rarity": rarity, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            st.session_state.nft_inventory.append(nft_item)
            add_nft_inventory("user_123", nft_item["name"], nft_item["rarity"])
            st.session_state.nft_inventory = get_nft_inventory()
            st.markdown(f"""
            <a href="{session.url}" target="_blank">
                <button style='background: linear-gradient(#FFD700, #FF69B4); color: white; border: none; padding: 1em 2em; border-radius: 8px; font-size: 16px;'>
                    NFTを購入する！
                </button>
            </a>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"NFT購入に失敗しました: {e}")

    if st.session_state.subscription_status:
        if st.button("サブスクを解約"):
            try:
                stripe.Subscription.delete(st.session_state.subscription_status["subscription_id"])
                st.session_state.subscription_status = None
                st.markdown("サブスクを解約しました。")
            except Exception as e:
                st.error(f"サブスク解約に失敗しました: {e}")

    st.markdown("## 決済履歴")
    for entry in st.session_state.payment_history:
        st.markdown(f"<p style='color: #666;'>{entry['type']}：{entry.get('plan', '')}{entry.get('amount', '')}{entry.get('item', '')}（{entry.get('rarity', '')}）- {entry['timestamp']}</p>", unsafe_allow_html=True)

# 予想師コミュニティセクション
elif menu == "予想師コミュニティ":
    st.markdown("## 予想師コミュニティ")
    user

user = ...
_id = "user_123"

forecast_comment = st.text_input("あなたの予想を投稿", key="forecast_comment")
if forecast_comment:
    forecast_id = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    st.session_state.forecasts[forecast_id] = {
        "user_id": user_id,
        "comment": forecast_comment,
        "hearts": 0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.success("予想が投稿されました！")
    
    if forecast_comment:
        forecast_id = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
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
        points = st.selectbox("投げ銭ポイントを選択", [10, 50, 100], key=f"tip_points_{forecast_id}")
        if st.button(f"{points} HEARTで応援", key=f"tip_{forecast_id}"):
            if st.session_state.heart_balance >= points:
                st.session_state.heart_balance -= points
                st.session_state.forecasts[forecast_id]["hearts"] += points
                st.session_state.heart_history.append({
                    "action": f"投げ銭（ユーザー{forecast['user_id']}）",
                    "amount": -points,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                update_heart_balance("user_123", st.session_state.heart_balance)
                add_heart_history("user_123", f"投げ銭（ユーザー{forecast['user_id']}）", -points)
                st.session_state.heart_history = get_heart_history()
                st.markdown(f"""
                <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
                    <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 応援ありがとう！ 🎉</h4>
                    <p style='color: white;'>{points} HEARTを贈りました！</p>
                    <p style='color: white;'>HEART残高：{st.session_state.heart_balance}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("HEARTが不足しています。商品一覧からチャージしてください。")

# バトルパスチャレンジセクション
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
        update_battle_pass("user_123", st.session_state.battle_pass)

    st.session_state.battle_pass["premium"] = st.checkbox("プレミアムパス加入者（500円/月）", value=st.session_state.battle_pass["premium"])
    update_battle_pass("user_123", st.session_state.battle_pass)

    if not st.session_state.battle_pass["push_horse"]:
        st.session_state.battle_pass["push_horse"] = st.selectbox("推し馬を選択（パーソナライズミッション用）", [f"馬番{i}" for i in range(1, 11)], key="push_horse")
        if st.session_state.battle_pass["push_horse"]:
            for key, mission in st.session_state.battle_pass["missions"].items():
                if mission["type"] == "cheer" and "パーソナライズ" in mission["label"]:
                    mission["label"] = f"{st.session_state.battle_pass['push_horse']}に50HEART投票（パーソナライズ）"
            update_battle_pass("user_123", st.session_state.battle_pass)

    st.title("【VibeCore】バトルパス")
    st.markdown(f"**シーズン：{st.session_state.battle_pass['season']}**")
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
                        add_nft_inventory("user_123", nft_item["name"], nft_item["rarity"])
                        st.session_state.nft_inventory = get_nft_inventory()
                if st.session_state.battle_pass["points"] >= 100 and "背景NFT" in mission["premium_reward"]:
                    st.session_state.heart_balance += 100
                    st.session_state.heart_history.append({
                        "action": "バトルパス報酬（100pt達成）",
                        "amount": 100,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    update_heart_balance("user_123", st.session_state.heart_balance)
                    add_heart_history("user_123", "バトルパス報酬（100pt達成）", 100)
                    st.session_state.heart_history = get_heart_history()
                update_battle_pass("user_123", st.session_state.battle_pass)
                st.markdown(f"""
                <div style='text-align: center; padding: 12px; background: linear-gradient(#FFD700, #FF69B4); border-radius: 12px;'>
                    <h4 style='color: white; text-shadow: 1px 1px 2px #000;'>🎉 ミッション達成！ 🎉</h4>
                    <p style='color: white;'>+{mission['pt']}ポイント獲得！</p>
                </div>
                """, unsafe_allow_html=True)

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
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 獲得報酬")
    for reward in st.session_state.battle_pass["rewards"]:
        st.markdown(f"- {reward}")

# 商品一覧セクション
elif menu == "商品一覧":
    items.display_items()

# HEART残高と履歴セクション
elif menu == "HEART残高と履歴":
    st.markdown("## HEART残高と利用履歴")
    st.session_state.heart_balance = get_heart_balance()
    st.session_state.heart_history = get_heart_history()
    st.markdown(f"**現在のHEART残高：{st.session_state.heart_balance} HEART**")
    st.markdown("### 利用履歴")
    if st.session_state.heart_history:
        for entry in st.session_state.heart_history:
            color = "green" if entry[1] > 0 else "red"
            st.markdown(f"""
            <div style='padding: 8px; background: #FFFACD; border-radius: 8px; margin-bottom: 4px;'>
                <p style='color: #666;'>{entry[0]}：<span style='color: {color};'>{entry[1]} HEART</span>（{entry[2]}）</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("まだ利用履歴はありません。")

# NFTコレクションセクション
elif menu == "NFTコレクション":
    st.markdown("## あなたのNFTコレクション")
    st.session_state.nft_inventory = get_nft_inventory()
    if st.session_state.nft_inventory:
        for item in st.session_state.nft_inventory:
            if not isinstance(item, dict) or "rarity" not in item or "name" not in item or "timestamp" not in item:
                st.warning(f"不正なNFTデータが検出されました: {item}")
                continue
            card_color = "linear-gradient(#FFD700, #FF69B4)" if item["rarity"] == "ウルトラレア" else "#FF69B4"
            st.markdown(f"""
            <div style='padding: 12px; background: {card_color}; border-radius: 12px; margin-bottom: 8px; color: white;'>
                <h5 style='margin-bottom: 4px;'>{item['name']}</h5>
                <p style='color: white;'>レア度：{item['rarity']}<br>獲得日：{item['timestamp']}</p>
                <button style='background: white; color: #FF69B4; border: none; padding: 8px 16px; border-radius: 8px;'>Xでシェア</button>
                <p style='color: white; font-size: 0.9em;'>※このボタンはシェアのプレビューです。</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("まだNFTはありません。商品一覧から購入してください。")

# 管理ダッシュボードセクション
elif menu == "管理ダッシュボード":
    st.markdown("## 管理者用ダッシュボード")
    st.markdown("### 投票数")
    votes_df = pd.DataFrame(list(st.session_state.votes.items()), columns=["馬番", "投票数"])
    st.dataframe(votes_df)

    st.markdown("### 売上")
    total_revenue = sum(entry.get("amount", 0) for entry in st.session_state.payment_history if entry["type"] in ["HEART購入", "NFT購入"])
    st.markdown(f"総売上：{total_revenue}円")

    st.markdown("### ユーザー分析")
    active_users = len(set([entry["user_id"] for entry in st.session_state.payment_history]))
    st.markdown(f"アクティブユーザー数：{active_users}人")

# CSSアニメーション
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
</style>
""", unsafe_allow_html=True)
