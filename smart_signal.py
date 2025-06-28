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

def get_fake_analysis(symbol, price, support, resistance, rsi):
    if rsi > 70:
        sentiment = "המניה במצב קנייה יתר. עלולה לתקן כלפי מטה."
        recommendation = "המתן להתייצבות לפני קנייה."
    elif rsi < 30:
        sentiment = "המניה במצב מכירת יתר. יתכן פוטנציאל לעלייה."
        recommendation = "שקול קנייה זהירה."
    else:
        sentiment = "RSI נייטרלי. אין איתות מובהק."
        recommendation = "מעקב בלבד בשלב זה."

    if price < support:
        trend = "נמצאת מתחת לרמת התמיכה – סכנת ירידה נוספת."
    elif price > resistance:
        trend = "פרצה את רמת ההתנגדות – מומנטום חיובי."
    else:
        trend = "נעה בין התמיכה להתנגדות – תעלה או תרד בהתאם לשוק."

    return f"""
### ניתוח חכם מדומה (ללא GPT)
- {sentiment}
- {trend}
- המלצה: **{recommendation}**
"""

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

        st.subheader("🧠 תחזית חכמה (ללא GPT)")
        with st.spinner("מנתח את המצב..."):
            gpt_result = get_fake_analysis(symbol, last_price, support, resistance, rsi_now)
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

        # Copilot אינטראקטיבי
        with st.expander("🤖 Copilot – שאל שאלה על המניה"):
            user_q = st.text_input("מה אתה רוצה לדעת על המניה?", key="copilot_q")
            if st.button("🔍 שאל את Copilot"):
                if "למכור" in user_q or "לא כדאי" in user_q:
                    st.warning("Copilot: אם המניה קרובה להתנגדות וה־RSI גבוה – ייתכן שכדאי לשקול המתנה או מכירה.")
                elif "לקנות" in user_q or "לעלות" in user_q:
                    st.success("Copilot: אם RSI נמוך והמניה קרובה לתמיכה – זו עשויה להיות הזדמנות קנייה.")
                elif "סיכון" in user_q:
                    st.info("Copilot: הסיכון גבוה כאשר המניה פרצה רמות תמיכה או כשה־RSI קיצוני.")
                else:
                    st.info("Copilot: אני כאן לעזור! נסה לשאול על קנייה, מכירה, תחזית או סיכון.")
