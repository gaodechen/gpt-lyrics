from plugin import LyricGenerationPlugin
from line_plugin import LineLyricGenerationPlugin
from structure_plugin import StructureLyricGenerationPlugin
from generate_continue_plugin import LyricGenerateContinuePlugin
from tuneflow_devkit import Runner
from pathlib import Path
import uvicorn

app = Runner(plugin_class_list=[LyricGenerationPlugin, LyricGenerateContinuePlugin, StructureLyricGenerationPlugin, LineLyricGenerationPlugin], bundle_file_path=str(Path(__file__).parent.joinpath(
    'bundle.json').absolute())).start(path_prefix='/lyrics-writer', config={
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)