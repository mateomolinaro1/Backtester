### Performance Attribution

Performance attribution goes beyond evaluating whether the strategy performed well.

Its purpose is to identify the economic sources of realized P&L.

Attribution can be performed along several dimensions:

``` math
\begin{equation}
\boxed{
\text{Portfolio P\&L}
\rightarrow
\begin{cases}
\text{Long / Short},\\
\text{Security},\\
\text{Sector / Country},\\
\text{Factor},\\
\text{Signal / Model},\\
\text{Beta / Pure Alpha},\\
\text{Implementation Costs}.
\end{cases}
}
\end{equation}
```

Different attribution schemes answer different questions and need not be mutually exclusive.

#### Attribution Framework

For a linear holdings-based attribution, the gross portfolio return can be written as

``` math
\begin{equation}
\boxed{
R_{p,t}^{\mathrm{gross}}
=
\sum_{i=1}^{N_t}
w_{i,t-1}^{\mathrm{implemented}}
R_{i,t},
}
\end{equation}
```

under the corresponding timing convention.

Define the security contribution

``` math
\begin{equation}
\boxed{
C_{i,t}
=
w_{i,t-1}^{\mathrm{implemented}}
R_{i,t}.
}
\end{equation}
```

Then

``` math
\begin{equation}
\boxed{
R_{p,t}^{\mathrm{gross}}
=
\sum_{i=1}^{N_t}
C_{i,t}.
}
\end{equation}
```

This simple additive identity forms the basis of many holdings-based attribution methods.

#### Long vs. Short Attribution

Partition the universe into long and short positions:

``` math
\begin{equation}
\mathcal{L}_t
=
\left\{
i:w_{i,t}>0
\right\},
\end{equation}
```

``` math
\begin{equation}
\mathcal{S}_t
=
\left\{
i:w_{i,t}<0
\right\}.
\end{equation}
```

The long contribution is

``` math
\begin{equation}
\boxed{
R_{L,t}
=
\sum_{i\in\mathcal{L}_t}
w_{i,t}R_{i,t},
}
\end{equation}
```

while the short contribution is

``` math
\begin{equation}
\boxed{
R_{S,t}
=
\sum_{i\in\mathcal{S}_t}
w_{i,t}R_{i,t}.
}
\end{equation}
```

Since short weights are negative, profitable short positions generate positive contributions when the corresponding securities decline.

Thus,

``` math
\begin{equation}
\boxed{
R_{p,t}^{\mathrm{gross}}
=
R_{L,t}
+
R_{S,t}.
}
\end{equation}
```

This decomposition helps determine whether performance is driven predominantly by long selection, short selection, or both.

#### Security-Level Attribution

Security-level contribution is

``` math
\begin{equation}
\boxed{
C_{i,t}
=
w_{i,t}R_{i,t}.
}
\end{equation}
```

Over a single period,

``` math
\begin{equation}
R_{p,t}
=
\sum_i C_{i,t}.
\end{equation}
```

Security contributions can be aggregated through time to identify persistent contributors and detractors.

For multi-period attribution, simple summation of percentage contributions does not in general reproduce compounded total return exactly. An appropriate multi-period linking methodology should therefore be used when exact cumulative attribution is required.

#### Sector and Industry Attribution

Let

``` math
\begin{equation}
\mathcal{I}_{g,t}
\end{equation}
```

denote the set of securities belonging to industry or sector $`g`$.

The sector contribution is

``` math
\begin{equation}
\boxed{
C_{g,t}^{\mathrm{sector}}
=
\sum_{i\in\mathcal{I}_{g,t}}
C_{i,t}.
}
\end{equation}
```

Therefore,

``` math
\begin{equation}
\boxed{
R_{p,t}^{\mathrm{gross}}
=
\sum_g
C_{g,t}^{\mathrm{sector}}.
}
\end{equation}
```

This decomposition can reveal whether an apparently diversified strategy derives a disproportionate fraction of its realized P&L from a small number of industries.

#### Country Attribution

Let

``` math
\begin{equation}
\mathcal{C}_{c,t}
\end{equation}
```

denote the set of securities assigned to country $`c`$.

Country-level contribution is

``` math
\begin{equation}
\boxed{
C_{c,t}^{\mathrm{country}}
=
\sum_{i\in\mathcal{C}_{c,t}}
C_{i,t}.
}
\end{equation}
```

The portfolio return can then be decomposed as

``` math
\begin{equation}
R_{p,t}^{\mathrm{gross}}
=
\sum_c
C_{c,t}^{\mathrm{country}}.
\end{equation}
```

For international portfolios, the interpretation should be consistent with the currency-conversion convention used in the backtest.

#### Factor Attribution

Suppose realized portfolio returns satisfy the factor representation

``` math
\begin{equation}
R_{p,t}-R_{f,t}
=
\alpha_p
+
\boldsymbol{\beta}_p^\top
\mathbf{F}_t
+
\varepsilon_t.
\end{equation}
```

The systematic factor component is

``` math
\begin{equation}
\boxed{
R_{p,t}^{\mathrm{factor}}
=
\boldsymbol{\beta}_p^\top
\mathbf{F}_t
=
\sum_{k=1}^{K}
\beta_{p,k}F_{k,t}.
}
\end{equation}
```

The contribution of factor $`k`$ is therefore

``` math
\begin{equation}
\boxed{
C_{k,t}^{\mathrm{factor}}
=
\beta_{p,k}F_{k,t}.
}
\end{equation}
```

This provides a return-based factor attribution.

A holdings-based risk-model attribution may instead use time-varying portfolio exposures

``` math
\begin{equation}
\mathbf{b}_{p,t}
=
\mathbf{B}_t^\top\mathbf{w}_t
\end{equation}
```

and corresponding factor returns.

The chosen attribution methodology should therefore be stated explicitly.

#### Signal Attribution

Suppose the final signal is constructed from $`K`$ component signals:

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{final}}
=
\sum_{k=1}^{K}
a_{k,t}
\mathbf{s}_{k,t}.
\end{equation}
```

It is often desirable to determine how much portfolio performance is associated with each component signal.

A simple diagnostic is to construct standalone portfolios

``` math
\begin{equation}
\mathbf{w}_{k,t}
=
\mathcal{G}
\left(
\mathbf{s}_{k,t}
\right)
\end{equation}
```

and evaluate their corresponding returns

``` math
\begin{equation}
R_{k,t}
=
\mathbf{w}_{k,t}^\top
\mathbf{R}_{t+1}.
\end{equation}
```

This provides a useful measure of standalone signal performance.

However,

``` math
\begin{equation}
\boxed{
R_{p,t}
\neq
\sum_{k=1}^{K}
a_{k,t}R_{k,t}
}
\end{equation}
```

in general when the portfolio-construction operator $`\mathcal{G}`$ is nonlinear or when optimization, constraints, clipping, transaction costs, or interactions between signals affect the final portfolio.

Therefore, standalone signal backtests should not automatically be interpreted as an exact additive attribution of the final portfolio.

Exact signal attribution requires a methodology consistent with the actual signal-combination and portfolio-construction process.

#### Model Attribution

For model-based strategies, attribution can be extended to the predictive model itself.

Suppose

``` math
\begin{equation}
\widehat{\boldsymbol{\mu}}_t
=
f_{\widehat{\theta}_t}
\left(
\mathbf{X}_t
\right),
\end{equation}
```

where $`\mathbf{X}_t`$ denotes model inputs and $`f_{\widehat{\theta}_t}(\cdot)`$ the fitted prediction function.

Model attribution may investigate:

- performance by model;

- performance by feature group;

- performance by prediction bucket;

- performance by confidence level;

- performance across market regimes;

- marginal performance from adding or removing model components.

For linear models,

``` math
\begin{equation}
\widehat{\mu}_{i,t}
=
\widehat{\beta}_{0,t}
+
\sum_{k=1}^{K}
X_{i,k,t}
\widehat{\beta}_{k,t},
\end{equation}
```

so the prediction itself admits an additive decomposition.

For nonlinear machine-learning or deep-learning models, feature attribution may require model-specific methods.

Importantly, prediction attribution and portfolio-return attribution are different objects.

A feature may contribute strongly to a model prediction without generating an equally large realized portfolio P&L contribution after portfolio construction.

#### Beta vs. Pure Alpha

For strategies intended to generate stock-selection alpha, it is useful to separate realized performance associated with market exposure from residual performance.

Under a simple market model,

``` math
\begin{equation}
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
\end{equation}
```

The market-related component is

``` math
\begin{equation}
\boxed{
R_{p,t}^{\beta}
=
\widehat{\beta}_p
\left(
R_{m,t}-R_{f,t}
\right),
}
\end{equation}
```

while the residual component is

``` math
\begin{equation}
\boxed{
R_{p,t}^{\mathrm{res}}
=
R_{p,t}-R_{f,t}
-
R_{p,t}^{\beta}.
}
\end{equation}
```

More generally, with time-varying portfolio beta,

``` math
\begin{equation}
\boxed{
R_{p,t}^{\beta}
=
\beta_{p,t-1}
R_{m,t},
}
\end{equation}
```

under the appropriate timing and return convention.

The residual return can then be interpreted as the portion of realized performance not mechanically explained by the modeled market exposure.

This decomposition is particularly informative when comparing long-only, long–short, and beta-neutral versions of the same underlying alpha signal.

#### Gross Alpha vs. Implementation Costs

A strategy may generate economically meaningful gross alpha while losing a substantial fraction of that alpha through implementation.

The basic decomposition is

``` math
\begin{equation}
\boxed{
R_{p,t}^{\mathrm{net}}
=
R_{p,t}^{\mathrm{gross}}
-
TC_t
-
FC_t
-
BC_t.
}
\end{equation}
```

Over an evaluation sample, one may compare

``` math
\begin{equation}
\boxed{
\text{Gross Alpha}
\quad\text{vs.}\quad
\text{Implementation Drag}
\quad\text{vs.}\quad
\text{Net Alpha}.
}
\end{equation}
```

This decomposition is particularly important when comparing signals with different turnover, liquidity, or shorting requirements.

#### Transaction Cost Attribution

Using the cost decomposition developed previously,

``` math
\begin{equation}
TC_t
=
TC_t^{\mathrm{fees}}
+
TC_t^{\mathrm{spread}}
+
TC_t^{\mathrm{slippage}}
+
TC_t^{\mathrm{impact}}.
\end{equation}
```

The implementation drag attributable to trading can therefore be decomposed as

``` math
\begin{equation}
\boxed{
TC_t
=
\underbrace{TC_t^{\mathrm{fees}}}_{\text{explicit fees}}
+
\underbrace{TC_t^{\mathrm{spread}}}_{\text{spread}}
+
\underbrace{TC_t^{\mathrm{slippage}}}_{\text{slippage}}
+
\underbrace{TC_t^{\mathrm{impact}}}_{\text{market impact}}.
}
\end{equation}
```

Costs can additionally be aggregated by:

- security;

- sector;

- country;

- rebalance date;

- long and short legs;

- signal or strategy sleeve.

This identifies which parts of the strategy consume the largest fraction of gross alpha.

#### Financing and Borrowing Cost Attribution

Holding-related costs should be separated from transaction costs.

Let

``` math
\begin{equation}
FC_t
\end{equation}
```

denote financing costs and

``` math
\begin{equation}
BC_t
\end{equation}
```

denote short-borrowing costs.

Total holding-cost drag is

``` math
\begin{equation}
\boxed{
HC_t
=
FC_t
+
BC_t.
}
\end{equation}
```

For a short portfolio, borrow-cost attribution can be performed security by security:

``` math
\begin{equation}
\boxed{
BC_t
=
\sum_{i\in\mathcal{S}_t}
BC_{i,t}.
}
\end{equation}
```

This is particularly important because securities with strong predicted alpha may simultaneously be expensive or difficult to borrow.

The economically relevant contribution of a short position is therefore not only its gross price return but its return after the cost of maintaining the position.

At the highest level, realized net strategy performance can finally be viewed as

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Net Strategy Performance}
&=
\text{Systematic Return Contribution}
\\
&\quad+
\text{Security-Selection / Pure Alpha Contribution}
\\
&\quad-
\text{Transaction-Cost Drag}
\\
&\quad-
\text{Financing and Borrowing Drag}.
\end{aligned}
}
\end{equation}
```

This final decomposition closes the backtesting pipeline.

Starting from raw point-in-time financial data, the framework has successively constructed cleaned firm-level characteristics, transformed them into signals, neutralized unwanted exposures, mapped those signals into portfolio positions, controlled portfolio risk and constraints, simulated implementation, and ultimately decomposed the resulting realized performance into its economic sources.

# Validation, Robustness, and Production

