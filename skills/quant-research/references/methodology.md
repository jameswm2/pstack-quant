# Quantitative methodology reference

Apply each item to the question. Record a rationale when an item is irrelevant. Missing evidence is a gap, not a passed check.

## Falsifiability and comparison

Specify the economic or measurement mechanism, unit of observation, target, horizon, alternative explanations, primary comparison, and what would disconfirm the hypothesis. Use an appropriate baseline and negative control. A zero forecast, lagged target, simple factor model, or existing risk model can be a better baseline than a strategy return. Avoid choosing the baseline after seeing the result.

## Temporal data validity

Distinguish event or observation time, initial publication time, availability to the researcher, revision time, decision time, and label completion. Record timezone, calendar, lag assumptions, data version, transformations, and fingerprints. A contemporary download of revised historical values is not point-in-time data.

Audit universe membership, eligibility, delistings, survivorship, corporate actions, and symbol mapping when applicable. Explain missingness and exclusions. Name unavailable data and which claims it blocks. Never invent a data-provider receipt or infer publication timestamps from row dates.

## Evaluation regime

Freeze temporal training, validation, and holdout periods before fitting. Estimate transformations on training data only. Explain dependence, overlapping labels, purge boundaries, and embargo lengths in terms of the labels and decision horizon. An arbitrary embargo is not a leakage proof.

Count the full family of tried variants, including negative, failed, and abandoned attempts. Record selection, stopping, and model comparison rules before execution. Use the decision rule suited to the study. There is no universal Sharpe, p-value, return, drawdown, or profitability threshold in this plugin.

## Financial and operational assumptions

For tradable strategies, specify decision and fill timing, spread, fees, slippage, turnover, liquidity, capacity, financing, and shorting constraints as applicable. Explain why the timestamped information could be available before the proposed fill. Quantify assumptions where evidence supports it. Label stylized fills and unmeasured capacity.

For forecasts, event studies, and risk models, define loss functions, event windows, exposure aggregation, estimation error, and downstream use. Explain why execution costs or fills do not apply when they do not. Independent execution-risk review still challenges model use and operational assumptions.

## Uncertainty and selection

Use effect sizes and uncertainty appropriate to serial, cross-sectional, event, or portfolio dependence. Explain sample-size limits, structural breaks, regime selection, sensitivity, and multiple testing. State what was computed and what remains qualitative. Do not turn a small synthetic result into a market finding.

[The probability of backtest overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf) motivates accounting for strategy selection across trials. [The deflated Sharpe ratio](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) discusses selection bias and non-normal returns. These are methodological references, not implemented statistical procedures in the evidence helper or example.

## Reproduction

Record the exact command, code revision or content hashes, environment and dependencies, seeds, input provenance, output hashes, and limits. Reproduce in a fresh directory and compare observed artifacts. For nondeterministic methods, preregister acceptable differences and explain observed differences. Compilation, a claimed rerun, and a reviewer agreeing with the author are not reproduction evidence.
