### Benchmark and Factor-Adjusted Performance

Absolute portfolio performance does not reveal whether returns result from genuine alpha or compensation for systematic risk exposures.

The strategy should therefore also be evaluated relative to an appropriate benchmark and, where relevant, a set of systematic risk factors.

#### Benchmark Excess Returns

Let

``` math
\begin{equation}
R_{b,t}
\end{equation}
```

denote the benchmark return.

The active return is

``` math
\begin{equation}
\boxed{
R_{p,t}^{\mathrm{active}}
=
R_{p,t}
-
R_{b,t}.
}
\end{equation}
```

The average active return is

``` math
\begin{equation}
\overline{R^{\mathrm{active}}}
=
\frac{1}{T}
\sum_{t=1}^{T}
\left(
R_{p,t}-R_{b,t}
\right).
\end{equation}
```

The choice of benchmark should reflect the economic mandate of the portfolio.

For a long-only equity strategy, a broad equity index may be appropriate.

For a market-neutral Pure Alpha strategy, benchmark-relative performance may be less informative than absolute return and factor-adjusted alpha.

#### Tracking Error

Tracking error is the volatility of active returns:

``` math
\begin{equation}
\boxed{
TE
=
\sqrt{A}
\,
\widehat{\sigma}
\left(
R_p-R_b
\right).
}
\end{equation}
```

Tracking error measures the variability of portfolio returns relative to the benchmark rather than the absolute volatility of the portfolio.

#### Information Ratio

The Information Ratio compares average active return with tracking error:

``` math
\begin{equation}
\boxed{
IR
=
\frac{
A\,
\overline{R_p-R_b}
}{
TE
}.
}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
\boxed{
IR
=
\sqrt{A}
\frac{
\overline{R_p-R_b}
}{
\widehat{\sigma}(R_p-R_b)
}.
}
\end{equation}
```

The Information Ratio is particularly relevant for benchmark-relative long-only portfolios.

#### CAPM Alpha and Beta

A first systematic-risk adjustment is provided by the CAPM regression:

``` math
\begin{equation}
\boxed{
R_{p,t}-R_{f,t}
=
\alpha_p
+
\beta_p
\left(
R_{m,t}-R_{f,t}
\right)
+
\varepsilon_t.
}
\end{equation}
```

Here,

``` math
\begin{equation}
\alpha_p
\end{equation}
```

is the periodic CAPM alpha,

``` math
\begin{equation}
\beta_p
\end{equation}
```

is the portfolio market beta, and

``` math
\begin{equation}
\varepsilon_t
\end{equation}
```

is the regression residual.

If the regression uses daily returns, annualized arithmetic alpha is commonly reported as

``` math
\begin{equation}
\boxed{
\alpha_p^{\mathrm{ann}}
\approx
252\alpha_p.
}
\end{equation}
```

More generally,

``` math
\begin{equation}
\alpha_p^{\mathrm{ann}}
\approx
A\alpha_p.
\end{equation}
```

The estimated beta provides an ex-post diagnostic of whether the realized portfolio behaved as intended with respect to market exposure.

#### Multifactor Regression

The CAPM framework can be generalized to $`K`$ systematic factors.

Let

``` math
\begin{equation}
\mathbf{F}_t
=
\begin{bmatrix}
F_{1,t}\\
\vdots\\
F_{K,t}
\end{bmatrix}
\in
\mathbb{R}^{K}
\end{equation}
```

denote factor returns.

The multifactor regression is

``` math
\begin{equation}
\boxed{
R_{p,t}-R_{f,t}
=
\alpha_p
+
\boldsymbol{\beta}_p^\top
\mathbf{F}_t
+
\varepsilon_t,
}
\end{equation}
```

where

``` math
\begin{equation}
\boldsymbol{\beta}_p
=
\begin{bmatrix}
\beta_{p,1}\\
\vdots\\
\beta_{p,K}
\end{bmatrix}
\in
\mathbb{R}^{K}.
\end{equation}
```

The factor set may include market, size, value, momentum, quality, low-risk, or other systematic return factors appropriate to the investment universe.

#### Style Factor Exposures

Two distinct notions of factor exposure should be distinguished.

First, holdings-based exposure can be computed from contemporaneous security factor exposures.

Let

``` math
\begin{equation}
\mathbf{B}_t
\in
\mathbb{R}^{N_t\times K}
\end{equation}
```

denote the security-level factor exposure matrix.

Portfolio exposure is

``` math
\begin{equation}
\boxed{
\mathbf{b}_{p,t}
=
\mathbf{B}_t^\top
\mathbf{w}_t.
}
\end{equation}
```

Second, realized return exposure can be estimated from the time-series regression

``` math
\begin{equation}
R_{p,t}
=
\alpha_p
+
\boldsymbol{\beta}_p^\top
\mathbf{F}_t
+
\varepsilon_t.
\end{equation}
```

These quantities answer related but different questions.

Holdings-based exposures describe the portfolio’s contemporaneous composition, whereas regression betas describe its realized historical co-movement with factor returns.

#### Factor-Adjusted Alpha

Under the multifactor model,

``` math
\begin{equation}
R_{p,t}-R_{f,t}
=
\alpha_p
+
\boldsymbol{\beta}_p^\top
\mathbf{F}_t
+
\varepsilon_t,
\end{equation}
```

the intercept

``` math
\begin{equation}
\boxed{
\alpha_p
}
\end{equation}
```

represents average portfolio performance unexplained by the included systematic factors.

This quantity should not automatically be interpreted as structural investment skill.

Its interpretation depends on:

- the factor model being sufficiently comprehensive;

- the stability of estimated factor exposures;

- the sample period;

- statistical estimation uncertainty;

- transaction costs and financing assumptions;

- the absence of backtest overfitting and data leakage.

The factor-adjusted return can also be represented period by period as

``` math
\begin{equation}
\boxed{
R_{p,t}^{\mathrm{factor\text{-}adjusted}}
=
R_{p,t}
-
\widehat{\boldsymbol{\beta}}_p^\top
\mathbf{F}_t.
}
\end{equation}
```

Its sample mean corresponds closely to the estimated regression alpha under the same regression specification.

