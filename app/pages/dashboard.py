import streamlit as st
import pandas as pd
import altair as alt
from app.database.connection import get_db
from app.services.project_service import ProjectService
from app.services.version_service import VersionService
from app.services.risk_service import RiskService
from app.components.cards import metric_card

st.markdown("""
<div style="padding-bottom: 2rem;">
    <h1 style="font-size: 40px; margin-bottom: 0;">Overview</h1>
    <p style="color: #86868b; font-size: 16px; margin-top: 5px;">Key metrics and risk insights for all AI projects.</p>
</div>
""", unsafe_allow_html=True)

# Get database session
db = next(get_db())

# Fetch basic metrics
projects = ProjectService.get_all_projects(db)
total_projects = len(projects)

total_versions = 0
open_risks = 0
closed_risks = 0

# For charts
status_counts = {"Open": 0, "In Progress": 0, "Mitigated": 0, "Accepted": 0, "Closed": 0}
bu_counts = {}

for p in projects:
    p_data = p.get_data()
    bu = p_data.get('business_unit', 'Unknown')
    bu_counts[bu] = bu_counts.get(bu, 0) + 1
    
    versions = VersionService.get_versions_for_project(db, p.project_id)
    total_versions += len(versions)
    for v in versions:
        risks = RiskService.get_risks_for_version(db, v.id)
        for r in risks:
            r_data = r.get_data()
            status = r_data.get('status', 'Unknown')
            if status in status_counts:
                status_counts[status] += 1
            if status == 'Closed':
                closed_risks += 1
            else:
                open_risks += 1

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Total Projects", str(total_projects))
with col2:
    metric_card("Total Versions", str(total_versions))
with col3:
    metric_card("Active Risks", str(open_risks))
with col4:
    metric_card("Resolved Risks", str(closed_risks))

st.markdown("<br><h3 style='margin-bottom: 1rem;'>Risk & Portfolio Analytics</h3>", unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

# Define an accessible, softer enterprise color scale for statuses
status_colors = alt.Scale(
    domain=['Open', 'In Progress', 'Mitigated', 'Accepted', 'Closed'],
    range=['#D9534F', '#F0AD4E', '#5BC0DE', '#777777', '#5CB85C'] # Muted, accessible bootstrap-like colors
)

with chart_col1:
    with st.container(border=True):
        st.markdown("<h4 style='font-size: 16px; color: #333;'>Risks by Status</h4>", unsafe_allow_html=True)
        if open_risks > 0 or closed_risks > 0:
            df_status = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
            df_status = df_status[df_status['Count'] > 0]
            
            chart1 = alt.Chart(df_status).mark_arc(innerRadius=60, cornerRadius=2).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Status", type="nominal", scale=status_colors, legend=alt.Legend(title="Status")),
                tooltip=['Status', 'Count']
            ).properties(height=320).configure_view(strokeWidth=0).configure(
                background='transparent',
                legend=alt.LegendConfig(labelColor='#333333', titleColor='#333333', labelFontSize=12, titleFontSize=13)
            )
            st.altair_chart(chart1, use_container_width=True, theme=None)
        else:
            st.info("No risks logged yet.")

with chart_col2:
    with st.container(border=True):
        st.markdown("<h4 style='font-size: 16px; color: #333;'>Projects by Business Unit</h4>", unsafe_allow_html=True)
        if total_projects > 0:
            df_bu = pd.DataFrame(list(bu_counts.items()), columns=['Business Unit', 'Count'])
            
            chart2 = alt.Chart(df_bu).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X('Business Unit', sort='-y', axis=alt.Axis(labelAngle=-45, labelColor='#333333', titleColor='#333333', labelFontSize=12, titleFontSize=13)),
                y=alt.Y('Count', axis=alt.Axis(labelColor='#333333', titleColor='#333333', labelFontSize=12, titleFontSize=13, tickMinStep=1)),
                color=alt.value('#4A90E2'), # Softer, professional blue
                tooltip=['Business Unit', 'Count']
            ).properties(height=320).configure_view(strokeWidth=0).configure(
                background='transparent'
            )
            st.altair_chart(chart2, use_container_width=True, theme=None)
        else:
            st.info("No projects created yet.")
