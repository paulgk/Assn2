import streamlit as st
from agents import process_customer

# -----------------------------------------------------------
# Initialize session state
# -----------------------------------------------------------
if "applications" not in st.session_state:
    st.session_state.applications = []

if "current_application" not in st.session_state:
    st.session_state.current_application = None

# -----------------------------------------------------------
# Helper functions
# -----------------------------------------------------------

def status_badge(status):
    """Return colored HTML badge for Approved / Rejected / Pending."""
    if status.lower() == "approved":
        color = "#2ecc71"  # green
    elif status.lower() == "rejected":
        color = "#e74c3c"  # red
    else:
        color = "#f1c40f"  # yellow

    return f"""
        <span style="
            background:{color};
            padding:4px 10px;
            border-radius:12px;
            color:white;
            font-weight:600;">
            {status}
        </span>
    """


def card(title, content):
    """Reusable card component."""
    return f"""
        <div style="
            border:1px solid #DDD;
            padding:15px;
            border-radius:10px;
            margin-top:10px;
            background:#fafafa;">
            <h4 style='margin-bottom:8px;'>{title}</h4>
            <div>{content}</div>
        </div>
    """

# -----------------------------------------------------------
# Evaluate Customer
# -----------------------------------------------------------
def evaluate_customer(customer_input):
    with st.spinner("🔎 Evaluating customer…"):
        result = process_customer(customer_input)

    st.session_state.current_application = {
        "customer": customer_input,
        "customer_name": result.get("customer_name"),
        "nationality": result.get("nationality"),
        "pr_status": result.get("pr_status"),
        "ai_decision": result.get("decision", "Pending").capitalize(),
        "risk": result.get("risk"),
        "rate": result.get("rate"),
        "memo": result.get("output"),
    }


# -----------------------------------------------------------
# Save officer decision to history
# -----------------------------------------------------------
def save_officer_decision(choice):
    app = st.session_state.current_application
    if not app:
        st.error("No active evaluation.")
        return

    st.session_state.applications.append({
        **app,
        "decision": choice,
    })

    st.success(f"Loan Officer Decision Saved: {choice}")
    st.session_state.current_application = None


# -----------------------------------------------------------
# MAIN UI
# -----------------------------------------------------------
st.title("🏦 Loan Evaluation Dashboard")
st.write("Evaluate a customer's loan eligibility using AI + officer review.")

st.divider()

customer_input = st.text_input("🔍 Enter Customer ID or Name")

colA, colB = st.columns([1,0.4])
with colA:
    if st.button("Evaluate Loan", use_container_width=True):
        if not customer_input.strip():
            st.warning("Please enter a valid name or ID.")
        else:
            evaluate_customer(customer_input)

# -----------------------------------------------------------
# Show AI evaluation block
# -----------------------------------------------------------
app = st.session_state.current_application

if app:
    st.subheader("📌 Customer Summary")

    st.markdown(card(
        "Customer Details",
        f"""
        <b>Name:</b> {app['customer_name']}<br>
        <b>Nationality:</b> {app['nationality']}<br>
        <b>PR Status:</b> {app['pr_status']}<br>
        """
    ), unsafe_allow_html=True)

    # -------- AI Decision Summary --------
    st.subheader("🤖 AI Evaluation Summary")

    badge_html = status_badge(app["ai_decision"])
    st.markdown(card(
        "AI Decision",
        f"""
        <b>Status:</b> {badge_html}<br><br>
        <b>Risk Level:</b> {app['risk']}<br>
        <b>Suggested Interest Rate:</b> {app['rate']}
        """
    ), unsafe_allow_html=True)

    # -------- Formal Letter --------
    st.subheader("📄 AI-Generated Formal Letter")
    st.markdown(
        f"""
        <div style="
            padding:15px;
            border:1px solid #ccc;
            background:white;
            border-radius:10px;">
            {app["memo"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------- Officer Review --------
    st.subheader("🧑‍💼 Loan Officer Decision")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✔️ Approve Loan", use_container_width=True):
            save_officer_decision("Approved")

    with col2:
        if st.button("❌ Reject Loan", use_container_width=True):
            save_officer_decision("Rejected")

    st.divider()


# -----------------------------------------------------------
# SIDEBAR DASHBOARD
# -----------------------------------------------------------
st.sidebar.title("📊 Loan Dashboard")

apps = st.session_state.applications

# Stats
approved = sum(1 for a in apps if a["decision"] == "Approved")
rejected = sum(1 for a in apps if a["decision"] == "Rejected")
total = len(apps)

st.sidebar.metric("Total Evaluations", total)
st.sidebar.metric("Approved", approved)
st.sidebar.metric("Rejected", rejected)

st.sidebar.write("---")
st.sidebar.subheader("📁 Recent Applications")

for app in reversed(apps[-10:]):
    st.sidebar.markdown(
        card(
            f"{app['customer_name']} ({app['customer']})",
            f"""
            {status_badge(app['decision'])}<br><br>
            <b>Nationality:</b> {app['nationality']}<br>
            <b>PR Status:</b> {app['pr_status']}<br>
            <b>Risk:</b> {app['risk']}<br>
            <b>Rate:</b> {app['rate']}<br>
            """
        ),
        unsafe_allow_html=True,
    )
