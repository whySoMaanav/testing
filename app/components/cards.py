import streamlit as st

def metric_card(title: str, value: str, delta: str = None):
    """Render a styled metric card."""
    st.markdown(
        f"""
        <div style="
            background-color: #f0f7ff;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 86, 179, 0.08);
            border: 1px solid #cce5ff;
            border-left: 6px solid #0056b3;
            margin-bottom: 20px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(0, 86, 179, 0.15)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0, 86, 179, 0.08)';">
            <h4 style="margin: 0; color: #003865; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">{title}</h4>
            <h2 style="margin: 8px 0 0 0; color: #0056b3; font-size: 38px; font-weight: 800; letter-spacing: -0.02em;">{value}</h2>
            {f'<p style="margin: 8px 0 0 0; color: #008800; font-size: 14px; font-weight: 600;">{delta}</p>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True
    )
