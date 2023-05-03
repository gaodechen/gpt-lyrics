class BasePrompt():
    '''
    A BasePrompt instance is used to generate API-specific prompts. It currently supports Chat and Completion backbones.
    One prompt to a request usually consists of system, assistant, and user prompts.
    For a more specific task, such as lyric writing, we derive a new class from BasePrompt and implement each method within.
    '''
    SUPPORT_LANGUAGES = ["zh", "en"]
    
    def __init__(self, lang):
        self.lang = lang
        
        if (self.lang not in BasePrompt.SUPPORT_LANGUAGES):
            raise NotImplementedError(
                "The language {} is not supported.".format(self.lang))
    
    def get_system_prompt(self):
        raise NotImplementedError
    
    def get_assistant_prompt(self):
        raise NotImplementedError
    
    def get_user_prompt(self):
        raise NotImplementedError
    
    def get_chat_prompt(self):
        ''' Prompts to the Chat API'''
        raise NotImplementedError
    
    def get_completion_prompt(self):
        ''' Prompts to the Completion API '''
        raise NotImplementedError
    

class LyricPrompt(BasePrompt):
    '''
    LyricPrompt generates chat or completion prompts for lyric writing from scratch.
    The prompts consist of system, assistant, and user prompts.
    The expected output is a string that begins with the specified [start] token and concludes with the [end] token.
    '''
    def __init__(self, lang="en", error_message="[error]"):
        '''
        Args:
            lang (str): The language of the prompt. Currently supports "zh" and "en".
            error_message (str): The error message to output when the API fails to generate the lyrics.
        '''
        super().__init__(lang)
        self.error_message = error_message
        

    def get_system_prompt(self):
        ''' Description of the lyric writer '''
        content = {
            "zh": "你是一个专业、才华横溢的音乐人，并且严格遵循以下需求提供作词服务。",
            "en": "You are a professional and talented musician who provides songwriting services and strictly adheres to the following requirements."
        }
        return {
            "role": "system",
            "content": content[self.lang]
        }

    def get_assistant_prompt(self):
        ''' Requirements that the lyrics should meet '''''
        content = {
            "zh": "不要包含任何类似chorus或verse等音乐段落和结构名。\
                    仅输出歌词正文，每句歌词独立成行。\
                    在歌词开始之前输出[start]，歌词结束后输出[end]。\
                    若无法生成歌词，请输出{error_message}。",
            "en": "Do not mention or use any music structure names such as intro, chorus, verse.\
                    Just write the lines of the lyrics with each line being separate and distinct.\
                    Output [start] before the lyrics begin and [end] after the lyrics end.\
                    If you cannot generate the lyrics, output {error_message}."
        }
        return {
            "role": "assistant",
            "content": content[self.lang].format(error_message=self.error_message)
        }

    def get_user_prompt(self, user_demands):
        ''' Encode additional user demands for the lyrics '''
        content = {
            "zh": "请生成歌词，这里是客户关于主题或风格的要求：{user_prompt}。",
            "en": "Please write lyrics for a song. Here are additional requirements for the song you need to follow: {user_prompt}."
        }
        return {
            "role": "user",
            "content": content[self.lang].format(user_prompt=user_demands)
        }

    def get_completion_prompt(self, user_demands):
        ''' Prompts to the Completion API '''
        return '\n'.join([
            prompt["content"] for prompt in [
                self.get_system_prompt(),
                self.get_assistant_prompt(),
                self.get_user_prompt(user_demands),
            ] if "content" in prompt
        ])

    def get_chat_prompt(self, user_demands):
        ''' Prompts to the Chat API '''
        return [
            self.get_system_prompt(),
            self.get_assistant_prompt(),
            self.get_user_prompt(user_demands),
        ]
