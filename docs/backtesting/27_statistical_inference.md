### Statistical Inference

Performance statistics such as average return, Sharpe ratio, Information Coefficient, or long–short spread are sample estimates.

They are therefore subject to sampling uncertainty.

A backtest that produces a positive average return does not automatically imply that the underlying strategy has positive expected return.

The purpose of statistical inference is to assess whether the observed performance is sufficiently large relative to its sampling variability.

Let

``` math
\begin{equation}
R_t,
\qquad
t=1,\ldots,T,
\end{equation}
```

denote the strategy return series.

The sample mean is

``` math
\begin{equation}
\bar{R}
=
\frac{1}{T}
\sum_{t=1}^{T}
R_t.
\end{equation}
```

The central inferential question is whether the population mean

``` math
\begin{equation}
\mu
=
\mathbb{E}[R_t]
\end{equation}
```

is statistically different from a reference value, usually zero.

However, financial backtests create several complications:

- returns may be heteroskedastic;

- returns may be serially correlated;

- portfolio holding periods may overlap;

- many strategies may have been tested before the reported one was selected;

- parameters and hyperparameters may have been chosen using the same historical sample;

- the reported Sharpe ratio may therefore be upward biased by selection.

Consequently,

``` math
\begin{equation}
\boxed{
\text{Statistical Significance}
\neq
\text{Economic Significance}
\neq
\text{Research Robustness}.
}
\end{equation}
```

All three dimensions should be considered jointly.

#### Mean Return Tests and $`t`$-Statistics

Consider the null hypothesis

``` math
\begin{equation}
\boxed{
H_0:
\mu
=
\mu_0,
}
\end{equation}
```

against an alternative such as

``` math
\begin{equation}
H_1:
\mu
>
\mu_0.
\end{equation}
```

Usually,

``` math
\begin{equation}
\mu_0=0.
\end{equation}
```

Under the simplest independent and identically distributed assumption, the sample variance is

``` math
\begin{equation}
\widehat{\sigma}^{2}
=
\frac{1}{T-1}
\sum_{t=1}^{T}
(R_t-\bar{R})^2.
\end{equation}
```

The standard error of the sample mean is

``` math
\begin{equation}
\boxed{
SE(\bar{R})
=
\frac{
\widehat{\sigma}
}{
\sqrt{T}
}.
}
\end{equation}
```

The corresponding $`t`$-statistic is

``` math
\begin{equation}
\boxed{
t
=
\frac{
\bar{R}-\mu_0
}{
SE(\bar{R})
}
=
\frac{
\sqrt{T}
(\bar{R}-\mu_0)
}{
\widehat{\sigma}
}.
}
\end{equation}
```

##### Connection with the Sharpe Ratio

If

``` math
\begin{equation}
\mu_0=0,
\end{equation}
```

the non-annualized sample Sharpe ratio is

``` math
\begin{equation}
\widehat{SR}
=
\frac{
\bar{R}
}{
\widehat{\sigma}
}.
\end{equation}
```

Therefore,

``` math
\begin{equation}
\boxed{
t
=
\sqrt{T}
\widehat{SR}.
}
\end{equation}
```

If the Sharpe ratio is annualized using $`A`$ observations per year,

``` math
\begin{equation}
\widehat{SR}_{\mathrm{ann}}
=
\sqrt{A}
\frac{
\bar{R}
}{
\widehat{\sigma}
},
\end{equation}
```

then

``` math
\begin{equation}
\boxed{
t
=
\sqrt{
\frac{T}{A}
}
\widehat{SR}_{\mathrm{ann}}.
}
\end{equation}
```

Thus, statistical evidence depends jointly on the magnitude of the Sharpe ratio and the length of the historical sample.

##### One-Sided vs. Two-Sided Tests

A two-sided hypothesis test uses

``` math
\begin{equation}
H_1:
\mu\neq0,
\end{equation}
```

whereas a one-sided test may use

``` math
\begin{equation}
H_1:
\mu>0.
\end{equation}
```

A one-sided test is appropriate only if the direction of the alternative was specified before observing the data.

Changing from a two-sided to a one-sided test after observing positive performance constitutes an additional research choice and can overstate statistical evidence.

#### Serial Dependence and Heteroskedasticity

The standard error

``` math
\begin{equation}
SE(\bar{R})
=
\frac{
\widehat{\sigma}
}{
\sqrt{T}
}
\end{equation}
```

is valid under restrictive assumptions.

Financial strategy returns may exhibit:

``` math
\begin{equation}
\boxed{
\text{Heteroskedasticity}
}
\end{equation}
```

and

``` math
\begin{equation}
\boxed{
\text{Serial Dependence}.
}
\end{equation}
```

##### Heteroskedasticity

Heteroskedasticity means that conditional variance changes through time:

``` math
\begin{equation}
\operatorname{Var}
\left(
R_t
\mid
\mathcal{I}_{t-1}
\right)
=
\sigma_t^2,
\end{equation}
```

where

``` math
\begin{equation}
\sigma_t^2
\end{equation}
```

is not constant.

This is common in financial returns because volatility tends to cluster.

##### Serial Correlation

Serial correlation means

``` math
\begin{equation}
\boxed{
\operatorname{Cov}
\left(
R_t,
R_{t-k}
\right)
\neq
0
}
\end{equation}
```

for some lag $`k>0`$.

Define the autocovariance at lag $`k`$ as

``` math
\begin{equation}
\gamma_k
=
\operatorname{Cov}
\left(
R_t,
R_{t-k}
\right).
\end{equation}
```

The variance of the sample mean is then not simply

``` math
\begin{equation}
\frac{\sigma^2}{T}.
\end{equation}
```

More generally,

``` math
\begin{equation}
\operatorname{Var}(\bar{R})
=
\frac{1}{T^2}
\sum_{t=1}^{T}
\sum_{s=1}^{T}
\operatorname{Cov}(R_t,R_s).
\end{equation}
```

For a weakly stationary process, this can be written approximately as

``` math
\begin{equation}
\boxed{
\operatorname{Var}(\bar{R})
\approx
\frac{1}{T}
\left[
\gamma_0
+
2
\sum_{k=1}^{\infty}
\gamma_k
\right].
}
\end{equation}
```

The term

``` math
\begin{equation}
\gamma_0
+
2
\sum_{k=1}^{\infty}
\gamma_k
\end{equation}
```

is the long-run variance.

##### Overlapping Returns

Serial dependence is especially important when holding periods overlap.

Suppose a strategy forms daily forecasts of future $`h`$-day returns:

``` math
\begin{equation}
R_{t\rightarrow t+h}.
\end{equation}
```

Adjacent observations,

``` math
\begin{equation}
R_{t\rightarrow t+h}
\end{equation}
```

and

``` math
\begin{equation}
R_{t+1\rightarrow t+h+1},
\end{equation}
```

share most of their underlying daily returns.

Therefore, the observations are mechanically dependent.

Ignoring this dependence generally understates the standard error and overstates the corresponding $`t`$-statistic.

#### Newey–West Standard Errors

Newey–West standard errors provide a *heteroskedasticity- and autocorrelation-consistent* estimate of the sampling variance.

For inference on the mean return, define residuals

``` math
\begin{equation}
u_t
=
R_t-\bar{R}.
\end{equation}
```

The sample autocovariance at lag $`k`$ is

``` math
\begin{equation}
\boxed{
\widehat{\gamma}_k
=
\frac{1}{T}
\sum_{t=k+1}^{T}
u_tu_{t-k}.
}
\end{equation}
```

Choose a truncation lag

``` math
\begin{equation}
L\geq0.
\end{equation}
```

The Newey–West estimate of the long-run variance is

``` math
\begin{equation}
\boxed{
\widehat{\Omega}_{NW}
=
\widehat{\gamma}_0
+
2
\sum_{k=1}^{L}
\omega_k
\widehat{\gamma}_k,
}
\end{equation}
```

where the Bartlett weights are

``` math
\begin{equation}
\boxed{
\omega_k
=
1
-
\frac{k}{L+1}.
}
\end{equation}
```

The HAC standard error of the sample mean is then

``` math
\begin{equation}
\boxed{
SE_{NW}(\bar{R})
=
\sqrt{
\frac{
\widehat{\Omega}_{NW}
}{
T
}
}.
}
\end{equation}
```

The corresponding $`t`$-statistic is

``` math
\begin{equation}
\boxed{
t_{NW}
=
\frac{
\bar{R}-\mu_0
}{
SE_{NW}(\bar{R})
}.
}
\end{equation}
```

##### Choice of Lag Length

The lag parameter $`L`$ determines how much serial dependence is incorporated.

If $`L=0`$, the estimator allows for heteroskedasticity but ignores serial correlation.

As $`L`$ increases, more autocovariances are included.

For overlapping $`h`$-period returns, a natural minimum diagnostic choice is often related to

``` math
\begin{equation}
h-1,
\end{equation}
```

although the appropriate lag depends on the exact data-generating process and sampling frequency.

Robustness to alternative reasonable lag choices should therefore be checked.

#### Bootstrap Methods

Bootstrap methods approximate the sampling distribution of a statistic by resampling the observed data.

Let

``` math
\begin{equation}
\widehat{\theta}
=
g
\left(
R_1,\ldots,R_T
\right)
\end{equation}
```

denote a statistic such as:

- mean return;

- Sharpe ratio;

- maximum drawdown;

- Information Ratio;

- factor alpha.

A bootstrap generates replicated samples

``` math
\begin{equation}
\left\{
R_t^{*(b)}
\right\}_{t=1}^{T},
\qquad
b=1,\ldots,B,
\end{equation}
```

and corresponding statistics

``` math
\begin{equation}
\boxed{
\widehat{\theta}^{*(b)}
=
g
\left(
R_1^{*(b)},
\ldots,
R_T^{*(b)}
\right).
}
\end{equation}
```

The empirical distribution

``` math
\begin{equation}
\left\{
\widehat{\theta}^{*(1)},
\ldots,
\widehat{\theta}^{*(B)}
\right\}
\end{equation}
```

approximates the sampling distribution of the statistic.

##### IID Bootstrap

The simplest bootstrap independently resamples individual return observations.

This is appropriate only when serial dependence is negligible.

If returns are autocorrelated, independently resampling observations destroys the temporal dependence structure.

##### Block Bootstrap

To preserve local serial dependence, consecutive blocks of observations can be resampled.

Let the block length be

``` math
\begin{equation}
L_B.
\end{equation}
```

A block bootstrap resamples sequences such as

``` math
\begin{equation}
(R_t,\ldots,R_{t+L_B-1})
\end{equation}
```

rather than isolated observations.

Common variants include:

- moving-block bootstrap;

- circular-block bootstrap;

- stationary bootstrap.

Block methods are generally more appropriate for financial strategies with serially dependent returns.

##### Bootstrap Confidence Intervals

For confidence level $`1-\alpha`$, a simple percentile interval is

``` math
\begin{equation}
\boxed{
\left[
q_{\alpha/2}
\left(
\widehat{\theta}^{*}
\right),
\;
q_{1-\alpha/2}
\left(
\widehat{\theta}^{*}
\right)
\right].
}
\end{equation}
```

This allows uncertainty to be quantified for statistics whose analytical sampling distributions may be difficult to derive.

#### Multiple Hypothesis Testing

Backtesting frequently involves testing many candidate strategies.

Suppose

``` math
\begin{equation}
M
\end{equation}
```

hypotheses are tested:

``` math
\begin{equation}
H_{0,1},
\ldots,
H_{0,M}.
\end{equation}
```

Even if every null hypothesis is true, some strategies will appear significant by chance.

If each independent hypothesis is tested at significance level $`\alpha`$, the probability of obtaining at least one false positive is

``` math
\begin{equation}
\boxed{
P(\text{at least one false positive})
=
1-(1-\alpha)^M.
}
\end{equation}
```

As

``` math
\begin{equation}
M\rightarrow\infty,
\end{equation}
```

this probability approaches one.

##### Bonferroni Correction

A conservative adjustment is to use the individual significance threshold

``` math
\begin{equation}
\boxed{
\alpha_{\mathrm{ind}}
=
\frac{
\alpha
}{
M
}.
}
\end{equation}
```

Equivalently, raw $`p`$-values may be multiplied by $`M`$:

``` math
\begin{equation}
\boxed{
p_i^{\mathrm{adj}}
=
\min
\left(
Mp_i,
1
\right).
}
\end{equation}
```

##### False Discovery Rate

Rather than controlling the probability of any false positive, False Discovery Rate methods control the expected proportion of false discoveries among the rejected hypotheses.

This can be less conservative when many strategies or signals are evaluated.

The appropriate correction depends on the research objective and dependence structure among tested hypotheses.

#### Data Snooping Adjustments

Multiple hypothesis testing becomes particularly problematic when only the best historical strategy is ultimately reported.

Suppose a researcher evaluates

``` math
\begin{equation}
M
\end{equation}
```

strategies and selects

``` math
\begin{equation}
m^*
=
\underset{m=1,\ldots,M}{\arg\max}
\;
\widehat{SR}_m.
\end{equation}
```

Then

``` math
\begin{equation}
\boxed{
\mathbb{E}
\left[
\widehat{SR}_{m^*}
\right]
}
\end{equation}
```

is upward biased relative to the performance of a strategy chosen independently of the historical sample.

This phenomenon is often referred to as data snooping or selection bias.

##### What Counts as a Trial?

The effective number of trials is not limited to completely different trading strategies.

Research choices may include:

- different characteristics;

- alternative lookback windows;

- alternative winsorization thresholds;

- alternative neutralization specifications;

- alternative portfolio mappings;

- different investment universes;

- different model hyperparameters;

- different transaction-cost assumptions.

If these choices are influenced by backtest performance, they contribute to the effective amount of data snooping.

##### Dependent Trials

Candidate strategies are often highly correlated.

Therefore,

``` math
\begin{equation}
M_{\mathrm{effective}}
<
M
\end{equation}
```

may hold when many tested strategies are only minor variations of one another.

Nevertheless, correlation between trials does not eliminate the selection problem.

The statistical correction should ideally reflect both the number and dependence structure of the experiments performed.

#### Deflated Sharpe Ratio

The Sharpe ratio of a selected backtest is generally upward biased when the reported strategy has been chosen after testing multiple alternatives.

Suppose the researcher evaluates $`N`$ candidate strategy specifications and selects the strategy with the highest observed Sharpe ratio:

``` math
\begin{equation}
m^*
=
\arg\max_{m=1,\ldots,N}
\widehat{SR}_m.
\end{equation}
```

Even if none of the candidate strategies possesses genuine alpha, the maximum

``` math
\begin{equation}
\max_m \widehat{SR}_m
\end{equation}
```

will generally be positive simply because several noisy estimates were examined.

The Deflated Sharpe Ratio (DSR) addresses this problem by asking whether the Sharpe ratio of the selected strategy is sufficiently large relative to a benchmark that accounts for:

- finite-sample estimation uncertainty;

- non-Gaussian returns;

- multiple strategy trials;

- selection of the best-performing specification.

The logic can be summarized as

``` math
\begin{equation}
\boxed{
\text{Observed Sharpe}
\rightarrow
\text{Multiple-Trial Benchmark}
\rightarrow
\text{Sampling Adjustment}
\rightarrow
\text{Deflated Sharpe Ratio}.
}
\end{equation}
```

##### Observed Sharpe Ratio

Let

``` math
\begin{equation}
\widehat{SR}
\end{equation}
```

denote the Sharpe ratio of the strategy ultimately selected by the research process.

All Sharpe ratios used in the DSR calculation must follow the same convention.

In particular, they must use the same:

- return frequency;

- annualization convention;

- risk-free-rate convention;

- gross or net return convention;

- evaluation sample.

For example, if daily returns are used,

``` math
\begin{equation}
\widehat{SR}^{\mathrm{ann}}
=
\sqrt{252}
\frac{
\bar{R}
}{
\widehat{\sigma}(R)
}.
\end{equation}
```

The same annualization must be applied to the Sharpe ratios of all alternative strategy trials.

##### What Constitutes a Strategy Trial?

A trial is not restricted to a completely different investment strategy.

Any research decision that was influenced by observed historical performance may constitute an additional trial.

Examples include testing alternative:

- characteristics or signals;

- lookback windows;

- signal lags;

- winsorization thresholds;

- neutralization specifications;

- signal-combination weights;

- portfolio mapping functions;

- numbers of selected securities;

- rebalance frequencies;

- investment universes;

- volatility targets;

- optimization parameters;

- model specifications;

- machine-learning hyperparameters.

Consequently, if the final specification was selected from a collection of backtests

``` math
\begin{equation}
\mathcal{S}
=
\left\{
S_1,\ldots,S_N
\right\},
\end{equation}
```

the complete set of economically relevant trials should ideally be retained.

This is an important implementation requirement.

A research framework should therefore store, for every trial,

``` math
\begin{equation}
\boxed{
\left(
\text{Configuration},
\text{Return Series},
\widehat{SR},
\text{Experiment ID}
\right).
}
\end{equation}
```

Retaining only the final successful backtest makes subsequent correction for research selection substantially more difficult.

##### Multiple-Trial Benchmark Sharpe Ratio

The DSR does not generally test the selected Sharpe ratio against zero.

Instead, it compares the observed Sharpe ratio with a benchmark

``` math
\begin{equation}
\boxed{
SR_0
}
\end{equation}
```

representing the Sharpe ratio that the best-performing strategy could reasonably achieve purely because multiple alternatives were tested.

Let

``` math
\begin{equation}
\widehat{SR}_1,
\ldots,
\widehat{SR}_N
\end{equation}
```

denote the Sharpe ratios of the candidate strategies.

Their sample variance is

``` math
\begin{equation}
\boxed{
\widehat{V}[SR]
=
\frac{1}{N-1}
\sum_{m=1}^{N}
\left(
\widehat{SR}_m
-
\overline{SR}
\right)^2,
}
\end{equation}
```

where

``` math
\begin{equation}
\overline{SR}
=
\frac{1}{N}
\sum_{m=1}^{N}
\widehat{SR}_m.
\end{equation}
```

Let

``` math
\begin{equation}
\sigma_{SR,\mathrm{trials}}
=
\sqrt{
\widehat{V}[SR]
}.
\end{equation}
```

For $`N`$ approximately independent trials, the expected maximum Sharpe ratio can be approximated by

``` math
\begin{equation}
\boxed{
SR_0
\approx
\sigma_{SR,\mathrm{trials}}
\left[
(1-\gamma)
\Phi^{-1}
\left(
1-\frac{1}{N}
\right)
+
\gamma
\Phi^{-1}
\left(
1-\frac{1}{Ne}
\right)
\right],
}
\end{equation}
```

where

``` math
\begin{equation}
\gamma
\approx
0.57721566
\end{equation}
```

is the Euler–Mascheroni constant,

``` math
\begin{equation}
e
\approx
2.71828,
\end{equation}
```

and $`\Phi^{-1}(\cdot)`$ denotes the inverse standard-normal cumulative distribution function.

Hence,

``` math
\begin{equation}
\boxed{
SR_0
=
\text{approximate Sharpe ratio expected from the best trial under repeated
search}.
}
\end{equation}
```

As either the number of trials or the dispersion of their Sharpe ratios increases, the benchmark $`SR_0`$ increases.

##### Why the Raw Number of Trials May Be Misleading

The previous expression assumes approximately independent strategy trials.

This assumption is often unrealistic.

For example, strategies using momentum lookbacks of

``` math
\begin{equation}
240,\;241,\;242,\;\ldots,\;260
\end{equation}
```

days will generally produce highly correlated return series.

Treating these $`21`$ specifications as $`21`$ independent experiments exaggerates the amount of independent information contained in the search.

Conversely, simply treating them as one trial ignores the fact that the researcher still selected among several alternatives.

It is therefore useful to distinguish

``` math
\begin{equation}
N
=
\text{number of recorded strategy trials}
\end{equation}
```

from

``` math
\begin{equation}
\boxed{
N_{\mathrm{eff}}
=
\text{effective number of approximately independent trials}.
}
\end{equation}
```

In practice,

``` math
\begin{equation}
1
\leq
N_{\mathrm{eff}}
\leq
N.
\end{equation}
```

##### Estimating the Dependence Between Strategy Trials

Suppose the research process stores the return series of all $`N`$ candidate strategies over a common sample of $`T`$ observations.

Construct the matrix

``` math
\begin{equation}
\mathbf{R}
=
\begin{bmatrix}
R_{1,1} & R_{2,1} & \cdots & R_{N,1}
\\
R_{1,2} & R_{2,2} & \cdots & R_{N,2}
\\
\vdots & \vdots & \ddots & \vdots
\\
R_{1,T} & R_{2,T} & \cdots & R_{N,T}
\end{bmatrix}
\in
\mathbb{R}^{T\times N},
\end{equation}
```

where column $`m`$ contains the return series of strategy trial $`m`$.

Estimate the trial correlation matrix

``` math
\begin{equation}
\boxed{
\widehat{\mathbf{C}}
=
\operatorname{Corr}
\left(
\mathbf{R}
\right)
\in
\mathbb{R}^{N\times N}.
}
\end{equation}
```

The element

``` math
\begin{equation}
\widehat{C}_{ij}
\end{equation}
```

measures the historical return correlation between strategy trials $`i`$ and $`j`$.

Highly correlated trials contain less independent information than unrelated trials.

##### Effective Number of Trials from the Correlation Spectrum

There is no unique universally correct estimator of the effective number of independent strategy trials.

For implementation, a transparent diagnostic can be constructed from the eigenvalues of the strategy-return correlation matrix.

Let

``` math
\begin{equation}
\lambda_1,\ldots,\lambda_N
\end{equation}
```

denote the eigenvalues of

``` math
\begin{equation}
\widehat{\mathbf{C}}.
\end{equation}
```

Because $`\widehat{\mathbf{C}}`$ is a correlation matrix,

``` math
\begin{equation}
\sum_{j=1}^{N}\lambda_j
=
N.
\end{equation}
```

If all strategy trials are independent,

``` math
\begin{equation}
\lambda_j=1
\qquad
\forall j,
\end{equation}
```

and the effective number of trials should be close to $`N`$.

If all trials are nearly identical, one eigenvalue dominates while the remaining eigenvalues are close to zero, implying an effective number much closer to one.

##### Participation-Ratio Effective Rank

A convenient estimator is the participation ratio

``` math
\begin{equation}
\boxed{
N_{\mathrm{eff}}^{PR}
=
\frac{
\left(
\sum_{j=1}^{N}\lambda_j
\right)^2
}{
\sum_{j=1}^{N}\lambda_j^2
}.
}
\end{equation}
```

Since

``` math
\begin{equation}
\sum_{j=1}^{N}\lambda_j=N,
\end{equation}
```

this becomes

``` math
\begin{equation}
\boxed{
N_{\mathrm{eff}}^{PR}
=
\frac{
N^2
}{
\sum_{j=1}^{N}\lambda_j^2
}.
}
\end{equation}
```

This estimator has useful limiting behavior.

If all strategies are independent,

``` math
\begin{equation}
\lambda_1=\cdots=\lambda_N=1,
\end{equation}
```

and therefore

``` math
\begin{equation}
N_{\mathrm{eff}}^{PR}
=
N.
\end{equation}
```

If all strategies are perfectly correlated,

``` math
\begin{equation}
\lambda_1=N,
\qquad
\lambda_2=\cdots=\lambda_N=0,
\end{equation}
```

and

``` math
\begin{equation}
N_{\mathrm{eff}}^{PR}
=
1.
\end{equation}
```

##### Entropy Effective Rank

An alternative is the entropy effective rank.

Normalize the eigenvalues as

``` math
\begin{equation}
p_j
=
\frac{
\lambda_j
}{
\sum_{k=1}^{N}\lambda_k
}.
\end{equation}
```

Then define

``` math
\begin{equation}
\boxed{
N_{\mathrm{eff}}^{ER}
=
\exp
\left(
-
\sum_{j=1}^{N}
p_j\log p_j
\right).
}
\end{equation}
```

Again,

``` math
\begin{equation}
1
\leq
N_{\mathrm{eff}}^{ER}
\leq
N.
\end{equation}
```

The participation ratio and entropy effective rank are not identical estimators, but both summarize how many independent dimensions are present in the collection of strategy returns.

##### Practical Default for the Backtester

For a programmatic implementation, a practical workflow is:

1.  Store the return series of every strategy trial.

2.  Align all trial returns on a common evaluation sample.

3.  Compute the $`N\times N`$ strategy-return correlation matrix $`\widehat{\mathbf{C}}`$.

4.  Compute its eigenvalues $`\lambda_1,\ldots,\lambda_N`$.

5.  Compute $`N_{\mathrm{eff}}^{PR}`$ and, optionally, $`N_{\mathrm{eff}}^{ER}`$.

6.  Report both the literal number of trials $`N`$ and the estimated effective number $`N_{\mathrm{eff}}`$.

7.  Use the chosen $`N_{\mathrm{eff}}`$ in the multiple-trial benchmark calculation.

Thus, the benchmark becomes

``` math
\begin{equation}
\boxed{
SR_0
\approx
\sigma_{SR,\mathrm{trials}}
\left[
(1-\gamma)
\Phi^{-1}
\left(
1-\frac{1}{N_{\mathrm{eff}}}
\right)
+
\gamma
\Phi^{-1}
\left(
1-\frac{1}{N_{\mathrm{eff}}e}
\right)
\right].
}
\end{equation}
```

Since $`N_{\mathrm{eff}}`$ need not be an integer, the formula can be evaluated directly using its real-valued estimate.

##### Important Interpretation of $`N_{\mathrm{eff}}`$

The effective-rank procedure measures dependence among the *return series* of the recorded strategy trials.

It does not reconstruct experiments that were never logged.

Therefore,

``` math
\begin{equation}
\boxed{
N_{\mathrm{eff}}
\text{ can correct for dependence among recorded trials, but not for
unrecorded research decisions.}
}
\end{equation}
```

This is why systematic experiment tracking is part of statistical validation rather than merely a software-engineering convenience.

##### Standard Error of the Selected Sharpe Ratio

Once $`SR_0`$ has been determined, the uncertainty of the selected Sharpe ratio must be estimated.

Let

``` math
\begin{equation}
\widehat{\gamma}_3
\end{equation}
```

denote the sample skewness of the selected strategy returns and

``` math
\begin{equation}
\widehat{\gamma}_4
\end{equation}
```

their sample kurtosis.

Under a commonly used asymptotic approximation,

``` math
\begin{equation}
\boxed{
\widehat{\sigma}_{SR}
=
\sqrt{
\frac{
1
-
\widehat{\gamma}_3
\widehat{SR}
+
\frac{
\widehat{\gamma}_4-1
}{4}
\widehat{SR}^{2}
}{
T-1
}
}.
}
\end{equation}
```

The presence of skewness and kurtosis means that the uncertainty of the Sharpe ratio is not determined solely by sample size.

##### Computing the Deflated Sharpe Ratio

The standardized statistic is

``` math
\begin{equation}
\boxed{
Z_{DSR}
=
\frac{
\widehat{SR}-SR_0
}{
\widehat{\sigma}_{SR}
}.
}
\end{equation}
```

The Deflated Sharpe Ratio is

``` math
\begin{equation}
\boxed{
DSR
=
\Phi
\left(
Z_{DSR}
\right),
}
\end{equation}
```

where $`\Phi(\cdot)`$ denotes the standard-normal cumulative distribution function.

Equivalently,

``` math
\begin{equation}
\boxed{
DSR
=
\Phi
\left(
\frac{
\widehat{SR}-SR_0
}{
\widehat{\sigma}_{SR}
}
\right).
}
\end{equation}
```

A larger value indicates stronger evidence that the selected strategy’s Sharpe ratio exceeds the level that could reasonably be expected from the research selection process.

##### Implementation Algorithm

The complete computation can therefore be implemented as follows.

Given:

``` math
\begin{equation}
\mathbf{R}
\in
\mathbb{R}^{T\times N},
\end{equation}
```

the matrix of returns from all recorded strategy trials:

1.  Compute the Sharpe ratio of each trial:

    ``` math
    \begin{equation}
        \widehat{SR}_1,\ldots,\widehat{SR}_N.
    \end{equation}
    ```

2.  Identify the selected strategy and its Sharpe ratio

    ``` math
    \begin{equation}
        \widehat{SR}.
    \end{equation}
    ```

3.  Compute the cross-trial Sharpe variance

    ``` math
    \begin{equation}
        \widehat{V}[SR].
    \end{equation}
    ```

4.  Compute the trial-return correlation matrix

    ``` math
    \begin{equation}
        \widehat{\mathbf{C}}
        =
        \operatorname{Corr}(\mathbf{R}).
    \end{equation}
    ```

5.  Compute the eigenvalues of $`\widehat{\mathbf{C}}`$.

6.  Estimate the effective number of trials, for example using

    ``` math
    \begin{equation}
        N_{\mathrm{eff}}
        =
        \frac{
        \left(\sum_j\lambda_j\right)^2
        }{
        \sum_j\lambda_j^2
        }.
    \end{equation}
    ```

7.  Compute the multiple-trial benchmark

    ``` math
    \begin{equation}
        SR_0.
    \end{equation}
    ```

8.  Compute skewness and kurtosis of the selected strategy:

    ``` math
    \begin{equation}
        \widehat{\gamma}_3,
        \qquad
        \widehat{\gamma}_4.
    \end{equation}
    ```

9.  Compute

    ``` math
    \begin{equation}
        \widehat{\sigma}_{SR}.
    \end{equation}
    ```

10. Finally compute

    ``` math
    \begin{equation}
        \boxed{
        DSR
        =
        \Phi
        \left(
        \frac{
        \widehat{SR}-SR_0
        }{
        \widehat{\sigma}_{SR}
        }
        \right).
        }
    \end{equation}
    ```

##### Concrete Example

Suppose the research process contains

``` math
\begin{equation}
N=100
\end{equation}
```

recorded backtests.

Because many specifications are similar, their return series are strongly correlated.

Suppose the correlation-spectrum calculation produces

``` math
\begin{equation}
N_{\mathrm{eff}}=25.
\end{equation}
```

Assume further that the standard deviation of the Sharpe ratios across trials is

``` math
\begin{equation}
\sigma_{SR,\mathrm{trials}}
=
0.40.
\end{equation}
```

The relevant benchmark is then computed using

``` math
\begin{equation}
N_{\mathrm{eff}}=25,
\end{equation}
```

rather than mechanically treating all $`100`$ trials as independent.

Thus,

``` math
\begin{equation}
SR_0
\approx
0.40
\left[
(1-\gamma)
\Phi^{-1}
\left(
1-\frac{1}{25}
\right)
+
\gamma
\Phi^{-1}
\left(
1-\frac{1}{25e}
\right)
\right].
\end{equation}
```

If the selected strategy has

``` math
\begin{equation}
\widehat{SR}=1.50,
\end{equation}
```

the relevant question is therefore not

``` math
\begin{equation}
\boxed{
\text{Is }1.50>0?
}
\end{equation}
```

but rather

``` math
\begin{equation}
\boxed{
\text{Is }1.50\text{ sufficiently above }SR_0
\text{ given the sample size and return distribution?}
}
\end{equation}
```

##### Interpretation and Reporting

The DSR should not be reported alone.

A useful backtest report should include at least

``` math
\begin{equation}
\boxed{
\left(
\widehat{SR},
SR_0,
DSR,
N,
N_{\mathrm{eff}},
T,
\widehat{\gamma}_3,
\widehat{\gamma}_4
\right).
}
\end{equation}
```

This makes the statistical correction auditable.

A large raw Sharpe ratio becomes less convincing when:

- many independent strategy variants were tested;

- Sharpe ratios vary substantially across trials;

- the selected strategy was chosen after extensive optimization;

- the historical sample is short;

- returns exhibit substantial skewness or kurtosis.

Conversely, a strategy whose Sharpe ratio remains convincingly above the multiple-trial benchmark provides stronger evidence that the observed performance is not merely the result of selecting the best outcome from a large research search.

The DSR therefore changes the inferential question from

``` math
\begin{equation}
\boxed{
H_0:
SR=0
}
\end{equation}
```

to the substantially more demanding question

``` math
\begin{equation}
\boxed{
H_0:
SR\leq SR_0,
}
\end{equation}
```

where $`SR_0`$ reflects the advantage created by the research and strategy selection process.

#### Probability of Backtest Overfitting

The Probability of Backtest Overfitting, or PBO, evaluates how frequently a strategy selected as the best performer in-sample performs relatively poorly out of sample.

The central idea is to repeatedly divide the available historical observations into complementary training and test subsets.

##### Candidate Strategies

Suppose there are

``` math
\begin{equation}
M
\end{equation}
```

candidate strategy specifications.

For each partition $`b`$, compute an in-sample performance statistic

``` math
\begin{equation}
S_{m,b}^{IS}
\end{equation}
```

and an out-of-sample statistic

``` math
\begin{equation}
S_{m,b}^{OOS}.
\end{equation}
```

Select the best in-sample strategy:

``` math
\begin{equation}
\boxed{
m_b^*
=
\underset{m}{\arg\max}
\;
S_{m,b}^{IS}.
}
\end{equation}
```

Then evaluate the relative out-of-sample rank of this selected strategy.

##### Out-of-Sample Relative Rank

Let

``` math
\begin{equation}
r_b^{OOS}
\in
(0,1)
\end{equation}
```

denote the percentile rank of strategy $`m_b^*`$ among all candidate strategies in the corresponding out-of-sample subset.

If

``` math
\begin{equation}
r_b^{OOS}
<
\frac{1}{2},
\end{equation}
```

the strategy selected as best in-sample performs below the out-of-sample median.

PBO can therefore be estimated as

``` math
\begin{equation}
\boxed{
PBO
=
P
\left(
r_b^{OOS}
<
\frac{1}{2}
\right).
}
\end{equation}
```

Empirically,

``` math
\begin{equation}
\boxed{
\widehat{PBO}
=
\frac{1}{B}
\sum_{b=1}^{B}
\mathbb{I}
\left(
r_b^{OOS}
<
\frac{1}{2}
\right).
}
\end{equation}
```

##### Logit Representation

A common transformation of the out-of-sample relative rank is

``` math
\begin{equation}
\boxed{
\lambda_b
=
\log
\left(
\frac{
r_b^{OOS}
}{
1-r_b^{OOS}
}
\right).
}
\end{equation}
```

Then

``` math
\begin{equation}
\lambda_b<0
\end{equation}
```

corresponds to an out-of-sample rank below the median.

Thus,

``` math
\begin{equation}
\boxed{
PBO
=
P(\lambda_b<0).
}
\end{equation}
```

##### Interpretation

A high PBO indicates that choosing the historically best specification frequently leads to below-median performance on data not used for selection.

This is direct evidence that the research-selection process may be fitting historical noise.

A low PBO does not prove that the strategy will perform well in live trading, but it provides evidence that the selected strategy is less dependent on in-sample optimization.

##### Statistical Inference Summary

The statistical validation process should progressively answer four questions.

First,

``` math
\begin{equation}
\boxed{
\text{Is average performance statistically distinguishable from zero?}
}
\end{equation}
```

This is addressed through mean-return tests and appropriate standard errors.

Second,

``` math
\begin{equation}
\boxed{
\text{Are the reported standard errors robust to dependence and
heteroskedasticity?}
}
\end{equation}
```

This motivates Newey–West and bootstrap procedures.

Third,

``` math
\begin{equation}
\boxed{
\text{How much strategy selection and repeated testing occurred?}
}
\end{equation}
```

This motivates multiple-testing and data-snooping adjustments.

Finally,

``` math
\begin{equation}
\boxed{
\text{Would the strategy still appear attractive after accounting for the
research process that produced it?}
}
\end{equation}
```

This motivates tools such as the Deflated Sharpe Ratio and the Probability of Backtest Overfitting.

The complete progression can therefore be summarized as

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Observed Performance}
&\rightarrow
\text{Sampling Uncertainty}
\\
&\rightarrow
\text{Dependence-Adjusted Inference}
\\
&\rightarrow
\text{Multiple-Testing Adjustment}
\\
&\rightarrow
\text{Backtest-Selection Adjustment}
\\
&\rightarrow
\text{Statistically Credible Evidence}.
\end{aligned}
}
\end{equation}
```

Statistical significance should nevertheless remain only one component of the research decision.

A credible investment strategy should simultaneously exhibit economically meaningful performance, robustness across reasonable specifications, realistic implementation assumptions, and statistical evidence that is not explained primarily by repeated historical experimentation.

