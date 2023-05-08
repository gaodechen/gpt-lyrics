from tuneflow_py import TuneflowPlugin, ParamDescriptor, Song
from typing import Dict, Any


class LineLyricGenerationPlugin(TuneflowPlugin):
    @staticmethod
    def provider_id() -> str:
        return 'andantei'

    @staticmethod
    def plugin_id() -> str:
        return 'gpt-lyrics-line'

    @staticmethod
    def params(song: Song) -> Dict[str, ParamDescriptor]:
        return {}

    @staticmethod
    def run(song: Song, params: Dict[str, Any]):
        print(params)
