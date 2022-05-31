import numpy as np
import mmap
from contextlib import contextmanager
import weakref

print(np.__version__)

data = np.arange(10, dtype=np.int32)
with open("test.bin", "wb") as f_out:
    data.tofile(f_out)

@contextmanager
def my_data():
    with open("test.bin", "r+b") as f_in:
        with mmap.mmap(f_in.fileno(), 0) as mm:
            mydict = { "x": np.frombuffer(mm, dtype=np.int32, count=10, offset=0) }
            content = mydict["x"]
            yield weakref.ref(content)
            del content
            del mydict

with my_data() as d:
    print(d())
print(d())

