import streamlit as st
import requests

st.set_page_config(page_title="AI Hedge Fund Simulator", page_icon="📈", layout="wide")
st.title("📈 AI Hedge Fund Simulator Dashboard")

st.sidebar.header("Simulation Parameters")
tickers_input = st.sidebar.text_input("Tickers (comma separated)", "AAPL,MSFT,NVDA")
portfolio_value = st.sidebar.number_input("Initial Portfolio Value ($)", value=100000.0)

if st.sidebar.button("Run Simulation"):
    tickers_list = [t.strip() for t in tickers_input.split(",")]
    
    with st.spinner("Running Multi-Agent Simulation..."):
        try:
            response = requests.post(
                "http://localhost:8000/simulate",
                json={"tickers": tickers_list, "portfolio_value": portfolio_value}
            )
            data = response.json()
            st.session_state['sim_data'] = data
            st.success("Simulation Complete!")
        except Exception as e:
            st.error(f"Error connecting to API: {e}. Is FastAPI running?")

tab1, tab2, tab3, tab4 = st.tabs(["Live Portfolio", "Agent Reasoning", "Backtest Results", "Risk Management"])

if 'sim_data' in st.session_state:
    data = st.session_state['sim_data']
    
    with tab1:
        st.header("Portfolio Allocations")
        st.json(data.get("portfolio_decision", {}))
        
    with tab2:
        st.header("Explainable AI - Agent Outputs")
        st.subheader("Macro Analyst")
        st.json(data["agent_outputs"]["macro"])
        
        st.subheader("Technical Analyst")
        st.json(data["agent_outputs"]["technical"])
        
        st.subheader("News Analyst")
        st.json(data["agent_outputs"]["news"])
        
        st.subheader("Quant Analyst")
        st.json(data["agent_outputs"]["quant"])
        
    with tab3:
        st.header("Backtest Results")
        st.info("Historical backtest integration via Backtrader pending data feed connection.")
        
    with tab4:
        st.header("Risk Management")
        st.subheader("Risk Analyst Limits")
        st.json(data["agent_outputs"]["risk"])
else:
    st.info("Run a simulation from the sidebar to view results.")
