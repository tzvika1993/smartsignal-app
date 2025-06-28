import streamlit as st
import yfinance as yf
import plotly.graph_objs as go

st.set_page_config(layout="wide")
st.title("📈 SmartSignal – ניתוח חכם למניה")

symbol = st.text_input("🔍 הזן סמל מניה (למשל MSFT):", "MSFT")

if st.button("נתח עכשיו"):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1mo")

    if hist.empty:
        st.error("לא נמצאו נתונים עבור הסמל הזה.")
    else:
        last_price = hist['Close'][-1]
        support = hist['Close'].min()
        resistance = hist['Close'].max()
        range_mid = (support + resistance) / 2

        st.subheader("📌 ניתוח טכני בסיסי")
        st.write(f"**מחיר נוכחי:** {last_price:.2f} $")
        st.write(f"**תמיכה:** {support:.2f} $")
        st.write(f"**התנגדות:** {resistance:.2f} $")

        if last_price < range_mid:
            st.success("✅ המלצה: קנייה זהירה – המניה עדיין מתחת להתנגדות.")
        else:
            st.warning("⚠️ המלצה: המתן לפריצה – המניה קרובה להתנגדות.")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='מחיר'))
        fig.add_hline(y=support, line=dict(color='green', dash='dot'))
        fig.add_hline(y=resistance, line=dict(color='red', dash='dot'))
        st.plotly_chart(fig, use_container_width=True)
