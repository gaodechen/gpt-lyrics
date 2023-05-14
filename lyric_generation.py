from tuneflow_py import TuneflowPlugin, ParamDescriptor, Song, Lyrics, WidgetType, TuneflowPluginTriggerData, InjectSource

import math
from typing import Dict, Any

from ai_config import AIConfig
from ai_api import get_engine_api
from ai_prompt import LyricPrompt
from utils import DEFAULT_WORD_TICKS
from utils import get_writing_language, split_lyrics


class LyricsGenerationPlugin(TuneflowPlugin):
    '''
    Write lyrics from scratch or continue writing based on the lyric context
    '''
    @staticmethod
    def provider_id() -> str:
        return 'andantei'

    @staticmethod
    def plugin_id() -> str:
        return 'gpt-lyrics-generate'

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
                    "zh": "简短的描述你想要生成歌词的风格、主题、内容等"
                },
                "defaultValue": None,
                "widget": {
                    "type": WidgetType.TextArea.value,
                    "config": {
                        "placeholder": {
                            "zh": "样例：有关梦想和希望的流行歌曲",
                            "en": "e.g. a pop song about dreams and hope"
                        },
                        "maxLength": 300
                    }
                }
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
                    "en": "Esimated Nubmer of Lines",
                    "zh": "预计乐句数量"
                },
                "defaultValue": 4,
                "description": {
                    "en": "The estimated of lines to generate or continue writing",
                    "zh": "生成或续写乐句的大致数量"
                },
                "widget": {
                    "type": WidgetType.Slider.value,
                    "config": {
                        "minValue": 1,
                        "maxValue": 64,
                        "step": 1,
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
            "empty": {
                "displayName": {
                    "en": "Empty Current Lyrics",
                    "zh": "清空当前歌词"
                },
                "description": {
                    "en": "Whether to empty the current lyrics before generating",
                    "zh": "是否在生成新歌词前清空当前已有歌词"
                },
                "defaultValue": False,
                "widget": {
                    "type": WidgetType.Switch.value,
                },
            }
        }

    @staticmethod
    def run(song: Song, params: Dict[str, Any]):
        lang = params["language"]
        user_lang = params["userLanguage"]
        num_lines = params["numLines"]
        empty = params["empty"]
        lang = get_writing_language(lang, user_lang)
        
        trigger: TuneflowPluginTriggerData = params["trigger"]
        
        lyrics = Lyrics(song)
        if empty:
            lyrics.clear()
        # Whether to continue writing rather than generate from scratch
        from_scratch = len(lyrics) == 0
            
        start_tick: int = 0
        end_tick: int = math.inf
        
        if trigger["type"] == "lyrics-generate":
            # Triggered by the global lyric editor
            # Continue from the last line or generate from scratch
            start_tick = 0 if from_scratch else lyrics[len(lyrics)-1].get_start_tick()
        elif trigger["type"] == "context-track-content":
            # Triggered on a MIDI track
            track_id = trigger["entities"][0]["trackId"]
            track = song.get_track_by_id(track_id=track_id)
            if track is None:
                raise Exception('Track not found')
            visible_notes = sorted(
                track.get_visible_notes(),
                key=lambda note: note.get_start_tick()
            )
            if len(visible_notes) == 0:
                return
            # Lyrics are generated within the range of visible notes
            start_tick = visible_notes[0].get_start_tick()
            end_tick = visible_notes[-1].get_end_tick()
            if from_scratch:
                # Continue writing from the last line within visible notes if there is one
                start_tick = max(lyrics[len(lyrics)-1].get_start_tick(), start_tick)
        else:
            raise Exception('Trigger type not supported')

        # Generate lyrics through OpenAI APIs
        api = get_engine_api(
            cfg=AIConfig(),
            prompt=LyricPrompt(lang=lang)
        )
        
        lyric_contents = '\n'.join([line.get_sentence() for line in lyrics])
        response = api.generate(
            user_demands=params["prompt"],
            temperature=params["temperature"],
            context_before=lyric_contents,
            num_lines=num_lines,
        )

        # Parse the response and arrange lyric lines
        lines = split_lyrics(response)
        
        line_start_offset = start_tick
        for i, line in enumerate(lines):
            line_duration = DEFAULT_WORD_TICKS * len(line)
            if i > num_lines or line_start_offset + line_duration > end_tick:
                break
            lyrics.create_line_from_string(
                line, line_start_offset, line_start_offset + line_duration)
            line_start_offset += line_duration
