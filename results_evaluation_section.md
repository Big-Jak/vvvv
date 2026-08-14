# Results & Evaluation

## Evaluation Methodology

We evaluated our system along three complementary axes: (1) agreement between the LLM-generated scores and human-assigned scores, (2) a classical machine learning baseline as a sanity check on the LLM approach, and (3) human evaluation of the feedback text itself. We used Quadratic Weighted Kappa (QWK) as our primary agreement metric, since it penalizes larger scoring disagreements more heavily than small ones and is the standard metric for essay-scoring tasks. Pearson and Spearman correlation served as secondary checks.

A note on scope: due to time and API cost constraints, the LLM pipeline evaluation was run on a sample of 20 essays from a single essay set (essay_set 1 of the ASAP-AES dataset), using Claude Haiku. The baseline model and fairness analysis were run on the full ASAP 2.0 dataset (17,308 training essays, 3,710 validation essays). We address the resulting comparability limitations below.

## LLM Pipeline vs. Human Scores

On the 20-essay sample, the LLM-generated overall scores showed **no meaningful agreement** with human-assigned scores: QWK = -0.084, Pearson r = -0.113 (p = 0.635), Spearman r = -0.170 (p = 0.474). Neither correlation was statistically significant given the small sample.

Investigating the cause, we found two contributing issues. First, a scale mismatch: our prompt asked the model to score essays on a 1–6 scale, but essay_set 1's actual human scores range from 6–11, meaning no output from the model could have matched the human scale even in principle. Second, and more concerning, the model showed very little score variance of its own: 18 of the 20 essays received an identical score of 2, regardless of essay quality, indicating the model was not meaningfully discriminating between essays at all.

## Classical Baseline

To sanity-check whether the LLM's poor performance reflected a fundamental limitation of the approach or an issue specific to this prompt/model combination, we trained a classical baseline: a Ridge regression model over TF-IDF text features, trained on the ASAP 2.0 training set and evaluated on the held-out validation set (n = 3,710). This baseline achieved QWK = 0.682, Pearson r = 0.743 (p < 0.001), and Spearman r = 0.735 (p < 0.001) — a substantially stronger result than the LLM pipeline.

This gap is informative rather than a case against LLM-based scoring in general: it demonstrates that a simple, well-scaled model can perform reasonably on this task, and strongly suggests our LLM pipeline's underperformance stems from the scale mismatch and low output variance identified above, rather than an inherent inability of LLMs to assess essay quality.

## Human Evaluation of Feedback Quality

Separately from the numeric scoring, we asked two raters (one team member, one outside volunteer) to rate the LLM-generated feedback text itself on actionability and correctness (1–5 scale), for a subset of 5 of the 20 essays. Mean actionability was 4.0/5 and mean correctness was 3.8/5. Clarity was not rated due to volunteer time constraints.

Although this sample is small, the result is notable: it suggests the LLM's qualitative feedback (strengths, weaknesses, suggestions) was reasonably useful and accurate even though its numeric overall score was not. This points toward the scoring mechanism specifically, rather than the feedback-generation pipeline as a whole, as the component needing correction.

## Fairness Analysis

Using the baseline model, we examined whether prediction accuracy differed across demographic subgroups available in the ASAP 2.0 dataset, evaluated on the validation set (n = 3,710):

| Group | n | QWK |
|---|---|---|
| ELL: No | 3,107 | 0.688 |
| ELL: Yes | 541 | 0.553 |
| Economically disadvantaged: No | 1,236 | 0.708 |
| Economically disadvantaged: Yes | 1,891 | 0.636 |
| Race/Ethnicity: Asian/Pacific Islander | 223 | 0.769 |
| Race/Ethnicity: White | 1,461 | 0.703 |
| Race/Ethnicity: American Indian/Alaskan Native | 16 | 0.663 |
| Race/Ethnicity: Black/African American | 658 | 0.648 |
| Race/Ethnicity: Hispanic/Latino | 1,111 | 0.648 |
| Race/Ethnicity: Two or more races/Other | 239 | 0.605 |

The clearest gap is by ELL status: the model agrees with human scores meaningfully less well for English-language learners (QWK 0.553) than for non-ELL students (QWK 0.688), a gap unlikely to be due to chance given the group size (n = 541). A smaller gap exists by economic disadvantage. Race/ethnicity shows more spread without one group standing out sharply. We discuss the likely cause and implications in the Ethical Considerations section.

## Limitations

Several limitations affect how these results should be read. The LLM evaluation and baseline/fairness evaluation used different dataset versions — ASAP-AES (essay_set 1, scores 6–11) for the LLM pipeline, and ASAP 2.0 (holistic scores 1–6, with demographic metadata) for the baseline and fairness analysis — so the two are not directly comparable on identical essays. The LLM sample size (20 essays, one essay set, one model) is small; results may not generalize to other essay sets or to a corrected prompt/model configuration. The human evaluation sample is smaller still (5 essays, 2 raters, 2 of 3 planned rubric dimensions). Given more time, the priority next steps would be: (1) correcting the LLM prompt's score scale to match each essay set, (2) re-running with a stronger model, and (3) evaluating on a matched sample across both dataset versions for a fair head-to-head comparison.

### 7. LLM Pipeline — Second Attempt (n=50, corrected prompt)

- Quadratic Weighted Kappa: 0.010
- Pearson r: 0.015 (p=0.919)
- Spearman r: 0.005 (p=0.97)

Finding: after fixing the score-variance issue (LLM scores now range 2-5,
vs. a flat 2 before), agreement with human scores is still near zero.
Unlike the first attempt, this is not a simple scale problem — the model's
relative ranking of essays doesn't track human rankings at all (e.g. essays
humans scored 6 and 11 receive similar LLM scores). This suggests the model
struggles with comparative judgment of essay quality, not just scale
calibration.

Conclusion: across two attempts, the LLM pipeline has not achieved
meaningful agreement with human scores on this task. The classical
baseline (QWK 0.682) remains the stronger-performing approach in our
evaluation. Given project time constraints, further LLM prompt iteration
(few-shot examples, stronger model) is noted as future work rather than
completed here.
