### Portfolio Optimization

Once the final signal and the portfolio risk model have been constructed, the backtester can determine the portfolio weights that best trade off expected return, risk, implementation costs, and portfolio stability.

The central optimization problem can be written abstractly as

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{target}}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\;
\mathcal{J}_t
\left(
\mathbf{w}
\right),
}
\end{equation}
```

where

``` math
\begin{equation}
\mathbf{w}
\in
\mathbb{R}^{N_t}
\end{equation}
```

is a candidate portfolio-weight vector and

``` math
\begin{equation}
\mathcal{W}_t
\end{equation}
```

denotes the feasible set defined by the portfolio constraints.

The objective function may incorporate several components:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathcal{J}_t(\mathbf{w})
=
&
\underbrace{
\mathcal{A}_t(\mathbf{w})
}_{\text{Expected Alpha}}
-
\underbrace{
\mathcal{R}_t(\mathbf{w})
}_{\text{Risk Penalty}}
\\
&
-
\underbrace{
\mathcal{C}_t(\mathbf{w},\mathbf{w}_{t^-})
}_{\text{Trading Cost}}
-
\underbrace{
\mathcal{P}_t(\mathbf{w})
}_{\text{Regularization}}.
\end{aligned}
}
\end{equation}
```

Here,

``` math
\begin{equation}
\mathbf{w}_{t^-}
\end{equation}
```

denotes portfolio weights immediately before the rebalance.

The exact formulation depends on the interpretation of the signal.

If

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{final}}
\end{equation}
```

is a calibrated expected-return vector, it can enter the optimization directly.

If it is only an ordinal or standardized alpha score, an explicit mapping from score to expected return may be required before using expected-return-based optimization.

Thus,

``` math
\begin{equation}
\boxed{
\text{Signal Score}
\neq
\text{Expected Return}
}
\end{equation}
```

unless the signal has been explicitly calibrated as such.

#### General Optimization Framework

Let

``` math
\begin{equation}
\widehat{\boldsymbol{\mu}}_t
=
\begin{bmatrix}
\widehat{\mu}_{1,t}
\\
\vdots
\\
\widehat{\mu}_{N_t,t}
\end{bmatrix}
\in
\mathbb{R}^{N_t}
\end{equation}
```

denote the vector of expected future security returns.

Let

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t
\in
\mathbb{R}^{N_t\times N_t}
\end{equation}
```

denote the ex-ante covariance matrix.

A generic optimization problem is

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{*}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\left[
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t
-
\lambda_R
\mathcal{R}_t(\mathbf{w})
-
\lambda_C
\mathcal{C}_t(\mathbf{w},\mathbf{w}_{t^-})
-
\lambda_P
\mathcal{P}_t(\mathbf{w})
\right].
}
\end{equation}
```

The coefficients

``` math
\begin{equation}
\lambda_R,
\qquad
\lambda_C,
\qquad
\lambda_P
\end{equation}
```

control the relative importance of risk, trading costs, and regularization.

##### Feasible Set

The feasible set may be written abstractly as

``` math
\begin{equation}
\boxed{
\mathcal{W}_t
=
\left\{
\mathbf{w}\in\mathbb{R}^{N_t}
:
\mathbf{w}
\text{ satisfies all portfolio constraints}
\right\}.
}
\end{equation}
```

Possible restrictions include:

- gross exposure limits;

- net exposure limits;

- individual position bounds;

- beta constraints;

- sector constraints;

- country constraints;

- factor-exposure limits;

- liquidity constraints;

- shortability constraints.

These constraints will be developed explicitly in subsequent sections.

##### Convexity

A major practical distinction is whether the optimization problem is convex.

If the objective is concave and the feasible set is convex, the optimizer can generally identify a global optimum reliably.

For example,

``` math
\begin{equation}
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t
-
\frac{\lambda}{2}
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}
\end{equation}
```

is concave in $`\mathbf{w}`$ when

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t
\succeq
0.
\end{equation}
```

Linear equality and inequality constraints preserve convexity.

By contrast, cardinality constraints, integer trading decisions, or certain nonlinear market-impact models may produce non-convex optimization problems.

#### Expected Return Maximization

The simplest optimization objective maximizes expected portfolio return:

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{*}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\;
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t.
}
\end{equation}
```

Expected portfolio return is

``` math
\begin{equation}
\boxed{
\widehat{\mu}_{p,t}
=
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t.
}
\end{equation}
```

##### Need for Constraints

Without constraints, the problem is generally ill posed.

If arbitrary leverage is allowed and at least one asset satisfies

``` math
\begin{equation}
\widehat{\mu}_{i,t}>0,
\end{equation}
```

the optimizer can increase expected return indefinitely by increasing the position.

Thus,

``` math
\begin{equation}
\boxed{
\text{Expected Return Maximization}
+
\text{No Risk or Leverage Constraint}
\Rightarrow
\text{Unbounded Problem}.
}
\end{equation}
```

Meaningful expected-return maximization therefore requires constraints such as

``` math
\begin{equation}
\sum_i |w_i|
\leq
G_{\max},
\end{equation}
```

or explicit risk limits.

##### Corner Solutions

Even with leverage constraints, pure expected-return maximization often produces highly concentrated portfolios.

For example, under a long-only fully invested constraint

``` math
\begin{equation}
w_i\geq0,
\qquad
\sum_iw_i=1,
\end{equation}
```

the solution is generally to allocate all capital to the security with the highest expected return:

``` math
\begin{equation}
w_{i^*}=1,
\end{equation}
```

where

``` math
\begin{equation}
i^*
=
\underset{i}{\arg\max}
\;
\widehat{\mu}_{i,t}.
\end{equation}
```

This illustrates why expected return alone is usually insufficient for realistic portfolio construction.

#### Mean–Variance Optimization

Mean–variance optimization explicitly balances expected return and portfolio variance.

The standard objective is

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{*}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\left[
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t
-
\frac{\lambda}{2}
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}
\right],
}
\end{equation}
```

where

``` math
\begin{equation}
\lambda>0
\end{equation}
```

is the risk-aversion parameter.

##### Interpretation

The first term,

``` math
\begin{equation}
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t,
\end{equation}
```

rewards expected return.

The second,

``` math
\begin{equation}
\frac{\lambda}{2}
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w},
\end{equation}
```

penalizes portfolio variance.

A larger $`\lambda`$ produces a more risk-averse portfolio.

##### Unconstrained Solution

If no constraints are imposed and

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t
\end{equation}
```

is positive definite, the first-order condition is

``` math
\begin{equation}
\widehat{\boldsymbol{\mu}}_t
-
\lambda
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}
=
0.
\end{equation}
```

Therefore,

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{*}
=
\frac{1}{\lambda}
\widehat{\boldsymbol{\Sigma}}_t^{-1}
\widehat{\boldsymbol{\mu}}_t.
}
\end{equation}
```

This expression illustrates the joint role of alpha and risk.

A security does not receive a large weight merely because its expected return is high. Its weight also depends on how its risk covaries with the rest of the portfolio.

##### Connection with Signal Mapping

If

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t
=
\sigma^2
\mathbf{I},
\end{equation}
```

then

``` math
\begin{equation}
\mathbf{w}_t^{*}
=
\frac{1}{\lambda\sigma^2}
\widehat{\boldsymbol{\mu}}_t.
\end{equation}
```

Thus,

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{*}
\propto
\widehat{\boldsymbol{\mu}}_t.
}
\end{equation}
```

Linear signal mapping is therefore a special case of mean–variance optimization when all assets have equal variance and zero covariance.

##### Estimation Error

The unconstrained solution depends on

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t^{-1}
\widehat{\boldsymbol{\mu}}_t.
\end{equation}
```

Both expected returns and covariance matrices are estimated with error.

Expected-return estimates are usually particularly noisy.

Consequently, unconstrained mean–variance optimization may produce extreme and unstable weights.

This motivates:

- covariance shrinkage;

- expected-return shrinkage;

- position constraints;

- turnover penalties;

- weight regularization.

#### Risk-Adjusted Optimization

Rather than choosing an explicit risk-aversion parameter, the optimizer may maximize a risk-adjusted objective.

##### Maximum Sharpe Ratio

Assuming a zero or already subtracted risk-free rate, the ex-ante portfolio Sharpe ratio is

``` math
\begin{equation}
\boxed{
SR_t(\mathbf{w})
=
\frac{
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t
}{
\sqrt{
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}
}
}.
}
\end{equation}
```

The optimization problem is

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{*}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\;
SR_t(\mathbf{w}).
}
\end{equation}
```

##### Scale Invariance

For any

``` math
\begin{equation}
c>0,
\end{equation}
```

one has

``` math
\begin{equation}
SR_t(c\mathbf{w})
=
SR_t(\mathbf{w}).
\end{equation}
```

Therefore, maximum-Sharpe optimization determines a portfolio direction but not its absolute leverage.

A separate volatility or gross-exposure target is required to determine scale.

##### Maximum Information Ratio

For benchmark-relative portfolios, expected active return may be written as

``` math
\begin{equation}
\widehat{\mu}_{p,t}^{\mathrm{active}}
=
\mathbf{w}^{\top}
\widehat{\boldsymbol{\alpha}}_t,
\end{equation}
```

where

``` math
\begin{equation}
\widehat{\boldsymbol{\alpha}}_t
\end{equation}
```

denotes expected benchmark-relative returns.

If

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t^{\mathrm{active}}
\end{equation}
```

describes active-return risk, the ex-ante Information Ratio is

``` math
\begin{equation}
\boxed{
IR_t(\mathbf{w})
=
\frac{
\mathbf{w}^{\top}
\widehat{\boldsymbol{\alpha}}_t
}{
\sqrt{
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t^{\mathrm{active}}
\mathbf{w}
}
}.
}
\end{equation}
```

This formulation is natural for benchmark-relative active equity portfolios.

##### Risk Budget Formulation

Another formulation maximizes expected return subject to a risk constraint:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\max_{\mathbf{w}}
\quad&
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t
\\
\text{s.t.}
\quad&
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}
\leq
\sigma_{\max}^{2},
\\
&
\mathbf{w}
\in
\mathcal{W}_t.
\end{aligned}
}
\end{equation}
```

This expresses the investment problem directly as:

``` math
\begin{equation}
\boxed{
\text{maximize alpha for a fixed risk budget}.
}
\end{equation}
```

#### Transaction-Cost-Aware Optimization

The portfolio with the highest gross expected alpha may not be optimal after implementation costs.

Let

``` math
\begin{equation}
\mathbf{w}_{t^-}
\in
\mathbb{R}^{N_t}
\end{equation}
```

denote pre-rebalance portfolio weights.

The required trade is

``` math
\begin{equation}
\boxed{
\Delta\mathbf{w}_t
=
\mathbf{w}_t
-
\mathbf{w}_{t^-}.
}
\end{equation}
```

Let

``` math
\begin{equation}
C_t
\left(
\Delta\mathbf{w}_t
\right)
\end{equation}
```

denote expected transaction costs expressed as a fraction of portfolio NAV.

A cost-aware mean–variance problem is

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{*}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\left[
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t
-
\frac{\lambda}{2}
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}
-
C_t
\left(
\mathbf{w}
-
\mathbf{w}_{t^-}
\right)
\right].
}
\end{equation}
```

##### Linear Transaction Costs

A simple proportional cost model is

``` math
\begin{equation}
\boxed{
C_t^{\mathrm{linear}}
=
\sum_{i=1}^{N_t}
c_{i,t}
\left|
w_{i,t}
-
w_{i,t^-}
\right|,
}
\end{equation}
```

where

``` math
\begin{equation}
c_{i,t}
\end{equation}
```

is the estimated one-way transaction cost per unit of traded portfolio notional.

The optimizer will trade only when the expected improvement in the objective is sufficient to compensate for these costs.

##### Nonlinear Market Impact

Large trades generally have higher marginal cost.

A stylized nonlinear cost function may take the form

``` math
\begin{equation}
\boxed{
C_{i,t}^{\mathrm{impact}}
=
\eta_{i,t}
\left|
\Delta w_{i,t}
\right|^{p},
\qquad
p>1.
}
\end{equation}
```

Then

``` math
\begin{equation}
C_t^{\mathrm{impact}}
=
\sum_i
C_{i,t}^{\mathrm{impact}}.
\end{equation}
```

The convexity of the cost function discourages concentrated large trades.

##### Costs in Currency Notional

If portfolio NAV is

``` math
\begin{equation}
A_t,
\end{equation}
```

the currency notional traded is

``` math
\begin{equation}
Q_{i,t}
=
A_t
|\Delta w_{i,t}|.
\end{equation}
```

Transaction costs may therefore depend on

``` math
\begin{equation}
C_{i,t}
=
C
\left(
Q_{i,t},
\mathrm{ADV}_{i,t},
\mathrm{Spread}_{i,t},
\sigma_{i,t},
\ldots
\right).
\end{equation}
```

This establishes the connection between portfolio optimization and the implementation data introduced earlier in the backtester.

#### Turnover-Aware Optimization

Turnover-aware optimization penalizes changes in portfolio weights even when a complete transaction-cost model is unavailable.

A natural turnover measure is

``` math
\begin{equation}
\boxed{
TO_t
=
\sum_{i=1}^{N_t}
\left|
w_{i,t}
-
w_{i,t^-}
\right|.
}
\end{equation}
```

A turnover-penalized objective is

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{*}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\left[
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t
-
\frac{\lambda}{2}
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}
-
\kappa
\left\|
\mathbf{w}
-
\mathbf{w}_{t^-}
\right\|_1
\right],
}
\end{equation}
```

where

``` math
\begin{equation}
\kappa\geq0.
\end{equation}
```

##### $`L^1`$ Turnover Penalty

The $`L^1`$ penalty is

``` math
\begin{equation}
\left\|
\mathbf{w}
-
\mathbf{w}_{t^-}
\right\|_1
=
\sum_i
|w_i-w_{i,t^-}|.
\end{equation}
```

It directly corresponds to total traded notional in weight space.

##### Quadratic Turnover Penalty

A smoother alternative is

``` math
\begin{equation}
\boxed{
\kappa
\left\|
\mathbf{w}
-
\mathbf{w}_{t^-}
\right\|_2^2.
}
\end{equation}
```

The optimization becomes

``` math
\begin{equation}
\mathbf{w}_t^{*}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\left[
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t
-
\frac{\lambda}{2}
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}
-
\kappa
\left\|
\mathbf{w}
-
\mathbf{w}_{t^-}
\right\|_2^2
\right].
\end{equation}
```

Unlike the $`L^1`$ penalty, this penalizes large trades disproportionately.

##### Turnover Constraint

Instead of penalizing turnover in the objective, a hard constraint may be imposed:

``` math
\begin{equation}
\boxed{
\sum_i
|w_{i,t}-w_{i,t^-}|
\leq
TO_{\max}.
}
\end{equation}
```

The distinction is

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Penalty}
&:
\quad
\text{turnover is allowed but costly},
\\
\text{Constraint}
&:
\quad
\text{turnover may not exceed a fixed limit}.
\end{aligned}
}
\end{equation}
```

##### Endogenous No-Trade Region

An important consequence of transaction-cost or $`L^1`$ turnover penalties is that small changes in expected alpha may optimally produce no trade.

Conceptually,

``` math
\begin{equation}
\boxed{
\text{Marginal Alpha Improvement}
<
\text{Marginal Trading Cost}
\Rightarrow
\Delta w_{i,t}^{*}=0.
}
\end{equation}
```

Thus, the optimization can generate an endogenous no-trade region rather than requiring an arbitrary signal threshold.

#### Regularization of Portfolio Weights

Portfolio optimization can be highly sensitive to estimation error in expected returns and covariance matrices.

Regularization reduces this sensitivity by penalizing extreme or unstable portfolio weights.

##### $`L^2`$ Weight Regularization

A quadratic weight penalty is

``` math
\begin{equation}
\boxed{
\lambda_w
\|\mathbf{w}\|_2^2
=
\lambda_w
\sum_{i=1}^{N_t}
w_i^2.
}
\end{equation}
```

A regularized mean–variance objective becomes

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{*}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\left[
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t
-
\frac{\lambda_R}{2}
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}
-
\lambda_w
\mathbf{w}^{\top}\mathbf{w}
\right].
}
\end{equation}
```

##### Equivalent Covariance Interpretation

The risk and regularization terms can be combined:

``` math
\begin{equation}
\frac{\lambda_R}{2}
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}
+
\lambda_w
\mathbf{w}^{\top}\mathbf{w}.
\end{equation}
```

This can be rewritten as

``` math
\begin{equation}
\boxed{
\frac{\lambda_R}{2}
\mathbf{w}^{\top}
\left(
\widehat{\boldsymbol{\Sigma}}_t
+
\frac{2\lambda_w}{\lambda_R}
\mathbf{I}
\right)
\mathbf{w}.
}
\end{equation}
```

Thus, $`L^2`$ weight regularization is mathematically related to adding a positive constant to the diagonal of the covariance matrix.

This improves numerical conditioning and discourages extreme positions.

##### $`L^1`$ Weight Regularization

An alternative is

``` math
\begin{equation}
\boxed{
\lambda_w
\|\mathbf{w}\|_1
=
\lambda_w
\sum_i |w_i|.
}
\end{equation}
```

However, if gross exposure is already fixed through

``` math
\begin{equation}
\sum_i|w_i|
=
G,
\end{equation}
```

then

``` math
\begin{equation}
\|\mathbf{w}\|_1
=
G
\end{equation}
```

is constant and an additional $`L^1`$ penalty has no effect.

This illustrates the importance of considering interactions between regularization terms and portfolio constraints.

##### Regularization Toward a Reference Portfolio

Rather than shrinking weights toward zero, one may shrink toward a reference portfolio

``` math
\begin{equation}
\mathbf{w}_t^{\mathrm{ref}}.
\end{equation}
```

The penalty is

``` math
\begin{equation}
\boxed{
\lambda_w
\left\|
\mathbf{w}
-
\mathbf{w}_t^{\mathrm{ref}}
\right\|_2^2.
}
\end{equation}
```

Possible reference portfolios include:

- equal weight;

- benchmark weights;

- previous portfolio weights;

- raw signal-mapped weights;

- risk-balanced weights.

This formulation allows the optimizer to deviate from a stable baseline only when the estimated benefits justify doing so.

##### Diversification Effect

Since

``` math
\begin{equation}
\|\mathbf{w}\|_2^2
=
\sum_i w_i^2,
\end{equation}
```

for a fixed gross or net exposure, minimizing the $`L^2`$ norm generally discourages concentration.

For a long-only fully invested portfolio,

``` math
\begin{equation}
\sum_i w_i=1,
\qquad
w_i\geq0,
\end{equation}
```

the minimum of

``` math
\begin{equation}
\sum_iw_i^2
\end{equation}
```

is achieved by

``` math
\begin{equation}
\boxed{
w_i
=
\frac{1}{N_t}.
}
\end{equation}
```

Therefore, $`L^2`$ regularization naturally pulls the optimizer toward more diversified allocations.

##### Unified Optimization Objective

The different components developed in this section can be combined into a general portfolio optimization problem:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{w}_t^{*}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\Bigg[
&
\mathbf{w}^{\top}
\widehat{\boldsymbol{\mu}}_t
-
\frac{\lambda_R}{2}
\mathbf{w}^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}
\\
&
-
C_t
\left(
\mathbf{w}-\mathbf{w}_{t^-}
\right)
\\
&
-
\lambda_{TO}
\left\|
\mathbf{w}-\mathbf{w}_{t^-}
\right\|_1
\\
&
-
\lambda_W
\left\|
\mathbf{w}-\mathbf{w}_t^{\mathrm{ref}}
\right\|_2^2
\Bigg].
\end{aligned}
}
\end{equation}
```

The optimizer therefore balances four competing objectives:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Expected Alpha}
&\uparrow,
\\
\text{Portfolio Risk}
&\downarrow,
\\
\text{Implementation Cost and Turnover}
&\downarrow,
\\
\text{Weight Instability and Concentration}
&\downarrow.
\end{aligned}
}
\end{equation}
```

##### Optimization Output

The optimization stage produces

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{*}
\in
\mathbb{R}^{N_t}.
}
\end{equation}
```

However, this vector is only valid if it satisfies all desired portfolio constraints.

Thus, the logical portfolio-construction sequence is

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{s}_t^{\mathrm{final}}
&\rightarrow
\widehat{\boldsymbol{\mu}}_t
\\
+
\widehat{\boldsymbol{\Sigma}}_t
&\rightarrow
\text{Optimization Objective}
\\
+
\mathcal{W}_t
&\rightarrow
\mathbf{w}_t^{\mathrm{target}}.
\end{aligned}
}
\end{equation}
```

The next step is therefore to define the feasible set $`\mathcal{W}_t`$ explicitly through portfolio exposure, leverage, position, factor, and liquidity constraints.

