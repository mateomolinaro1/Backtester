### Portfolio-Level Risk Scaling

The portfolio optimization and constraint framework developed previously produces the target portfolio

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{target}}
=
\begin{bmatrix}
w_{1,t}^{\mathrm{target}}
\\
\vdots
\\
w_{N_t,t}^{\mathrm{target}}
\end{bmatrix}
\in
\mathbb{R}^{N_t}.
}
\end{equation}
```

These weights determine the desired relative allocation across securities after accounting for the signal, risk model, optimization objective, and portfolio constraints.

However, the risk of a portfolio constructed using the same methodology may vary substantially over time as security volatilities and correlations change.

An optional additional step therefore consists of scaling the entire portfolio to target a desired level of ex-ante volatility.

This operation is commonly referred to as *volatility targeting*, *volatility scaling*, or *isovol scaling*.

The general transformation is

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{target}}
\quad
\xrightarrow{\text{portfolio-level risk scaling}}
\quad
\mathbf{w}_t^{\mathrm{final}}.
}
\end{equation}
```

Importantly, volatility targeting is not required in every strategy.

Portfolio risk may instead be controlled directly inside the optimization problem through a risk constraint or an appropriate objective function. The separate scaling procedure developed in this section is useful when the portfolio-construction process determines a desired portfolio composition but the final amount of risk allocated to that portfolio is controlled separately.

#### Portfolio Direction and Portfolio Scale

It is useful to distinguish between the *direction* of a portfolio and its *scale*.

The target weight vector

``` math
\begin{equation}
\mathbf{w}_t^{\mathrm{target}}
\in
\mathbb{R}^{N_t}
\end{equation}
```

determines the relative positions across securities.

Consider a positive scalar

``` math
\begin{equation}
\lambda_t>0.
\end{equation}
```

Scaling the portfolio gives

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{scaled}}
=
\lambda_t
\mathbf{w}_t^{\mathrm{target}}.
}
\end{equation}
```

For every pair of securities $`i`$ and $`j`$ with non-zero weights,

``` math
\begin{equation}
\frac{
w_{i,t}^{\mathrm{scaled}}
}{
w_{j,t}^{\mathrm{scaled}}
}
=
\frac{
\lambda_t w_{i,t}^{\mathrm{target}}
}{
\lambda_t w_{j,t}^{\mathrm{target}}
}
=
\frac{
w_{i,t}^{\mathrm{target}}
}{
w_{j,t}^{\mathrm{target}}
}.
\end{equation}
```

Thus, common positive scaling does not change relative portfolio composition.

It changes the amount of capital exposure assigned to that composition.

Conceptually,

``` math
\begin{equation}
\boxed{
\underbrace{
\mathbf{w}_t^{\mathrm{target}}
}_{\text{portfolio composition}}
\quad+\quad
\underbrace{
\lambda_t
}_{\text{portfolio scale}}
\quad\longrightarrow\quad
\underbrace{
\mathbf{w}_t^{\mathrm{final}}
}_{\text{final risk-scaled portfolio}}.
}
\end{equation}
```

This distinction is particularly useful for long–short strategies. The portfolio-construction engine may determine which securities should be long or short and their relative importance, while a separate risk-scaling layer determines how aggressively the strategy should be deployed.

#### Volatility Targeting

Let

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t
\in
\mathbb{R}^{N_t\times N_t}
\end{equation}
```

denote the ex-ante covariance matrix available at time $`t`$.

The forecast volatility of the target portfolio is

``` math
\begin{equation}
\boxed{
\widehat{\sigma}_{p,t}
=
\sqrt{
\left(
\mathbf{w}_t^{\mathrm{target}}
\right)^\top
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}_t^{\mathrm{target}}
}.
}
\end{equation}
```

Let

``` math
\begin{equation}
\sigma^{\mathrm{target}}>0
\end{equation}
```

denote the desired portfolio volatility.

The isovol scaling coefficient is

``` math
\begin{equation}
\boxed{
\lambda_t^{\mathrm{vol}}
=
\frac{
\sigma^{\mathrm{target}}
}{
\widehat{\sigma}_{p,t}
}.
}
\end{equation}
```

The volatility-scaled portfolio is therefore

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{vol}}
=
\lambda_t^{\mathrm{vol}}
\mathbf{w}_t^{\mathrm{target}}.
}
\end{equation}
```

##### Why the Scaling Works

Portfolio variance after scaling is

``` math
\begin{equation}
\begin{aligned}
\widehat{\sigma}_{p,t}^{2,\mathrm{vol}}
&=
\left(
\lambda_t^{\mathrm{vol}}
\mathbf{w}_t^{\mathrm{target}}
\right)^\top
\widehat{\boldsymbol{\Sigma}}_t
\left(
\lambda_t^{\mathrm{vol}}
\mathbf{w}_t^{\mathrm{target}}
\right)
\\
&=
\left(
\lambda_t^{\mathrm{vol}}
\right)^2
\left(
\mathbf{w}_t^{\mathrm{target}}
\right)^\top
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}_t^{\mathrm{target}}
\\
&=
\left(
\lambda_t^{\mathrm{vol}}
\right)^2
\widehat{\sigma}_{p,t}^{2}.
\end{aligned}
\end{equation}
```

Hence,

``` math
\begin{equation}
\widehat{\sigma}_{p,t}^{\mathrm{vol}}
=
\lambda_t^{\mathrm{vol}}
\widehat{\sigma}_{p,t}.
\end{equation}
```

Substituting

``` math
\begin{equation}
\lambda_t^{\mathrm{vol}}
=
\frac{
\sigma^{\mathrm{target}}
}{
\widehat{\sigma}_{p,t}
}
\end{equation}
```

gives

``` math
\begin{equation}
\boxed{
\widehat{\sigma}_{p,t}^{\mathrm{vol}}
=
\sigma^{\mathrm{target}}.
}
\end{equation}
```

Thus, under the covariance forecast used for scaling, the resulting portfolio has exactly the desired ex-ante volatility.

##### Time Variation in the Scaling Coefficient

The scaling coefficient varies through time:

``` math
\begin{equation}
\lambda_t^{\mathrm{vol}}
=
\frac{
\sigma^{\mathrm{target}}
}{
\widehat{\sigma}_{p,t}
}.
\end{equation}
```

Therefore,

``` math
\begin{equation}
\widehat{\sigma}_{p,t}
<
\sigma^{\mathrm{target}}
\quad\Rightarrow\quad
\lambda_t^{\mathrm{vol}}>1,
\end{equation}
```

so portfolio exposure is increased.

Conversely,

``` math
\begin{equation}
\widehat{\sigma}_{p,t}
>
\sigma^{\mathrm{target}}
\quad\Rightarrow\quad
\lambda_t^{\mathrm{vol}}<1,
\end{equation}
```

so portfolio exposure is reduced.

Hence,

``` math
\begin{equation}
\boxed{
\text{Low Forecast Risk}
\Rightarrow
\text{Higher Exposure},
}
\end{equation}
```

while

``` math
\begin{equation}
\boxed{
\text{High Forecast Risk}
\Rightarrow
\text{Lower Exposure}.
}
\end{equation}
```

##### Point-in-Time Volatility Estimation

The volatility forecast used in the scaling coefficient must be strictly point-in-time.

At time $`t`$, the backtester must compute

``` math
\begin{equation}
\widehat{\sigma}_{p,t}
\end{equation}
```

using only information available at or before the portfolio decision time.

For example, if the covariance matrix is estimated from historical returns,

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t
=
f
\left(
\mathbf{r}_{t-1},
\mathbf{r}_{t-2},
\ldots
\right),
\end{equation}
```

and not from future realized returns.

Using future realized volatility to determine $`\lambda_t^{\mathrm{vol}}`$ would introduce look-ahead bias.

##### Forecast vs. Realized Volatility

Volatility targeting guarantees the target only with respect to the risk estimate used at time $`t`$.

In general,

``` math
\begin{equation}
\boxed{
\widehat{\sigma}_{p,t}^{\mathrm{vol}}
=
\sigma^{\mathrm{target}}
\quad\not\Rightarrow\quad
\sigma_{p,t\rightarrow t+1}^{\mathrm{realized}}
=
\sigma^{\mathrm{target}}.
}
\end{equation}
```

The realized covariance structure over the subsequent holding period may differ from the covariance forecast.

Volatility targeting should therefore be interpreted as an *ex-ante risk control mechanism*, not as a guarantee of future realized volatility.

#### Leverage Caps and Scaling Limits

Pure volatility targeting may imply very large scaling coefficients when forecast volatility is unusually low.

For example,

``` math
\begin{equation}
\widehat{\sigma}_{p,t}
\rightarrow 0
\quad\Rightarrow\quad
\lambda_t^{\mathrm{vol}}
\rightarrow\infty.
\end{equation}
```

Such leverage is generally economically unrealistic and potentially dangerous.

A maximum scaling coefficient may therefore be imposed:

``` math
\begin{equation}
\boxed{
\lambda_t
=
\min
\left(
\lambda_t^{\mathrm{vol}},
\lambda_{\max}
\right).
}
\end{equation}
```

The resulting portfolio is

``` math
\begin{equation}
\mathbf{w}_t^{\mathrm{scaled}}
=
\lambda_t
\mathbf{w}_t^{\mathrm{target}}.
\end{equation}
```

##### Gross Exposure Cap

Scaling also changes gross exposure.

Before scaling,

``` math
\begin{equation}
G_t^{\mathrm{target}}
=
\left\|
\mathbf{w}_t^{\mathrm{target}}
\right\|_1.
\end{equation}
```

After multiplying all weights by $`\lambda_t`$,

``` math
\begin{equation}
\begin{aligned}
G_t^{\mathrm{scaled}}
&=
\left\|
\lambda_t
\mathbf{w}_t^{\mathrm{target}}
\right\|_1
\\
&=
\lambda_t
\left\|
\mathbf{w}_t^{\mathrm{target}}
\right\|_1.
\end{aligned}
\end{equation}
```

If gross exposure may not exceed $`G_{\max}`$, then

``` math
\begin{equation}
\lambda_t
G_t^{\mathrm{target}}
\leq
G_{\max}.
\end{equation}
```

Therefore,

``` math
\begin{equation}
\boxed{
\lambda_t^{\mathrm{gross}}
=
\frac{
G_{\max}
}{
\left\|
\mathbf{w}_t^{\mathrm{target}}
\right\|_1
}.
}
\end{equation}
```

Combining the volatility target, leverage cap, and gross-exposure constraint gives

``` math
\begin{equation}
\boxed{
\lambda_t
=
\min
\left(
\frac{
\sigma^{\mathrm{target}}
}{
\widehat{\sigma}_{p,t}
},
\lambda_{\max},
\frac{
G_{\max}
}{
\left\|
\mathbf{w}_t^{\mathrm{target}}
\right\|_1
}
\right).
}
\end{equation}
```

If the gross-exposure constraint is binding, the strategy cannot attain its desired volatility target without violating the mandate.

In that case,

``` math
\begin{equation}
\boxed{
\sigma_{p,t}^{\mathrm{final}}
<
\sigma^{\mathrm{target}}
}
\end{equation}
```

may be the correct portfolio outcome.

#### Interaction with Portfolio Constraints

Portfolio-level scaling occurs after the constrained portfolio has been constructed. It is therefore necessary to determine which constraints are preserved by common scaling and which may be violated.

##### Homogeneous Equality Constraints

Consider a linear neutrality constraint

``` math
\begin{equation}
\mathbf{B}_t^\top
\mathbf{w}_t^{\mathrm{target}}
=
\mathbf{0}.
\end{equation}
```

After scaling,

``` math
\begin{equation}
\begin{aligned}
\mathbf{B}_t^\top
\left(
\lambda_t
\mathbf{w}_t^{\mathrm{target}}
\right)
&=
\lambda_t
\mathbf{B}_t^\top
\mathbf{w}_t^{\mathrm{target}}
\\
&=
\mathbf{0}.
\end{aligned}
\end{equation}
```

Therefore,

``` math
\begin{equation}
\boxed{
\mathbf{B}_t^\top
\mathbf{w}_t^{\mathrm{target}}
=
\mathbf{0}
\quad\Rightarrow\quad
\mathbf{B}_t^\top
\mathbf{w}_t^{\mathrm{scaled}}
=
\mathbf{0}.
}
\end{equation}
```

Consequently, common portfolio scaling preserves exact zero-exposure constraints such as:

- dollar neutrality;

- beta neutrality;

- industry neutrality;

- country neutrality;

- style-factor neutrality.

For example, if

``` math
\begin{equation}
\boldsymbol{\beta}_t^\top
\mathbf{w}_t^{\mathrm{target}}
=
0,
\end{equation}
```

then

``` math
\begin{equation}
\boldsymbol{\beta}_t^\top
\mathbf{w}_t^{\mathrm{scaled}}
=
\lambda_t
\boldsymbol{\beta}_t^\top
\mathbf{w}_t^{\mathrm{target}}
=
0.
\end{equation}
```

##### Non-Zero Exposure Targets

The same result does not hold for constraints requiring a specific non-zero exposure.

Suppose

``` math
\begin{equation}
\mathbf{b}_t^\top
\mathbf{w}_t^{\mathrm{target}}
=
c,
\qquad
c\neq0.
\end{equation}
```

After scaling,

``` math
\begin{equation}
\mathbf{b}_t^\top
\mathbf{w}_t^{\mathrm{scaled}}
=
\lambda_t c.
\end{equation}
```

Therefore,

``` math
\begin{equation}
\boxed{
c\neq0
\quad\Rightarrow\quad
\text{common scaling generally changes the targeted exposure}.
}
\end{equation}
```

##### Inequality Constraints

Scaling may also violate upper or lower bounds.

For example, if

``` math
\begin{equation}
|w_{i,t}^{\mathrm{target}}|
\leq
w_{i,t}^{\max},
\end{equation}
```

then after scaling,

``` math
\begin{equation}
|w_{i,t}^{\mathrm{scaled}}|
=
\lambda_t
|w_{i,t}^{\mathrm{target}}|.
\end{equation}
```

For $`\lambda_t>1`$, it is possible that

``` math
\begin{equation}
|w_{i,t}^{\mathrm{scaled}}|
>
w_{i,t}^{\max}.
\end{equation}
```

The same issue applies to:

- gross exposure limits;

- individual position limits;

- liquidity and capacity limits;

- leverage limits;

- non-zero factor-exposure bands.

Thus, volatility scaling cannot be considered independently of the feasible set.

##### Maximum Feasible Scaling Coefficient

More generally, let

``` math
\begin{equation}
\lambda_t^{\mathrm{feasible}}
\end{equation}
```

denote the largest positive scalar such that

``` math
\begin{equation}
\lambda_t^{\mathrm{feasible}}
\mathbf{w}_t^{\mathrm{target}}
\end{equation}
```

continues to satisfy all relevant portfolio constraints.

Then the operational scaling coefficient can be written as

``` math
\begin{equation}
\boxed{
\lambda_t
=
\min
\left(
\lambda_t^{\mathrm{vol}},
\lambda_t^{\mathrm{feasible}}
\right).
}
\end{equation}
```

This formulation provides a general interpretation of constrained volatility targeting:

``` math
\begin{equation}
\boxed{
\text{take as much exposure as required by the risk target,
subject to remaining feasible}.
}
\end{equation}
```

#### Final Target Weights

After portfolio-level risk scaling, the final desired weights are

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{final}}
=
\lambda_t
\mathbf{w}_t^{\mathrm{target}}.
}
\end{equation}
```

where

``` math
\begin{equation}
\mathbf{w}_t^{\mathrm{final}}
\in
\mathbb{R}^{N_t}.
\end{equation}
```

If no separate portfolio-level risk scaling is required, then

``` math
\begin{equation}
\lambda_t=1,
\end{equation}
```

and therefore

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{final}}
=
\mathbf{w}_t^{\mathrm{target}}.
}
\end{equation}
```

The distinction between the two objects is therefore:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{w}_t^{\mathrm{target}}
&:
&&
\text{portfolio obtained from mapping, optimization, and constraints},
\\
\mathbf{w}_t^{\mathrm{final}}
&:
&&
\text{portfolio after optional portfolio-level risk scaling}.
\end{aligned}
}
\end{equation}
```

The complete portfolio-construction pipeline can now be summarized as

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{s}_t^{\mathrm{final}}
&\rightarrow
\text{Signal-to-Weight Mapping}
\\
&\rightarrow
\text{Risk Model}
\\
&\rightarrow
\text{Optimization}
\\
&\rightarrow
\text{Portfolio Constraints}
\\
&\rightarrow
\mathbf{w}_t^{\mathrm{target}}
\\
&\rightarrow
\text{Optional Isovol Scaling}
\\
&\rightarrow
\mathbf{w}_t^{\mathrm{final}}.
\end{aligned}
}
\end{equation}
```

At this point, the portfolio-construction problem is complete.

The vector

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{final}}
}
\end{equation}
```

represents the final desired economic exposure of the strategy at time $`t`$.

The remaining stages of the backtester no longer determine which portfolio *should* be held. Instead, they determine how the existing portfolio is moved toward these desired weights, how trades are executed and costed, and how the resulting realized portfolio performance is measured.

# Backtest Simulation and Implementation

The previous parts of the backtester determined the portfolio that the strategy *wants* to hold.

At each portfolio decision date, the portfolio-construction engine produces

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{final}}
\in
\mathbb{R}^{N_t},
}
\end{equation}
```

where $`\mathbf{w}_t^{\mathrm{final}}`$ denotes the final desired portfolio weights after signal construction, portfolio optimization, constraints, and any optional portfolio-level risk scaling.

The purpose of the present part is fundamentally different.

The backtester must now simulate how this desired portfolio would actually evolve through time.

This requires modeling:

- when portfolio decisions are made;

- when they can be executed;

- the portfolio already held before each rebalance;

- the trades required to reach the new target;

- execution prices and partial execution;

- transaction costs and market frictions;

- positions, cash, and mark-to-market valuation;

- realized portfolio profit and loss;

- the resulting net return series.

The simulation layer can therefore be summarized as

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{w}_t^{\mathrm{final}}
&\rightarrow
\text{Rebalance Decision}
\\
&\rightarrow
\mathbf{w}_{t^-}
\rightarrow
\Delta\mathbf{w}_t
\\
&\rightarrow
\text{Orders}
\rightarrow
\text{Execution}
\\
&\rightarrow
\mathbf{w}_t^{\mathrm{implemented}}
\\
&\rightarrow
\text{Portfolio State and P\&L}
\\
&\rightarrow
R_t^{\mathrm{gross}}
\rightarrow
R_t^{\mathrm{net}}
\rightarrow
NAV_t.
\end{aligned}
}
\end{equation}
```

The distinction between desired and implemented weights is essential.

The portfolio-construction engine produces

``` math
\begin{equation}
\mathbf{w}_t^{\mathrm{final}},
\end{equation}
```

whereas the simulation engine ultimately determines

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{implemented}},
}
\end{equation}
```

the portfolio actually held after accounting for execution, tradability, position rounding, partial fills, and other implementation effects.

