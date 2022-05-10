from pintFoam.utils import (generate_job_name)
import uuid

def test_generate_job_name():
    uid = uuid.uuid4()

    assert generate_job_name(0, 0.00125, 0.005, uid, "fine", tlength=2) == f"0-12-50-fine-{uid.hex}"
    assert generate_job_name(0, 0.00125, 0.005, uid, "fine", tlength=3) == f"0-125-500-fine-{uid.hex}"
    assert generate_job_name(1, 0.00125, 0.005, uid, "coarse", tlength=4) == f"1-1250-5000-coarse-{uid.hex}"