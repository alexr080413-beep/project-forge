from __future__ import annotations

from .pipeline import run_demo_pipeline


def main() -> int:
    execution = run_demo_pipeline()
    print(f"Pipeline: {execution.pipeline.identifier}")
    print(f"Status: {execution.status.value}")
    for result in execution.results:
        print(f"- {result.stage_identifier}: {result.status.value} ({result.metadata['service']})")
    return 0 if execution.status.value == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
