import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import ta
import openai

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

openai.api_key = "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"

def get_gpt_analysis(symbol, price, support, resistance, rsi):
    prompt = f"""
    אתה אנליסט מומחה לשוק ההון.
    נתח את מניית {symbol} בהתבסס על הנתונים הבאים:
    - מחיר נוכחי: {price:.2f}$
    - רמת תמיכה: {support:.2f}$
    - רמת התנגדות: {resistance:.2f}$
    - RSI נוכחי: {rsi:.2f}

    תן חוות דעת טכנית תמציתית והמלצה (קנייה/המתן/מכירה), בטון מקצועי וברור.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

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

        # חוות דעת GPT
        st.subheader("🧠 חוות דעת GPT")
        with st.spinner("GPT מנתח את המצב..."):
            gpt_result = get_gpt_analysis(symbol, last_price, support, resistance, rsi_now)
            st.success(gpt_result)

        # גרף
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
