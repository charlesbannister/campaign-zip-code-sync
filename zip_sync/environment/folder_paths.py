import os

def _get_project_root_path() -> str:
    """Return the absolute path to the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_secrets_dir_path() -> str:
    """Return the path to the secrets directory. Uses project-root if local, /tmp/secrets otherwise."""
    return os.path.abspath(os.path.join(_get_project_root_path(), "secrets"))

def _get_config_dir_path() -> str:
    """Return the path to the config directory."""
    return os.path.abspath(os.path.join(_get_project_root_path(), "config"))

def get_env_file_path() -> str:
    """Return the path to the .env file."""
    return os.path.join(_get_config_dir_path(), ".env")