# ~\~ language=Python filename=test/test_foam_run.py
# ~\~ begin <<lit/testing.md|test/test_foam_run.py>>[0]
from pathlib import Path
from shutil import copytree
from os import listdir

from pintFoam.vector import BaseCase
from pintFoam.solution import foam
from pintFoam.utils import pushd

def run_block_mesh(case: BaseCase):
    import subprocess
    subprocess.run("blockMesh", cwd=case.path, check=True)

def test_basic_pitzDaily(tmp_path):
    path = Path(tmp_path) / "case0"
    data = Path(".") / "test" / "cases" / "pitzDaily"
    copytree(data, path / "base")

    base_case = BaseCase(path, "base")
    run_block_mesh(base_case)

    init_vec = base_case.new_vector()
    end_vec = foam("scalarTransportFoam", 0.01, init_vec, 0.0, 0.1)
    print(listdir(path))
# ~\~ end
