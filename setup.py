from pathlib import Path
import shutil
from setuptools import setup
from setuptools.command.build_py import build_py

class BuildWithSkill(build_py):
    def run(self):
        super().run()
        root=Path(__file__).resolve().parent
        shutil.copytree(root/'skills/fig-cos',Path(self.build_lib)/'fig_cos/skills/fig-cos',
            dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))

setup(cmdclass={'build_py':BuildWithSkill})
