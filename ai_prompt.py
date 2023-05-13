class BasePrompt():
    '''
    A BasePrompt instance is used to generate API-specific prompts.
    It currently supports OpenAI Chat and Completion backbones.
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
    LyricPrompt generates Chat or Completion API prompts for lyric writing or continuing.
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
            "zh": "你是一个专业、才华横溢的音乐人，并且严格遵循用户需求提供作词服务。",
            "en": "You are a professional and talented musician who provides songwriting services and strictly adheres to user requirements."
        }
        return {
            "role": "system",
            "content": content[self.lang]
        }

    def get_user_prompt(self, user_demands: str, context_before: str = "", context_after: str = "", num_lines: int = 4):
        ''' Encode additional user demands for the lyrics '''
        # General requirements for lyric generation
        requirements = {
            "zh": [
                "我会为你提供一个要求列表，你需要严格遵循每一条要求生成歌词。列表中的每一条要求都以(R)开头。"
                "(R) 请遵循如下歌词创作风格、内容等要求：{user_demands}。",
                "(R) 使用中文创作歌词。",
                "(R) 不要包含任何音乐段落和结构名，例如chorus或verse",
                "(R) 仅输出新生成歌词的正文，每句歌词独立成行。",
                "(R) 在歌词开始之前输出[start]，歌词结束后输出[end]。",
                "(R) 若无法生成歌词，请输出{error_message}。"
                "(R) 歌词行数在{num_lines}行左右。"
            ],
            "en": [
                "I will provide you with a list of requirements, and you need to strictly generate lyrics according to each requirement. Each item on the list starts with (R).",
                "(R) Follow the following description regarding lyric contents or styles: {user_demands}.",
                "(R) Write lyrics in English.",
                "(R) Do not mention or use any music structure names such as intro, chorus, verse.",
                "(R) Just write the generated lines with each line being separate and distinct.",
                "(R) Output [start] before the lyrics begin and [end] after the lyrics end.",
                "(R) If you cannot generate the lyrics, output {error_message}."
                "(R) Please provide around {num_lines} lines of new lyrics."
            ]
        }
        # Requirements for lyric continuation
        if context_before.strip() != "":
            requirements["zh"] += ["(R) 新生成的歌词需要衔接上文，歌词上文如下：{context_before}。"]
            requirements["en"] += ["(R) The newly generated lyrics need to seamlessly connect to the previous lyrics. Previous lyrics are as follows: {context_before}."]
        # Requirements for lyric insertion
        if context_after.strip() != "":
            requirements["zh"] += ["(R) 新生成的歌词需要衔接下文，歌词下文如下：{context_after}。"]
            requirements["en"] += ["(R) The newly generated lyrics need to seamlessly connect to the previous lyrics. Previous lyrics are as follows: {context_after}."]
        content = {
            "zh": "\n".join(requirements["zh"]),
            "en": "\n".join(requirements["en"]),
        }
        return {
            "role": "user",
            "content": content[self.lang].format(
                user_demands=user_demands,
                error_message=self.error_message,
                num_lines=num_lines,
                context_before=context_before,
                context_after=context_after,
            )
        }

    def get_completion_prompt(self, user_demands: str, **kwargs):
        ''' Prompts to the Completion API '''
        return '\n'.join([
            prompt["content"] for prompt in [
                self.get_system_prompt(),
                self.get_user_prompt(user_demands, **kwargs),
            ] if "content" in prompt
        ])

    def get_chat_prompt(self, **kwargs):
        ''' Prompts to the Chat API '''
        return [
            self.get_system_prompt(),
            self.get_user_prompt(**kwargs),
        ]
