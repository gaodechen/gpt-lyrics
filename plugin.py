from tuneflow_py import TuneflowPlugin, ParamDescriptor, Song, WidgetType, TuneflowPluginTriggerData
from tuneflow_py import Lyrics

from typing import Dict, List, Any

from ai_config import AIConfig
from ai_api import get_engine_api
from ai_prompt import LyricPrompt
from utils import *

STRUCTURE_NAMES = ['chorus', 'verse', 'intro', 'bridge', 'outro']
# TODO: use dynamic word duration
DEFAULT_WORD_TICKS = 170


class LyricGenerationPlugin(TuneflowPlugin):
    @staticmethod
    def provider_id() -> str:
        return 'andantei'

    @staticmethod
    def plugin_id() -> str:
        return 'gpt-lyrics'

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
        }

    @staticmethod
    def split_lyrics(lyrics: str) -> List[str]:
        '''
        Post-process the API responses, splitting them into individual lines.
        The output may include structural labels and non-lyrical content,
        which should be removed to ensure only the desired lyrics are retained.
        '''
        start_index = lyrics.find("[start]")
        end_index = lyrics.find("[end]")
        lyrics = lyrics[start_index + len("[start]"):end_index]

        # Split the lyrics into lines and remove leading/trailing spaces
        lines = [line.strip() for line in lyrics.split("\n") if line.strip()]
        # Remove lines that contain structure names
        lines = [line for line in lines if not any(structure in line.lower() for structure in STRUCTURE_NAMES)]

        return lines

    @staticmethod
    def run(song: Song, params: Dict[str, Any]):
        trigger: TuneflowPluginTriggerData = params["trigger"]
        track_id = trigger["entities"][0]["trackId"]
        track = song.get_track_by_id(track_id=track_id)
        if track is None:
            raise Exception('Track not found')
        
        api = get_engine_api(
            cfg=AIConfig(),
            prompt=LyricPrompt(lang=contains_chinese(params["prompt"]) and "zh" or "en")
        )

        response = api.generate(
            user_demands=params["prompt"],
            temperature=params["temperature"],
        )

        lines = LyricGenerationPlugin.split_lyrics(response)

        visible_notes = sorted(
            track.get_visible_notes(),
            key=lambda note: note.get_start_tick()
        )
        melody_start_tick = visible_notes[0].get_start_tick()
        melody_end_tick = visible_notes[-1].get_end_tick()

        lyrics = Lyrics(song)
        lyrics.clear()

        line_start_offset = melody_start_tick
        for line in lines:
            line_duration = DEFAULT_WORD_TICKS * len(line)
            if line_start_offset + line_duration > melody_end_tick:
                break
            lyrics.create_line_from_string(
                line, line_start_offset, line_start_offset + line_duration)
            line_start_offset += line_duration
