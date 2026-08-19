import streamlit as st
import pandas as pd
import os
from google.genai as genai

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Life-OS | Digital Wellbeing",
    page_icon="🧠",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

.hero {
    padding: 25px 30px;
    border-radius: 18px;
    margin-bottom: 25px;
    border: 1px solid rgba(255,255,255,0.08);
    background: linear-gradient(
        135deg,
        rgba(34,211,238,0.10),
        rgba(99,102,241,0.08)
    );
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.hero-subtitle {
    font-size: 17px;
    opacity: 0.7;
}

.kpi-card {
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.035);
    min-height: 135px;
}

.kpi-label {
    font-size: 14px;
    opacity: 0.65;
    margin-bottom: 10px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 750;
}

.kpi-small {
    font-size: 13px;
    opacity: 0.65;
    margin-top: 7px;
}

.section-title {
    font-size: 23px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 10px;
}

.coach-box {
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(34,211,238,0.18);
    background: rgba(34,211,238,0.04);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

df = pd.read_csv(
    os.path.join(BASE_DIR, "screentime.csv")
)

# =====================================================
# HERO
# =====================================================

st.markdown("""
<div class="hero">

<div class="hero-title">🧠 Life-OS</div>

<div class="hero-subtitle">
Your AI-powered digital wellbeing command center.
Track your screen time. Understand your habits. Reclaim your time.
</div>

</div>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("⚙️ Life-OS Controls")

dates = sorted(df["Date"].unique())

selected_date = st.sidebar.selectbox(
    "📅 Select Day",
    dates
)

# Shareable Accountability Link
st.sidebar.divider()

st.sidebar.subheader("🔗 Accountability")

st.query_params["date"] = selected_date

share_link = (
    f"http://localhost:8501/?date={selected_date}"
)

st.sidebar.code(
    share_link,
    language="text"
)

st.sidebar.caption(
    "Share this link to show this day's stats."
)


daily_goal = st.sidebar.slider(
    "🎯 Daily Screen-Time Goal",
    min_value=60,
    max_value=600,
    value=240,
    step=15
)

st.sidebar.divider()

st.sidebar.caption(
    "Life-OS helps you understand where your digital time goes."
)

# =====================================================
# SELECTED DAY
# =====================================================

daily_data = df[df["Date"] == selected_date]

total_minutes = daily_data["Minutes_Used"].sum()

hours = total_minutes // 60
minutes = total_minutes % 60

screen_time = f"{hours}h {minutes}m"

# =====================================================
# APP USAGE
# =====================================================

app_usage = (
    daily_data
    .groupby("App_Name")["Minutes_Used"]
    .sum()
    .sort_values(ascending=False)
)

top_app = app_usage.idxmax()
top_app_minutes = app_usage.max()

# =====================================================
# GOAL
# =====================================================

difference = total_minutes - daily_goal

if daily_goal > 0:
    goal_percentage = min(
        int((total_minutes / daily_goal) * 100),
        100
    )
else:
    goal_percentage = 0

# =====================================================
# KPI ROW
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="kpi-card">

    <div class="kpi-label">
    📱 TOTAL SCREEN TIME
    </div>

    <div class="kpi-value">
    """ + screen_time + """
    </div>

    <div class="kpi-small">
    Selected day
    </div>

    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="kpi-card">

    <div class="kpi-label">
    🔥 MOST USED APP
    </div>

    <div class="kpi-value">
    """ + top_app + """
    </div>

    <div class="kpi-small">
    """ + str(top_app_minutes) + """ minutes
    </div>

    </div>
    """, unsafe_allow_html=True)

with col3:

    status = "Over goal" if difference > 0 else "Within goal"

    st.markdown("""
    <div class="kpi-card">

    <div class="kpi-label">
    🎯 DAILY GOAL
    </div>

    <div class="kpi-value">
    """ + f"{difference:+} min" + """
    </div>

    <div class="kpi-small">
    """ + status + """
    </div>

    </div>
    """, unsafe_allow_html=True)

# =====================================================
# GOAL PROGRESS
# =====================================================

st.markdown(
    '<div class="section-title">🎯 Goal Progress</div>',
    unsafe_allow_html=True
)

st.progress(goal_percentage / 100)

if total_minutes > daily_goal:

    st.warning(
        f"⚠️ You are {total_minutes - daily_goal} minutes "
        f"over your daily goal."
    )

else:

    st.success(
        f"✅ You still have {daily_goal - total_minutes} "
        f"minutes before reaching your goal."
    )

# =====================================================
# 14 DAY TREND
# =====================================================

st.markdown(
    '<div class="section-title">📈 14-Day Screen Time Trend</div>',
    unsafe_allow_html=True
)

daily_usage = (
    df.groupby("Date")["Minutes_Used"]
    .sum()
)

st.line_chart(daily_usage)

# =====================================================
# CATEGORY ANALYSIS
# =====================================================

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        '<div class="section-title">📊 Category Breakdown</div>',
        unsafe_allow_html=True
    )

    category_summary = (
        daily_data
        .groupby("Category")["Minutes_Used"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(category_summary)

with col2:

    st.markdown(
        '<div class="section-title">📱 App Usage</div>',
        unsafe_allow_html=True
    )

    st.bar_chart(app_usage)

# =====================================================
# AI LIFE COACH
# =====================================================

st.divider()

st.markdown(
    '<div class="section-title">🤖 AI Life Coach</div>',
    unsafe_allow_html=True
)

daily_summary = category_summary.to_string()

api_key = os.getenv("GEMINI_API_KEY")

if api_key:

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are Life-OS, a brutal-but-fair holistic productivity
and digital wellbeing coach.

Analyze the user's screen-time data for {selected_date}.

Total screen time:
{total_minutes} minutes

Daily goal:
{daily_goal} minutes

Category-wise usage:

{daily_summary}

Rules:

1. Identify the biggest sources of screen usage.
2. Separate productive usage from potentially wasteful usage.
3. Never give generic advice such as "use your phone less."
4. Suggest specific real-world replacements.
5. Recommend physical activities, walking, reading,
   meal preparation, hobbies, offline study or social activities.
6. Be direct and honest but never insulting.
7. Give exactly 3 practical actions for today.
8. Focus on realistic lifestyle changes.

Format:

### Reality Check

### Biggest Time Leak

### What To Replace It With

### 3 Actions For Today
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        st.markdown(
            '<div class="coach-box">',
            unsafe_allow_html=True
        )

        st.markdown(response.text)

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    except Exception as e:

        st.error(
            f"Gemini API Error: {e}"
        )

else:

    st.warning(
        "⚠️ Gemini API key not configured."
    )

# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "Life-OS • Track less. Live more. 🧠"
) 
