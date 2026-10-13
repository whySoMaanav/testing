import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, ColumnsAutoSizeMode

def render_dynamic_table(data_list: list, fields_config: list, key: str, selection_mode: str = 'single'):
    """
    Renders an AgGrid table based on the data and configuration.
    Returns the selected rows.
    """
    if not data_list:
        return None
        
    df = pd.DataFrame(data_list)
    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode, use_checkbox=True)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    
    # Configure columns based on YAML config
    existing_cols = df.columns.tolist()
    
    for field in fields_config:
        name = field['name']
        if name in existing_cols:
            gb.configure_column(name, header_name=field['label'])
            
    gridOptions = gb.build()
    
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        theme='alpine',
        key=key
    )
    
    if grid_response['selected_rows'] is not None and len(grid_response['selected_rows']) > 0:
         return pd.DataFrame(grid_response['selected_rows'])
    return None
