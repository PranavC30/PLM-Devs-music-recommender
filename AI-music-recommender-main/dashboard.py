import streamlit as st
import pandas as pd
import plotly.express as px

def render_dashboard(agent):
    st.header("📈 Q-Learning Intelligence Dashboard")
    st.markdown("Here you can observe the actual AI learning matrices adjusting to your taste.")
    
    q_table = agent.q_table
    
    if not q_table:
        st.info("The Q-Table is currently empty. Start interacting with the recommendations to train the AI.")
        return
        
    # Prepare data for rendering
    data = []
    actions = agent.actions
    for state, q_vals in q_table.items():
        row = {'State': state}
        for act in actions:
            row[act] = q_vals.get(act, 0.0)
        data.append(row)
        
    df = pd.DataFrame(data)
    
    st.markdown("### 🗺️ Q-Value Heatmap")
    st.write("This shows how strongly the AI associates different states with specific genres over time.")
    
    # We will reshape for a Plotly Heatmap
    df_melted = df.melt(id_vars='State', var_name='Genre', value_name='Q-Value')
    
    fig = px.density_heatmap(df_melted, x="Genre", y="State", z="Q-Value",
                             histfunc="avg", text_auto=True, 
                             color_continuous_scale="Viridis",
                             title="State-Genre Value Matrix")
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Show tabular data
    st.markdown("### 📊 Raw Tabular Memory")
    st.dataframe(df, use_container_width=True)
