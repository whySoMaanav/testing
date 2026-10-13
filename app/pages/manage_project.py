import streamlit as st
from app.database.connection import get_db
from app.services.project_service import ProjectService
from app.components.management_tabs import render_management_tabs

st.title("Manage Project")

if 'authenticated_project' not in st.session_state:
    st.session_state.authenticated_project = None

if not st.session_state.authenticated_project:
    st.subheader("Project Owner Authentication")
    with st.form("auth_form"):
        project_id = st.text_input("Project ID")
        access_code = st.text_input("Project Access Code", type="password")
        submitted = st.form_submit_button("Authenticate")
        
        if submitted:
            db = next(get_db())
            if ProjectService.authenticate_project(db, project_id, access_code):
                st.session_state.authenticated_project = project_id
                st.rerun()
            else:
                st.error("Authentication failed. Please check your Project ID and Access Code.")
else:
    project_id = st.session_state.authenticated_project
    st.success(f"Authenticated as Owner of {project_id}")
    if st.button("Logout"):
        st.session_state.authenticated_project = None
        st.rerun()
        
    db = next(get_db())
    render_management_tabs(db, project_id, user=f"Owner-{project_id}", is_admin=False)
