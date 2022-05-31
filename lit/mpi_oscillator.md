# Example using MPI and Dask Futures
There are two modes in which we may run Dask with MPI. One with a `dask-mpi` running as external scheduler, the other running everything as a single script. For this example we opt for the second, straight from the dask-mpi documentation:

``` {.python file=examples/mpi_futures.py #example-mpi}
from dask_mpi import initialize
initialize()

from dask.distributed import Client
client = Client()
```


