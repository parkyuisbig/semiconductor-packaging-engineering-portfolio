"""Generate crossed measurement-system studies for three project CTQs."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260818


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def quantize(values: np.ndarray, resolution: float) -> np.ndarray:
    return np.round(values / resolution) * resolution


def main() -> None:
    rng = np.random.default_rng(SEED)
    root = project_root()
    raw = root / "data" / "raw"
    operators = ["OP_A", "OP_B", "OP_C"]
    rows: list[dict] = []

    studies = {
        "Edge Void Area Ratio (%)": {
            "unit": "%", "resolution": 0.01, "tolerance": 1.00,
            "true": np.linspace(0.12, 1.08, 10) + rng.normal(0, 0.015, 10),
            "before_bias": [0.000, 0.065, -0.045], "before_noise": 0.045,
            "after_bias": [0.000, 0.012, -0.008], "after_noise": 0.018,
        },
        "Chip Offset (um)": {
            "unit": "um", "resolution": 0.10, "tolerance": 30.0,
            "true": np.linspace(4.0, 31.0, 10) + rng.normal(0, 0.25, 10),
            "before_bias": [0.00, 0.80, -0.60], "before_noise": 0.90,
            "after_bias": [0.00, 0.25, -0.20], "after_noise": 0.40,
        },
        "Surface Roughness Ra (um)": {
            "unit": "um", "resolution": 0.001, "tolerance": 0.50,
            "true": np.linspace(0.20, 0.70, 10) + rng.normal(0, 0.004, 10),
            "before_bias": [0.000, 0.012, -0.009], "before_noise": 0.012,
            "after_bias": [0.000, 0.003, -0.003], "after_noise": 0.004,
        },
    }

    for metric, cfg in studies.items():
        for phase in ["Before recipe lock", "After recipe lock"]:
            bias = cfg["before_bias"] if phase.startswith("Before") else cfg["after_bias"]
            noise = cfg["before_noise"] if phase.startswith("Before") else cfg["after_noise"]
            for part_index, true_value in enumerate(cfg["true"], start=1):
                part_sensitivity = (true_value - np.mean(cfg["true"])) / np.std(cfg["true"])
                for op_index, operator in enumerate(operators):
                    interaction = 0.18 * noise * part_sensitivity * (op_index - 1)
                    for repeat in range(1, 4):
                        measured = true_value + bias[op_index] + interaction + rng.normal(0, noise)
                        measured = quantize(np.array([measured]), cfg["resolution"])[0]
                        rows.append(
                            {
                                "metric": metric,
                                "unit": cfg["unit"],
                                "phase": phase,
                                "part": f"P{part_index:02d}",
                                "operator": operator,
                                "repeat": repeat,
                                "reference_value": true_value,
                                "measured_value": measured,
                                "resolution": cfg["resolution"],
                                "engineering_tolerance": cfg["tolerance"],
                            }
                        )

    data = pd.DataFrame(rows)
    data.to_csv(raw / "measurement_study.csv", index=False)
    print(f"generated MSA rows={len(data)}, metrics={data['metric'].nunique()}")


if __name__ == "__main__":
    main()

