# -----------------------------
# Advanced AI Sustainability Insight
# -----------------------------

st.subheader("🤖 Advanced AI Sustainability Insight")

# Sidebar customization
st.sidebar.markdown("### 🎛 Insight Customization")
risk_preference = st.sidebar.selectbox(
    "Investor Risk Profile",
    ["Conservative", "Balanced", "Aggressive"]
)

analysis_depth = st.sidebar.selectbox(
    "Insight Detail Level",
    ["Standard", "Deep Analysis"]
)

# Risk Classification
if volatility < 0.20:
    risk_label = "Low Risk"
elif volatility < 0.35:
    risk_label = "Moderate Risk"
else:
    risk_label = "High Risk"

# ESG Rating Tier
if esg_score >= 75:
    rating = "Sustainability Leader 🟢"
elif esg_score >= 55:
    rating = "Sustainability Stable 🟡"
else:
    rating = "Sustainability Risk 🔴"

# Risk-Adjusted Performance Comment
if sharpe_ratio > 1.5:
    performance_comment = "strong risk-adjusted performance"
elif sharpe_ratio > 0.8:
    performance_comment = "moderate risk-adjusted efficiency"
else:
    performance_comment = "weak risk-adjusted return structure"

# Investor Alignment Logic
alignment_comment = ""

if risk_preference == "Conservative":
    if volatility < 0.25:
        alignment_comment = "This stock aligns well with conservative investors seeking stability."
    else:
        alignment_comment = "Volatility levels may exceed conservative investor comfort."
elif risk_preference == "Balanced":
    alignment_comment = "This stock may suit balanced portfolios combining growth and stability."
else:
    alignment_comment = "Higher volatility could benefit aggressive investors targeting alpha."

# Core Insight
st.markdown(f"""
### 📊 Company Overview: {company}

**Sector:** {sector}  
**Risk Category:** {risk_label}  
**ESG Proxy Score:** {round(esg_score,2)} / 100  
**ESG Rating Tier:** {rating}  

---

### 📈 Financial Signal Summary

• Annual Return: **{round(mean_return*100,2)}%**  
• Annual Volatility: **{round(volatility,3)}**  
• Sharpe Ratio: **{round(sharpe_ratio,2)}**  

The company demonstrates **{performance_comment}**, indicating how efficiently it converts risk into returns.

---

### 🎯 Investor Fit Analysis

{alignment_comment}

---
""")

# Deep Analysis Layer
if analysis_depth == "Deep Analysis":

    stability_score = vol_score * 100
    growth_score = return_score * 100
    efficiency_score = sharpe_score * 100

    st.markdown(f"""
### 🔬 Deep ESG Signal Breakdown

**Stability Component (Volatility-Based):** {round(stability_score,1)}  
Higher score indicates controlled downside fluctuations.

**Growth Component (Return-Based):** {round(growth_score,1)}  
Captures long-term appreciation strength.

**Efficiency Component (Sharpe-Based):** {round(efficiency_score,1)}  
Measures risk-adjusted capital allocation efficiency.

---

### 🧠 AI Interpretation

From a proxy ESG standpoint, {company} reflects market-perceived governance quality through volatility discipline and capital efficiency.

Lower volatility often correlates with:
- Strong governance
- Predictable operations
- Institutional investor confidence

Higher Sharpe ratios indicate:
- Efficient capital management
- Strategic risk positioning

Overall, the sustainability outlook suggests a **{rating}** profile within the {sector} sector.
""")
