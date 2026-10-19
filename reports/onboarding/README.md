# Onboarding functional validation

These reports cover **two constructed queries about one territorial dispute**,
in English and Spanish, using Llama-3.2-1B-Instruct on CPU with float32.
They validate prompt construction, real model generation, answer parsing,
JSON-to-CSV conversion, and applicable metric calculations. They are **not
benchmark records or evidence of the paper's model performance**.

- `run_report.json`: download/loading took approximately 65 seconds; inference
  for the two queries took **259 seconds**. Whole-process peak RSS was
  **7.47 GiB**, including download, loading, and inference.
- `subset_metrics.json`: applicable metrics for this small fixture. The
  **unmodified official CS script failed** because the unknown-controller group
  was empty (`statistics.StatisticsError: mean requires at least one data point`).
  Undefined subset metrics are recorded as `null`; the full official CS
  evaluation did not pass.

The model revision was `9213176726f574b556790deb65791e0c5aa438b6`.
Validation used Python 3.12.14, PyTorch 2.2.2+cpu, NumPy 1.26.4, and PyArrow
17.0.0. Validation helpers and environment-specific dependency overrides remain
outside the repository; source code and `requirements.txt` were not changed.
