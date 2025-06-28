import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import ta
import requests

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

def get_ai_analysis(symbol, price, support, resistance, rsi):
    prompt = f"""
    Analyze stock {symbol}:
    - Current price: {price:.2f}$
    - Support: {support:.2f}$
    - Resistance: {resistance:.2f}$
    - RSI: {rsi:.2f}
    Provide a brief technical recommendation (Buy / Hold / Sell).
    """

    response = requests.post(
        "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
        headers={"Authorization": f"Bearer {st.secrets['hf_token']}"},
        json={"inputs": prompt}
    )

    if response.status_code == 200:
        return response.json()[0]['generated_text']
    else:
        return f"❌ שגיאה מהבינה: {response.status_code} - {response.text}"

symbol = st.text_input("🔍 הזן סמל מניה (למשל MSFT):", "MSFT")

if st.button("נתח עכשיו"):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="3mo")

    if hist.empty:
        st.error("לא נמצאו נתונים עבור הסמל הזה.")
    else:
        hist = hist.dropna()
        rsi_series = ta.momentum.RSIIndicator(close=hist['Close']).rsi()

        last_price = hist['Close'][-1]
        support = hist['Close'].min()
        resistance = hist['Close'].max()
        range_mid = (support + resistance) / 2
        rsi_now = rsi_series.iloc[-1]

        st.subheader("📌 ניתוח טכני")
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

        st.subheader("🤖 חוות דעת בינה מלאכותית חינמית")
        with st.spinner("הבינה מנתחת את המצב..."):
            gpt_result = get_ai_analysis(symbol, last_price, support, resistance, rsi_now)
            st.info(gpt_result)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='מחיר'))
        fig.add_trace(go.Scatter(x=rsi_series.index, y=rsi_series, mode='lines', name='RSI', yaxis='y2'))
        fig.add_hline(y=support, line=dict(color='green', dash='dot'))
        fig.add_hline(y=resistance, line=dict(color='red', dash='dot'))
        fig.update_layout(
            yaxis=dict(title='מחיר'),
            yaxis2=dict(title='RSI', overlaying='y', side='right', showgrid=False),
            title=f"גרף מחיר + RSI עבור {symbol}"
        )
        st.plotly_chart(fig, use_container_width=True)
