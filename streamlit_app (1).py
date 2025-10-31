import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os

# データ保存用CSV
DATA_FILE = "sleep_data.csv"
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "date","sleep_time","wake_time","wake_count","sleep_quality","stress_level","goal_bedtime"
    ])
    df.to_csv(DATA_FILE, index=False)

st.title("睡眠管理アプリ（目標就寝時間版）")

# --- 今日の入力フォーム ---
st.header("今日の睡眠データを入力")
with st.form("sleep_form"):
    sleep_time = st.text_input("寝た時間 (HH:MM)")
    wake_time = st.text_input("起きた時間 (HH:MM)")
    wake_count = st.number_input("途中覚醒回数", min_value=0, max_value=10, step=1)
    sleep_quality = st.slider("睡眠の質 (1-5)", 1, 5, 3)
    stress_level = st.slider("ストレスレベル (1-5)", 1, 5, 3)
    goal_bedtime = st.text_input("目標就寝時間 (HH:MM)")
    submitted = st.form_submit_button("保存してアドバイスを見る")

if submitted:
    try:
        sleep_dt = datetime.strptime(sleep_time, "%H:%M")
        wake_dt = datetime.strptime(wake_time, "%H:%M")
        goal_dt = datetime.strptime(goal_bedtime, "%H:%M")
        if wake_dt < sleep_dt:
            wake_dt += timedelta(days=1)
        sleep_hours = (wake_dt - sleep_dt).total_seconds()/3600
        # 達成率: 目標就寝時間との差で計算
        diff_minutes = (sleep_dt - goal_dt).total_seconds()/60
        # 目標より早く寝た場合も100%に
        achievement = max(0, min(100, 100 - diff_minutes))
    except:
        st.error("時間のフォーマットが正しくありません。HH:MM形式で入力してください。")
        st.stop()

    # データ保存
    new_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "sleep_time": sleep_time,
        "wake_time": wake_time,
        "wake_count": wake_count,
        "sleep_quality": sleep_quality,
        "stress_level": stress_level,
        "goal_bedtime": goal_bedtime
    }
    df = pd.read_csv(DATA_FILE)
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

    st.subheader("今日の睡眠データ")
    st.dataframe(pd.DataFrame([new_data]))

    # --- アドバイス ---
    st.subheader("アドバイザーのコメント")
    adv = []
    if diff_minutes > 30:
        adv.append("目標就寝時間より遅く寝ています。もう少し早めに寝ましょう。")
    if sleep_quality <= 2:
        adv.append("睡眠の質が低めです。寝る前のスマホやカフェインを控えましょう。")
    if stress_level >= 4:
        adv.append("ストレスレベルが高めです。リラックス法を試してみましょう。")
    if wake_count >= 2:
        adv.append("途中覚醒が多いです。寝室環境を見直しましょう。")
    if diff_minutes <= 30 and sleep_quality >= 4:
        adv.append("目標就寝時間に近く、良い睡眠です！維持しましょう。")

    for a in adv:
        st.write(f"- {a}")

    # --- 過去データのグラフ ---
    st.subheader("過去データの推移")
    df_plot = pd.read_csv(DATA_FILE)
    plt.figure(figsize=(10,5))
    plt.plot(pd.to_datetime(df_plot['date']), df_plot['sleep_time'].apply(lambda x: datetime.strptime(x,"%H:%M").hour + datetime.strptime(x,"%H:%M").minute/60), label='実際の就寝時間', marker='o', color='blue')
    plt.plot(pd.to_datetime(df_plot['date']), df_plot['goal_bedtime'].apply(lambda x: datetime.strptime(x,"%H:%M").hour + datetime.strptime(x,"%H:%M").minute/60), label='目標就寝時間', linestyle='--', marker='o', color='orange')
    plt.ylabel('就寝時間（時刻）')
    plt.xlabel('日付')
    plt.title('目標就寝時間と実際の就寝時間の推移')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)