"""Run a completely offline, synthetic demonstration."""

from ils_simpro.fixtures import sample_job
from ils_simpro.offline import OfflineJobRepository

if __name__ == "__main__":
    repository = OfflineJobRepository([sample_job()])
    print(repository.get_job("DEMO-1001").model_dump_json(indent=2))
