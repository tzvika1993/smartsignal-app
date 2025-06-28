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

# התחברות מאובטחת ל־OpenAI (מ־secrets של Streamlit)
client = openai.OpenAI(api_key=st.secrets "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")

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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

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

        # חוות דעת GPT
        st.subheader("🧠 חוות דעת GPT")
        with st.spinner("GPT מנתח את המצב..."):
            try:
                gpt_result = get_gpt_analysis(symbol, last_price, support, resistance, rsi_now)
                st.success(gpt_result)
            except Exception as e:
                st.error(f"שגיאה בעת קבלת תחזית GPT: {e}")

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
