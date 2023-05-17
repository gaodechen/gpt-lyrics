from lyric_line_completion import LyricLineCompletionPlugin
from lyric_structure_completion import LyricStructureCompletionPlugin
from lyric_generation import LyricGenerationPlugin
from tuneflow_devkit import Debugger
from pathlib import Path

if __name__ == "__main__":
    Debugger(plugin_class=LyricGenerationPlugin, bundle_file_path=str(
        Path(__file__).parent.joinpath('bundle.json').absolute())).start()
