import streamlit as st
from app.database.connection import get_db
from app.services.project_service import ProjectService
from app.utils.config_loader import load_config
from app.components.forms import render_dynamic_form, validate_dynamic_form

st.title("Create New Project")

project_fields_config = load_config('project_fields')['fields']

if 'created_project_code' not in st.session_state:
    st.session_state.created_project_code = None
    st.session_state.created_project_id = None

# --- Credentials Modal Dialog (Streamlit 1.34+) ---
def render_credentials_view(proj_id: str, access_code: str):
    st.success("### 🎉 Project Created Successfully!")
    
    st.markdown(f"""
    <div style="background-color: #f0fdf4; border: 2px solid #86efac; border-radius: 10px; padding: 20px; margin: 15px 0;">
        <h4 style="color: #166534; margin-top: 0; font-size: 18px;">⚠️ Save Your Project Credentials Now</h4>
        <p style="color: #166534; font-size: 14px; margin-bottom: 0;">
            You will need both your <b>Project ID</b> and this <b>Access Code</b> to manage or edit your project.<br>
            Due to secure encryption, this passcode <b>cannot be recovered</b> once you leave this page.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Project ID:** `{proj_id}`")
    st.markdown("**Your Secret Access Passcode (Click icon on right to copy):**")
    st.code(access_code, language="text")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🚀 Go to Manage Project (Auto-Log In)", type="primary", key="btn_goto_manage"):
            st.session_state.authenticated_project = proj_id
            st.switch_page("app/pages/manage_project.py")
    with col2:
        if st.button("➕ Create Another Project", key="btn_create_another"):
            st.session_state.created_project_code = None
            st.session_state.created_project_id = None
            st.rerun()

# Check if credentials are already in session state
if st.session_state.created_project_code:
    render_credentials_view(
        st.session_state.created_project_id,
        st.session_state.created_project_code
    )
else:
    placeholder = st.empty()
    with placeholder.container():
        with st.form("create_project_form"):
            form_data = render_dynamic_form(project_fields_config)
            submitted = st.form_submit_button("Create Project")
            
            if submitted:
                errors = validate_dynamic_form(project_fields_config, form_data)
                project_id = form_data.get('project_id')
                if not project_id:
                    errors.append("Project ID is required.")
                    
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    db = next(get_db())
                    # Check if exists
                    existing = ProjectService.get_project(db, project_id)
                    if existing:
                        st.error(f"Project with ID '{project_id}' already exists. Please choose a different Project ID.")
                        st.info("💡 **Need the passcode for an existing project?** An administrator can generate a new passcode anytime from **Admin Console > Select Project > Admin Actions > Generate New Code**.")
                    else:
                        try:
                            project, access_code = ProjectService.create_project(
                                db=db,
                                project_id=project_id,
                                data=form_data,
                                user="PublicUser"
                            )
                            st.session_state.created_project_code = access_code
                            st.session_state.created_project_id = project_id
                            st.session_state.authenticated_project = project_id
                            
                            # Immediately replace form container with credentials view (no st.rerun needed!)
                            placeholder.empty()
                            with placeholder.container():
                                render_credentials_view(project_id, access_code)
                                
                        except Exception as e:
                            st.error(f"Error creating project: {str(e)}")
