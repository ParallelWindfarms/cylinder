from pintFoam.utils import (generate_job_name)
import pytest
import uuid

def test_generate_job_name():
    uid = uuid.uuid4()

    # Test name generation
    assert generate_job_name(0, 0, 1, uid, "fine", tlength=2) == f"0-00-10-fine-{uid.hex}"
    assert generate_job_name(0, 0.0, 1, uid, "fine", tlength=3) == f"0-000-100-fine-{uid.hex}"
    assert generate_job_name(0, 0.00125, 0.005, uid, "fine", tlength=2) == f"0-12-50-fine-{uid.hex}"
    assert generate_job_name(0, 0.00125, 0.005, uid, "fine", tlength=3) == f"0-125-500-fine-{uid.hex}"
    assert generate_job_name(1, 0.00125, 0.005, uid, "coarse", tlength=4) == f"1-1250-5000-coarse-{uid.hex}"

    # Test errors
    with pytest.raises(ValueError):
        generate_job_name(-1, 0, -1, uid, "fine", tlength=2)
        generate_job_name(0, -1, -1, uid, "fine", tlength=2)