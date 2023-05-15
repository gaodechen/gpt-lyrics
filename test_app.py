from lyric_line_completion import LyricLineCompletionPlugin
from lyric_generation import LyricGenerationPlugin
from tuneflow_devkit import Runner
from pathlib import Path
import uvicorn

app = Runner(plugin_class_list=[LyricGenerationPlugin, LyricLineCompletionPlugin], bundle_file_path=str(Path(__file__).parent.joinpath(
    'bundle.json').absolute())).start(path_prefix='/plugin-service/lyrics_writer')

if __name__ == '__main__':
    uvicorn.run(app)
