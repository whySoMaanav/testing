import streamlit as st
import pandas as pd
from app.database.connection import get_db
from app.services.project_service import ProjectService
from app.services.version_service import VersionService
from app.services.risk_service import RiskService
from app.utils.config_loader import load_config
from app.utils.risk_matrix import calculate_risk, get_risk_badge_html, LEVEL_COLORS

st.markdown("""
<div style="padding-bottom: 2rem;">
    <h1 style="font-size: 40px; margin-bottom: 0;">Project Directory</h1>
    <p style="color: #64748b; font-size: 16px; margin-top: 5px;">Browse and explore all registered AI initiatives.</p>
</div>
""", unsafe_allow_html=True)

db = next(get_db())
projects = ProjectService.get_all_projects(db)

if not projects:
    st.info("No projects found. Create a new project to get started.")
else:
    # --- Search Bar ---
    st.markdown("<h3 style='font-size: 18px; margin-bottom: 8px;'>Search Projects</h3>", unsafe_allow_html=True)
    search_query = st.text_input("Search Projects", label_visibility="collapsed", placeholder="🔍 Search by Project Name, ID, or Owner...").lower()
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Store the selected project to display details below
    if 'selected_directory_project' not in st.session_state:
        st.session_state.selected_directory_project = None
    if 'projects_df_key_version' not in st.session_state:
        st.session_state.projects_df_key_version = 0
        
    data_list = []
    for p in projects:
        p_data = p.get_data()
        pid = p.project_id
        name = p_data.get('project_name', '')
        owner = p_data.get('owner', '')
        
        # Apply Search Filter
        if search_query:
            if search_query not in pid.lower() and \
               search_query not in name.lower() and \
               search_query not in owner.lower():
                continue
                
        p_data['project_id'] = pid
        p_data['db_id'] = p.id
        data_list.append(p_data)
        
    if not data_list:
        st.warning("No projects matched your search.")
    else:
        project_fields_config = load_config('project_fields')['fields']
        
        # Build dataframe for native Streamlit rendering
        df = pd.DataFrame(data_list)
        # Select columns to display based on config
        display_cols = ['project_id']
        col_names = {'project_id': 'Project ID'}
        for field in project_fields_config:
            if field['name'] in df.columns and field['name'] != 'project_id':
                display_cols.append(field['name'])
                col_names[field['name']] = field['label']
                
        df_display = df[display_cols].rename(columns=col_names)
        
        st.markdown("<p style='font-size: 15px; font-weight: 600; color: #003865; margin-bottom: 8px;'>Select a project row to view details:</p>", unsafe_allow_html=True)
        
        # Native Streamlit DataFrame with Selection
        df_key = f"projects_directory_df_{st.session_state.projects_df_key_version}"
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
            st.session_state.selected_directory_project = selected_pid
        elif event and event.selection and len(event.selection.rows) == 0:
             # Deselected
             st.session_state.selected_directory_project = None

    if st.session_state.selected_directory_project:
        st.markdown("<hr style='margin: 3rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
        selected_pid = st.session_state.selected_directory_project
        
        project_obj = ProjectService.get_project(db, selected_pid)
        if project_obj:
            data = project_obj.get_data()
            project_fields_config = load_config('project_fields')['fields']
            
            # --- Status Badge Helper ---
            proj_status = data.get('status', 'Unknown')
            status_colors = {
                "Active": {"bg": "#ecfdf5", "text": "#059669", "border": "#a7f3d0"},
                "In Development": {"bg": "#f0f9ff", "text": "#0284c7", "border": "#bae6fd"},
                "Proposed": {"bg": "#fffbeb", "text": "#d97706", "border": "#fde68a"},
                "Sunset": {"bg": "#f3f4f6", "text": "#4b5563", "border": "#e5e7eb"}
            }
            sc = status_colors.get(proj_status, {"bg": "#f8fafc", "text": "#475569", "border": "#cbd5e1"})
            
            # --- Header Row with Close Button ---
            header_col1, header_col2 = st.columns([5, 1])
            with header_col1:
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                    <h2 style="margin: 0; font-size: 28px; color: #003865;">{data.get('project_name', selected_pid)}</h2>
                    <span style="display: inline-block; padding: 4px 12px; font-size: 13px; font-weight: 700; border-radius: 9999px; background-color: {sc['bg']}; color: {sc['text']}; border: 1px solid {sc['border']};">
                        {proj_status}
                    </span>
                    <span style="font-size: 13px; color: #64748b; font-weight: 600; background-color: #f1f5f9; padding: 4px 10px; border-radius: 6px;">
                        ID: {selected_pid}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            with header_col2:
                if st.button("✕ Close Details", key="close_details", use_container_width=True):
                    st.session_state.selected_directory_project = None
                    st.session_state.projects_df_key_version += 1
                    st.rerun()

            # --- Crisp, Non-faded Details Layout ---
            # Group fields into metadata grid and full-width description cards
            meta_col1, meta_col2 = st.columns(2)
            
            with meta_col1:
                st.markdown(f"""
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 14px 18px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Owner</div>
                    <div style="font-size: 15px; font-weight: 600; color: #003865;">{data.get('owner', 'Not specified')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 14px 18px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Business Unit</div>
                    <div style="font-size: 15px; font-weight: 600; color: #003865;">{data.get('business_unit', 'Not specified')}</div>
                </div>
                """, unsafe_allow_html=True)

            with meta_col2:
                contact = data.get('contact_email', 'Not specified')
                mail_link = f"<a href='mailto:{contact}' style='color: #0056b3; text-decoration: none; font-weight: 600;'>{contact}</a>" if '@' in contact else contact
                st.markdown(f"""
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 14px 18px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Contact Email</div>
                    <div style="font-size: 15px; font-weight: 600; color: #003865;">{mail_link}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 14px 18px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Status</div>
                    <div style="font-size: 15px; font-weight: 600; color: #003865;">{proj_status}</div>
                </div>
                """, unsafe_allow_html=True)

            # Full-width Scope and Description
            st.markdown(f"""
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Scope</div>
                <div style="font-size: 14px; font-weight: 500; color: #1e293b; line-height: 1.6; white-space: pre-wrap;">{data.get('scope', 'No scope detailed.')}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Description</div>
                <div style="font-size: 14px; font-weight: 500; color: #1e293b; line-height: 1.6; white-space: pre-wrap;">{data.get('description', 'No description detailed.')}</div>
            </div>
            """, unsafe_allow_html=True)

            # --- Fetch All Risks For This Project Across Versions ---
            versions = VersionService.get_versions_for_project(db, selected_pid)
            all_project_risks = []
            for v in versions:
                v_data = v.get_data()
                v_num = v_data.get('version_number', f"V{v.id}")
                v_risks = RiskService.get_risks_for_version(db, v.id)
                for r in v_risks:
                    rd = r.get_data()
                    rd['id'] = r.id
                    rd['version_number'] = v_num
                    rd['version_id'] = v.id
                    # Calculate risk score if not yet populated
                    if not rd.get('risk_score_label') and (rd.get('likelihood') or rd.get('impact')):
                        calc = calculate_risk(rd.get('likelihood'), rd.get('impact'))
                        rd['risk_score_label'] = calc['label']
                        rd['risk_score'] = calc['score']
                        rd['risk_level'] = calc['level']
                    elif not rd.get('risk_score_label'):
                        rd['risk_score_label'] = 'Unassessed'
                        rd['risk_level'] = 'Unassessed'
                    all_project_risks.append(rd)

            total_risks_count = len(all_project_risks)

            # --- Risks Dropdown at the End of Details ---
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            with st.expander(f"⚠️ Risks ({total_risks_count})", expanded=False):
                if total_risks_count == 0:
                    st.info("No risks currently logged for this project.")
                else:
                    # Quick Risk Posture Summary Bar
                    high_count = sum(1 for r in all_project_risks if r.get('risk_level') in ['High', 'Very High'])
                    resolved_count = sum(1 for r in all_project_risks if r.get('status') in ['Mitigated', 'Closed'])
                    
                    st.markdown(f"""
                    <div style="display: flex; gap: 16px; margin-bottom: 16px; padding: 12px 16px; background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; font-size: 13px;">
                        <div><strong style="color: #003865;">Total Risks:</strong> {total_risks_count}</div>
                        <div><strong style="color: #c2410c;">High / Very High:</strong> {high_count}</div>
                        <div><strong style="color: #059669;">Mitigated / Closed:</strong> {resolved_count}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Group risks by Category
                    category_map = {}
                    for r in all_project_risks:
                        cat = r.get('category', 'Other')
                        category_map.setdefault(cat, []).append(r)

                    # Order categories logically: standard categories first
                    configured_cats = ["Privacy", "Security", "Bias & Fairness", "Performance", "Compliance", "Other"]
                    sorted_categories = [c for c in configured_cats if c in category_map]
                    for c in category_map:
                        if c not in sorted_categories:
                            sorted_categories.append(c)

                    # Risk Status Badge Styling Helper
                    risk_status_colors = {
                        "Open": {"bg": "#fef2f2", "text": "#dc2626", "border": "#fca5a5"},
                        "In Progress": {"bg": "#fffbeb", "text": "#d97706", "border": "#fde68a"},
                        "Mitigated": {"bg": "#f0fdfa", "text": "#0d9488", "border": "#99f6e4"},
                        "Accepted": {"bg": "#eff6ff", "text": "#2563eb", "border": "#bfdbfe"},
                        "Closed": {"bg": "#f0fdf4", "text": "#16a34a", "border": "#bbf7d0"},
                    }

                    # Render each category as a drop-down (nested expander)
                    for cat_name in sorted_categories:
                        cat_risks = category_map[cat_name]
                        with st.expander(f"📁 {cat_name} ({len(cat_risks)} {'Risk' if len(cat_risks) == 1 else 'Risks'})", expanded=False):
                            for r in cat_risks:
                                r_status = r.get('status', 'Open')
                                rsc = risk_status_colors.get(r_status, {"bg": "#f1f5f9", "text": "#475569", "border": "#cbd5e1"})
                                r_level = r.get('risk_level', 'Unassessed')
                                r_score = r.get('risk_score')
                                r_score_badge = get_risk_badge_html(r_level, r_score)
                                
                                likelihood_str = r.get('likelihood', 'Not assessed')
                                impact_str = r.get('impact', 'Not assessed')
                                mitigation_str = r.get('mitigation', '')

                                # Border color corresponding to risk severity
                                level_c = LEVEL_COLORS.get(r_level, {"border": "#cbd5e1"})
                                card_border_color = level_c["border"] if r_score is not None else "#cbd5e1"

                                st.markdown(f"""
                                <div style="background-color: #ffffff; border: 1.5px solid {card_border_color}; border-left: 5px solid {card_border_color}; border-radius: 8px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
                                        <div style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">
                                            Risk #{r['id']} • Version {r.get('version_number', '1.0')}
                                        </div>
                                        <div style="display: flex; gap: 8px; align-items: center;">
                                            {r_score_badge}
                                            <span style="display: inline-block; padding: 3px 10px; font-size: 12px; font-weight: 700; border-radius: 9999px; background-color: {rsc['bg']}; color: {rsc['text']}; border: 1px solid {rsc['border']};">
                                                {r_status}
                                            </span>
                                        </div>
                                    </div>
                                    <div style="font-size: 15px; font-weight: 600; color: #1e293b; line-height: 1.5; margin-bottom: 12px;">
                                        {r.get('description', 'No description provided.')}
                                    </div>
                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; background-color: #f8fafc; padding: 10px 14px; border-radius: 6px; border: 1px solid #e2e8f0; font-size: 13px; margin-bottom: 10px;">
                                        <div><span style="color: #64748b; font-weight: 600;">Likelihood:</span> <span style="color: #003865; font-weight: 700;">{likelihood_str}</span></div>
                                        <div><span style="color: #64748b; font-weight: 600;">Impact:</span> <span style="color: #003865; font-weight: 700;">{impact_str}</span></div>
                                        <div><span style="color: #64748b; font-weight: 600;">Calculated Score:</span> <span style="color: #003865; font-weight: 700;">{r.get('risk_score_label', 'Unassessed')}</span></div>
                                    </div>
                                    {f'''<div style="padding: 10px 14px; background-color: #ffffff; border-radius: 6px; border: 1px solid #e2e8f0; font-size: 13px;">
                                        <strong style="color: #003865;">🛡️ Mitigation Strategy:</strong>
                                        <div style="color: #334155; margin-top: 4px; line-height: 1.5;">{mitigation_str}</div>
                                    </div>''' if mitigation_str else '<div style="color: #94a3b8; font-size: 12px; font-style: italic;">No mitigation strategy documented yet.</div>'}
                                </div>
                                """, unsafe_allow_html=True)
