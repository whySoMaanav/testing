import streamlit as st
from app.database.connection import get_db
from app.services.project_service import ProjectService
from app.components.tables import render_dynamic_table
from app.components.management_tabs import render_management_tabs
from app.utils.config_loader import load_config

st.title("Admin Console")

# A very basic mock admin auth
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if not st.session_state.is_admin:
    st.info("Administrator authentication (Mock for MVP)")
    admin_pw = st.text_input("Admin Password", type="password")
    if st.button("Login"):
        if admin_pw == "admin123": # Mock password
            st.session_state.is_admin = True
            st.rerun()
        else:
            st.error("Invalid credentials.")
else:
    if st.button("Logout"):
        st.session_state.is_admin = False
        st.session_state.pop('admin_selected_project', None)
        st.rerun()
        
    db = next(get_db())
    
    # State to manage if an admin is currently viewing a specific project
    if 'admin_selected_project' not in st.session_state:
        st.session_state.admin_selected_project = None
    if 'admin_df_key_version' not in st.session_state:
        st.session_state.admin_df_key_version = 0
        
    if not st.session_state.admin_selected_project:
        st.subheader("Project Directory")
        projects = ProjectService.get_all_projects(db)
        
        if not projects:
            st.info("No projects found.")
        else:
            data_list = []
            for p in projects:
                p_data = p.get_data()
                p_data['project_id'] = p.project_id
                p_data['db_id'] = p.id
                data_list.append(p_data)
                
            project_fields_config = load_config('project_fields')['fields']
            
            # Build dataframe for native Streamlit rendering
            import pandas as pd
            df = pd.DataFrame(data_list)
            # Select columns to display based on config
            display_cols = ['project_id']
            col_names = {'project_id': 'Project ID'}
            for field in project_fields_config:
                if field['name'] in df.columns and field['name'] != 'project_id':
                    display_cols.append(field['name'])
                    col_names[field['name']] = field['label']
                    
            df_display = df[display_cols].rename(columns=col_names)
            
            st.markdown("<p style='font-size: 15px; font-weight: 600; color: #003865; margin-bottom: 8px;'>Select a project row to manage it.</p>", unsafe_allow_html=True)
            
            # Native Streamlit DataFrame with Selection
            df_key = f"admin_projects_df_{st.session_state.admin_df_key_version}"
            event = st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                # pyrefly: ignore [unexpected-keyword]
                on_select="rerun",
                # pyrefly: ignore [unexpected-keyword]
                selection_mode="single-row",
                # pyrefly: ignore [unexpected-keyword]
                key=df_key
            )
            
            if event and event.selection and len(event.selection.rows) > 0:
                selected_idx = event.selection.rows[0]
                # Get the original project_id from the unsorted df using the selected index
                selected_pid = df.iloc[selected_idx]['project_id']
                st.session_state.admin_selected_project = selected_pid
                st.rerun()
    else:
        project_id = st.session_state.admin_selected_project
        st.subheader(f"Managing Project: {project_id}")
        
        if st.button("← Back to Directory"):
            st.session_state.admin_selected_project = None
            st.session_state.admin_df_key_version += 1
            st.rerun()
            
        render_management_tabs(db, project_id, user="AdminUser", is_admin=True)
