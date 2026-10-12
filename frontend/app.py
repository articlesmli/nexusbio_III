import streamlit as st
import requests
import os

# Page configuration
st.set_page_config(
    page_title="NexusBio - HITL Research Dashboard",
    layout="wide",
)

# Configuration for local containerized backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Sidebar for Navigation & Authentication Status
st.sidebar.title("NexusBio Control Panel")
st.sidebar.markdown("---")
user_role = st.sidebar.selectbox("User Role", ["Lead Researcher", "Safety Officer", "Auditor"])
st.sidebar.markdown(f"**Authenticated as:** `{user_role}`")
st.sidebar.markdown("**Environment:** `Local Containerized AI Sandbox`")

st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["Active Agent Loops", "Compound HITL Gate", "Audit Trail & History"])

if page == "Active Agent Loops":
    st.title("Active Multi-Agent Orchestration Loops")
    st.markdown("Monitor real-time execution across the Literature Miner (BioGPT), Pathway Synthesizer, and Molecular Design agents.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Active Sessions", value="3", delta="+1 today")
    with col2:
        st.metric(label="BioGPT Chunks Processed", value="1,248", delta="High Accuracy")
    with col3:
        st.metric(label="Pending Approvals", value="2", delta="Action Required", delta_color="inverse")

    st.markdown("---")
    st.subheader("Current Execution State: `sess_93b71a8c`")
    
    # Progress visualization of the cyclical loop
    steps = ["Literature Mining", "Pathway Synthesis", "Molecular Design", "HITL Review"]
    current_step_idx = 2  # Currently waiting at Molecular Design / HITL
    
    st.markdown("### Agent Progress Pipeline")
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        with cols[i]:
            if i < current_step_idx:
                st.success(f"{step}")
            elif i == current_step_idx:
                st.warning(f"{step} (Active)")
            else:
                st.info(f"{step}")

elif page == "Compound HITL Gate":
    st.title("Human-in-the-Loop (HITL) Compound Gate")
    st.markdown("Review and evaluate chemical structures using the local RDKit sandbox backend.")

    # Live Sandbox Testing Section using `requests`
    with st.expander(" Test SMILES via Live FastAPI Sandbox", expanded=True):
        test_smiles = st.text_input("Enter SMILES String", value="CC(=O)OC1=CC=CC=C1C(=O)O")
        if st.button("Evaluate via FastAPI Backend"):
            try:
                payload = {
                    "session_id": "sess_live_test",
                    "compound_id": "CMP-LIVE-01",
                    "smiles": test_smiles,
                    "target_metrics": ["qed", "molecular_weight", "lipinski_violations"]
                }
                response = requests.post(f"{BACKEND_URL}/evaluate-smiles", json=payload, timeout=5)
                if response.status_code == 200:
                    st.success("Successfully connected to FastAPI backend!")
                    st.json(response.json())
                else:
                    st.error(f"Sandbox returned status code {response.status_code}: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"Could not connect to FastAPI backend at {BACKEND_URL}. Ensure your container is running.")

    st.markdown("---")

    # Mock pending compound item workflow
    with st.container():
        st.markdown("### Proposal ID: `CMP-2026-0042`")
        
        col_a, col_b = st.columns([1, 2])
        
        with col_a:
            st.markdown("**SMILES Structure:**")
            st.code("CC(=O)OC1=CC=CC=C1C(=O)O", language="text")
            st.markdown("**Target Pathway:** `COX-2 Inhibition`")
            st.markdown("**Source Literature:** `Local BioGPT Biomedical Base`")

        with col_b:
            st.markdown("**Cheminformatics Validation Metrics (RDKit Sandbox):**")
            metric_cols = st.columns(3)
            metric_cols[0].metric("QED Score", "0.82", "Optimal")
            metric_cols[1].metric("Molecular Weight", "180.16 g/mol", "Valid")
            metric_cols[2].metric("Lipinski Violations", "0", "Passed")

        st.markdown("---")
        
        # Action Buttons
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 4])
        with btn_col1:
            if st.button("Approve Compound", type="primary"):
                st.success("Compound CMP-2026-0042 approved! Written to local audit trail.")
        with btn_col2:
            if st.button("Reject Compound", type="secondary"):
                st.error("Compound rejected and logged for agent feedback loop.")

elif page == "Audit Trail & History":
    st.title("System Audit Trail & State History")
    st.markdown("Immutable record tracking data provenance and local agent decisions.")

    # Mock audit table display
    audit_data = [
        {"Timestamp": "2026-04-06 20:40:00", "Session": "sess_93b71a8c", "Agent": "Literature Miner", "Action": "Queried local BioGPT knowledge base"},
        {"Timestamp": "2026-04-06 20:41:12", "Session": "sess_93b71a8c", "Agent": "Pathway Synthesizer", "Action": "Mapped COX-2 target vector via BioGPT pipeline"},
        {"Timestamp": "2026-04-06 20:42:30", "Session": "sess_93b71a8c", "Agent": "Molecular Design", "Action": "Evaluated SMILES via local RDKit Sandbox"},
    ]
    
    st.table(audit_data)