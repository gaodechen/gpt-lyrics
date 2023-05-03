import os
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)

DEFAULT_OPENAI_API_MAX_TOKENS = 1024
# gpt-3.5-turbo performs at a similar capability to text-davinci-003
# but is at 10% the price per token
DEFAULT_OPENAI_API_ENGINE = 'gpt-3.5-turbo'


class AIConfig:
    """
    A class that contains the configurations for the OpenAI APIs
    Configurations are read from the .env file under the root directory
    """

    def __init__(self) -> None:
      self.openai_api_key = os.getenv("OPENAI_API_KEY")
      if not self.openai_api_key:
        raise Exception("OPENAI_API_KEY is not set")
      
      self.openai_api_organization_id = os.getenv("OPENAI_API_ORGANIZATION_ID")
      if not self.openai_api_organization_id:
        raise Exception("ORGANIZATION_ID is not set")
      
      self.openai_api_engine = os.getenv("OPENAI_API_ENGINE", DEFAULT_OPENAI_API_ENGINE)
      
      try:
        self.openai_api_max_tokens = int(os.getenv(
          "OPENAI_API_MAX_TOKENS",
          default=DEFAULT_OPENAI_API_MAX_TOKENS
        ))
      except ValueError:
        self.openai_api_max_tokens = DEFAULT_OPENAI_API_MAX_TOKENS

    def get_openai_api_key(self) -> str:
      return self.openai_api_key

    def get_organization_id(self) -> str:
      return self.organization_id

    def get_openai_api_engine(self) -> str:
      return self.openai_api_engine

    def get_openai_max_tokens(self) -> int:
      return self.openai_api_max_tokens
