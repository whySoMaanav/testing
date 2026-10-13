import streamlit as st
from datetime import datetime

def render_dynamic_form(fields_config: list, default_values: dict = None, key_prefix: str = "") -> dict:
    """
    Renders a Streamlit form based on the fields configuration.
    Returns a dictionary of the input values.
    """
    if default_values is None:
        default_values = {}
        
    results = {}
    
    for field in fields_config:
        name = field['name']
        label = field['label']
        field_type = field['type']
        required = field.get('required', False)
        description = field.get('description', '')
        widget_key = f"{key_prefix}_{name}" if key_prefix else None
        
        display_label = f"{label} *" if required else label
        default_val = default_values.get(name, "")
        
        if field_type == 'text':
            results[name] = st.text_input(display_label, value=str(default_val) if default_val is not None else "", help=description, key=widget_key)
        elif field_type == 'textarea':
            results[name] = st.text_area(display_label, value=str(default_val) if default_val is not None else "", help=description, key=widget_key)
        elif field_type == 'select':
            options = field.get('options', [])
            index = 0
            if default_val in options:
                index = options.index(default_val)
            results[name] = st.selectbox(display_label, options=options, index=index, help=description, key=widget_key)
        elif field_type == 'radio':
            options = field.get('options', [])
            index = 0
            if default_val in options:
                index = options.index(default_val)
            elif default_val:
                for idx, opt in enumerate(options):
                    if str(default_val).lower() in opt.lower() or opt.startswith(str(default_val)):
                        index = idx
                        break
            horizontal = field.get('horizontal', False)
            results[name] = st.radio(display_label, options=options, index=index, help=description, horizontal=horizontal, key=widget_key)
        elif field_type == 'date':
            # Handle date defaults
            if default_val and isinstance(default_val, str):
                try:
                    default_val = datetime.strptime(default_val, "%Y-%m-%d").date()
                except ValueError:
                    default_val = "today"
            elif not default_val:
                default_val = "today"
            date_val = st.date_input(display_label, value=default_val, help=description, key=widget_key)
            results[name] = date_val.strftime("%Y-%m-%d") if date_val else ""
        else:
            st.warning(f"Unsupported field type: {field_type}")
            
    return results

def validate_dynamic_form(fields_config: list, form_data: dict) -> list:
    """
    Validates form data against the configuration.
    Returns a list of error messages.
    """
    errors = []
    for field in fields_config:
        if field.get('required', False):
            val = form_data.get(field['name'])
            if val is None or str(val).strip() == "":
                errors.append(f"{field['label']} is required.")
    return errors
