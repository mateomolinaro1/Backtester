### Signal Diagnostics

Before converting the final investable signal into portfolio weights, it is useful to introduce a short diagnostic step.

At this stage of the backtesting pipeline, we have constructed

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{final}}
=
\begin{bmatrix}
s_{1,t}^{\mathrm{final}}
\\
\vdots
\\
s_{N_t,t}^{\mathrm{final}}
\end{bmatrix}
\in
\mathbb{R}^{N_t},
}
\end{equation}
```

but we have not yet determined how much capital should be allocated to each security.

The reader should therefore view this section as a temporary diagnostic layer between signal construction and portfolio construction:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Signal Construction}
&\rightarrow
\mathbf{s}_t^{\mathrm{final}}
\\
&\rightarrow
\underbrace{
\text{Signal Diagnostics}
}_{\text{current section}}
\\
&\rightarrow
\text{Portfolio Construction}
\rightarrow
\mathbf{w}_t.
\end{aligned}
}
\end{equation}
```

The purpose is to answer a simple question before introducing position sizing, risk models, leverage, constraints, and transaction costs:

``` math
\begin{equation}
\boxed{
\text{Does the signal itself contain useful information about future returns?}
}
\end{equation}
```

This distinction is important because portfolio performance depends jointly on

``` math
\begin{equation}
\boxed{
\text{Signal Quality}
+
\text{Portfolio Construction}
+
\text{Implementation}.
}
\end{equation}
```

A weak signal may occasionally produce an attractive backtest because of unintended factor exposures or a favorable portfolio-construction choice. Conversely, a genuinely predictive signal may produce disappointing portfolio performance if it is mapped inefficiently into positions or generates excessive turnover.

Signal diagnostics therefore attempt to study the statistical and economic properties of the signal before these additional layers are introduced.

#### Cross-Sectional Signal Distribution

The first diagnostic is simply to examine the cross-sectional distribution of the final signal.

At each decision date $`t`$, define the cross-sectional mean

``` math
\begin{equation}
\boxed{
\bar{s}_t
=
\frac{1}{N_t}
\sum_{i=1}^{N_t}
s_{i,t}^{\mathrm{final}}.
}
\end{equation}
```

The cross-sectional standard deviation is

``` math
\begin{equation}
\boxed{
\sigma_{s,t}
=
\sqrt{
\frac{1}{N_t}
\sum_{i=1}^{N_t}
\left(
s_{i,t}^{\mathrm{final}}
-
\bar{s}_t
\right)^2
}.
}
\end{equation}
```

Other useful diagnostics include:

- minimum and maximum;

- median;

- selected quantiles;

- skewness;

- kurtosis;

- fraction of positive and negative observations;

- fraction of missing observations.

These statistics help detect abnormal changes in the signal-generation pipeline.

For example, a sudden collapse in

``` math
\begin{equation}
\sigma_{s,t}
\end{equation}
```

may indicate that the signal has lost cross-sectional discriminatory power or that an upstream data-processing step has malfunctioned.

Conversely, an unusually large dispersion may indicate extreme observations, a change in data coverage, or instability in a predictive model.

##### Cross-Sectional Dispersion Through Time

The time series

``` math
\begin{equation}
\left\{
\sigma_{s,t}
\right\}_{t=1}^{T}
\end{equation}
```

is itself an important diagnostic.

If the final signal has been standardized at every date, one may expect

``` math
\begin{equation}
\sigma_{s,t}
\approx 1.
\end{equation}
```

If it has not been standardized, changes in signal dispersion may contain economic information but may also mechanically change downstream portfolio exposure when the signal-to-weight mapping depends on signal magnitude.

#### Information Coefficient

One of the most common measures of cross-sectional predictive power is the Information Coefficient, or IC.

Let

``` math
\begin{equation}
R_{i,t\rightarrow t+h}
\end{equation}
```

denote the realized return of security $`i`$ over the future horizon $`[t,t+h]`$.

At decision date $`t`$, the Information Coefficient is defined as the cross-sectional correlation between the signal and subsequent returns:

``` math
\begin{equation}
\boxed{
IC_t
=
\operatorname{Corr}_i
\left(
s_{i,t}^{\mathrm{final}},
R_{i,t\rightarrow t+h}
\right).
}
\end{equation}
```

Using the Pearson correlation coefficient,

``` math
\begin{equation}
IC_t
=
\frac{
\sum_{i=1}^{N_t}
\left(
s_{i,t}^{\mathrm{final}}
-
\bar{s}_t
\right)
\left(
R_{i,t\rightarrow t+h}
-
\bar{R}_{t\rightarrow t+h}
\right)
}{
\sqrt{
\sum_{i=1}^{N_t}
\left(
s_{i,t}^{\mathrm{final}}
-
\bar{s}_t
\right)^2
}
\sqrt{
\sum_{i=1}^{N_t}
\left(
R_{i,t\rightarrow t+h}
-
\bar{R}_{t\rightarrow t+h}
\right)^2
}
}.
\end{equation}
```

A positive IC means that securities with higher signals tended, on average, to subsequently outperform securities with lower signals.

A negative IC indicates the opposite relationship.

##### Average Information Coefficient

Across $`T`$ decision dates,

``` math
\begin{equation}
\boxed{
\overline{IC}
=
\frac{1}{T}
\sum_{t=1}^{T}
IC_t.
}
\end{equation}
```

A positive average IC indicates persistent positive cross-sectional predictive power.

However, the magnitude of $`\overline{IC}`$ should not be interpreted in isolation. Its stability through time is equally important.

##### Prediction Horizon

The IC depends explicitly on the future-return horizon $`h`$:

``` math
\begin{equation}
IC_t^{(h)}
=
\operatorname{Corr}_i
\left(
s_{i,t}^{\mathrm{final}},
R_{i,t\rightarrow t+h}
\right).
\end{equation}
```

Computing ICs for several horizons,

``` math
\begin{equation}
h
\in
\{1,5,20,60,\ldots\},
\end{equation}
```

can therefore help characterize the decay of the signal’s predictive content.

A short-lived signal may have

``` math
\begin{equation}
IC^{(1)}>0
\end{equation}
```

but

``` math
\begin{equation}
IC^{(60)}
\approx 0.
\end{equation}
```

This information will later be relevant when choosing the portfolio rebalancing frequency.

#### Rank Information Coefficient

The Rank Information Coefficient replaces the raw values of the signal and future returns with their cross-sectional ranks.

It is therefore the cross-sectional Spearman correlation:

``` math
\begin{equation}
\boxed{
RIC_t
=
\operatorname{Corr}_i^{\mathrm{Spearman}}
\left(
s_{i,t}^{\mathrm{final}},
R_{i,t\rightarrow t+h}
\right).
}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
RIC_t
=
\operatorname{Corr}_i
\left(
\operatorname{Rank}_i
\left(
s_{i,t}^{\mathrm{final}}
\right),
\operatorname{Rank}_i
\left(
R_{i,t\rightarrow t+h}
\right)
\right).
\end{equation}
```

##### Interpretation

The Pearson IC measures linear association between signal magnitude and future returns.

The Rank IC instead measures whether higher-ranked securities tend to have higher-ranked subsequent returns.

Therefore,

``` math
\begin{equation}
\boxed{
\text{IC}
\rightarrow
\text{Linear Predictive Relationship},
}
\end{equation}
```

whereas

``` math
\begin{equation}
\boxed{
\text{Rank IC}
\rightarrow
\text{Monotonic Predictive Relationship}.
}
\end{equation}
```

Rank IC is particularly useful when the signal is ordinal, such as a percentile score, rank transformation, or nonlinear model output whose absolute magnitude has no direct economic interpretation.

It is also less sensitive than Pearson correlation to extreme realized returns.

#### Information Coefficient Information Ratio

The average IC measures the average strength of the relationship, but does not capture its stability.

Define the time-series standard deviation of the IC as

``` math
\begin{equation}
\sigma_{IC}
=
\sqrt{
\frac{1}{T-1}
\sum_{t=1}^{T}
\left(
IC_t-\overline{IC}
\right)^2
}.
\end{equation}
```

The Information Coefficient Information Ratio is

``` math
\begin{equation}
\boxed{
ICIR
=
\frac{
\overline{IC}
}{
\sigma_{IC}
}.
}
\end{equation}
```

If the IC is measured at a frequency with $`F`$ observations per year, an annualized version may be reported as

``` math
\begin{equation}
\boxed{
ICIR_{\mathrm{ann}}
=
\sqrt{F}
\frac{
\overline{IC}
}{
\sigma_{IC}
}.
}
\end{equation}
```

The same construction can be applied to Rank IC:

``` math
\begin{equation}
\boxed{
RICIR
=
\frac{
\overline{RIC}
}{
\sigma_{RIC}
}.
}
\end{equation}
```

A signal with a moderate but stable IC may be economically more useful than a signal with a larger average IC driven by a small number of exceptional periods.

##### Serial Dependence

The usual annualization

``` math
\begin{equation}
\sqrt{F}
\end{equation}
```

implicitly treats successive IC observations as sufficiently independent.

This assumption may be inappropriate when future-return horizons overlap or when the signal is highly persistent.

For example, if a daily IC is computed against future 20-day returns, adjacent IC observations use strongly overlapping return windows.

Consequently, annualized ICIR values should be interpreted carefully in the presence of serial dependence.

#### Quantile and Decile Returns

Correlation-based diagnostics summarize the entire cross-section with a single number.

A complementary approach is to divide securities into groups according to their signal values and examine their subsequent returns.

Suppose the cross-section is divided into $`Q`$ quantiles.

Define

``` math
\begin{equation}
\mathcal{Q}_{q,t}
\subseteq
\mathcal{U}_t,
\qquad
q=1,\ldots,Q,
\end{equation}
```

where $`\mathcal{Q}_{1,t}`$ contains the lowest-signal securities and $`\mathcal{Q}_{Q,t}`$ contains the highest-signal securities.

For deciles,

``` math
\begin{equation}
Q=10.
\end{equation}
```

The future equal-weighted return of quantile $`q`$ is

``` math
\begin{equation}
\boxed{
R_{q,t\rightarrow t+h}
=
\frac{1}{
|\mathcal{Q}_{q,t}|
}
\sum_{i\in\mathcal{Q}_{q,t}}
R_{i,t\rightarrow t+h}.
}
\end{equation}
```

More generally, securities within each quantile may be weighted according to a specified weighting rule.

##### Average Quantile Returns

Over the backtest,

``` math
\begin{equation}
\boxed{
\overline{R}_q
=
\frac{1}{T}
\sum_{t=1}^{T}
R_{q,t\rightarrow t+h}.
}
\end{equation}
```

The sequence

``` math
\begin{equation}
\overline{R}_1,
\overline{R}_2,
\ldots,
\overline{R}_Q
\end{equation}
```

provides a direct visualization of how future returns vary with the signal.

#### Long–Short Spread

The extreme quantiles can be used to construct a simple diagnostic long–short spread.

For $`Q`$ signal portfolios,

``` math
\begin{equation}
\boxed{
R_{t}^{LS}
=
R_{Q,t}
-
R_{1,t}.
}
\end{equation}
```

For deciles,

``` math
\begin{equation}
R_t^{D10-D1}
=
R_{10,t}
-
R_{1,t}.
\end{equation}
```

The average spread is

``` math
\begin{equation}
\boxed{
\overline{R}^{LS}
=
\frac{1}{T}
\sum_{t=1}^{T}
R_t^{LS}.
}
\end{equation}
```

This provides an intuitive measure of the economic separation between high-signal and low-signal securities.

##### Diagnostic Portfolio vs. Final Portfolio

The long–short spread constructed here should not be confused with the final investment portfolio.

It is deliberately simple and is primarily intended to diagnose the signal.

It may ignore:

- optimal position sizing;

- covariance information;

- leverage targets;

- portfolio-level factor constraints;

- liquidity constraints;

- turnover optimization;

- transaction costs.

These elements will be introduced in the portfolio-construction and implementation sections.

#### Monotonicity

A useful signal should often produce an economically coherent relationship between signal strength and subsequent returns.

For a positively oriented signal, one may expect

``` math
\begin{equation}
\boxed{
\overline{R}_1
\leq
\overline{R}_2
\leq
\cdots
\leq
\overline{R}_Q.
}
\end{equation}
```

This property is referred to as monotonicity.

##### Why Monotonicity Matters

Suppose the top decile strongly outperforms the bottom decile, but the intermediate deciles exhibit no systematic ordering.

The signal may still be economically useful, but its predictive relationship may be concentrated only in the tails.

Conversely, a smooth increase in returns across quantiles provides stronger evidence that the signal captures a broad cross-sectional relationship.

##### Simple Monotonicity Measures

One possible diagnostic is the correlation between quantile number and average quantile return:

``` math
\begin{equation}
\boxed{
M
=
\operatorname{Corr}
\left(
\begin{bmatrix}
1\\
2\\
\vdots\\
Q
\end{bmatrix},
\begin{bmatrix}
\overline{R}_1\\
\overline{R}_2\\
\vdots\\
\overline{R}_Q
\end{bmatrix}
\right).
}
\end{equation}
```

A value close to one indicates a strongly increasing relationship.

A rank-based version may also be used when only the ordering of quantile returns is of interest.

#### Hit Rate

The hit rate measures how frequently the signal produces the expected directional relationship.

##### IC Hit Rate

A simple definition is the fraction of periods with positive IC:

``` math
\begin{equation}
\boxed{
HR_{IC}
=
\frac{1}{T}
\sum_{t=1}^{T}
\mathbb{I}
\left(
IC_t>0
\right),
}
\end{equation}
```

where $`\mathbb{I}(\cdot)`$ denotes the indicator function.

Similarly,

``` math
\begin{equation}
HR_{RIC}
=
\frac{1}{T}
\sum_{t=1}^{T}
\mathbb{I}
\left(
RIC_t>0
\right).
\end{equation}
```

##### Long–Short Hit Rate

For the diagnostic long–short spread,

``` math
\begin{equation}
\boxed{
HR_{LS}
=
\frac{1}{T}
\sum_{t=1}^{T}
\mathbb{I}
\left(
R_t^{LS}>0
\right).
}
\end{equation}
```

A high hit rate indicates that the signal works frequently, whereas a lower hit rate combined with strong average performance may indicate that returns are generated by relatively infrequent but large successful periods.

Hit rate should therefore always be interpreted jointly with the magnitude and distribution of returns.

#### Signal Persistence and Autocorrelation

Signal persistence measures how rapidly the cross-sectional investment view changes through time.

A natural measure is the cross-sectional correlation between signals at different dates.

For lag $`\ell`$,

``` math
\begin{equation}
\boxed{
\rho_s(\ell)
=
\operatorname{Corr}_{i,t}
\left(
s_{i,t}^{\mathrm{final}},
s_{i,t-\ell}^{\mathrm{final}}
\right).
}
\end{equation}
```

More commonly, the correlation is first computed cross-sectionally at each date:

``` math
\begin{equation}
\rho_{s,t}^{(\ell)}
=
\operatorname{Corr}_i
\left(
s_{i,t}^{\mathrm{final}},
s_{i,t-\ell}^{\mathrm{final}}
\right),
\end{equation}
```

and then averaged through time:

``` math
\begin{equation}
\boxed{
\overline{\rho}_s^{(\ell)}
=
\frac{1}{T_\ell}
\sum_t
\rho_{s,t}^{(\ell)}.
}
\end{equation}
```

A rank-based persistence measure can similarly be defined using Spearman correlations.

##### Interpretation

A highly persistent signal satisfies approximately

``` math
\begin{equation}
\rho_s(1)
\approx 1.
\end{equation}
```

Such a signal changes slowly and will generally require less portfolio rebalancing.

A rapidly changing signal may have

``` math
\begin{equation}
\rho_s(1)
\approx 0,
\end{equation}
```

which may imply substantially greater turnover.

##### Persistence Curve

Evaluating

``` math
\begin{equation}
\overline{\rho}_s^{(1)},
\overline{\rho}_s^{(2)},
\ldots,
\overline{\rho}_s^{(L)}
\end{equation}
```

provides a persistence curve.

This helps characterize the effective memory of the signal and can inform the choice of rebalance frequency and smoothing parameters.

#### Signal Turnover

Signal turnover measures how much the signal changes between consecutive decision dates.

It should not be confused with portfolio turnover, which is defined from actual changes in portfolio weights.

A simple measure is

``` math
\begin{equation}
\boxed{
TO_t^{s}
=
\frac{1}{N_t}
\sum_{i=1}^{N_t}
\left|
s_{i,t}^{\mathrm{final}}
-
s_{i,t-1}^{\mathrm{final}}
\right|.
}
\end{equation}
```

If signal scales vary through time, this measure should be interpreted carefully.

For rank-based signals, one may instead examine rank changes:

``` math
\begin{equation}
\boxed{
TO_t^{\mathrm{rank}}
=
\frac{1}{N_t}
\sum_{i=1}^{N_t}
\left|
\operatorname{Rank}_{i,t}
-
\operatorname{Rank}_{i,t-1}
\right|.
}
\end{equation}
```

##### Signal Turnover vs. Portfolio Turnover

In general,

``` math
\begin{equation}
\boxed{
TO_t^{s}
\neq
TO_t^{p}.
}
\end{equation}
```

Portfolio turnover depends on the signal-to-weight mapping, constraints, portfolio drift, and previous holdings.

Nevertheless, high signal turnover is an early warning that implementation costs may become important.

#### Factor Exposure Diagnostics

If the signal has been neutralized against a set of systematic exposures, these exposures should be verified after the complete final-signal construction pipeline.

Let

``` math
\begin{equation}
\mathbf{B}_t
\in
\mathbb{R}^{N_t\times K}
\end{equation}
```

denote the relevant exposure matrix.

Under OLS neutralization, one may examine

``` math
\begin{equation}
\boxed{
\mathbf{e}_t^{s}
=
\mathbf{B}_t^\top
\mathbf{s}_t^{\mathrm{final}}
\in
\mathbb{R}^{K}.
}
\end{equation}
```

If the final signal is intended to remain neutral,

``` math
\begin{equation}
\mathbf{e}_t^{s}
\approx
\mathbf{0}.
\end{equation}
```

Under WLS neutralization with weighting matrix

``` math
\begin{equation}
\mathbf{W}_t
\in
\mathbb{R}^{N_t\times N_t},
\end{equation}
```

the relevant condition becomes

``` math
\begin{equation}
\boxed{
\mathbf{B}_t^\top
\mathbf{W}_t
\mathbf{s}_t^{\mathrm{final}}
\approx
\mathbf{0}.
}
\end{equation}
```

##### Why Recheck Exposures?

Neutrality may have been imposed earlier on

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{neutral}},
\end{equation}
```

but subsequent nonlinear transformations can reintroduce systematic exposures.

For example,

``` math
\begin{equation}
s_{i,t}^{\mathrm{final}}
=
g
\left(
s_{i,t}^{\mathrm{neutral}}
\right)
\end{equation}
```

does not generally preserve

``` math
\begin{equation}
\mathbf{B}_t^\top
\mathbf{s}_t^{\mathrm{neutral}}
=
0.
\end{equation}
```

Factor exposures should therefore be monitored on the actual signal passed to the portfolio-construction engine.

#### Cross-Sectional and Temporal Stability

A final diagnostic concerns whether signal properties remain stable across different parts of the investment universe and through different periods.

##### Cross-Sectional Stability

Signal performance may be evaluated separately across groups such as:

- large-, mid-, and small-cap securities;

- liquidity buckets;

- industries and sectors;

- countries and regions;

- high- and low-volatility securities.

For subgroup $`g`$, one may compute

``` math
\begin{equation}
IC_{g,t},
\end{equation}
```

and compare

``` math
\begin{equation}
\overline{IC}_g
\end{equation}
```

across groups.

A signal whose apparent predictive power is entirely concentrated in a small, illiquid subset of the universe may be difficult to implement even if its aggregate IC is attractive.

##### Temporal Stability

The same diagnostics should be examined through time.

For example, define a rolling average IC over a window of length $`L`$:

``` math
\begin{equation}
\boxed{
\overline{IC}_{t}^{(L)}
=
\frac{1}{L}
\sum_{\ell=0}^{L-1}
IC_{t-\ell}.
}
\end{equation}
```

Similarly, one may examine rolling:

- Rank IC;

- ICIR;

- long–short returns;

- hit rates;

- signal dispersion;

- persistence;

- factor exposures.

This can reveal regime dependence or structural deterioration that is hidden by full-sample averages.

##### Subperiod Analysis

The sample may also be divided into economically meaningful subperiods:

``` math
\begin{equation}
\mathcal{T}
=
\mathcal{T}_1
\cup
\mathcal{T}_2
\cup
\cdots
\cup
\mathcal{T}_J.
\end{equation}
```

Diagnostics can then be computed independently within each subperiod.

The objective is not to require identical performance in every regime, but to understand whether the signal’s historical performance is broad and persistent or concentrated in a particular environment.

##### Final Diagnostic Summary

At the end of the signal-diagnostic stage, the backtester should have answered four distinct questions:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Predictiveness:}
&\quad
\text{Does the signal predict future cross-sectional returns?}
\\
\text{Economic Shape:}
&\quad
\text{Are returns monotonic across signal levels?}
\\
\text{Persistence:}
&\quad
\text{Is the signal sufficiently stable through time?}
\\
\text{Robustness:}
&\quad
\text{Does the relationship survive across periods and subuniverses?}
\end{aligned}
}
\end{equation}
```

These diagnostics characterize the signal itself, but they do not determine whether the resulting investment strategy is attractive after portfolio construction and implementation.

We now return to the main backtesting pipeline:

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{final}}
\quad
\longrightarrow
\quad
\text{Portfolio Construction}
\quad
\longrightarrow
\quad
\mathbf{w}_t^{\mathrm{target}}.
}
\end{equation}
```

The next step determines how the information contained in the signal should be translated into actual capital allocations.

# Portfolio Construction

