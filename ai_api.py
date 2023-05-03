import openai
from ai_config import AIConfig
from ai_prompt import BasePrompt


class BaseAPI:
    '''
    Initializes an OpenAI API engine with the given configuration
    To adopt different backbone engines in AIGenerator, wrap the backone with BaseAPI
    and implement the `generate` method

    Args:
        cfg (AIConfig): An object that stores the API key, engine, and max tokens to use.
        prompt (BasePrompt): An object that generates prompts.
    '''

    def __init__(self, cfg: AIConfig, prompt: BasePrompt, lang="en") -> None:
        self.api_key = cfg.get_openai_api_key()
        self.engine = cfg.get_openai_api_engine()
        self.max_tokens = cfg.get_openai_max_tokens()
        self.prompt = prompt
        self.lang = lang
        openai.api_key = self.api_key

    def _get_content(self):
        ''' Get the text contents from the response package. '''
        raise NotImplementedError

    def _get_prompts(self):
        ''' Generate engine-specific prompts that consist of system, assistant, and user prompts. '''
        raise NotImplementedError

    def generate(self, user_demands: str, temperature: float = 0.5) -> str:
        '''
        Generate text based on a given prompt and temperature.

        Args:
            prompt (str): The prompt to generate text from. 
            temperature (float): A value controlling the randomness and creativity of the generated text.

        Returns:
            str: The generated text.
        '''
        if not isinstance(user_demands, str) or not user_demands or not user_demands.strip():
            raise ValueError(f"Invalid prompt: {user_demands}")
        if temperature < 0 or temperature > 1:
            raise ValueError(f"Invalid temperature: {temperature}")


class TextDavinci(BaseAPI):
    '''
    Generates a text completion using OpenAI's API `text-davinci-003`.

    Args:
        prompt (str): The text prompt to generate a completion for.
        temperature (float): Controls the "creativity" of the generated text. 
            Higher values result in more varied and unpredictable completions.

    Returns:
        str: The generated text completion as a string.
    '''
    def _get_prompts(self, user_demands) -> str:
        return self.prompt.get_completion_prompt(user_demands)

    def _get_content(self, response) -> str:
        if not response or not hasattr(response, "choices") or not response.choices:
            raise ValueError(f"Incomplete response object: {response}")
        if len(response.choices) < 1 or not hasattr(response.choices[0], "text"):
            raise ValueError(f"Incomplete response choices: {response}")
        text = response.choices[0].text
        if not isinstance(text, str) or not text or not text.strip():
            raise TypeError(f"Invalid response of type {type(text)} and value {text}")
        return text.strip()

    def generate(self, user_demands: str, temperature: float) -> str:
        super().generate(user_demands, temperature)
        
        response = openai.Completion.create(
            engine=self.engine,
            prompt=self._get_prompts(user_demands),
            max_tokens=self.max_tokens,
            temperature=temperature,
        )
        return self._get_content(response)


class ChatGPT(BaseAPI):
    '''
    Generates a text completion using OpenAI's API `gpt-3.5-turbo` (recommended).

    Args:
        prompt (str): The text prompt to generate a completion for.
        temperature (float): Controls the "creativity" of the generated text. 
            Higher values result in more varied and unpredictable completions.

    Returns:
        str: The generated text completion as a string.
    '''
    def _get_prompts(self, user_demands) -> str:
        return self.prompt.get_chat_prompt(user_demands)
    
    def _get_content(self, response) -> str:
        if not response or not hasattr(response, "choices") or not response.choices:
            raise ValueError(f"Incomplete response object: {response}")
        if len(response.choices) < 1 or not hasattr(response.choices[0], "message"):
            raise ValueError(f"Incomplete response choices: {response}")
        text = response.choices[0].message.content
        if not isinstance(text, str) or not text or not text.strip():
            raise TypeError(f"Invalid response of type {type(text)} and value {text}")
        return text.strip()

    def generate(self, user_demands: str, temperature: float) -> str:
        super().generate(user_demands, temperature)
        
        response = openai.ChatCompletion.create(
            model=self.engine,
            messages=self._get_prompts(user_demands),
            max_tokens=self.max_tokens,
            temperature=temperature,
        )
        return self._get_content(response)


def get_engine_api(cfg: AIConfig, prompt: BasePrompt):
    '''
    Map the OpenAI language engine name to the corresponding API class
    Supported engines: `text-davinci-003` and `gpt-3.5-turbo`
    '''
    engine_apis = {
        "text-davinci-003": TextDavinci,
        "gpt-3.5-turbo": ChatGPT,
    }
    if cfg.get_openai_api_engine() not in engine_apis:
        raise NotImplementedError
    return engine_apis[cfg.get_openai_api_engine()](cfg, prompt)
