from tuneflow_py import TuneflowPlugin, ParamDescriptor, Song, Lyrics, WidgetType, TuneflowPluginTriggerData, InjectSource

import math
from typing import Dict, Any

from ai_config import AIConfig
from ai_api import get_engine_api
from ai_prompt import LyricPrompt
from utils import get_writing_language, split_lyrics, DEFAULT_LINE_TICKS

class LyricStructureCompletionPlugin(TuneflowPlugin):
    @staticmethod
    def provider_id() -> str:
        return 'andantei'

    @staticmethod
    def plugin_id() -> str:
        return 'gpt-lyrics-structure'

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
                    "zh": "简短的描述你想要生成段落的风格、主题、内容等"
                },
                "defaultValue": "",
                "widget": {
                    "type": WidgetType.TextArea.value,
                    "config": {
                        "placeholder": {
                            "zh": "样例：请在本段落描写梦想和希望",
                            "en": "e.g. write a paragraph about dreams and hope"
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
            "numLines": {
                "displayName": {
                    "en": "Estimated Number of Lines",
                    "zh": "预计乐句数量"
                },
                "defaultValue": 6,
                "description": {
                    "en": "The estimated number of lines to generate",
                    "zh": "生成段落歌词的乐句大致数量"
                },
                "widget": {
                    "type": WidgetType.Slider.value,
                    "config": {
                        "minValue": 0,
                        "maxValue": 32,
                        "step": 1
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
        structure_index = trigger["entities"][0]["lyricsStructureIndex"]
        lyrics = Lyrics(song)
        structures = song.get_structures()
        
        # The context before and after the completed part
        context_before = ""
        context_after = ""
        
        # The number of lines to generate within the paragraph
        num_lines = params["numLines"]

        # Get the range of selected structure paragraph
        start_tick = structures[structure_index].get_tick()
        end_tick = song.get_last_tick() if structure_index == len(structures) - 1 else structures[structure_index + 1].get_tick()
        
        # Find indices of lyric lines that lie within [start_tick, end_tick]
        lyrics_lines = list(lyrics.get_lines())
        indices_within_range = [i for i, line in enumerate(lyrics_lines) if start_tick <= line.get_start_tick() and line.get_end_tick() <= end_tick]
        # Approximate the number of lines to generate
        num_lines = min(num_lines, int((end_tick - start_tick) / DEFAULT_LINE_TICKS))

        # Find the last line before the range as context_before
        context_before = '\n'.join([line.get_sentence() for line in lyrics_lines if line.get_end_tick() <= start_tick])
        # Find the first line after the range as context_after
        context_after = '\n'.join([line.get_sentence() for line in lyrics_lines if line.get_start_tick() >= end_tick])
        
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
            num_lines=num_lines,
        )

        # Parse the response and arrange lyric lines
        lines = split_lyrics(response)
        if len(lines) < 1:
            raise Exception('No lyrics generated')

        # Remove the original lyric lines within the paragraph
        for line_index in reversed(sorted(indices_within_range)):
            lyrics.remove_line_at_index(line_index)
        # Insert the generated lyric lines
        num_lines = min(num_lines, len(lines))
        ticks_per_line = int((end_tick - start_tick) / num_lines)
        for i in range(num_lines - 1):
            lyrics.create_line_from_string(lines[i], start_tick + i * ticks_per_line, start_tick + (i + 1) * ticks_per_line)
        lyrics.create_line_from_string(lines[-1], start_tick + (num_lines - 1) * ticks_per_line, start_tick + num_lines * ticks_per_line)
