from pathlib import Path
import shutil

shutil.copytree(Path("frontend/dist"), Path("public"), dirs_exist_ok=True)
