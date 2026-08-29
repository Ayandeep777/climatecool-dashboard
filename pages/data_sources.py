import streamlit as st

def render(app_data):
    st.title("📊 Data Sources & Assumptions")
    st.write("Data provenance and assumptions")
    
    provenance = app_data.get('DATA_PROVENANCE', pd.DataFrame())
    if not provenance.empty:
        st.dataframe(provenance, use_container_width=True)
    else:
        st.info("No provenance data available")
