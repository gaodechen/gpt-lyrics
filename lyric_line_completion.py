from tuneflow_py import TuneflowPlugin, ParamDescriptor, Song, Lyrics, WidgetType, TuneflowPluginTriggerData, InjectSource

import math
from typing import Dict, Any

from ai_config import AIConfig
from ai_api import get_engine_api
from ai_prompt import LyricPrompt
from utils import get_writing_language, split_lyrics

class LyricLineCompletionPlugin(TuneflowPlugin):
    @staticmethod
    def provider_id() -> str:
        return 'andantei'

    @staticmethod
    def plugin_id() -> str:
        return 'gpt-lyrics-line'

    @staticmethod
    def params(song: Song) -> Dict[str, ParamDescriptor]:
        return {
            "prompt": {
                "displayName": {
                    "en": "Prompt",
                    "zh": "提示词"
                },
                "description": {
                    "en": "Describe the styles, topics, and contents of lyrics you want to generate",
                    "zh": "简短的描述你想要生成乐句的风格、主题、内容等"
                },
                "defaultValue": "",
                "widget": {
                    "type": WidgetType.TextArea.value,
                    "config": {
                        "placeholder": {
                            "zh": "样例：这句话的主题是梦想和希望",
                            "en": "e.g. write a lyric line about dreams and hope"
                        },
                        "maxLength": 300
                    }
                },
                "optional": True
            },
            "temperature": {
                "displayName": {
                    "en": "Creativity",
                    "zh": "创造力"
                },
                "defaultValue": 0.9,
                "description": {
                    "en": "The degree of randomness and creativity of generated lyrics",
                    "zh": "该值越高，生成歌词的随机性、创造性越强"
                },
                "widget": {
                    "type": WidgetType.Slider.value,
                    "config": {
                        "minValue": 0.0,
                        "maxValue": 1.0,
                        "step": 0.05
                    }
                }
            },
            "language": {
                "displayName": {
                    "en": "Writing Language",
                    "zh": "写作语言"
                },
                "defaultValue": "auto",
                "widget": {
                    "type": WidgetType.Select.value,
                    "config": {
                        "placeholder": {
                            "zh": "样例：有关梦想和希望的流行歌曲",
                            "en": "e.g. a pop song about dreams and hope"
                        },
                        "options": [
                            {
                                "label": {
                                    "en": "Auto",
                                    "zh": "自动",
                                },
                                "value": "auto"
                            },
                            {
                                "label": "English",
                                "value": "en"
                            },
                            {
                                "label": "中文",
                                "value": "zh"
                            }
                        ]
                    }
                }
            },
            "userLanguage": {
                "displayName": {
                    "en": "User Language",
                    "zh": "用户语言"
                },
                "defaultValue": None,
                "injectFrom": InjectSource.Language.value,
                "widget": {
                    "type": WidgetType.NoWidget.value,
                },
                "hidden": True,
                "optional": True
            },
        }
    
    @staticmethod
    def run(song: Song, params: Dict[str, Any]):
        lang = params["language"]
        user_lang = params["userLanguage"]
        lang = get_writing_language(lang, user_lang)
        
        trigger: TuneflowPluginTriggerData = params["trigger"]
        lyrics = Lyrics(song)
        
        # The context before and after the completed part
        context_before = ""
        context_after = ""
        
        # Rewrite the selected lyric line
        line_index = trigger["entities"][0]["lyricsLineIndex"]
        start_tick = lyrics[line_index].get_start_tick()
        end_tick = lyrics[line_index].get_end_tick()
        # Get the context before and after the selected line
        context_before = "\n".join(lyrics[i].get_sentence() for i in range(line_index))
        context_after = "\n".join(lyrics[i].get_sentence() for i in range(line_index + 1, len(lyrics)))
        
        # Complete lyrics through OpenAI APIs
        api = get_engine_api(
            cfg=AIConfig(),
            prompt=LyricPrompt(lang=lang)
        )

        response = api.generate(
            user_demands=params["prompt"],
            temperature=params["temperature"],
            context_before=context_before,
            context_after=context_after,
            num_lines=1,
        )

        # Parse the response and arrange lyric lines
        lines = split_lyrics(response)
        if len(lines) < 1:
            raise Exception('No lyrics generated')
        # Remove the original lyric lines and insert the new ones
        lyrics.remove_line_at_index(line_index)
        lyrics.create_line_from_string(lines[0], start_tick, end_tick)
