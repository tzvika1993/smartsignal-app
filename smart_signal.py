import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import ta

st.set_page_config(layout="wide")
st.title("📈 SmartSignal – ניתוח חכם למניה")
st.markdown("""
<style>
body, .stApp {
    direction: rtl;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

symbol = st.text_input("🔍 הזן סמל מניה (למשל MSFT):", "MSFT")
period_option = st.selectbox("בחר טווח זמן לניתוח:", ["1 שבוע", "1 חודש", "3 חודשים", "1 שנה", "5 שנים"], index=2)

period_map = {
    "1 שבוע": "7d",
    "1 חודש": "1mo",
    "3 חודשים": "3mo",
    "1 שנה": "1y",
    "5 שנים": "5y"
}

if st.button("נתח עכשיו"):
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period_map[period_option])

    if hist.empty:
        st.error("לא נמצאו נתונים עבור הסמל הזה.")
    else:
        hist = hist.dropna()
        rsi_series = ta.momentum.RSIIndicator(close=hist['Close']).rsi()
        ema_50 = ta.trend.EMAIndicator(close=hist['Close'], window=50).ema_indicator()
        ema_200 = ta.trend.EMAIndicator(close=hist['Close'], window=200).ema_indicator()

        last_price = hist['Close'][-1]
        support = hist['Close'].min()
        resistance = hist['Close'].max()
        range_mid = (support + resistance) / 2
        rsi_now = rsi_series.iloc[-1]

        st.subheader("📌 ניתוח טכני")
        st.write(f"**טווח ניתוח:** {period_option}")
        st.write(f"**מחיר נוכחי:** {last_price:.2f} $")
        st.write(f"**רמת תמיכה:** {support:.2f} $")
        st.write(f"**רמת התנגדות:** {resistance:.2f} $")
        st.write(f"**RSI נוכחי:** {rsi_now:.2f}")

        if rsi_now > 70:
            st.warning("⚠️ המניה במצב קנייה יתר – יתכן תיקון בקרוב.")
        elif rsi_now < 30:
            st.success("✅ המניה במצב מכירת יתר – עשויה לעלות.")
        else:
            st.info("ℹ️ RSI נייטרלי – עקוב אחרי התנועה הבאה.")

        if last_price < range_mid:
            st.success("✅ המלצה כללית: קנייה זהירה – המניה עדיין מתחת להתנגדות.")
        else:
            st.warning("⚠️ המלצה כללית: המתן לפריצה – המניה קרובה להתנגדות.")

        st.subheader("📊 גרף טכני – נרות, RSI ו-EMA")
        fig = go.Figure()

        # נרות יפניים
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name='נרות'
        ))

        # EMA
        fig.add_trace(go.Scatter(x=hist.index, y=ema_50, mode='lines', name='EMA 50'))
        fig.add_trace(go.Scatter(x=hist.index, y=ema_200, mode='lines', name='EMA 200'))

        # קווי תמיכה והתנגדות
        fig.add_hline(y=support, line=dict(color='green', dash='dot'))
        fig.add_hline(y=resistance, line=dict(color='red', dash='dot'))

        fig.update_layout(
            title=f"ניתוח טכני למניית {symbol} – כולל EMA ונרות",
            yaxis_title='מחיר',
            xaxis_title='תאריך',
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)
