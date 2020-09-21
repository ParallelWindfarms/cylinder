# ~\~ language=Python filename=test/test_foam_run.py
# ~\~ begin <<lit/testing.md|test/test_foam_run.py>>[0]
from pathlib import Path
from shutil import copytree
import numpy as np

from pintFoam.vector import BaseCase
from pintFoam.solution import (run_block_mesh, foam, get_times)

pitzDaily_fields = {
    "region0/field/{}".format(f)
    for f in ["T", "U", "phi"]
}

def test_basic_pitzDaily(tmp_path):
    path = Path(tmp_path) / "case0"
    data = Path(".") / "test" / "cases" / "pitzDaily"
    copytree(data, path / "base")

    base_case = BaseCase(path, "base")
    base_case.fields = pitzDaily_fields
    run_block_mesh(base_case)

    base_vec = base_case.new_vector()
    init_vec = foam("scalarTransportFoam", 0.001, base_vec, 0.0, 0.001)
    init_vec.time = "0"
    end_vec = foam("scalarTransportFoam", 0.01, init_vec, 0.0, 0.1)

    assert (end_vec.path / "adiosData").exists()
    assert end_vec.time == "0.1"

    end_vec_clone = end_vec.clone()
    assert end_vec_clone.time == "0.1"
    assert get_times(end_vec_clone.path) == ["0.1"]

    assert pitzDaily_fields < set(end_vec.data().available_variables().keys())
    diff_vec = end_vec - init_vec
    assert pitzDaily_fields < set(diff_vec.data().available_variables().keys())

    for f in pitzDaily_fields:
        a = end_vec.read(f)
        b = init_vec.read(f)
        c = diff_vec.read(f)
        assert np.abs(a - b - c).mean() < 1e-6

    assert diff_vec.time == "0.1"
    orig_vec = init_vec + diff_vec
    should_be_zero = end_vec - orig_vec
    for f in pitzDaily_fields:
        f = should_be_zero.data().read(f)
        assert np.all(np.abs(f) < 10e-6)
# ~\~ end
