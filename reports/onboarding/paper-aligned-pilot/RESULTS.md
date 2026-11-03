# Results

New independent cohorts; complete available MRS; max top10; original candidate scoring with validated cache. These are small-model subset results, not full-paper performance.

| Round | Model | Mode | KB | Control | Non-control | Delta | CST all | CST unknown | Official status |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | llama | no_ir | 50.00% | 66.67% | 50.00% | 33.33% | 93.33% | 100.00% | passed |
| 1 | qwen | no_ir | 83.33% | 83.33% | 50.00% | 66.67% | 66.67% | 58.33% | passed |
| 1 | llama | qlang | 50.00% | 66.67% | 33.33% | 100.00% | 43.33% | 58.33% | passed |
| 1 | qwen | qlang | 66.67% | 66.67% | 33.33% | 100.00% | 66.67% | 58.33% | passed |
| 1 | llama | rel_langs | 50.00% | 50.00% | 16.67% | 200.00% | 66.67% | 83.33% | passed |
| 1 | qwen | rel_langs | 66.67% | 83.33% | 66.67% | 25.00% | 53.33% | 50.00% | passed |
| 2 | llama | no_ir | 16.67% | 16.67% | 16.67% | 0.00% | 93.33% | 83.33% | passed |
| 2 | qwen | no_ir | 100.00% | 100.00% | 66.67% | 50.00% | 63.33% | 58.33% | passed |
| 2 | llama | qlang | 83.33% | 100.00% | 33.33% | 200.00% | 50.00% | 75.00% | passed |
| 2 | qwen | qlang | 100.00% | 100.00% | 83.33% | 20.00% | 70.00% | 50.00% | passed |
| 2 | llama | rel_langs | 83.33% | 100.00% | 50.00% | 100.00% | 63.33% | 83.33% | passed |
| 2 | qwen | rel_langs | 100.00% | 100.00% | 83.33% | 20.00% | 76.67% | 66.67% | passed |
| 3 | llama | no_ir | 42.86% | 42.86% | 42.86% | 0.00% | 93.33% | 77.78% | passed |
| 3 | qwen | no_ir | 42.86% | 57.14% | 71.43% | -20.00% | 56.67% | 55.56% | passed |
| 3 | llama | qlang | 57.14% | 57.14% | 42.86% | 33.33% | 46.67% | 22.22% | passed |
| 3 | qwen | qlang | 57.14% | 85.71% | 57.14% | 50.00% | 43.33% | 44.44% | passed |
| 3 | llama | rel_langs | 71.43% | 42.86% | 71.43% | -40.00% | 36.67% | 22.22% | passed |
| 3 | qwen | rel_langs | 57.14% | 85.71% | 85.71% | 0.00% | 66.67% | 55.56% | passed |
| pooled | llama | no_ir | 36.84% | 42.11% | 36.84% | 14.29% | 93.33% | 87.88% | independently_pooled_from_territories |
| macro_mean | llama | no_ir | 36.51% | 42.06% | 36.51% | 11.11% | 93.33% | 87.04% | arithmetic_mean_of_three_rounds |
| pooled | qwen | no_ir | 73.68% | 78.95% | 63.16% | 25.00% | 62.22% | 57.58% | independently_pooled_from_territories |
| macro_mean | qwen | no_ir | 75.40% | 80.16% | 62.70% | 32.22% | 62.22% | 57.41% | arithmetic_mean_of_three_rounds |
| pooled | llama | qlang | 63.16% | 73.68% | 36.84% | 100.00% | 46.67% | 54.55% | independently_pooled_from_territories |
| macro_mean | llama | qlang | 63.49% | 74.60% | 36.51% | 111.11% | 46.67% | 51.85% | arithmetic_mean_of_three_rounds |
| pooled | qwen | qlang | 73.68% | 84.21% | 57.89% | 45.45% | 60.00% | 51.52% | independently_pooled_from_territories |
| macro_mean | qwen | qlang | 74.60% | 84.13% | 57.94% | 56.67% | 60.00% | 50.93% | arithmetic_mean_of_three_rounds |
| pooled | llama | rel_langs | 68.42% | 63.16% | 47.37% | 33.33% | 55.56% | 66.67% | independently_pooled_from_territories |
| macro_mean | llama | rel_langs | 68.25% | 64.29% | 46.03% | 86.67% | 55.56% | 62.96% | arithmetic_mean_of_three_rounds |
| pooled | qwen | rel_langs | 73.68% | 89.47% | 78.95% | 13.33% | 65.56% | 57.58% | independently_pooled_from_territories |
| macro_mean | qwen | rel_langs | 74.60% | 89.68% | 78.57% | 15.00% | 65.56% | 57.41% | arithmetic_mean_of_three_rounds |

Pooled metrics use 30 territory records per model/mode, with 19 known and 11 unknown. Macro means give each round equal weight; KB/Control/Non-control and CST unknown have different denominators across rounds, so macro and pooled may differ. Delta is recomputed after pooling Control and Non-control, not averaged as if additive.

All 540 questions, prompts, raw generated text, selected native/canonical answers, candidate scores, IDs and language distributions are saved in all_questions_and_answers.json and per-run files. Raw generated text is diagnostic: the scored choice is used for evaluation.

Source and requirements unchanged. See integrity_check.json. Old pilot results remain unchanged. Sampling and scoring changed relative to the old pilots, so old-versus-new differences cannot be attributed solely to top-k or question changes.

## llama: paired retrieval comparison

- qlang versus no_ir: KB +26.32 percentage points; CST all -46.67 percentage points; CST unknown -33.33 percentage points. CST improves/worsens/is unchanged for 1/16/13 territories. Selected answers change on 56/90 identical queries.
  Controller agreement and cross-language consistency move in opposite directions here; these measure different properties and should not be treated as interchangeable accuracy metrics.
- rel_langs versus no_ir: KB +31.58 percentage points; CST all -37.78 percentage points; CST unknown -21.21 percentage points. CST improves/worsens/is unchanged for 0/12/18 territories. Selected answers change on 60/90 identical queries.
  Controller agreement and cross-language consistency move in opposite directions here; these measure different properties and should not be treated as interchangeable accuracy metrics.
- rel_langs versus qlang: KB +5.26 percentage points; CST all +8.89 percentage points; CST unknown +12.12 percentage points. CST improves/worsens/is unchanged for 6/3/21 territories. Selected answers change on 18/90 identical queries.
- no_ir: round-wise normalized Delta CS = 33.33%, 0.00%, 0.00%. A zero non-control denominator remains undefined; invariance across a small sample is not proof that the questions determine invariance.
- qlang: round-wise normalized Delta CS = 100.00%, 200.00%, 33.33%. A zero non-control denominator remains undefined; invariance across a small sample is not proof that the questions determine invariance.
- rel_langs: round-wise normalized Delta CS = 200.00%, 100.00%, -40.00%. A zero non-control denominator remains undefined; invariance across a small sample is not proof that the questions determine invariance.

## qwen: paired retrieval comparison

- qlang versus no_ir: KB +0.00 percentage points; CST all -2.22 percentage points; CST unknown -6.06 percentage points. CST improves/worsens/is unchanged for 5/7/18 territories. Selected answers change on 19/90 identical queries.
- rel_langs versus no_ir: KB +0.00 percentage points; CST all +3.33 percentage points; CST unknown +0.00 percentage points. CST improves/worsens/is unchanged for 7/7/16 territories. Selected answers change on 18/90 identical queries.
- rel_langs versus qlang: KB +0.00 percentage points; CST all +5.56 percentage points; CST unknown +6.06 percentage points. CST improves/worsens/is unchanged for 6/3/21 territories. Selected answers change on 13/90 identical queries.
- no_ir: round-wise normalized Delta CS = 66.67%, 50.00%, -20.00%. A zero non-control denominator remains undefined; invariance across a small sample is not proof that the questions determine invariance.
- qlang: round-wise normalized Delta CS = 100.00%, 20.00%, 50.00%. A zero non-control denominator remains undefined; invariance across a small sample is not proof that the questions determine invariance.
- rel_langs: round-wise normalized Delta CS = 25.00%, 20.00%, 0.00%. A zero non-control denominator remains undefined; invariance across a small sample is not proof that the questions determine invariance.

## Interpretation limits

Retrieval-mode comparisons within this new experiment are paired. Previous pilots changed sampling, top-k and answer-selection implementation relative to this experiment, so comparisons with those pilots are not a controlled estimate of any single factor. No statistical significance or generalization to larger models is established. KB/Control/Non-control measure agreement with the supplied Controller annotation; CST measures equality of selected countries across claimant languages, not correctness.

Each round retains every available archive language for each selected territory; size-2/3/4 and controller strata approximate original composition, while geographic and exact language frequencies remain unmatched. rel_langs permits multilingual candidates but applies no per-language quota in the final global top10.
