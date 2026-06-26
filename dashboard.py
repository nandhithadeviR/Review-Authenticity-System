import streamlit as st
import requests
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Review Authenticity Analyser", layout="wide")

st.title("🛡️ Intelligent Review Authenticity Analyser")
st.markdown("Analyze review reliability across any e-commerce, hospitality, or digital application platform.")

# Setup Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Analysis Input")
    review_text = st.text_area("Paste Review Text Here:", height=150, 
                               placeholder="Type or paste the review text you want to evaluate...")
    
    domain = st.selectbox("Domain Type", ["Product", "Hotel", "Restaurant", "Apps"])
    platform = st.text_input("Source Platform Name:", placeholder="e.g., Amazon, Tripadvisor, Google Maps")
    
    # Mocking historical context for demo similarity check
    simulate_bot_farm = st.checkbox("Simulate duplicate pattern detection (Bot-Farm check)")
    historical_data = []
    if simulate_bot_farm:
        historical_data = [review_text] * 3  # Feeds identical text to trigger the match rule

    if st.button("Run Diagnostic Check"):
        if review_text:
            payload = {
                "text": review_text,
                "domain": domain,
                "platform": platform if platform else "Generic",
                "historical_context": historical_data
            }
            try:
                response = requests.post("http://127.0.0.1:8000/analyze", json=payload).json()
                st.session_state['result'] = response
            except Exception as e:
                st.error(f"Could not connect to analysis backend API: {e}")
        else:
            st.warning("Please enter some text to evaluate.")

with col2:
    st.subheader("Diagnostic Results")
    if 'result' in st.session_state:
        res = st.session_state['result']
        score = res['trust_score']
        
        # Color coding metrics
        if score >= 75:
            st.success(f"Trust Score: {score}/100 — {res['status']}")
        elif score >= 50:
            st.warning(f"Trust Score: {score}/100 — {res['status']}")
        else:
            st.error(f"Trust Score: {score}/100 — {res['status']}")
            
        st.write("**Flagged Indicators:**")
        for reason in res['reasons']:
            st.write(f"- {reason}")
            
        # Mock Comparative Analytics Chart
        st.write("---")
        st.subheader("Cross-Platform Integrity Insights")
        mock_chart_data = pd.DataFrame({
            'Platform': [res['platform'], 'Competitor A', 'Competitor B'],
            'Average Platform Trust Integrity': [score, 78, 42]
        })
        fig = px.bar(mock_chart_data, x='Platform', y='Average Platform Trust Integrity', range_y=[0,100], color='Average Platform Trust Integrity', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Awaiting input data. Enter text on the left pane and run analysis.")
