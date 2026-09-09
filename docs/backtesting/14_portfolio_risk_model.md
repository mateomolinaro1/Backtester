### Portfolio Risk Model

The signal-construction process determines which securities are attractive, but does not describe the risk created by holding them.

Two securities with identical expected attractiveness may have very different volatilities, and two individually risky securities may together form a relatively low-risk portfolio if their returns are weakly or negatively correlated.

The portfolio-construction engine therefore requires a model of the joint distribution of asset returns.

Let

``` math
\begin{equation}
\mathbf{R}_{t+1}
=
\begin{bmatrix}
R_{1,t+1}\\
\vdots\\
R_{N_t,t+1}
\end{bmatrix}
\in
\mathbb{R}^{N_t}
\end{equation}
```

denote the vector of future security returns.

The central object of the portfolio risk model is the conditional covariance matrix

``` math
\begin{equation}
\boxed{
\boldsymbol{\Sigma}_t
=
\operatorname{Cov}
\left(
\mathbf{R}_{t+1}
\mid
\mathcal{I}_t
\right)
\in
\mathbb{R}^{N_t\times N_t}.
}
\end{equation}
```

Its elements are

``` math
\begin{equation}
\Sigma_{ij,t}
=
\operatorname{Cov}_t
\left(
R_{i,t+1},
R_{j,t+1}
\right).
\end{equation}
```

The diagonal elements contain individual asset variances:

``` math
\begin{equation}
\Sigma_{ii,t}
=
\sigma_{i,t}^{2},
\end{equation}
```

while the off-diagonal elements contain pairwise covariances.

The risk model therefore provides the mapping

``` math
\begin{equation}
\boxed{
\text{Security Positions}
+
\text{Joint Return Distribution}
\rightarrow
\text{Portfolio Risk}.
}
\end{equation}
```

At this stage of the backtester, the two principal inputs to portfolio construction are therefore

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{s}_t^{\mathrm{final}}
&\in
\mathbb{R}^{N_t}
&&
\text{: investment attractiveness},
\\
\boldsymbol{\Sigma}_t
&\in
\mathbb{R}^{N_t\times N_t}
&&
\text{: estimated joint risk}.
\end{aligned}
}
\end{equation}
```

Additional exposure matrices, liquidity variables, and portfolio constraints will subsequently complement these two objects.

#### Portfolio Variance and Covariance

Let

``` math
\begin{equation}
\mathbf{w}_t
=
\begin{bmatrix}
w_{1,t}\\
\vdots\\
w_{N_t,t}
\end{bmatrix}
\in
\mathbb{R}^{N_t}
\end{equation}
```

denote portfolio weights.

The future portfolio return is

``` math
\begin{equation}
\boxed{
R_{p,t+1}
=
\mathbf{w}_t^{\top}
\mathbf{R}_{t+1}.
}
\end{equation}
```

Conditional on the information available at time $`t`$, portfolio variance is

``` math
\begin{equation}
\operatorname{Var}_t
\left(
R_{p,t+1}
\right)
=
\operatorname{Var}_t
\left(
\mathbf{w}_t^\top
\mathbf{R}_{t+1}
\right).
\end{equation}
```

Using the covariance matrix,

``` math
\begin{equation}
\boxed{
\sigma_{p,t}^{2}
=
\mathbf{w}_t^\top
\boldsymbol{\Sigma}_t
\mathbf{w}_t.
}
\end{equation}
```

Hence portfolio volatility is

``` math
\begin{equation}
\boxed{
\sigma_{p,t}
=
\sqrt{
\mathbf{w}_t^\top
\boldsymbol{\Sigma}_t
\mathbf{w}_t
}.
}
\end{equation}
```

##### Expanded Representation

Portfolio variance can also be written as

``` math
\begin{equation}
\sigma_{p,t}^{2}
=
\sum_{i=1}^{N_t}
w_{i,t}^{2}
\sigma_{i,t}^{2}
+
\sum_{\substack{i,j=1\\i\neq j}}^{N_t}
w_{i,t}w_{j,t}
\sigma_{ij,t}.
\end{equation}
```

Equivalently,

``` math
\begin{equation}
\boxed{
\sigma_{p,t}^{2}
=
\sum_{i=1}^{N_t}
w_{i,t}^{2}
\sigma_{i,t}^{2}
+
2
\sum_{i<j}
w_{i,t}w_{j,t}
\sigma_{ij,t}.
}
\end{equation}
```

Portfolio risk therefore depends not only on individual-security volatility but also on the dependence structure between securities.

##### Covariance and Correlation

For securities $`i`$ and $`j`$,

``` math
\begin{equation}
\boxed{
\sigma_{ij,t}
=
\rho_{ij,t}
\sigma_{i,t}
\sigma_{j,t},
}
\end{equation}
```

where

``` math
\begin{equation}
\rho_{ij,t}
\in[-1,1]
\end{equation}
```

is their correlation.

Define the diagonal volatility matrix

``` math
\begin{equation}
\mathbf{D}_{\sigma,t}
=
\operatorname{diag}
\left(
\sigma_{1,t},
\ldots,
\sigma_{N_t,t}
\right).
\end{equation}
```

If

``` math
\begin{equation}
\mathbf{C}_t
\in
\mathbb{R}^{N_t\times N_t}
\end{equation}
```

denotes the correlation matrix, then

``` math
\begin{equation}
\boxed{
\boldsymbol{\Sigma}_t
=
\mathbf{D}_{\sigma,t}
\mathbf{C}_t
\mathbf{D}_{\sigma,t}.
}
\end{equation}
```

This decomposition separates the estimation of marginal volatility from the estimation of cross-security dependence.

##### Properties of a Valid Covariance Matrix

A valid covariance matrix must satisfy

``` math
\begin{equation}
\boldsymbol{\Sigma}_t
=
\boldsymbol{\Sigma}_t^\top
\end{equation}
```

and must be positive semidefinite:

``` math
\begin{equation}
\boxed{
\mathbf{x}^\top
\boldsymbol{\Sigma}_t
\mathbf{x}
\geq
0
\qquad
\forall
\mathbf{x}\in\mathbb{R}^{N_t}.
}
\end{equation}
```

This property guarantees that estimated portfolio variance cannot be negative.

For some optimization problems, positive definiteness,

``` math
\begin{equation}
\mathbf{x}^\top
\boldsymbol{\Sigma}_t
\mathbf{x}
>
0
\qquad
\forall\mathbf{x}\neq0,
\end{equation}
```

is particularly useful because it implies invertibility.

#### Historical Covariance Estimation

The simplest covariance estimator uses historical returns.

Suppose a lookback window contains $`L`$ observations:

``` math
\begin{equation}
\mathbf{R}_{t-L+1},
\ldots,
\mathbf{R}_{t}.
\end{equation}
```

Define the historical mean-return vector

``` math
\begin{equation}
\overline{\mathbf{R}}_t
=
\frac{1}{L}
\sum_{\ell=0}^{L-1}
\mathbf{R}_{t-\ell}.
\end{equation}
```

The sample covariance matrix is

``` math
\begin{equation}
\boxed{
\widehat{\boldsymbol{\Sigma}}_t^{\mathrm{sample}}
=
\frac{1}{L-1}
\sum_{\ell=0}^{L-1}
\left(
\mathbf{R}_{t-\ell}
-
\overline{\mathbf{R}}_t
\right)
\left(
\mathbf{R}_{t-\ell}
-
\overline{\mathbf{R}}_t
\right)^\top.
}
\end{equation}
```

Its dimension is

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t^{\mathrm{sample}}
\in
\mathbb{R}^{N_t\times N_t}.
\end{equation}
```

##### Point-in-Time Requirement

The covariance estimate used for portfolio construction at time $`t`$ must depend only on returns already observed at the decision time.

If the portfolio decision occurs before the return for date $`t`$ is known, the estimation window must instead terminate at $`t-1`$.

Thus, schematically,

``` math
\begin{equation}
\boxed{
\widehat{\boldsymbol{\Sigma}}_t
=
g
\left(
\mathbf{R}_{t-1},
\mathbf{R}_{t-2},
\ldots
\right).
}
\end{equation}
```

##### Estimation Error

The covariance matrix contains

``` math
\begin{equation}
\frac{
N_t(N_t+1)
}{
2
}
\end{equation}
```

distinct parameters.

Therefore, estimation becomes difficult when the number of securities is large relative to the number of historical observations.

For example,

``` math
\begin{equation}
N_t=500
\end{equation}
```

requires estimating

``` math
\begin{equation}
\frac{500\times501}{2}
=
125{,}250
\end{equation}
```

distinct covariance elements.

This is one of the principal reasons why naive historical covariance matrices can be unstable in large equity universes.

##### Singularity

Let

``` math
\begin{equation}
\mathbf{X}
\in
\mathbb{R}^{L\times N_t}
\end{equation}
```

denote the centered historical return matrix.

The sample covariance is proportional to

``` math
\begin{equation}
\mathbf{X}^\top\mathbf{X}.
\end{equation}
```

Its rank satisfies

``` math
\begin{equation}
\operatorname{rank}
\left(
\widehat{\boldsymbol{\Sigma}}
\right)
\leq
\min
\left(
N_t,L-1
\right).
\end{equation}
```

Consequently, if

``` math
\begin{equation}
N_t>L-1,
\end{equation}
```

then

``` math
\begin{equation}
\boxed{
\widehat{\boldsymbol{\Sigma}}
\text{ is necessarily singular}.
}
\end{equation}
```

This is a major practical limitation for portfolio optimization.

##### Rolling vs. Expanding Estimation

A rolling estimator uses only the most recent $`L`$ observations:

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t
=
g
\left(
\mathbf{R}_{t-L+1},
\ldots,
\mathbf{R}_{t}
\right).
\end{equation}
```

An expanding estimator uses the complete history up to $`t`$.

The same trade-off encountered in predictive modeling applies:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Longer History}
&\rightarrow
\text{Lower Sampling Noise, Slower Adaptation},
\\
\text{Shorter History}
&\rightarrow
\text{Higher Sampling Noise, Faster Adaptation}.
\end{aligned}
}
\end{equation}
```

##### Exponentially Weighted Covariance

Recent observations may be assigned larger weights.

Let

``` math
\begin{equation}
0<\lambda<1
\end{equation}
```

denote the decay parameter.

Normalized historical weights may be defined as

``` math
\begin{equation}
\omega_\ell
=
\frac{
(1-\lambda)\lambda^\ell
}{
1-\lambda^L
},
\qquad
\ell=0,\ldots,L-1.
\end{equation}
```

Then

``` math
\begin{equation}
\sum_{\ell=0}^{L-1}
\omega_\ell
=
1.
\end{equation}
```

The exponentially weighted covariance estimator is

``` math
\begin{equation}
\boxed{
\widehat{\boldsymbol{\Sigma}}_t^{EW}
=
\sum_{\ell=0}^{L-1}
\omega_\ell
\left(
\mathbf{R}_{t-\ell}
-
\boldsymbol{\mu}_{t}^{EW}
\right)
\left(
\mathbf{R}_{t-\ell}
-
\boldsymbol{\mu}_{t}^{EW}
\right)^\top,
}
\end{equation}
```

where

``` math
\begin{equation}
\boldsymbol{\mu}_{t}^{EW}
=
\sum_{\ell=0}^{L-1}
\omega_\ell
\mathbf{R}_{t-\ell}.
\end{equation}
```

This allows the covariance estimate to react more quickly to changing market conditions.

#### Shrinkage Estimators

Sample covariance matrices can be noisy, particularly when

``` math
\begin{equation}
N_t
\end{equation}
```

is large relative to

``` math
\begin{equation}
L.
\end{equation}
```

Shrinkage reduces estimation error by combining the sample covariance matrix with a more structured target matrix.

Let

``` math
\begin{equation}
\mathbf{S}_t
=
\widehat{\boldsymbol{\Sigma}}_t^{\mathrm{sample}}
\end{equation}
```

denote the sample covariance matrix and let

``` math
\begin{equation}
\mathbf{F}_t
\end{equation}
```

denote a structured target.

A general shrinkage estimator is

``` math
\begin{equation}
\boxed{
\widehat{\boldsymbol{\Sigma}}_t^{\mathrm{shrunk}}
=
(1-\delta_t)
\mathbf{S}_t
+
\delta_t
\mathbf{F}_t,
}
\end{equation}
```

where

``` math
\begin{equation}
0\leq\delta_t\leq1.
\end{equation}
```

##### Interpretation of the Shrinkage Intensity

If

``` math
\begin{equation}
\delta_t=0,
\end{equation}
```

then

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t^{\mathrm{shrunk}}
=
\mathbf{S}_t.
\end{equation}
```

If

``` math
\begin{equation}
\delta_t=1,
\end{equation}
```

then

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t^{\mathrm{shrunk}}
=
\mathbf{F}_t.
\end{equation}
```

Intermediate values trade off sample-specific information against structural stability.

##### Possible Shrinkage Targets

Possible targets include:

- diagonal covariance matrices;

- constant-correlation models;

- single-factor market models;

- multi-factor risk models.

For example, a diagonal target is

``` math
\begin{equation}
\boxed{
\mathbf{F}_t
=
\operatorname{diag}
\left(
\widehat{\sigma}_{1,t}^{2},
\ldots,
\widehat{\sigma}_{N_t,t}^{2}
\right).
}
\end{equation}
```

This retains estimated individual variances while shrinking all pairwise covariances toward zero.

##### Why Shrinkage Can Improve Portfolio Construction

Portfolio optimization frequently depends on

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t^{-1}.
\end{equation}
```

Small estimation errors in covariance eigenvalues can become greatly amplified through matrix inversion.

Shrinkage typically reduces extreme estimated eigenvalues and improves conditioning.

Thus,

``` math
\begin{equation}
\boxed{
\text{Slightly Biased Risk Estimate}
\quad\text{may be preferable to}\quad
\text{Highly Noisy Unbiased Estimate}.
}
\end{equation}
```

#### Factor Risk Models

A factor risk model reduces the dimensionality of the covariance-estimation problem by assuming that security returns are driven by a smaller number of systematic factors plus security-specific residuals.

Let

``` math
\begin{equation}
K
\ll
N_t
\end{equation}
```

denote the number of risk factors.

For security $`i`$,

``` math
\begin{equation}
\boxed{
R_{i,t}
=
\mathbf{b}_{i,t}^{\top}
\mathbf{f}_t
+
\varepsilon_{i,t},
}
\end{equation}
```

where

``` math
\begin{equation}
\mathbf{b}_{i,t}
\in
\mathbb{R}^{K}
\end{equation}
```

is the vector of factor exposures and

``` math
\begin{equation}
\mathbf{f}_t
\in
\mathbb{R}^{K}
\end{equation}
```

is the vector of factor returns.

Across all securities,

``` math
\begin{equation}
\boxed{
\mathbf{R}_t
=
\mathbf{B}_t
\mathbf{f}_t
+
\boldsymbol{\varepsilon}_t,
}
\end{equation}
```

with

``` math
\begin{equation}
\mathbf{B}_t
\in
\mathbb{R}^{N_t\times K}.
\end{equation}
```

##### Factor Covariance Matrix

Let

``` math
\begin{equation}
\boldsymbol{\Omega}_t
=
\operatorname{Cov}_t
\left(
\mathbf{f}_{t+1}
\right)
\in
\mathbb{R}^{K\times K}
\end{equation}
```

denote the factor covariance matrix.

Let

``` math
\begin{equation}
\mathbf{D}_t
=
\operatorname{Cov}_t
\left(
\boldsymbol{\varepsilon}_{t+1}
\right)
\in
\mathbb{R}^{N_t\times N_t}.
\end{equation}
```

Under the common assumption that specific returns are mutually uncorrelated,

``` math
\begin{equation}
\boxed{
\mathbf{D}_t
=
\operatorname{diag}
\left(
\sigma_{\varepsilon,1,t}^{2},
\ldots,
\sigma_{\varepsilon,N_t,t}^{2}
\right).
}
\end{equation}
```

The asset covariance matrix becomes

``` math
\begin{equation}
\boxed{
\boldsymbol{\Sigma}_t
=
\mathbf{B}_t
\boldsymbol{\Omega}_t
\mathbf{B}_t^\top
+
\mathbf{D}_t.
}
\end{equation}
```

##### Dimensionality Reduction

The factor model replaces direct estimation of approximately

``` math
\begin{equation}
\frac{N_t(N_t+1)}{2}
\end{equation}
```

asset-covariance parameters with estimation of:

- $`N_tK`$ factor exposures;

- $`K(K+1)/2`$ factor covariances;

- $`N_t`$ specific variances.

When

``` math
\begin{equation}
K\ll N_t,
\end{equation}
```

this imposes substantial structure on the risk model.

##### Types of Risk Factors

Risk factors may be:

- statistical factors, such as principal components;

- macroeconomic factors;

- market and country factors;

- industry factors;

- style factors such as size, value, momentum, or volatility.

The choice of risk factors need not coincide with the factors used to construct the alpha signal.

#### Systematic and Specific Risk

The factor model provides a natural decomposition of portfolio risk.

For portfolio weights

``` math
\begin{equation}
\mathbf{w}_t
\in
\mathbb{R}^{N_t},
\end{equation}
```

portfolio factor exposure is

``` math
\begin{equation}
\boxed{
\mathbf{b}_{p,t}
=
\mathbf{B}_t^\top
\mathbf{w}_t
\in
\mathbb{R}^{K}.
}
\end{equation}
```

Using

``` math
\begin{equation}
\boldsymbol{\Sigma}_t
=
\mathbf{B}_t
\boldsymbol{\Omega}_t
\mathbf{B}_t^\top
+
\mathbf{D}_t,
\end{equation}
```

portfolio variance becomes

``` math
\begin{equation}
\sigma_{p,t}^{2}
=
\mathbf{w}_t^\top
\mathbf{B}_t
\boldsymbol{\Omega}_t
\mathbf{B}_t^\top
\mathbf{w}_t
+
\mathbf{w}_t^\top
\mathbf{D}_t
\mathbf{w}_t.
\end{equation}
```

Since

``` math
\begin{equation}
\mathbf{b}_{p,t}
=
\mathbf{B}_t^\top\mathbf{w}_t,
\end{equation}
```

we obtain

``` math
\begin{equation}
\boxed{
\sigma_{p,t}^{2}
=
\underbrace{
\mathbf{b}_{p,t}^{\top}
\boldsymbol{\Omega}_t
\mathbf{b}_{p,t}
}_{\text{systematic variance}}
+
\underbrace{
\mathbf{w}_t^\top
\mathbf{D}_t
\mathbf{w}_t
}_{\text{specific variance}}.
}
\end{equation}
```

##### Systematic Risk

Systematic risk results from portfolio exposure to common factors:

``` math
\begin{equation}
\boxed{
\sigma_{p,t,\mathrm{sys}}^{2}
=
\mathbf{b}_{p,t}^{\top}
\boldsymbol{\Omega}_t
\mathbf{b}_{p,t}.
}
\end{equation}
```

It cannot generally be eliminated merely by increasing the number of securities while maintaining the same factor exposures.

##### Specific Risk

Specific risk is

``` math
\begin{equation}
\boxed{
\sigma_{p,t,\mathrm{spec}}^{2}
=
\mathbf{w}_t^\top
\mathbf{D}_t
\mathbf{w}_t.
}
\end{equation}
```

If specific returns are independent and positions are sufficiently diversified, this component can decrease substantially as the number of holdings increases.

##### Portfolio Risk Decomposition

Thus,

``` math
\begin{equation}
\boxed{
\text{Total Portfolio Risk}
=
\text{Systematic Risk}
+
\text{Specific Risk}
}
\end{equation}
```

when expressed in variance terms under the factor-model assumptions.

The corresponding volatilities are not additive:

``` math
\begin{equation}
\sigma_{p,t}
\neq
\sigma_{p,t,\mathrm{sys}}
+
\sigma_{p,t,\mathrm{spec}}.
\end{equation}
```

Instead,

``` math
\begin{equation}
\boxed{
\sigma_{p,t}
=
\sqrt{
\sigma_{p,t,\mathrm{sys}}^{2}
+
\sigma_{p,t,\mathrm{spec}}^{2}
}.
}
\end{equation}
```

#### Beta Estimation

Market beta is one of the most common security-level risk exposures.

For security $`i`$, consider

``` math
\begin{equation}
\boxed{
R_{i,\tau}^{e}
=
\alpha_{i,t}
+
\beta_{i,t}
R_{M,\tau}^{e}
+
\varepsilon_{i,\tau},
}
\end{equation}
```

estimated over a historical window

``` math
\begin{equation}
\tau
\in
\mathcal{W}_t.
\end{equation}
```

Here:

- $`R_{i,\tau}^{e}`$ is the security excess return;

- $`R_{M,\tau}^{e}`$ is the market excess return;

- $`\beta_{i,t}`$ is the estimated market exposure at decision date $`t`$.

##### Covariance Representation

For a single-factor regression with an intercept, the population beta is

``` math
\begin{equation}
\boxed{
\beta_{i,t}
=
\frac{
\operatorname{Cov}_t
\left(
R_i^{e},
R_M^{e}
\right)
}{
\operatorname{Var}_t
\left(
R_M^{e}
\right)
}.
}
\end{equation}
```

The sample estimator is

``` math
\begin{equation}
\widehat{\beta}_{i,t}
=
\frac{
\widehat{\operatorname{Cov}}_t
\left(
R_i^{e},
R_M^{e}
\right)
}{
\widehat{\operatorname{Var}}_t
\left(
R_M^{e}
\right)
}.
\end{equation}
```

##### Portfolio Beta

For a linear portfolio,

``` math
\begin{equation}
R_{p,t}
=
\sum_i
w_{i,t}
R_{i,t},
\end{equation}
```

portfolio beta is

``` math
\begin{equation}
\boxed{
\beta_{p,t}
=
\sum_{i=1}^{N_t}
w_{i,t}
\beta_{i,t}.
}
\end{equation}
```

In vector notation,

``` math
\begin{equation}
\boxed{
\beta_{p,t}
=
\boldsymbol{\beta}_t^\top
\mathbf{w}_t,
}
\end{equation}
```

where

``` math
\begin{equation}
\boldsymbol{\beta}_t
=
\begin{bmatrix}
\beta_{1,t}\\
\vdots\\
\beta_{N_t,t}
\end{bmatrix}
\in
\mathbb{R}^{N_t}.
\end{equation}
```

##### Rolling Beta

A rolling beta estimate may use the most recent $`L`$ returns:

``` math
\begin{equation}
\widehat{\beta}_{i,t}^{(L)}
=
\frac{
\widehat{\operatorname{Cov}}
\left(
R_{i,t-L+1:t},
R_{M,t-L+1:t}
\right)
}{
\widehat{\operatorname{Var}}
\left(
R_{M,t-L+1:t}
\right)
}.
\end{equation}
```

A shorter lookback adapts more quickly but produces noisier estimates.

A longer lookback is more stable but may react slowly to structural changes in the security’s market exposure.

##### Exponentially Weighted Beta

Historical observations may receive exponentially decaying weights.

A weighted beta estimator can be represented as

``` math
\begin{equation}
\boxed{
\widehat{\beta}_{i,t}^{EW}
=
\frac{
\widehat{\operatorname{Cov}}_{EW,t}
\left(
R_i,R_M
\right)
}{
\widehat{\operatorname{Var}}_{EW,t}
\left(
R_M
\right)
}.
}
\end{equation}
```

This gives more importance to recent comovements.

##### Point-in-Time Beta

The beta used for portfolio construction must be estimated entirely from historical observations available at the decision time.

Thus,

``` math
\begin{equation}
\boxed{
\widehat{\beta}_{i,t}
\in
\mathcal{I}_t.
}
\end{equation}
```

Using future returns when estimating historical betas would directly introduce look-ahead bias.

#### Factor Exposure Estimation

In a multi-factor risk model, each security has factor exposure vector

``` math
\begin{equation}
\boxed{
\mathbf{b}_{i,t}
=
\begin{bmatrix}
b_{i,t}^{(1)}
\\
\vdots\\
b_{i,t}^{(K)}
\end{bmatrix}
\in
\mathbb{R}^{K}.
}
\end{equation}
```

The exposure matrix is

``` math
\begin{equation}
\boxed{
\mathbf{B}_t
=
\begin{bmatrix}
(\mathbf{b}_{1,t})^\top\\
\vdots\\
(\mathbf{b}_{N_t,t})^\top
\end{bmatrix}
\in
\mathbb{R}^{N_t\times K}.
}
\end{equation}
```

Factor exposures can be estimated or directly observed depending on the type of factor.

##### Time-Series Estimated Exposures

For traded or return-based factors,

``` math
\begin{equation}
R_{i,\tau}
=
\alpha_i
+
\mathbf{b}_{i,t}^\top
\mathbf{f}_\tau
+
\varepsilon_{i,\tau}.
\end{equation}
```

Given a historical factor-return matrix

``` math
\begin{equation}
\mathbf{F}
\in
\mathbb{R}^{L\times K},
\end{equation}
```

the OLS estimator is

``` math
\begin{equation}
\boxed{
\widehat{\mathbf{b}}_{i,t}
=
\left(
\mathbf{F}^\top
\mathbf{F}
\right)^{-1}
\mathbf{F}^\top
\mathbf{r}_i,
}
\end{equation}
```

after appropriate treatment of the intercept.

##### Observed Exposures

Some risk factors are based directly on observable security characteristics.

Examples include:

- industry membership;

- country membership;

- log market capitalization;

- leverage;

- liquidity;

- volatility.

These exposures may be transformed or standardized cross-sectionally before entering the risk model.

##### Portfolio Factor Exposures

For weights

``` math
\begin{equation}
\mathbf{w}_t
\in
\mathbb{R}^{N_t},
\end{equation}
```

portfolio exposures are

``` math
\begin{equation}
\boxed{
\mathbf{b}_{p,t}
=
\mathbf{B}_t^\top
\mathbf{w}_t
\in
\mathbb{R}^{K}.
}
\end{equation}
```

The $`k`$-th component is

``` math
\begin{equation}
b_{p,t}^{(k)}
=
\sum_{i=1}^{N_t}
w_{i,t}
b_{i,t}^{(k)}.
\end{equation}
```

This linear aggregation will later allow the portfolio optimizer to impose factor-exposure constraints directly.

#### Volatility Forecasting

Historical volatility is not necessarily the same as expected future volatility.

Portfolio construction requires an estimate

``` math
\begin{equation}
\widehat{\sigma}_{i,t}
\end{equation}
```

or

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t
\end{equation}
```

that is intended to describe risk over the future portfolio holding period.

##### Rolling Historical Volatility

For daily returns and lookback window $`L`$,

``` math
\begin{equation}
\widehat{\sigma}_{i,t}^{\mathrm{daily}}
=
\sqrt{
\frac{1}{L-1}
\sum_{\ell=1}^{L}
\left(
R_{i,t-\ell}
-
\bar{R}_{i,t}
\right)^2
}.
\end{equation}
```

Assuming $`F`$ observations per year, annualized volatility is

``` math
\begin{equation}
\boxed{
\widehat{\sigma}_{i,t}^{\mathrm{ann}}
=
\sqrt{F}
\,
\widehat{\sigma}_{i,t}^{\mathrm{daily}}.
}
\end{equation}
```

For daily data, one commonly uses

``` math
\begin{equation}
F\approx252.
\end{equation}
```

##### Exponentially Weighted Volatility

An exponentially weighted variance can be defined recursively as

``` math
\begin{equation}
\boxed{
\widehat{\sigma}_{i,t}^{2}
=
\lambda
\widehat{\sigma}_{i,t-1}^{2}
+
(1-\lambda)
R_{i,t-1}^{2},
}
\end{equation}
```

when returns are treated as approximately mean zero over the relevant horizon.

Here,

``` math
\begin{equation}
0<\lambda<1.
\end{equation}
```

A smaller $`\lambda`$ gives more weight to recent observations and produces a more reactive volatility estimate.

##### Half-Life

The decay parameter may alternatively be expressed through a half-life $`H`$:

``` math
\begin{equation}
\boxed{
\lambda
=
2^{-1/H}.
}
\end{equation}
```

After $`H`$ periods, the relative weight assigned to an observation falls by one half.

##### Conditional Volatility Models

More sophisticated models explicitly model time-varying conditional variance.

For example, a GARCH$`(1,1)`$ model is

``` math
\begin{equation}
\boxed{
\sigma_{i,t}^{2}
=
\omega
+
\alpha
\varepsilon_{i,t-1}^{2}
+
\beta
\sigma_{i,t-1}^{2},
}
\end{equation}
```

where

``` math
\begin{equation}
\omega>0,
\qquad
\alpha\geq0,
\qquad
\beta\geq0.
\end{equation}
```

Such models capture volatility clustering by allowing large recent shocks to increase the forecast of future risk.

##### Forecast Horizon

Risk estimates should match the relevant portfolio horizon.

If daily covariance is estimated as

``` math
\begin{equation}
\boldsymbol{\Sigma}_t^{(1d)},
\end{equation}
```

then under an independent and identically distributed approximation, an $`h`$-day covariance could be approximated by

``` math
\begin{equation}
\boxed{
\boldsymbol{\Sigma}_t^{(h)}
\approx
h
\boldsymbol{\Sigma}_t^{(1d)}.
}
\end{equation}
```

Corresponding volatility scales as

``` math
\begin{equation}
\boxed{
\sigma_t^{(h)}
\approx
\sqrt{h}
\sigma_t^{(1d)}.
}
\end{equation}
```

These square-root-of-time relations rely on strong assumptions and may fail in the presence of serial correlation or time-varying volatility.

##### Forecast Risk vs. Realized Risk

A crucial distinction is

``` math
\begin{equation}
\boxed{
\widehat{\sigma}_{p,t}
\neq
\sigma_{p,t}^{\mathrm{realized}}.
}
\end{equation}
```

The first is an ex-ante forecast available when the portfolio is constructed.

The second is an ex-post quantity observed after returns have occurred.

The accuracy of the risk model can later be evaluated by comparing predicted and realized risk.

##### Risk Model Output

At the end of the risk-model stage, the backtester should provide at least

``` math
\begin{equation}
\boxed{
\widehat{\boldsymbol{\Sigma}}_t
\in
\mathbb{R}^{N_t\times N_t}.
}
\end{equation}
```

If a factor model is used, the underlying components should also be retained:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{B}_t
&\in
\mathbb{R}^{N_t\times K},
\\
\widehat{\boldsymbol{\Omega}}_t
&\in
\mathbb{R}^{K\times K},
\\
\widehat{\mathbf{D}}_t
&\in
\mathbb{R}^{N_t\times N_t},
\\
\widehat{\boldsymbol{\Sigma}}_t
&=
\mathbf{B}_t
\widehat{\boldsymbol{\Omega}}_t
\mathbf{B}_t^\top
+
\widehat{\mathbf{D}}_t.
\end{aligned}
}
\end{equation}
```

The portfolio-construction engine now has two central objects:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{s}_t^{\mathrm{final}}
&\in
\mathbb{R}^{N_t},
&&
\text{expected attractiveness},
\\
\widehat{\boldsymbol{\Sigma}}_t
&\in
\mathbb{R}^{N_t\times N_t},
&&
\text{expected risk}.
\end{aligned}
}
\end{equation}
```

These objects provide the core inputs for the optimization problems developed in the following sections:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Final Signal}
\;(\mathbf{s}_t^{\mathrm{final}})
&+
\text{Risk Model}
\;(\widehat{\boldsymbol{\Sigma}}_t)
\\
&\rightarrow
\text{Portfolio Optimization}
\\
&\rightarrow
\mathbf{w}_t^{\mathrm{target}}.
\end{aligned}
}
\end{equation}
```

