### From Firm-Level Characteristics to Raw Scores

After data cleaning and outlier treatment, the next stage of the investment process transforms economically meaningful firm-level characteristics into cross-sectionally comparable investment scores.

Let

``` math
\begin{equation}
x_{i,t}^{(k)}
\end{equation}
```

denote characteristic $`k`$ for security $`i`$ at decision time $`t`$, after all required point-in-time construction, cleaning, and outlier treatment.

Examples of characteristics include valuation ratios, profitability measures, earnings revisions, momentum measures, or any other firm-level quantity used by the investment strategy.

The purpose of the scoring layer is to construct

``` math
\begin{equation}
s_{i,t}^{(k),\mathrm{raw}},
\end{equation}
```

where the score represents the relative attractiveness of security $`i`$ according to characteristic $`k`$.

Abstractly,

``` math
\begin{equation}
\boxed{
s_{i,t}^{(k),\mathrm{raw}}
=
\mathcal{S}_t^{(k)}
\left(
x_{i,t}^{(k)}
\right),
}
\end{equation}
```

where $`\mathcal{S}_t^{(k)}`$ denotes the chosen scoring transformation.

For a cross-sectional strategy, the transformation generally depends on the complete eligible cross-section:

``` math
\begin{equation}
\boxed{
s_{i,t}^{(k),\mathrm{raw}}
=
\mathcal{S}^{(k)}
\left(
x_{i,t}^{(k)};
\left\{
x_{j,t}^{(k)}
:
j\in\mathcal{U}_t
\right\}
\right).
}
\end{equation}
```

The scoring transformation serves several possible purposes:

- placing characteristics measured in different units on comparable scales;

- expressing the relative position of each security in the cross-section;

- controlling the influence of characteristic magnitude;

- establishing a common sign convention;

- facilitating the combination of multiple characteristics.

Importantly, the different transformations developed below are generally *alternative scoring conventions* rather than mandatory sequential steps.

For example,

``` math
\begin{equation}
x_{i,t}
\rightarrow
z_{i,t}
\end{equation}
```

and

``` math
\begin{equation}
x_{i,t}
\rightarrow
\operatorname{Rank}_{i,t}
\end{equation}
```

represent two different ways of constructing a score from the same characteristic.

#### Definition of a Firm-Level Characteristic

A firm-level characteristic is a measurable quantity associated with a security or its underlying company at a given point in time.

For characteristic $`k`$,

``` math
\begin{equation}
\boxed{
x_{i,t}^{(k)}
\in
\mathbb{R}
}
\end{equation}
```

denotes the characteristic value for security $`i`$ at time $`t`$.

For $`N_t`$ eligible securities, the corresponding cross-sectional characteristic vector is

``` math
\begin{equation}
\boxed{
\mathbf{x}_t^{(k)}
=
\begin{bmatrix}
x_{1,t}^{(k)}
\\
x_{2,t}^{(k)}
\\
\vdots
\\
x_{N_t,t}^{(k)}
\end{bmatrix}
\in
\mathbb{R}^{N_t}.
}
\end{equation}
```

With $`K`$ characteristics, the complete characteristic matrix is

``` math
\begin{equation}
\boxed{
\mathbf{X}_t
=
\begin{bmatrix}
x_{1,t}^{(1)} & \cdots & x_{1,t}^{(K)}
\\
\vdots & \ddots & \vdots
\\
x_{N_t,t}^{(1)} & \cdots & x_{N_t,t}^{(K)}
\end{bmatrix}
\in
\mathbb{R}^{N_t\times K}.
}
\end{equation}
```

##### Characteristic vs. Score

A characteristic should be distinguished from an investment score.

The characteristic

``` math
\begin{equation}
x_{i,t}^{(k)}
\end{equation}
```

has an economic definition and may retain its natural units.

For example,

``` math
\begin{equation}
x_{i,t}^{(k)}
=
\frac{
\mathrm{BookEquity}_{i,t}
}{
\mathrm{MarketCapitalization}_{i,t}
}
\end{equation}
```

is a valuation characteristic.

The score

``` math
\begin{equation}
s_{i,t}^{(k)}
\end{equation}
```

instead represents how that observation is interpreted by the investment process relative to other securities.

Thus,

``` math
\begin{equation}
\boxed{
\text{Economic Characteristic}
\rightarrow
\text{Scoring Transformation}
\rightarrow
\text{Investment Score}.
}
\end{equation}
```

##### Characteristic Definition

The exact mathematical definition of each characteristic should be specified before its predictive performance is evaluated.

A characteristic definition includes, where relevant:

- the underlying raw variables;

- the transformation applied to those variables;

- the historical lookback window;

- the required lag;

- the observation frequency;

- the treatment of missing observations;

- the sign of the expected relationship with future returns.

For example, a generic momentum characteristic may be defined as

``` math
\begin{equation}
x_{i,t}^{\mathrm{mom}}
=
\prod_{\tau=t-L_2}^{t-L_1}
\left(
1+R_{i,\tau}
\right)
-1,
\end{equation}
```

where $`L_1`$ and $`L_2`$ determine the exclusion and lookback periods.

Once the characteristic definition is fixed, the scoring layer should not change its underlying economic meaning.

#### Cross-Sectional vs. Time-Series Transformations

A characteristic can be transformed relative to two fundamentally different reference sets.

##### Cross-Sectional Transformation

A cross-sectional transformation compares security $`i`$ with other securities at the same time $`t`$.

Define

``` math
\begin{equation}
\mathcal{X}_t^{(k)}
=
\left\{
x_{j,t}^{(k)}
:
j\in\mathcal{U}_t
\right\}.
\end{equation}
```

Then

``` math
\begin{equation}
\boxed{
s_{i,t}^{(k)}
=
\mathcal{S}^{CS}
\left(
x_{i,t}^{(k)};
\mathcal{X}_t^{(k)}
\right).
}
\end{equation}
```

The resulting score answers a question of the form:

``` math
\begin{equation}
\boxed{
\text{How attractive is security }i
\text{ relative to other securities at time }t?
}
\end{equation}
```

This is the natural framework for cross-sectional stock-selection strategies.

##### Time-Series Transformation

A time-series transformation instead compares the current characteristic with its own historical distribution.

Let

``` math
\begin{equation}
\mathcal{H}_{i,t}^{(k)}
=
\left\{
x_{i,\tau}^{(k)}
:
\tau\leq t
\right\}.
\end{equation}
```

Then

``` math
\begin{equation}
\boxed{
s_{i,t}^{(k),TS}
=
\mathcal{S}^{TS}
\left(
x_{i,t}^{(k)};
\mathcal{H}_{i,t}^{(k)}
\right).
}
\end{equation}
```

For example,

``` math
\begin{equation}
s_{i,t}^{(k),TS}
=
\frac{
x_{i,t}^{(k)}
-
\widehat{\mu}_{i,t}^{(k)}
}{
\widehat{\sigma}_{i,t}^{(k)}
}.
\end{equation}
```

This answers a different question:

``` math
\begin{equation}
\boxed{
\text{How unusual is the current value for security }i
\text{ relative to its own history?}
}
\end{equation}
```

##### Distinction

In general,

``` math
\begin{equation}
\boxed{
s_{i,t}^{CS}
\neq
s_{i,t}^{TS}.
}
\end{equation}
```

A firm may appear cheap relative to other firms while simultaneously appearing expensive relative to its own historical valuation.

The reference distribution must therefore be chosen according to the economic hypothesis being tested.

#### Z-Score Transformation

A standard cross-sectional transformation is the z-score.

For characteristic $`k`$, define the cross-sectional mean

``` math
\begin{equation}
\mu_t^{(k)}
=
\frac{1}{N_t}
\sum_{i=1}^{N_t}
x_{i,t}^{(k)},
\end{equation}
```

and standard deviation

``` math
\begin{equation}
\sigma_t^{(k)}
=
\sqrt{
\frac{1}{N_t-1}
\sum_{i=1}^{N_t}
\left(
x_{i,t}^{(k)}
-
\mu_t^{(k)}
\right)^2
}.
\end{equation}
```

The standardized characteristic is

``` math
\begin{equation}
\boxed{
z_{i,t}^{(k)}
=
\frac{
x_{i,t}^{(k)}
-
\mu_t^{(k)}
}{
\sigma_t^{(k)}
}.
}
\end{equation}
```

By construction,

``` math
\begin{equation}
\frac{1}{N_t}
\sum_{i=1}^{N_t}
z_{i,t}^{(k)}
=
0,
\end{equation}
```

while its cross-sectional variance is normalized according to the chosen variance convention.

##### Interpretation

A positive z-score indicates that the characteristic lies above the cross-sectional mean:

``` math
\begin{equation}
z_{i,t}^{(k)}>0
\quad\Longleftrightarrow\quad
x_{i,t}^{(k)}
>
\mu_t^{(k)}.
\end{equation}
```

For example,

``` math
\begin{equation}
z_{i,t}^{(k)}=2
\end{equation}
```

indicates that the observation lies two cross-sectional standard deviations above the mean.

##### Invariance to Affine Rescaling

Suppose

``` math
\begin{equation}
y_{i,t}
=
a
+
b x_{i,t},
\qquad
b>0.
\end{equation}
```

Then

``` math
\begin{equation}
z_{i,t}^{y}
=
z_{i,t}^{x}.
\end{equation}
```

Thus, positive affine changes in units do not affect the standardized score.

If

``` math
\begin{equation}
b<0,
\end{equation}
```

the sign is reversed.

##### Sensitivity to Extreme Observations

The mean and standard deviation are sensitive to extreme values.

Consequently, even after outlier treatment,

``` math
\begin{equation}
\mu_t^{(k)}
\end{equation}
```

and

``` math
\begin{equation}
\sigma_t^{(k)}
\end{equation}
```

may be influenced by heavy-tailed cross-sectional distributions.

This motivates robust alternatives.

#### Robust Z-Score Transformation

Let

``` math
\begin{equation}
m_t^{(k)}
=
\operatorname{Median}_{i\in\mathcal{U}_t}
x_{i,t}^{(k)}
\end{equation}
```

and

``` math
\begin{equation}
MAD_t^{(k)}
=
\operatorname{Median}_{i\in\mathcal{U}_t}
\left|
x_{i,t}^{(k)}
-
m_t^{(k)}
\right|.
\end{equation}
```

A robust z-score is

``` math
\begin{equation}
\boxed{
z_{i,t}^{(k),\mathrm{rob}}
=
\frac{
x_{i,t}^{(k)}
-
m_t^{(k)}
}{
1.4826\,MAD_t^{(k)}
}.
}
\end{equation}
```

The factor $`1.4826`$ makes the MAD-based scale approximately consistent with the standard deviation under Gaussianity.

##### Relationship with Outlier Treatment

The same robust statistic may appear both in outlier detection and in scoring, but the objectives differ.

In the outlier layer,

``` math
\begin{equation}
z_{i,t}^{\mathrm{rob}}
\end{equation}
```

may be used to decide whether an observation is unusually extreme.

In the scoring layer,

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{raw}}
=
z_{i,t}^{\mathrm{rob}}
}
\end{equation}
```

may itself be the investment score.

Thus,

``` math
\begin{equation}
\boxed{
\text{Same Mathematical Transformation}
\neq
\text{Same Role in the Pipeline}.
}
\end{equation}
```

#### Rank Transformation

Rank transformations discard the magnitude of cross-sectional differences and retain only their ordering.

Let

``` math
\begin{equation}
r_{i,t}^{(k)}
=
\operatorname{Rank}_t
\left(
x_{i,t}^{(k)}
\right),
\end{equation}
```

with the convention

``` math
\begin{equation}
r_{i,t}^{(k)}
\in
\{1,\ldots,N_t\},
\end{equation}
```

where rank $`1`$ corresponds to the smallest characteristic value and rank $`N_t`$ to the largest.

##### Rank Invariance

For any strictly increasing transformation $`g`$,

``` math
\begin{equation}
\boxed{
\operatorname{Rank}
\left(
g(x_{i,t})
\right)
=
\operatorname{Rank}
\left(
x_{i,t}
\right).
}
\end{equation}
```

Thus, ranking is invariant to monotonic transformations.

This property makes rank-based signals robust to extreme magnitudes and changes in the scale of the characteristic.

##### Loss of Magnitude Information

The robustness comes at a cost.

Suppose

``` math
\begin{equation}
x_{1,t}=1,
\qquad
x_{2,t}=2,
\qquad
x_{3,t}=100.
\end{equation}
```

The ranks are simply

``` math
\begin{equation}
1,\quad2,\quad3.
\end{equation}
```

The fact that the third observation is dramatically farther from the second than the second is from the first is discarded.

Thus,

``` math
\begin{equation}
\boxed{
\text{Rank Score}
=
\text{Ordinal Information},
}
\end{equation}
```

whereas a z-score retains information about relative magnitude.

##### Ties

If multiple observations have identical values, a tie-breaking convention is required.

Common approaches include:

- average ranks;

- minimum ranks;

- maximum ranks;

- deterministic secondary ordering.

Random tie breaking should generally be avoided unless the random seed is explicitly controlled and the procedure is economically justified.

#### Percentile Transformation

Raw ranks depend mechanically on the number of securities in the universe.

A percentile transformation maps ranks onto a common interval.

One convention is

``` math
\begin{equation}
\boxed{
p_{i,t}^{(k)}
=
\frac{
r_{i,t}^{(k)}-1
}{
N_t-1
},
}
\end{equation}
```

for

``` math
\begin{equation}
N_t>1.
\end{equation}
```

Then

``` math
\begin{equation}
p_{i,t}^{(k)}
\in
[0,1].
\end{equation}
```

The lowest-ranked security receives

``` math
\begin{equation}
p_{i,t}^{(k)}=0,
\end{equation}
```

and the highest-ranked security receives

``` math
\begin{equation}
p_{i,t}^{(k)}=1.
\end{equation}
```

##### Centered Percentile Score

For long–short applications, it is often convenient to center the percentile score around zero:

``` math
\begin{equation}
\boxed{
s_{i,t}^{(k)}
=
2p_{i,t}^{(k)}-1.
}
\end{equation}
```

Then

``` math
\begin{equation}
s_{i,t}^{(k)}
\in
[-1,1].
\end{equation}
```

The bottom of the distribution receives scores close to $`-1`$, the median receives scores close to zero, and the top receives scores close to $`+1`$.

##### Alternative Percentile Conventions

Other conventions are possible, such as

``` math
\begin{equation}
p_{i,t}
=
\frac{r_{i,t}}{N_t+1}
\end{equation}
```

or

``` math
\begin{equation}
p_{i,t}
=
\frac{r_{i,t}-0.5}{N_t}.
\end{equation}
```

These differ slightly in finite samples.

The precise convention should therefore be specified explicitly, particularly if percentile scores are subsequently transformed through an inverse distribution function.

#### Quantile and Decile Scores

A continuous cross-sectional score may be discretized into $`Q`$ groups.

Let

``` math
\begin{equation}
q_{i,t}
\in
\{1,\ldots,Q\}
\end{equation}
```

denote the quantile group assigned to security $`i`$.

For deciles,

``` math
\begin{equation}
Q=10.
\end{equation}
```

A simple approximation is

``` math
\begin{equation}
\boxed{
q_{i,t}
=
1
+
\left\lfloor
Q
\frac{
r_{i,t}-1
}{
N_t
}
\right\rfloor,
}
\end{equation}
```

with the final value restricted to

``` math
\begin{equation}
q_{i,t}
\in
\{1,\ldots,Q\}.
\end{equation}
```

##### Discrete Scores

The group label may itself be transformed into a centered score:

``` math
\begin{equation}
\boxed{
s_{i,t}^{Q}
=
\frac{
2q_{i,t}
-
(Q+1)
}{
Q-1
}.
}
\end{equation}
```

This maps

``` math
\begin{equation}
q=1
\end{equation}
```

to

``` math
\begin{equation}
s^Q=-1,
\end{equation}
```

and

``` math
\begin{equation}
q=Q
\end{equation}
```

to

``` math
\begin{equation}
s^Q=+1.
\end{equation}
```

##### Score vs. Portfolio Formation

Quantile assignment at this stage should be distinguished from constructing a quantile portfolio.

Here,

``` math
\begin{equation}
q_{i,t}
\end{equation}
```

is simply a discrete representation of the signal.

Later, portfolio construction may decide to hold only

``` math
\begin{equation}
q_{i,t}=1
\end{equation}
```

and

``` math
\begin{equation}
q_{i,t}=Q,
\end{equation}
```

or to assign weights across all groups.

Thus,

``` math
\begin{equation}
\boxed{
\text{Quantile Score}
\neq
\text{Quantile Portfolio}.
}
\end{equation}
```

#### Gaussian Rank Transformation

A Gaussian rank transformation combines the robustness of ranking with a continuous score having an approximately Gaussian cross-sectional shape.

First construct a percentile strictly inside $`(0,1)`$, for example

``` math
\begin{equation}
u_{i,t}
=
\frac{
r_{i,t}-0.5
}{
N_t
}.
\end{equation}
```

Then apply the inverse standard-normal cumulative distribution function:

``` math
\begin{equation}
\boxed{
g_{i,t}
=
\Phi^{-1}
\left(
u_{i,t}
\right),
}
\end{equation}
```

where

``` math
\begin{equation}
\Phi(\cdot)
\end{equation}
```

is the standard-normal cumulative distribution function.

##### Why Interior Percentiles Are Required

If percentile ranks equal exactly zero or one, then

``` math
\begin{equation}
\Phi^{-1}(0)
=
-\infty
\end{equation}
```

and

``` math
\begin{equation}
\Phi^{-1}(1)
=
+\infty.
\end{equation}
```

This is why a convention such as

``` math
\begin{equation}
u_{i,t}
=
\frac{r_{i,t}-0.5}{N_t}
\end{equation}
```

is preferable when applying an inverse-normal transformation.

##### Interpretation

The transformation preserves the ordering:

``` math
\begin{equation}
x_{i,t}<x_{j,t}
\quad\Rightarrow\quad
g_{i,t}<g_{j,t},
\end{equation}
```

but imposes a predetermined relationship between rank and score magnitude.

Securities near the center receive scores close to zero, while securities in the tails receive increasingly large absolute scores.

Thus,

``` math
\begin{equation}
\boxed{
\text{Rank Information}
+
\text{Gaussian Score Geometry}.
}
\end{equation}
```

#### Direction and Sign Convention

The raw mathematical transformation does not necessarily have the desired investment direction.

For each characteristic $`k`$, define a direction parameter

``` math
\begin{equation}
d_k
\in
\{-1,+1\}.
\end{equation}
```

The direction-adjusted score is

``` math
\begin{equation}
\boxed{
s_{i,t}^{(k)}
=
d_k
\widetilde{s}_{i,t}^{(k)},
}
\end{equation}
```

where $`\widetilde{s}_{i,t}^{(k)}`$ is the score before sign adjustment.

A useful global convention is

``` math
\begin{equation}
\boxed{
s_{i,t}^{(k)}>0
\quad\Longleftrightarrow\quad
\text{higher expected attractiveness}.
}
\end{equation}
```

Consequently,

``` math
\begin{equation}
s_{i,t}^{(k)}<0
\end{equation}
```

indicates lower expected attractiveness.

##### Example

Suppose higher profitability is expected to predict higher returns.

Then

``` math
\begin{equation}
d_{\mathrm{profitability}}=+1.
\end{equation}
```

Suppose lower valuation multiples are considered more attractive.

If the raw characteristic is P/E, then

``` math
\begin{equation}
d_{\mathrm{PE}}=-1.
\end{equation}
```

The scoring convention therefore ensures that all characteristics point in the same investment direction before they are combined.

##### Direction Must Be Defined Ex Ante

The sign should follow from the economic hypothesis or predefined research design.

Selecting

``` math
\begin{equation}
d_k
\end{equation}
```

after observing which direction produced the best historical performance is itself a form of data snooping.

#### Score Clipping and Bounding

Even after outlier treatment at the characteristic level, the scoring transformation may produce scores with undesirable magnitudes.

For example, a z-score or Gaussian rank score is theoretically unbounded.

A symmetric clipping rule is

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{clip}}
=
\min
\left[
\max
\left(
s_{i,t},
-c
\right),
c
\right].
}
\end{equation}
```

For example,

``` math
\begin{equation}
c=3
\end{equation}
```

implies

``` math
\begin{equation}
s_{i,t}^{\mathrm{clip}}
\in
[-3,3].
\end{equation}
```

##### Characteristic Winsorization vs. Score Clipping

These two operations occur at different levels.

Characteristic-level treatment modifies

``` math
\begin{equation}
x_{i,t},
\end{equation}
```

whereas score clipping modifies

``` math
\begin{equation}
s_{i,t}.
\end{equation}
```

Thus,

``` math
\begin{equation}
\boxed{
x_{i,t}
\rightarrow
x_{i,t}^{\mathrm{treated}}
\rightarrow
s_{i,t}
\rightarrow
s_{i,t}^{\mathrm{clip}}.
}
\end{equation}
```

They should not be treated as interchangeable operations.

##### Bounded Nonlinear Transformations

Instead of hard clipping, an unbounded score may be mapped smoothly into a bounded interval.

For example,

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{bounded}}
=
\tanh
\left(
\frac{s_{i,t}}{\kappa}
\right),
}
\end{equation}
```

where

``` math
\begin{equation}
\kappa>0
\end{equation}
```

controls the degree of compression.

Then

``` math
\begin{equation}
s_{i,t}^{\mathrm{bounded}}
\in
(-1,1).
\end{equation}
```

Unlike hard clipping, this transformation compresses large values smoothly.

#### Combining Multiple Characteristics

A strategy may use several characteristics simultaneously.

Suppose $`K`$ characteristics have been transformed into directionally consistent scores:

``` math
\begin{equation}
s_{i,t}^{(1)},
\ldots,
s_{i,t}^{(K)}.
\end{equation}
```

Collect them into

``` math
\begin{equation}
\mathbf{s}_{i,t}
=
\begin{bmatrix}
s_{i,t}^{(1)}
\\
\vdots
\\
s_{i,t}^{(K)}
\end{bmatrix}
\in
\mathbb{R}^{K}.
\end{equation}
```

##### Equal-Weighted Combination

The simplest composite score is

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{comp}}
=
\frac{1}{K}
\sum_{k=1}^{K}
s_{i,t}^{(k)}.
}
\end{equation}
```

This requires the individual scores to be on sufficiently comparable scales.

##### Weighted Combination

More generally,

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{comp}}
=
\sum_{k=1}^{K}
\omega_{k,t}
s_{i,t}^{(k)},
}
\end{equation}
```

where

``` math
\begin{equation}
\boldsymbol{\omega}_t
=
\begin{bmatrix}
\omega_{1,t}
&
\cdots
&
\omega_{K,t}
\end{bmatrix}^{\top}.
\end{equation}
```

In vector form,

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{comp}}
=
\boldsymbol{\omega}_t^{\top}
\mathbf{s}_{i,t}.
}
\end{equation}
```

A common normalization is

``` math
\begin{equation}
\sum_{k=1}^{K}
\omega_{k,t}
=
1,
\end{equation}
```

although this is not mathematically required.

##### Static vs. Dynamic Combination Weights

Combination weights may be static:

``` math
\begin{equation}
\omega_{k,t}
=
\omega_k,
\end{equation}
```

or dynamic:

``` math
\begin{equation}
\omega_{k,t}
=
g_k
\left(
\mathcal{I}_t
\right).
\end{equation}
```

Dynamic weights may depend on historically estimated predictive performance, risk, regime variables, or other information available at time $`t`$.

Any estimated weighting rule must itself respect the point-in-time constraint.

##### Missing Component Scores

If some component scores are unavailable, the aggregation rule must specify how the composite score is constructed.

Let

``` math
\begin{equation}
\mathcal{K}_{i,t}^{\mathrm{avail}}
=
\left\{
k:
s_{i,t}^{(k)}
\text{ is available}
\right\}.
\end{equation}
```

One possible renormalized combination is

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{comp}}
=
\frac{
\sum_{k\in\mathcal{K}_{i,t}^{\mathrm{avail}}}
\omega_{k,t}s_{i,t}^{(k)}
}{
\sum_{k\in\mathcal{K}_{i,t}^{\mathrm{avail}}}
\omega_{k,t}
},
}
\end{equation}
```

provided the denominator is non-zero.

However, this changes the effective characteristic mix across securities.

The resulting scores may therefore no longer be directly comparable if missingness is substantial.

##### Correlation Between Characteristics

A simple average implicitly treats each component as a separate contribution.

If two characteristics are highly correlated,

``` math
\begin{equation}
\operatorname{Corr}
\left(
s_t^{(k)},
s_t^{(\ell)}
\right)
\approx1,
\end{equation}
```

including both may effectively overweight the same underlying information.

Thus, signal combination should consider not only individual predictive strength but also redundancy across characteristics.

More sophisticated combination methods may therefore use covariance, regression, optimization, or predictive models.

Such approaches connect naturally to the model-based signal construction developed in the following section.

#### Final Raw Score

The output of the characteristic-based signal-construction layer is a raw score for every eligible security.

Define

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{raw}}
}
\end{equation}
```

as the final characteristic-based raw score before explicit risk or factor neutralization.

Collecting all securities gives

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{raw}}
=
\begin{bmatrix}
s_{1,t}^{\mathrm{raw}}
\\
s_{2,t}^{\mathrm{raw}}
\\
\vdots
\\
s_{N_t,t}^{\mathrm{raw}}
\end{bmatrix}
\in
\mathbb{R}^{N_t}.
}
\end{equation}
```

##### Interpretation

Under the sign convention adopted above,

``` math
\begin{equation}
s_{i,t}^{\mathrm{raw}}>0
\end{equation}
```

represents relatively attractive securities, whereas

``` math
\begin{equation}
s_{i,t}^{\mathrm{raw}}<0
\end{equation}
```

represents relatively unattractive securities.

However,

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{raw}}
\neq
w_{i,t}.
}
\end{equation}
```

A score is an investment signal, not a portfolio weight.

Its magnitude expresses relative conviction under the chosen scoring convention, but does not yet specify:

- portfolio gross exposure;

- net exposure;

- position size;

- beta exposure;

- industry exposure;

- factor exposure;

- leverage;

- risk contribution;

- trading constraints.

These are handled by subsequent stages of the investment process.

##### Characteristic-Based Signal Pipeline

For a single characteristic, the complete transformation can be represented as

``` math
\begin{equation}
\boxed{
\begin{aligned}
x_{i,t}^{\mathrm{raw}}
&\rightarrow
x_{i,t}^{\mathrm{clean}}
\rightarrow
x_{i,t}^{\mathrm{treated}}
\\[0.1cm]
&\rightarrow
\mathcal{S}_t
\left(
x_{i,t}^{\mathrm{treated}}
\right)
\rightarrow
s_{i,t}^{\mathrm{raw}}.
\end{aligned}
}
\end{equation}
```

For multiple characteristics,

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{x}_{i,t}
&\rightarrow
\mathbf{x}_{i,t}^{\mathrm{clean}}
\rightarrow
\mathbf{x}_{i,t}^{\mathrm{treated}}
\\[0.1cm]
&\rightarrow
\mathbf{s}_{i,t}
\rightarrow
\mathcal{A}
\left(
\mathbf{s}_{i,t}
\right)
\rightarrow
s_{i,t}^{\mathrm{raw}},
\end{aligned}
}
\end{equation}
```

where $`\mathcal{A}`$ denotes the chosen score-aggregation operator.

##### Interface with the Downstream Engine

The key architectural principle is that the subsequent backtesting engine receives

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{raw}}
\in
\mathbb{R}^{N_t}
}
\end{equation}
```

regardless of how the score was produced.

A characteristic-based strategy may generate

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{raw}}
=
\mathcal{S}
\left(
\mathbf{X}_t
\right),
\end{equation}
```

while a predictive model developed in the next section may generate

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{raw}}
=
\mathcal{P}
\left(
\widehat{\mathbf{y}}_{t+h|t}
\right).
\end{equation}
```

Both objects then enter the same downstream pipeline:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{s}_t^{\mathrm{raw}}
&\rightarrow
\text{Signal Neutralization}
\rightarrow
\mathbf{s}_t^{\mathrm{neutral}}
\\[0.1cm]
&\rightarrow
\text{Final Signal}
\rightarrow
\mathbf{s}_t^{\mathrm{final}}
\rightarrow
\text{Portfolio Construction}.
\end{aligned}
}
\end{equation}
```

This separation allows signal generation and portfolio construction to remain modular: the downstream portfolio engine need not know whether the raw score originated from a single firm characteristic, a composite score, an econometric model, or a machine-learning model. “‘latex

