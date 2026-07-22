import sys
import os
import json
import streamlit as st
import pandas as pd
import numpy as np

# Add project root to sys.path for module resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sentinel.risk_engine import RiskEngine

# Page Config
st.set_page_config(page_title="SentinelMCP Security Dashboard", layout="wide", page_icon="🛡️")

# App Header
st.title("🛡️ SentinelMCP Runtime Behavioral Security & SRI Engine Status")
st.markdown("> **CrowdStrike for AI Agents** — Continuous Runtime Verification & Policy Enforcement Layer")

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTACKS_DIR = os.path.join(BASE_DIR, "data", "attacks")
EVAL_FILE = os.path.join(BASE_DIR, "evaluation", "evaluation_results.json")

# Initialize Risk Engine
risk_engine = RiskEngine()

# Sidebar
st.sidebar.header("Data Source Configuration")
load_option = st.sidebar.radio("Input Source", ["Load Sample Session", "Raw JSON Input"])

selected_trace_data = None

if load_option == "Load Sample Session":
    st.sidebar.subheader("Sample Traces")
    
    if not os.path.exists(ATTACKS_DIR):
        st.sidebar.warning(f"Attacks directory not found at {ATTACKS_DIR}.")
    else:
        files = []
        for root, dirs, filenames in os.walk(ATTACKS_DIR):
            for filename in filenames:
                if filename.endswith('.json'):
                    files.append(os.path.join(root, filename))
                    
        if files:
            file_options = {os.path.basename(f): f for f in files}
            selected_file = st.sidebar.selectbox("Select Trace", list(file_options.keys()))
            try:
                with open(file_options[selected_file], 'r') as f:
                    selected_trace_data = json.load(f)
            except Exception as e:
                st.sidebar.error(f"Error loading trace: {e}")
        else:
            st.sidebar.warning("No JSON trace files found in data/attacks/")
else:
    raw_json = st.sidebar.text_area("Paste Trace JSON here:")
    if raw_json:
        try:
            selected_trace_data = json.loads(raw_json)
        except json.JSONDecodeError:
            st.sidebar.error("Invalid JSON format.")

# Main Panel Tabs
tab1, tab2 = st.tabs(["Security Analysis", "IEEE Model Comparison"])

with tab1:
    if selected_trace_data:
        # Dynamically evaluate trace via RiskEngine if not pre-evaluated
        if "sri_score" not in selected_trace_data or "components" not in selected_trace_data:
            analysis = risk_engine.evaluate_session(selected_trace_data)
            selected_trace_data["sri_score"] = analysis["sri_score"]
            selected_trace_data["decision"] = analysis["decision"]
            
            vals = analysis["breakdown"]["values"]
            selected_trace_data["components"] = {
                "CD": round(vals.get("CD", 0) * 100, 1),
                "PV": round(vals.get("PV", 0) * 100, 1),
                "TR": round(vals.get("TR", 0) * 100, 1),
                "ST": round(vals.get("ST", 0) * 100, 1),
                "ML": round(vals.get("ML", 0) * 100, 1)
            }
            
            calls = selected_trace_data.get("tool_sequence", selected_trace_data.get("tool_calls", []))
            selected_trace_data["timeline"] = [
                {
                    "step": c.get("step", i + 1),
                    "tool_name": c.get("tool_name", c.get("tool", "unknown")),
                    "arguments": str(c.get("args", c.get("arguments", {}))),
                    "source_trust": c.get("source_trust", 1.0)
                }
                for i, c in enumerate(calls)
            ]
            
            selected_trace_data["audit_log"] = [
                {"check": "Context Drift (CD)", "score": round(vals.get("CD", 0) * 100, 1), "status": "Flagged" if vals.get("CD", 0) > 0.4 else "Normal"},
                {"check": "Policy Violation (PV)", "score": round(vals.get("PV", 0) * 100, 1), "status": "Flagged" if vals.get("PV", 0) > 0.4 else "Normal"},
                {"check": "Tool Transition Risk (TR)", "score": round(vals.get("TR", 0) * 100, 1), "status": "Flagged" if vals.get("TR", 0) > 0.4 else "Normal"},
                {"check": "Source Trust (ST)", "score": round(vals.get("ST", 0) * 100, 1), "status": "Flagged" if vals.get("ST", 0) > 0.4 else "Normal"},
                {"check": "ML Structural Detector (ML)", "score": round(vals.get("ML", 0) * 100, 1), "status": "Flagged" if vals.get("ML", 0) > 0.4 else "Normal"}
            ]

        st.header("Executive Risk Analysis")
        
        # 1. Executive Risk Gauge
        sri_score = selected_trace_data.get("sri_score", 0)
        decision = selected_trace_data.get("decision", "UNKNOWN")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Final SRI Score", value=f"{sri_score:.1f}/100" if isinstance(sri_score, float) else f"{sri_score}/100", delta=None)
        
        with col2:
            color = "green" if decision == "SAFE" else "blue" if decision == "MONITOR" else "orange" if decision == "SUSPICIOUS" else "red"
            st.markdown(f"### Decision Badge: <span style='color:{color}'>{decision}</span>", unsafe_allow_html=True)
            
        st.divider()
        
        # 2. Decomposable Component Breakdown
        st.subheader("Component Breakdown ($CD$, $PV$, $TR$, $ST$, $ML$)")
        components = selected_trace_data.get("components", {})
        
        cd_val = components.get("CD", 0)
        pv_val = components.get("PV", 0)
        tr_val = components.get("TR", 0)
        st_val = components.get("ST", 0)
        ml_val = components.get("ML", 0)
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Command Danger (CD)", cd_val)
        c1.progress(min(1.0, cd_val / 100.0))
        
        c2.metric("Param Vulnerability (PV)", pv_val)
        c2.progress(min(1.0, pv_val / 100.0))
        
        c3.metric("Trust Reputation (TR)", tr_val)
        c3.progress(min(1.0, tr_val / 100.0))
        
        c4.metric("State Transition (ST)", st_val)
        c4.progress(min(1.0, st_val / 100.0))
        
        c5.metric("Machine Learning (ML)", ml_val)
        c5.progress(min(1.0, ml_val / 100.0))
        
        st.divider()
        
        # 3. Tool Call Execution Timeline
        st.subheader("Tool Call Execution Timeline")
        timeline = selected_trace_data.get("timeline", [])
        if timeline:
            df_timeline = pd.DataFrame(timeline)
            st.dataframe(df_timeline, use_container_width=True)
        else:
            st.info("No timeline data available.")
            
        st.divider()
        
        # 4. Policy & Evidence Audit Log
        st.subheader("Policy & Evidence Audit Log")
        audit_log = selected_trace_data.get("audit_log", [])
        if audit_log:
            df_audit = pd.DataFrame(audit_log)
            st.dataframe(df_audit, use_container_width=True)
        else:
            st.info("No audit log available.")
    else:
        st.info("Please load or input a session trace from the sidebar to view security analysis.")

with tab2:
    st.header("IEEE 4-Model Ablation Comparison")
    
    # Load evaluation results
    if os.path.exists(EVAL_FILE):
        try:
            with open(EVAL_FILE, 'r') as f:
                eval_data = json.load(f)
            
            st.write("Ablation Summary Table")
            
            # Format clean dataframe for tabular display
            table_rows = []
            chart_rows = []
            for item in eval_data:
                model_name = item.get("Model")
                datasets = item.get("Datasets", {})
                for ds_name, metrics in datasets.items():
                    f1 = metrics.get("F1", 0.0)
                    auc = metrics.get("AUC", 0.0)
                    ci = metrics.get("F1_CI", [0.0, 0.0])
                    
                    table_rows.append({
                        "Model": model_name,
                        "Dataset": ds_name,
                        "Precision": round(metrics.get("Precision", 0.0), 3),
                        "Recall": round(metrics.get("Recall", 0.0), 3),
                        "F1-Score": round(f1, 3),
                        "95% CI": f"[{ci[0]:.3f}, {ci[1]:.3f}]" if isinstance(ci, list) and len(ci)==2 else "-",
                        "AUC": round(auc, 3) if auc is not None else "-"
                    })
                    
                    chart_rows.append({
                        "Model": model_name,
                        "Dataset": ds_name,
                        "F1-Score": round(f1, 3)
                    })
                    
            df_table = pd.DataFrame(table_rows)
            st.dataframe(df_table, use_container_width=True)
            
            st.subheader("F1-Score Comparison Chart Across Datasets")
            df_chart = pd.DataFrame(chart_rows)
            df_pivot = df_chart.pivot(index="Model", columns="Dataset", values="F1-Score")
            st.bar_chart(df_pivot)
            
        except Exception as e:
            st.error(f"Error loading evaluation results: {e}")
    else:
        st.warning(f"Evaluation file not found at {EVAL_FILE}.")
