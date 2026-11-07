"""Run a completely offline, synthetic demonstration."""

from ils_simpro.fixtures import sample_job

if __name__ == "__main__":
    print(sample_job().model_dump_json(indent=2))
