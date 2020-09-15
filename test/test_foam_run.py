# ~\~ language=Python filename=test/test_foam_run.py
# ~\~ begin <<lit/testing.md|test/test_foam_run.py>>[0]
from pathlib import Path
from shutil import copytree

from pintFoam.vector import BaseCase
from pintFoam.solution import (run_block_mesh, foam, get_times)

def test_basic_pitzDaily(tmp_path):
    path = Path(tmp_path) / "case0"
    data = Path(".") / "test" / "cases" / "pitzDaily"
    copytree(data, path / "base")

    base_case = BaseCase(path, "base")
    run_block_mesh(base_case)

    init_vec = base_case.new_vector()
    end_vec = foam("scalarTransportFoam", 0.01, init_vec, 0.0, 0.1)

    assert (end_vec.path / "adiosData").exists()
    assert end_vec.time == "0.1"

    end_vec_clone = end_vec.clone()
    assert end_vec_clone.time == "0.1"
    print(list(end_vec_clone.path.glob("adiosData/*")))
    assert get_times(end_vec_clone.path) == ["0.1"]
# ~\~ end
