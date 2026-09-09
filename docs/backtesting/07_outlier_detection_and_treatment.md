### Outlier Detection and Treatment

After structural data cleaning, the remaining dataset may still contain observations whose magnitude is unusually large relative to the rest of the sample.

Such observations are commonly referred to as *outliers*.

However, an outlier is not necessarily an erroneous observation. In financial data, extreme observations may reflect genuine economic events such as:

- earnings surprises;

- bankruptcies;

- acquisitions;

- market crashes;

- liquidity shocks;

- large analyst revisions;

- extreme valuation changes.

Consequently,

``` math
\begin{equation}
\boxed{
\text{Extreme Observation}
\not\Rightarrow
\text{Invalid Observation}.
}
\end{equation}
```

The purpose of outlier treatment is therefore generally not to remove all extreme observations, but rather to prevent a small number of observations from exerting disproportionate influence on statistical estimates, signals, or portfolio weights.

Let

``` math
\begin{equation}
X_{i,t}
\end{equation}
```

denote a cleaned variable for security $`i`$ at time $`t`$.

An outlier-treatment operator can be represented as

``` math
\begin{equation}
\boxed{
\widetilde{X}_{i,t}
=
\mathcal{O}
\left(
X_{i,t};
\theta_t
\right),
}
\end{equation}
```

where $`\theta_t`$ contains the parameters required by the chosen treatment, such as quantile thresholds, medians, or robust scale estimates.

The parameters themselves must respect the information constraint.

For a cross-sectional transformation at time $`t`$,

``` math
\begin{equation}
\theta_t
=
g
\left(
\left\{
X_{j,t}
:
j\in\mathcal{U}_t
\right\}
\right),
\end{equation}
```

while for a time-series transformation,

``` math
\begin{equation}
\theta_{i,t}
=
g
\left(
X_{i,t-1},
X_{i,t-2},
\ldots
\right).
\end{equation}
```

Future observations must never enter the estimation of the treatment parameters.

#### Definition of an Outlier

There is no universal definition of an outlier.

An observation is generally considered an outlier if it is unusually distant from a reference distribution or inconsistent with the typical behavior of the variable under consideration.

Let

``` math
\begin{equation}
\mathcal{X}
=
\left\{
X_1,\ldots,X_N
\right\}
\end{equation}
```

denote a sample.

An outlier-detection rule can be written abstractly as

``` math
\begin{equation}
O_i
=
\begin{cases}
1,
&
X_i
\text{ is classified as an outlier},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

More generally,

``` math
\begin{equation}
\boxed{
O_i
=
\mathbb{I}
\left(
D(X_i;\mathcal{X})
>
c
\right),
}
\end{equation}
```

where:

- $`D(\cdot)`$ is a measure of distance from the reference distribution;

- $`c`$ is a predefined threshold.

##### Univariate vs. Multivariate Outliers

An observation may be extreme with respect to a single variable:

``` math
\begin{equation}
|X_i|
\gg
|X_j|,
\end{equation}
```

or extreme only through a combination of variables.

Suppose

``` math
\begin{equation}
X_i
\in
\mathbb{R}^{K}.
\end{equation}
```

A multivariate observation may appear normal along each dimension separately while being unusual jointly.

A classical multivariate distance is the Mahalanobis distance:

``` math
\begin{equation}
\boxed{
D_i^2
=
(X_i-\mu)^\top
\Sigma^{-1}
(X_i-\mu),
}
\end{equation}
```

where $`\mu`$ and $`\Sigma`$ denote the location vector and covariance matrix.

However, both $`\mu`$ and $`\Sigma`$ can themselves be highly sensitive to outliers. Robust location and covariance estimators may therefore be preferable when multivariate outlier detection is required.

##### Distribution Dependence

Whether an observation should be considered unusual depends on the underlying distribution.

For example,

``` math
\begin{equation}
|Z_i|>3
\end{equation}
```

may be rare under a Gaussian distribution, but financial variables often exhibit:

- heavy tails;

- skewness;

- multimodality;

- heteroskedasticity.

Therefore, fixed Gaussian thresholds should not automatically be interpreted as universal definitions of financial outliers.

#### Cross-Sectional vs. Time-Series Outliers

Outlier detection in quantitative equity research generally occurs along one of two dimensions:

``` math
\begin{equation}
\boxed{
\text{Cross-Sectional}
\qquad\text{or}\qquad
\text{Time-Series}.
}
\end{equation}
```

The distinction is fundamental because the corresponding reference distributions are different.

##### Cross-Sectional Outliers

At a fixed date $`t`$, define the cross-section

``` math
\begin{equation}
\mathcal{X}_t
=
\left\{
X_{i,t}
:
i\in\mathcal{U}_t
\right\}.
\end{equation}
```

A cross-sectional outlier is unusual relative to other securities observed at the same date.

For example, a valuation ratio may satisfy

``` math
\begin{equation}
X_{i,t}
\gg
\operatorname{Median}_{j\in\mathcal{U}_t}
X_{j,t}.
\end{equation}
```

Cross-sectional treatment is particularly relevant for variables used to rank securities against one another, such as:

- valuation ratios;

- profitability measures;

- analyst revisions;

- earnings surprises;

- momentum signals;

- quality metrics.

The treatment parameters should normally be estimated separately at each date:

``` math
\begin{equation}
\boxed{
\theta_t^{CS}
=
g
\left(
\mathcal{X}_t
\right).
}
\end{equation}
```

##### Time-Series Outliers

For a fixed security $`i`$, define the historical series

``` math
\begin{equation}
\mathcal{X}_{i,t}^{TS}
=
\left\{
X_{i,t-L},
\ldots,
X_{i,t}
\right\}.
\end{equation}
```

A time-series outlier is unusual relative to the historical behavior of the same security or variable.

A generic rule may compare

``` math
\begin{equation}
X_{i,t}
\end{equation}
```

with a historical location estimate

``` math
\begin{equation}
\widehat{\mu}_{i,t}
\end{equation}
```

and scale estimate

``` math
\begin{equation}
\widehat{\sigma}_{i,t}.
\end{equation}
```

For example,

``` math
\begin{equation}
\left|
\frac{
X_{i,t}-\widehat{\mu}_{i,t}
}{
\widehat{\sigma}_{i,t}
}
\right|
>
c
\end{equation}
```

may identify an unusually large deviation.

##### Different Economic Meaning

Consider an earnings-growth rate of $`50\%`$.

It may be completely normal for company $`i`$ relative to its own history but extreme relative to the current cross-section.

Alternatively, it may be ordinary relative to other firms but highly unusual for company $`i`$ itself.

Thus,

``` math
\begin{equation}
\boxed{
\text{Cross-Sectional Extremeness}
\neq
\text{Time-Series Extremeness}.
}
\end{equation}
```

The appropriate dimension should therefore be chosen according to the investment hypothesis.

##### Panel Data

For panel data, both treatments can in principle be applied:

``` math
\begin{equation}
X_{i,t}
\rightarrow
\widetilde{X}_{i,t}^{TS}
\rightarrow
\widetilde{X}_{i,t}^{CS}.
\end{equation}
```

However, the ordering matters.

A time-series treatment modifies the historical behavior of each security, whereas a cross-sectional treatment modifies relative dispersion across securities.

The sequence should therefore be economically motivated and explicitly documented.

#### Quantile-Based Winsorization

Quantile-based winsorization is one of the most common outlier treatments in cross-sectional financial research.

At time $`t`$, let

``` math
\begin{equation}
Q_{\alpha,t}
\end{equation}
```

and

``` math
\begin{equation}
Q_{1-\alpha,t}
\end{equation}
```

denote the lower and upper empirical quantiles of the cross-sectional distribution.

For example, with

``` math
\begin{equation}
\alpha=0.01,
\end{equation}
```

the thresholds correspond to the $`1`$st and $`99`$th percentiles.

##### Winsorization Operator

The winsorized observation is

``` math
\begin{equation}
\boxed{
\widetilde{X}_{i,t}
=
\min
\left[
\max
\left(
X_{i,t},
Q_{\alpha,t}
\right),
Q_{1-\alpha,t}
\right].
}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
\widetilde{X}_{i,t}
=
\begin{cases}
Q_{\alpha,t},
&
X_{i,t}
<
Q_{\alpha,t},
\\[0.15cm]
X_{i,t},
&
Q_{\alpha,t}
\leq
X_{i,t}
\leq
Q_{1-\alpha,t},
\\[0.15cm]
Q_{1-\alpha,t},
&
X_{i,t}
>
Q_{1-\alpha,t}.
\end{cases}
\end{equation}
```

The observation remains in the dataset, but its magnitude is capped.

##### Example

Suppose the cross-sectional thresholds are

``` math
\begin{equation}
Q_{0.01,t}
=
-3
\end{equation}
```

and

``` math
\begin{equation}
Q_{0.99,t}
=
4.
\end{equation}
```

Then

``` math
\begin{equation}
X_{i,t}=10
\end{equation}
```

becomes

``` math
\begin{equation}
\widetilde{X}_{i,t}=4,
\end{equation}
```

while

``` math
\begin{equation}
X_{j,t}=-8
\end{equation}
```

becomes

``` math
\begin{equation}
\widetilde{X}_{j,t}=-3.
\end{equation}
```

##### Point-in-Time Computation

For a cross-sectional signal, the thresholds should be estimated independently at each time $`t`$:

``` math
\begin{equation}
Q_{\alpha,t}
=
Q_{\alpha}
\left(
\left\{
X_{j,t}
:
j\in\mathcal{U}_t
\right\}
\right).
\end{equation}
```

One should not compute

``` math
\begin{equation}
Q_{\alpha}
\end{equation}
```

once over the full panel

``` math
\begin{equation}
\left\{
X_{i,t}
:
i=1,\ldots,N,
\;
t=1,\ldots,T
\right\}
\end{equation}
```

and then apply it historically.

Doing so allows future observations to influence historical thresholds and may also ignore changes in the cross-sectional distribution through time.

##### Advantages and Limitations

Quantile winsorization has several advantages:

- it makes few distributional assumptions;

- it is easy to implement;

- it is robust to extreme magnitudes;

- it adapts to the cross-sectional scale of the variable.

However, it also has limitations:

- the choice of $`\alpha`$ is arbitrary;

- it treats all observations beyond the threshold identically;

- it may suppress economically meaningful extreme information;

- small cross-sections can produce unstable quantiles.

#### MAD-Based Methods

The Median Absolute Deviation provides a robust alternative to the standard deviation for measuring dispersion.

For a sample

``` math
\begin{equation}
X_1,\ldots,X_N,
\end{equation}
```

define the median

``` math
\begin{equation}
m
=
\operatorname{Median}(X_i).
\end{equation}
```

The Median Absolute Deviation is

``` math
\begin{equation}
\boxed{
MAD
=
\operatorname{Median}
\left(
|X_i-m|
\right).
}
\end{equation}
```

Unlike the sample mean and standard deviation, the median and MAD are much less sensitive to extreme observations.

##### Gaussian-Consistency Scaling

For normally distributed data,

``` math
\begin{equation}
MAD
\approx
0.67449\,\sigma.
\end{equation}
```

Therefore, a consistent estimator of Gaussian scale is

``` math
\begin{equation}
\boxed{
\widehat{\sigma}_{MAD}
=
1.4826
\,MAD.
}
\end{equation}
```

since approximately

``` math
\begin{equation}
1.4826
=
\frac{1}{0.67449}.
\end{equation}
```

##### MAD-Based Thresholds

A robust outlier rule may be defined as

``` math
\begin{equation}
\boxed{
|X_i-m|
>
c
\widehat{\sigma}_{MAD}.
}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
X_i
<
m-c\widehat{\sigma}_{MAD}
\end{equation}
```

or

``` math
\begin{equation}
X_i
>
m+c\widehat{\sigma}_{MAD}.
\end{equation}
```

The threshold $`c`$ determines the aggressiveness of the rule.

##### Degenerate MAD

A practical issue arises when

``` math
\begin{equation}
MAD=0.
\end{equation}
```

This may occur when a large fraction of observations have identical values.

In that case,

``` math
\begin{equation}
\frac{X_i-m}{MAD}
\end{equation}
```

is undefined.

The backtester should therefore specify an explicit fallback policy, such as:

- no MAD-based treatment;

- alternative robust scale estimator;

- quantile-based treatment;

- explicit handling of discrete variables.

A silent division by zero should never determine the resulting signal.

#### Robust Z-Scores

The conventional z-score is

``` math
\begin{equation}
Z_i
=
\frac{
X_i-\bar{X}
}{
s_X
},
\end{equation}
```

where

``` math
\begin{equation}
\bar{X}
=
\frac{1}{N}
\sum_{i=1}^{N}
X_i
\end{equation}
```

and

``` math
\begin{equation}
s_X
=
\sqrt{
\frac{1}{N-1}
\sum_{i=1}^{N}
(X_i-\bar{X})^2
}.
\end{equation}
```

Both $`\bar{X}`$ and $`s_X`$ can be strongly influenced by outliers.

##### Robust Z-Score

Replacing the mean and standard deviation with the median and MAD gives

``` math
\begin{equation}
\boxed{
Z_i^{\mathrm{rob}}
=
\frac{
X_i-m
}{
1.4826\,MAD
}.
}
\end{equation}
```

An observation may then be flagged whenever

``` math
\begin{equation}
\boxed{
|Z_i^{\mathrm{rob}}|
>
c.
}
\end{equation}
```

Alternatively, the robust z-score itself may be used as the transformed feature.

##### Cross-Sectional Robust Standardization

At time $`t`$,

``` math
\begin{equation}
m_t
=
\operatorname{Median}_{i\in\mathcal{U}_t}
X_{i,t},
\end{equation}
```

and

``` math
\begin{equation}
MAD_t
=
\operatorname{Median}_{i\in\mathcal{U}_t}
|X_{i,t}-m_t|.
\end{equation}
```

Then

``` math
\begin{equation}
\boxed{
Z_{i,t}^{\mathrm{rob}}
=
\frac{
X_{i,t}-m_t
}{
1.4826\,MAD_t
}.
}
\end{equation}
```

This transformation provides both centering and robust cross-sectional scaling.

##### Detection vs. Transformation

It is important to distinguish using the robust z-score to identify outliers

``` math
\begin{equation}
|Z_{i,t}^{\mathrm{rob}}|>c,
\end{equation}
```

from using it as the actual transformed signal:

``` math
\begin{equation}
\widetilde{X}_{i,t}
=
Z_{i,t}^{\mathrm{rob}}.
\end{equation}
```

These are different operations.

The first produces a diagnostic flag. The second changes the scale and cross-sectional interpretation of the variable.

#### Truncation, Winsorization, and Observation Removal

Once an observation has been identified as extreme, several treatments are possible.

The three most common approaches are:

``` math
\begin{equation}
\boxed{
\text{Winsorization},
\qquad
\text{Truncation},
\qquad
\text{Removal}.
}
\end{equation}
```

##### Winsorization

As defined previously, winsorization caps values at predefined boundaries.

For lower and upper bounds $`L_t`$ and $`U_t`$,

``` math
\begin{equation}
\boxed{
\widetilde{X}_{i,t}
=
\begin{cases}
L_t,
&
X_{i,t}<L_t,
\\
X_{i,t},
&
L_t\leq X_{i,t}\leq U_t,
\\
U_t,
&
X_{i,t}>U_t.
\end{cases}
}
\end{equation}
```

The observation remains in the sample.

##### Truncation

Terminology varies across fields. In this document, *truncation* refers to treating observations outside the admissible interval as missing:

``` math
\begin{equation}
\boxed{
\widetilde{X}_{i,t}
=
\begin{cases}
X_{i,t},
&
L_t\leq X_{i,t}\leq U_t,
\\
\mathrm{NA},
&
\text{otherwise}.
\end{cases}
}
\end{equation}
```

The security itself need not necessarily be removed; only the affected variable is invalidated for that observation.

##### Observation Removal

A more aggressive procedure removes the entire observation from the cross-section:

``` math
\begin{equation}
i
\notin
\mathcal{S}_t
\end{equation}
```

if

``` math
\begin{equation}
X_{i,t}
\notin
[L_t,U_t].
\end{equation}
```

This means that all variables associated with the corresponding security-date observation are excluded from that particular analysis.

##### Comparison

The three approaches have different consequences:

``` math
\begin{equation}
\boxed{
\begin{array}{lll}
\text{Winsorization}
&
\rightarrow
&
\text{retain observation, reduce magnitude},
\\[0.15cm]
\text{Truncation}
&
\rightarrow
&
\text{retain row, invalidate variable},
\\[0.15cm]
\text{Removal}
&
\rightarrow
&
\text{remove observation entirely}.
\end{array}
}
\end{equation}
```

Winsorization generally preserves cross-sectional coverage better, whereas removal may introduce sample-selection effects if extreme observations are economically non-random.

##### Clipping

A deterministic bound may also be imposed using economically defined limits.

For example,

``` math
\begin{equation}
\widetilde{X}_{i,t}
=
\min
\left[
\max
\left(
X_{i,t},
L
\right),
U
\right].
\end{equation}
```

Unlike quantile winsorization, the thresholds $`L`$ and $`U`$ are fixed rather than estimated from the data.

This may be appropriate when the variable has known economic or structural bounds.

##### Effect on Ranking

For rank-based strategies, winsorization may have less impact than for magnitude-based strategies.

Suppose

``` math
\begin{equation}
X_1<X_2<\cdots<X_N.
\end{equation}
```

If the largest values are winsorized to a common upper threshold, several securities may become tied:

``` math
\begin{equation}
\widetilde{X}_{N-k}
=
\cdots
=
\widetilde{X}_{N}.
\end{equation}
```

The ranking method must therefore specify how ties are handled.

By contrast, if only the order matters and winsorization does not change the ordering, portfolio membership may remain unchanged.

##### Effect on Linear Models

Magnitude-based models can be much more sensitive.

Consider

``` math
\begin{equation}
Y_i
=
\alpha
+
\beta X_i
+
\varepsilon_i.
\end{equation}
```

An observation with unusually large $`|X_i|`$ may have high leverage and exert substantial influence on

``` math
\begin{equation}
\widehat{\beta}.
\end{equation}
```

Winsorization, robust regression, or alternative estimators may therefore substantially change estimated model parameters.

#### Economic Sanity Checks

Statistical outlier rules should not replace economic reasoning.

Before modifying an extreme observation, the backtester should determine whether its magnitude is economically plausible and whether it can be explained by the underlying data-generating process.

##### Mechanical Ratio Explosions

Many financial ratios can become extremely large because their denominator is close to zero.

Consider

``` math
\begin{equation}
X_i
=
\frac{A_i}{B_i}.
\end{equation}
```

If

``` math
\begin{equation}
B_i
\rightarrow
0,
\end{equation}
```

then

``` math
\begin{equation}
|X_i|
\rightarrow
\infty
\end{equation}
```

even when $`A_i`$ is economically ordinary.

Examples include:

- P/E ratios when earnings approach zero;

- growth rates when the lagged value is close to zero;

- leverage ratios when equity is very small;

- percentage analyst revisions relative to near-zero forecasts.

In such cases, winsorization treats the symptom rather than the structural source of instability.

##### Ratio Domain Checks

Suppose

``` math
\begin{equation}
PE_{i,t}
=
\frac{
P_{i,t}
}{
EPS_{i,t}
}.
\end{equation}
```

If

``` math
\begin{equation}
EPS_{i,t}<0,
\end{equation}
```

the economic interpretation of the P/E ratio changes substantially.

The appropriate treatment may therefore be to classify the ratio as non-meaningful rather than treating a large negative P/E as a conventional statistical outlier.

##### Corporate Events

An extreme return may result from:

- acquisition announcements;

- bankruptcy;

- spin-offs;

- special dividends;

- rights issues;

- incorrectly adjusted stock splits.

Before applying statistical treatment, the data should therefore be checked against relevant corporate-action information.

##### Units and Scaling

Extreme observations may indicate inconsistent units.

For example, one provider may store a percentage as

``` math
\begin{equation}
5
\end{equation}
```

while another stores the same quantity as

``` math
\begin{equation}
0.05.
\end{equation}
```

Similarly, monetary quantities may be expressed in:

- units;

- thousands;

- millions;

- different currencies.

A unit mismatch can easily appear statistically as an extreme observation.

Therefore,

``` math
\begin{equation}
\boxed{
\text{Outlier Detection}
\text{ should occur only after }
\text{unit and structural validation}.
}
\end{equation}
```

##### Group-Conditional Distributions

A variable may have systematically different distributions across industries, countries, or other groups.

Suppose

``` math
\begin{equation}
g(i,t)
\end{equation}
```

denotes the industry of security $`i`$.

Instead of computing global thresholds

``` math
\begin{equation}
Q_{\alpha,t},
\end{equation}
```

one may compute group-specific thresholds

``` math
\begin{equation}
Q_{\alpha,g,t}.
\end{equation}
```

Then winsorization becomes

``` math
\begin{equation}
\widetilde{X}_{i,t}
=
\min
\left[
\max
\left(
X_{i,t},
Q_{\alpha,g(i,t),t}
\right),
Q_{1-\alpha,g(i,t),t}
\right].
\end{equation}
```

This can be useful when economic distributions differ structurally across groups.

However, small groups may produce unstable threshold estimates.

##### Treatment Hierarchy

A robust outlier process can therefore be summarized as

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Extreme Observation}
&\rightarrow
\text{Structural Validation}
\rightarrow
\text{Economic Interpretation}
\\[0.1cm]
&\rightarrow
\text{Outlier Detection}
\rightarrow
\text{Treatment Decision}.
\end{aligned}
}
\end{equation}
```

The ordering is important.

Statistical clipping should not be used to conceal errors that should instead be corrected during data cleaning.

#### Point-in-Time Outlier Treatment

Outlier treatment itself forms part of the historical information-processing pipeline and must therefore respect chronology.

For a cross-sectional transformation,

``` math
\begin{equation}
\widetilde{X}_{i,t}
=
\mathcal{O}
\left(
X_{i,t};
\theta_t
\right),
\end{equation}
```

the parameters $`\theta_t`$ may use the cross-section available at time $`t`$:

``` math
\begin{equation}
\theta_t
=
g
\left(
\left\{
X_{j,t}
:
j\in\mathcal{U}_t
\right\}
\right).
\end{equation}
```

For a time-series transformation,

``` math
\begin{equation}
\theta_{i,t}
=
g
\left(
X_{i,t-1},
X_{i,t-2},
\ldots,
X_{i,t-L}
\right),
\end{equation}
```

if the signal is constructed before $`X_{i,t}`$ becomes fully observable.

More generally,

``` math
\begin{equation}
\boxed{
\theta_{i,t}
\in
\mathcal{I}_t.
}
\end{equation}
```

Global full-sample preprocessing violates this principle whenever future observations influence historical thresholds.

#### Outlier-Treatment Diagnostics

Outlier treatment should be monitored quantitatively.

For each date $`t`$, define the fraction of observations affected by the treatment:

``` math
\begin{equation}
\boxed{
p_t^{\mathrm{out}}
=
\frac{
1
}{
N_t
}
\sum_{i=1}^{N_t}
\mathbb{I}
\left(
\widetilde{X}_{i,t}
\neq
X_{i,t}
\right).
}
\end{equation}
```

For quantile winsorization at symmetric level $`\alpha`$, one would expect approximately

``` math
\begin{equation}
p_t^{\mathrm{out}}
\approx
2\alpha,
\end{equation}
```

subject to ties and finite-sample effects.

Useful diagnostics include:

- number and proportion of treated observations;

- lower and upper thresholds through time;

- securities repeatedly classified as outliers;

- industries or countries disproportionately affected;

- pre- and post-treatment distributions;

- effect on signal ranks;

- effect on model coefficients;

- effect on portfolio turnover and performance.

A sudden change in

``` math
\begin{equation}
p_t^{\mathrm{out}}
\end{equation}
```

may indicate a regime change, a data-quality problem, or a structural change in the variable rather than an ordinary increase in outliers.

#### Output of the Outlier Layer

The output of the outlier layer should preserve both the original and treated observations.

For each variable, one may retain

``` math
\begin{equation}
\boxed{
\left(
X_{i,t}^{\mathrm{clean}},
X_{i,t}^{\mathrm{treated}},
O_{i,t},
M_{i,t}^{\mathrm{treatment}}
\right),
}
\end{equation}
```

where:

- $`X_{i,t}^{\mathrm{clean}}`$ is the economically validated observation;

- $`X_{i,t}^{\mathrm{treated}}`$ is the value passed downstream;

- $`O_{i,t}`$ is an outlier indicator;

- $`M_{i,t}^{\mathrm{treatment}}`$ records the applied treatment.

The data pipeline therefore becomes

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathcal{D}^{\mathrm{raw}}
&\rightarrow
\mathcal{D}^{\mathrm{PIT}}
\rightarrow
\mathcal{D}^{\mathrm{clean}}
\\[0.1cm]
&\rightarrow
\mathcal{D}^{\mathrm{treated}}
\rightarrow
\text{Feature Engineering}
\rightarrow
\text{Signal Construction}.
\end{aligned}
}
\end{equation}
```

The distinction between these stages should remain explicit:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Data Cleaning}
&:
\text{ Is the observation valid?}
\\
\text{Outlier Detection}
&:
\text{ Is the valid observation unusually extreme?}
\\
\text{Outlier Treatment}
&:
\text{ How much influence should that extreme observation retain?}
\end{aligned}
}
\end{equation}
```

# Signal Construction

