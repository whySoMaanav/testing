import streamlit as st
import pandas as pd
from app.services.project_service import ProjectService
from app.services.version_service import VersionService
from app.services.risk_service import RiskService
from app.utils.config_loader import load_config
from app.components.forms import render_dynamic_form, validate_dynamic_form

def render_management_tabs(db, project_id: str, user: str, is_admin: bool = False):
    project = ProjectService.get_project(db, project_id)
    if not project:
        st.error("Project not found.")
        return

    tab_titles = ["Edit Project Details", "Manage Versions", "Manage Risks"]
    if is_admin:
        tab_titles.append("Admin Actions")
        
    tabs = st.tabs(tab_titles)
    
    # --- Edit Project Details ---
    with tabs[0]:
        st.subheader("Project Metadata")
        project_fields_config = load_config('project_fields')['fields']
        
        with st.form("edit_project_form"):
            form_data = render_dynamic_form(project_fields_config, default_values=project.get_data())
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                errors = validate_dynamic_form(project_fields_config, form_data)
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    try:
                        ProjectService.update_project(
                            db=db, 
                            project_id=project_id, 
                            new_data=form_data, 
                            user=user,
                            is_admin=is_admin,
                            auth_project_id=project_id if not is_admin else None
                        )
                        st.success("Project updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                        
    # --- Manage Versions ---
    with tabs[1]:
        st.subheader("Version History")
        version_fields_config = load_config('version_fields')['fields']
        versions = VersionService.get_versions_for_project(db, project_id)
        
        if versions:
            v_data_list = []
            for v in versions:
                vd = v.get_data()
                vd['id'] = v.id
                v_data_list.append(vd)
            
            df_v = pd.DataFrame(v_data_list)
            display_cols = ['id']
            col_names = {'id': 'ID'}
            for field in version_fields_config:
                if field['name'] in df_v.columns:
                    display_cols.append(field['name'])
                    col_names[field['name']] = field['label']
                    
            df_v_display = df_v[display_cols].rename(columns=col_names)
            
            event_v = st.dataframe(
                df_v_display,
                use_container_width=True,
                hide_index=True,
                # pyrefly: ignore [unexpected-keyword]
                on_select="rerun",
                # pyrefly: ignore [unexpected-keyword]
                selection_mode="single-row",
                # pyrefly: ignore [unexpected-keyword]
                key=f"versions_table_{project_id}"
            )
            
            if is_admin and event_v and event_v.selection and len(event_v.selection.rows) > 0:
                selected_idx = event_v.selection.rows[0]
                v_id_to_delete = int(df_v.iloc[selected_idx]['id'])
                
                if st.button("Delete Selected Version", type="primary"):
                    try:
                        VersionService.delete_version(db, v_id_to_delete, user, is_admin=True)
                        st.success("Version deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting version: {str(e)}")
        else:
            st.info("No versions found for this project.")
            
        st.markdown("---")
        st.subheader("Add New Version")
        with st.form("add_version_form"):
            v_form_data = render_dynamic_form(version_fields_config)
            v_submitted = st.form_submit_button("Add Version")
            if v_submitted:
                v_errors = validate_dynamic_form(version_fields_config, v_form_data)
                if v_errors:
                    for error in v_errors:
                        st.error(error)
                else:
                    try:
                        VersionService.create_version(
                            db=db, 
                            project_id=project_id, 
                            data=v_form_data, 
                            user=user,
                            is_admin=is_admin,
                            auth_project_id=project_id if not is_admin else None
                        )
                        st.success("Version added!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                    
    # --- Manage Risks ---
    with tabs[2]:
        st.subheader("Risk Inventory")
        
        # Risk Matrix Reference Guide
        with st.expander("📊 View Risk Scoring Matrix Reference", expanded=False):
            from app.utils.risk_matrix import render_matrix_table_html
            st.html(render_matrix_table_html())
            
        versions = VersionService.get_versions_for_project(db, project_id)
        if not versions:
            st.warning("You must add a version before logging risks.")
        else:
            from app.utils.risk_matrix import calculate_risk, get_risk_badge_html
            version_opts = {f"V{v.id} - {v.get_data().get('version_number', '')}": v.id for v in versions}
            selected_v_name = st.selectbox("Select Version to Manage Risks", options=list(version_opts.keys()), key=f"risk_v_select_{project_id}")
            selected_v_id = version_opts[selected_v_name]
            
            risk_fields_config = load_config('risk_fields')['fields']
            risks = RiskService.get_risks_for_version(db, selected_v_id)
            
            if risks:
                r_data_list = []
                for r in risks:
                    rd = r.get_data()
                    rd['id'] = r.id
                    if 'likelihood' not in rd:
                        rd['likelihood'] = 'Not assessed'
                    if 'impact' not in rd:
                        rd['impact'] = 'Not assessed'
                    if not rd.get('risk_score_label') and (rd.get('likelihood') not in [None, '', 'Not assessed'] or rd.get('impact') not in [None, '', 'Not assessed']):
                        calc = calculate_risk(rd.get('likelihood'), rd.get('impact'))
                        rd['risk_score_label'] = calc['label']
                        rd['risk_score'] = calc['score']
                        rd['risk_level'] = calc['level']
                    elif not rd.get('risk_score_label'):
                        rd['risk_score_label'] = 'Unassessed'
                    r_data_list.append(rd)
                
                df_r = pd.DataFrame(r_data_list)
                preferred_order = ['id', 'category', 'description', 'likelihood', 'impact', 'risk_score_label', 'status', 'mitigation']
                col_names_r = {
                    'id': 'ID',
                    'category': 'Category',
                    'description': 'Description',
                    'likelihood': 'Likelihood',
                    'impact': 'Impact',
                    'risk_score_label': 'Risk Score',
                    'status': 'Status',
                    'mitigation': 'Mitigation'
                }
                display_cols_r = [c for c in preferred_order if c in df_r.columns]
                for field in risk_fields_config:
                    if field['name'] in df_r.columns and field['name'] not in display_cols_r:
                        display_cols_r.append(field['name'])
                        col_names_r[field['name']] = field['label']
                        
                df_r_display = df_r[display_cols_r].rename(columns=col_names_r)
                
                event_r = st.dataframe(
                    df_r_display,
                    use_container_width=True,
                    hide_index=True,
                    # pyrefly: ignore [unexpected-keyword]
                    on_select="rerun",
                    # pyrefly: ignore [unexpected-keyword]
                    selection_mode="single-row",
                    # pyrefly: ignore [unexpected-keyword]
                    key=f"risks_table_{project_id}_{selected_v_id}"
                )
                
                if event_r and event_r.selection and len(event_r.selection.rows) > 0:
                    selected_idx = event_r.selection.rows[0]
                    risk_to_edit = int(df_r.iloc[selected_idx]['id'])
                    
                    st.markdown("---")
                    st.subheader("Edit Selected Risk")
                    risk_data = next((r for r in r_data_list if r['id'] == risk_to_edit), {})
                    
                    calc_existing = calculate_risk(risk_data.get('likelihood'), risk_data.get('impact'))
                    if calc_existing['score'] is not None:
                        st.markdown(
                            f"<div style='margin-bottom: 12px; font-size: 14px; font-weight: 600; color: #003865;'>"
                            f"Current Risk Assessment: {get_risk_badge_html(calc_existing['level'], calc_existing['score'])}"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    
                    with st.form(f"edit_risk_form_{risk_to_edit}"):
                        edit_r_form_data = render_dynamic_form(risk_fields_config, default_values=risk_data, key_prefix=f"edit_risk_{risk_to_edit}")
                        edit_r_submitted = st.form_submit_button("Update Risk")
                        if edit_r_submitted:
                            edit_r_errors = validate_dynamic_form(risk_fields_config, edit_r_form_data)
                            if edit_r_errors:
                                for error in edit_r_errors:
                                    st.error(error)
                            else:
                                try:
                                    RiskService.update_risk(
                                        db=db,
                                        risk_id=risk_to_edit,
                                        new_data=edit_r_form_data,
                                        user=user,
                                        is_admin=is_admin,
                                        auth_project_id=project_id if not is_admin else None
                                    )
                                    calc_updated = calculate_risk(edit_r_form_data.get('likelihood'), edit_r_form_data.get('impact'))
                                    st.success(f"Risk updated! Calculated Score: {calc_updated.get('label', 'Saved')}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))
            else:
                st.info("No risks logged for this version.")
                
            st.markdown("---")
            st.subheader("Add New Risk")
            with st.form("add_risk_form"):
                r_form_data = render_dynamic_form(risk_fields_config, key_prefix=f"add_risk_{selected_v_id}")
                r_submitted = st.form_submit_button("Add Risk")
                if r_submitted:
                    r_errors = validate_dynamic_form(risk_fields_config, r_form_data)
                    if r_errors:
                        for error in r_errors:
                            st.error(error)
                    else:
                        try:
                            RiskService.add_risk(
                                db=db, 
                                version_id=selected_v_id, 
                                data=r_form_data, 
                                user=user,
                                is_admin=is_admin,
                                auth_project_id=project_id if not is_admin else None
                            )
                            calc_new = calculate_risk(r_form_data.get('likelihood'), r_form_data.get('impact'))
                            st.success(f"Risk added! Calculated Score: {calc_new.get('label', 'Saved')}")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                            
    # --- Admin Actions ---
    if is_admin:
        with tabs[3]:
            st.subheader("Regenerate Access Code")
            st.warning("Regenerating the access code will immediately invalidate the current code. Project owners will need the new code to edit their project.")
            if st.button("Generate New Code", type="primary"):
                try:
                    new_code = ProjectService.regenerate_access_code(db, project_id, user, is_admin=True)
                    st.success("Access Code Regenerated Successfully!")
                    st.info(f"**New Access Code**: `{new_code}`")
                    st.markdown("Please copy this code and provide it to the project owner. It will not be shown again.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
