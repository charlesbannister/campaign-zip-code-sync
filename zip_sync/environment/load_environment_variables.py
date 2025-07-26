import os

from dotenv import load_dotenv

from environment.folder_paths import get_env_file_path


def load_environment_variables() -> None:
    """
    Load environment variables from the .env file
    And load the cert and key if they don't exist as environment variables already
    """

    # load all environment variables from the .env file
    # if it exists (it will only exist locally / during development)
    env_file_path = get_env_file_path()
    if os.path.exists(env_file_path):
        load_dotenv(env_file_path)