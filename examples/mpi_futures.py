# ~\~ language=Python filename=examples/mpi_futures.py
# ~\~ begin <<lit/mpi_oscillator.md|example-mpi>>[0]
from dask_mpi import initialize
initialize()

from dask.distributed import Client
client = Client()
# ~\~ end
