import os
import yaml

def load_config(config_name: str) -> dict:
    """Load a YAML configuration file from app/config/"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, 'config', f'{config_name}.yaml')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
