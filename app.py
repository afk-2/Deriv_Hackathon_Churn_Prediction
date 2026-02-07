import streamlit as st
import pandas as pd
import plotly.express as px
import time  
import google.generativeai as genai

# ==========================================
# 1. AI SETUP (Keep at the Top)
# ==========================================
genai.configure(api_key="AIzaSyDVlsn48uQ2TUEh4eZK-83k3AG1YwkOwJo")
model = genai.GenerativeModel('gemini-3-flash-preview')

# def generate_ai_response(partner_data, strategy_type):
#     drivers = partner_data['Top_Risk_Drivers']
#     region = partner_data['Region']
#     tier = partner_data['Partner_Tier']
#     churn_prob = f"{partner_data['churn_probability']:.1%}"
    
#     prompt = f"""
#     You are an expert Partner Relationship Manager. 
#     A partner ({partner_data['Partner_ID']}) has a {churn_prob} churn risk.
    
#     Context:
#     - Region: {region}
#     - Tier: {tier}
#     - Risk Drivers: {drivers}
    
#     Task: 
#     Generate a {strategy_type}. 
#     - If it's an email, include a professional subject line.
#     - If it's a call script, provide talking points for a 10-minute sync.
#     - Address the specific Risk Drivers identified by the AI model.
#     """
#     try:
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         return f"⚠️ AI Error: {str(e)}"

def generate_ai_response(partner_data, strategy_type):
    drivers = partner_data['Top_Risk_Drivers']
    region = partner_data['Region']
    tier = partner_data['Partner_Tier']
    churn_prob = f"{partner_data['churn_probability']:.1%}"

    # Create specific instructions for each button
    if "Email" in strategy_type:
        specific_instruction = "Write ONLY a professional email draft. Include a subject line. Address the risk drivers directly."
    elif "Call" in strategy_type:
        specific_instruction = "Provide ONLY a structured 10-minute call script with bullet points for the conversation. Focus on resolving the risk drivers."
    else: # Offer Incentive
        specific_instruction = "Suggest ONLY a specific incentive package (e.g., credits, bonuses, or tier upgrades) tailored to this partner's tier and region to prevent churn."

    prompt = f"""
    You are an expert Partner Relationship Manager. 
    A partner ({partner_data['Partner_ID']}) has a {churn_prob} churn risk.
    
    Context:
    - Region: {region}
    - Tier: {tier}
    - Risk Drivers: {drivers}
    
    Task: 
    {specific_instruction}

    CRITICAL RULES:
    1. Output ONLY the requested {strategy_type} text. 
    2. Do NOT provide alternative options or introductory commentary.
    3. Use the Risk Drivers ({drivers}) to make the content personalized and actionable.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

# ... (Existing load_data and Sidebar code) ...

# 1. SETUP & STYLE
st.set_page_config(page_title="Churn Prediction", layout="wide", page_icon="🛡️")

# Custom CSS for "Pro" Look
st.markdown("""
<style>
    .metric-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B; 
        color: white;
    }
    .email-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# 2. LOAD DATA
@st.cache_data
def load_data():
    try:
        return pd.read_csv("streamlit_ready_churn_dashboard.csv")
    except:
        return pd.DataFrame() # Return empty if error

df = load_data()

if df.empty:
    st.error("⚠️ Data not found! Please run 'chrun_predictor.py' first.")
    st.stop()

# 3. SIDEBAR: MANAGER PROFILE
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.markdown("### 👋 Welcome, Alex")
    st.caption("Senior Partner Manager")
    st.markdown("---")
    
    st.markdown("**⚡ System Status**")
    st.success("✅ Model: XGBoost v2.1")
    st.info("🔄 Last Update: Just Now")
    
    st.markdown("---")
    st.markdown("**🎯 Monthly Targets**")
    st.progress(0.75, text="Churn Retention Goal")

# 4. DASHBOARD HEADER
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.title("🛡️ Partner Guard AI")
    st.markdown("### *Advanced Early Warning & Intervention System*")

st.markdown("---")

# 5. TOP LEVEL METRICS (With "Trend" Simulation for Effect)
total_partners = len(df)
high_risk_partners = len(df[df['risk_tier'] == 'HIGH'])
avg_churn_prob = df['churn_probability'].mean()
revenue_at_risk = high_risk_partners * 5200 # Simulated $

col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Partners", total_partners, "12 New this month")
col2.metric("🔥 High Priority Alerts", high_risk_partners, "-2 from yesterday", delta_color="inverse")
col3.metric("Avg Churn Risk", f"{avg_churn_prob:.1%}", "stable")
col4.metric("💰 Rev. at Risk", f"${revenue_at_risk:,.0f}", "Requires Action")

st.markdown("---")

# 6. MAIN WORKSPACE TABS
tab1, tab2, tab3 = st.tabs(["🚨 Triage Board", "🧬 AI Partner Deep Dive", "🌍 Strategic Overview"])

# --- TAB 1: TRIAGE BOARD ---
with tab1:
    st.subheader("📋 Priority Action List")
    st.caption("Partners requiring immediate intervention based on predictive risk scoring.")
    
    # Filter for High Risk
    action_df = df[df['risk_tier'].isin(['HIGH', 'MEDIUM'])].sort_values('churn_probability', ascending=False)
    
    st.dataframe(
        action_df[['Partner_ID', 'Region', 'Partner_Tier', 'churn_probability', 'Top_Risk_Drivers', 'Recommended_Action']],
        column_config={
            "churn_probability": st.column_config.ProgressColumn(
                "Risk Probability", format="%.2f", min_value=0, max_value=1
            ),
            "Top_Risk_Drivers": st.column_config.TextColumn("Primary Risk Factors"),
            "Recommended_Action": st.column_config.TextColumn("AI Recommendation"),
        },
        use_container_width=True,
        hide_index=True,
        height=400
    )

# # --- TAB 2: AI PARTNER DEEP DIVE (THE IMPRESSIVE PART) ---

with tab2:
    st.subheader("🧬 AI Diagnostic & Intervention Center")
    
    # Selection logic must happen BEFORE calling the data
    selected_partner = st.selectbox("Select Partner for Analysis:", df['Partner_ID'].unique())
    
    # Define partner_data AFTER selection
    partner_data = df[df['Partner_ID'] == selected_partner].iloc[0]

    col_left, col_right = st.columns([1, 1])

    with col_left:
        # (Existing Metrics and Risk Driver display code)
        st.info(f"Analysis for {selected_partner}")
        st.metric("Churn Probability", f"{partner_data['churn_probability']:.1%}")
        st.write("**Top Risk Factors:**", partner_data['Top_Risk_Drivers'])

    with col_right:
        st.success("🤖 **AI Co-Pilot Action Center**")
        
        # 1. Define action_type first
        action_type = st.radio(
            "Choose Strategy:", 
            ["📧 Email Draft", "📞 Call Script", "🎁 Offer Incentive"], 
            horizontal=True
        )

        # 2. Use action_type and partner_data in the button
        if st.button(f"Generate {action_type}"):
            with st.spinner("Gemini is synthesizing behavioral trends..."):
                final_text = generate_ai_response(partner_data, action_type)
                st.markdown(f"<div class='email-box'>{final_text}</div>", unsafe_allow_html=True)
                st.balloons()

# --- TAB 3: STRATEGIC OVERVIEW ---
with tab3:
    st.subheader("🌍 Portfolio Heatmap")
    
    heatmap_data = df.groupby(['Region', 'Partner_Tier'])['churn_probability'].mean().reset_index()
    fig = px.density_heatmap(
        heatmap_data, x='Region', y='Partner_Tier', z='churn_probability', 
        text_auto='.0%', color_continuous_scale="Reds", title="Risk Concentration"
    )
    st.plotly_chart(fig, use_container_width=True)

