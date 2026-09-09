### Portfolio Constraints

Portfolio optimization does not operate over all possible weight vectors. Instead, the optimizer must choose weights inside a feasible set determined by the investment mandate, risk limits, liquidity, leverage, and implementation constraints.

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

denote a candidate portfolio-weight vector at time $`t`$.

The feasible set is

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

The optimization problem developed previously can therefore be written as

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{target}}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\;
\mathcal{J}_t(\mathbf{w}).
}
\end{equation}
```

A constraint is fundamentally different from a penalty.

A penalty enters the objective function and may be violated if the expected benefit is sufficiently large. A hard constraint defines admissibility:

``` math
\begin{equation}
\boxed{
\mathbf{w}\notin\mathcal{W}_t
\quad\Rightarrow\quad
\mathbf{w}
\text{ cannot be selected},
}
\end{equation}
```

regardless of its expected alpha.

The constraints below can be combined depending on the portfolio mandate.

#### Gross Exposure

Gross exposure measures the total absolute size of all long and short positions.

It is defined as

``` math
\begin{equation}
\boxed{
G_t
=
\sum_{i=1}^{N_t}
|w_{i,t}|
=
\|\mathbf{w}_t\|_1.
}
\end{equation}
```

A maximum gross-exposure constraint is

``` math
\begin{equation}
\boxed{
\|\mathbf{w}_t\|_1
\leq
G_{\max}.
}
\end{equation}
```

Alternatively, the portfolio may be required to maintain an exact gross exposure:

``` math
\begin{equation}
\boxed{
\|\mathbf{w}_t\|_1
=
G_{\mathrm{target}}.
}
\end{equation}
```

##### Interpretation

For example,

``` math
\begin{equation}
G_t=1
\end{equation}
```

corresponds to $`100\%`$ gross exposure, whereas

``` math
\begin{equation}
G_t=2
\end{equation}
```

corresponds to $`200\%`$ gross exposure.

A market-neutral portfolio that is $`100\%`$ long and $`100\%`$ short satisfies

``` math
\begin{equation}
G_t
=
1+1
=
2.
\end{equation}
```

#### Net Exposure

Net exposure measures the signed total portfolio exposure:

``` math
\begin{equation}
\boxed{
N_t
=
\sum_{i=1}^{N_t}
w_{i,t}
=
\mathbf{1}^{\top}\mathbf{w}_t.
}
\end{equation}
```

A dollar-neutral portfolio satisfies

``` math
\begin{equation}
\boxed{
\mathbf{1}^{\top}\mathbf{w}_t
=
0.
}
\end{equation}
```

More generally,

``` math
\begin{equation}
N_{\min}
\leq
\mathbf{1}^{\top}\mathbf{w}_t
\leq
N_{\max}.
\end{equation}
```

##### Gross vs. Net Exposure

Gross and net exposure measure different concepts.

For example, suppose

``` math
\begin{equation}
G_t=2
\end{equation}
```

and

``` math
\begin{equation}
N_t=0.
\end{equation}
```

The portfolio may be $`100\%`$ long and $`100\%`$ short.

By contrast,

``` math
\begin{equation}
G_t=1
\qquad
\text{and}
\qquad
N_t=1
\end{equation}
```

corresponds to a fully invested long-only portfolio.

Thus,

``` math
\begin{equation}
\boxed{
\text{Gross Exposure}
\neq
\text{Net Exposure}.
}
\end{equation}
```

#### Long and Short Budgets

Define the long-leg exposure as

``` math
\begin{equation}
\boxed{
G_t^{L}
=
\sum_{i=1}^{N_t}
\max(w_{i,t},0),
}
\end{equation}
```

and the absolute short-leg exposure as

``` math
\begin{equation}
\boxed{
G_t^{S}
=
\sum_{i=1}^{N_t}
\max(-w_{i,t},0).
}
\end{equation}
```

Then

``` math
\begin{equation}
\boxed{
G_t
=
G_t^{L}
+
G_t^{S},
}
\end{equation}
```

while

``` math
\begin{equation}
\boxed{
N_t
=
G_t^{L}
-
G_t^{S}.
}
\end{equation}
```

Therefore,

``` math
\begin{equation}
\boxed{
G_t^{L}
=
\frac{
G_t+N_t
}{2},
}
\end{equation}
```

and

``` math
\begin{equation}
\boxed{
G_t^{S}
=
\frac{
G_t-N_t
}{2}.
}
\end{equation}
```

This relation is particularly useful because gross and net exposure uniquely determine long and short budgets.

##### Explicit Leg Budgets

The portfolio may impose directly

``` math
\begin{equation}
G_t^{L}
=
G_{\mathrm{target}}^{L},
\end{equation}
```

and

``` math
\begin{equation}
G_t^{S}
=
G_{\mathrm{target}}^{S}.
\end{equation}
```

For example,

``` math
\begin{equation}
G_{\mathrm{target}}^{L}
=
G_{\mathrm{target}}^{S}
=
1
\end{equation}
```

implies

``` math
\begin{equation}
G_t=2,
\qquad
N_t=0.
\end{equation}
```

#### Leverage Constraints

Leverage describes portfolio exposure relative to NAV.

In weight space, gross exposure is often used as a direct leverage measure:

``` math
\begin{equation}
\boxed{
L_t
=
\|\mathbf{w}_t\|_1.
}
\end{equation}
```

A leverage constraint is therefore

``` math
\begin{equation}
\boxed{
\|\mathbf{w}_t\|_1
\leq
L_{\max}.
}
\end{equation}
```

However, economic leverage may also depend on the instruments used.

For example, derivatives, futures, swaps, and financed positions may have different cash requirements despite generating similar economic exposures.

Thus, the backtester should distinguish where necessary between

``` math
\begin{equation}
\boxed{
\text{Economic Exposure}
\qquad\text{and}\qquad
\text{Balance-Sheet or Margin Usage}.
}
\end{equation}
```

For a cash-equity backtester, gross exposure is generally a sufficient first representation.

#### Position Limits

Individual-security limits prevent the optimizer from concentrating too much capital in a single position.

For each security,

``` math
\begin{equation}
\boxed{
w_{i,t}^{\min}
\leq
w_{i,t}
\leq
w_{i,t}^{\max}.
}
\end{equation}
```

A symmetric constraint is

``` math
\begin{equation}
\boxed{
|w_{i,t}|
\leq
w_{\max}.
}
\end{equation}
```

##### Asymmetric Long and Short Limits

Long and short limits need not be identical.

For example,

``` math
\begin{equation}
-w_{\max}^{S}
\leq
w_{i,t}
\leq
w_{\max}^{L}.
\end{equation}
```

This may reflect different liquidity, borrow, or risk constraints on the short side.

##### Security-Specific Limits

Position bounds may depend on security characteristics:

``` math
\begin{equation}
\boxed{
w_{i,t}^{\max}
=
g
\left(
\mathrm{ADV}_{i,t},
\mathrm{MCap}_{i,t},
\sigma_{i,t},
\mathrm{Borrow}_{i,t},
\ldots
\right).
}
\end{equation}
```

Thus, liquid large-cap securities may support larger positions than illiquid small-cap securities.

#### Beta Neutrality

Let

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
\mathbb{R}^{N_t}
\end{equation}
```

denote security-level market betas.

Portfolio beta is

``` math
\begin{equation}
\boxed{
\beta_{p,t}
=
\boldsymbol{\beta}_t^{\top}
\mathbf{w}_t.
}
\end{equation}
```

Exact beta neutrality requires

``` math
\begin{equation}
\boxed{
\boldsymbol{\beta}_t^{\top}
\mathbf{w}_t
=
0.
}
\end{equation}
```

A tolerance band may instead be imposed:

``` math
\begin{equation}
\boxed{
-\beta_{\max}
\leq
\boldsymbol{\beta}_t^{\top}
\mathbf{w}_t
\leq
\beta_{\max}.
}
\end{equation}
```

##### Signal vs. Portfolio Beta Neutrality

As discussed previously,

``` math
\begin{equation}
\boldsymbol{\beta}_t^\top
\mathbf{s}_t^{\mathrm{neutral}}
=
0
\end{equation}
```

does not necessarily imply

``` math
\begin{equation}
\boldsymbol{\beta}_t^\top
\mathbf{w}_t
=
0.
\end{equation}
```

Therefore,

``` math
\begin{equation}
\boxed{
\text{Signal-Level Neutrality}
\neq
\text{Portfolio-Level Neutrality}.
}
\end{equation}
```

If portfolio beta neutrality is a mandate requirement, it should be imposed directly on the portfolio weights.

#### Industry and Sector Neutrality

Let

``` math
\begin{equation}
\mathbf{D}_t
\in
\mathbb{R}^{N_t\times G}
\end{equation}
```

denote the industry-exposure matrix, where $`G`$ is the number of industries.

Portfolio industry exposures are

``` math
\begin{equation}
\boxed{
\mathbf{e}_t^{\mathrm{industry}}
=
\mathbf{D}_t^\top
\mathbf{w}_t
\in
\mathbb{R}^{G}.
}
\end{equation}
```

Exact industry neutrality requires

``` math
\begin{equation}
\boxed{
\mathbf{D}_t^\top
\mathbf{w}_t
=
\mathbf{0}_{G}.
}
\end{equation}
```

##### Industry Exposure Bands

Exact neutrality may be unnecessarily restrictive.

Instead,

``` math
\begin{equation}
-\mathbf{u}_t
\leq
\mathbf{D}_t^\top
\mathbf{w}_t
\leq
\mathbf{u}_t,
\end{equation}
```

where

``` math
\begin{equation}
\mathbf{u}_t
\in
\mathbb{R}_{+}^{G}
\end{equation}
```

contains maximum absolute industry exposures.

##### Benchmark-Relative Constraints

For benchmark-relative portfolios, sector exposure may be constrained relative to benchmark weights.

Let

``` math
\begin{equation}
\mathbf{w}_t^{B}
\end{equation}
```

denote benchmark weights.

Active weights are

``` math
\begin{equation}
\mathbf{a}_t
=
\mathbf{w}_t
-
\mathbf{w}_t^{B}.
\end{equation}
```

Industry active exposure is

``` math
\begin{equation}
\boxed{
\mathbf{D}_t^\top
\mathbf{a}_t.
}
\end{equation}
```

A benchmark-relative sector constraint is therefore

``` math
\begin{equation}
-\mathbf{u}
\leq
\mathbf{D}_t^\top
\left(
\mathbf{w}_t-\mathbf{w}_t^{B}
\right)
\leq
\mathbf{u}.
\end{equation}
```

#### Country Neutrality

Let

``` math
\begin{equation}
\mathbf{C}_t
\in
\mathbb{R}^{N_t\times J}
\end{equation}
```

denote country exposures.

The portfolio country-exposure vector is

``` math
\begin{equation}
\boxed{
\mathbf{e}_t^{\mathrm{country}}
=
\mathbf{C}_t^\top
\mathbf{w}_t.
}
\end{equation}
```

Exact country neutrality requires

``` math
\begin{equation}
\boxed{
\mathbf{C}_t^\top
\mathbf{w}_t
=
\mathbf{0}_{J}.
}
\end{equation}
```

Alternatively, exposure bands may be imposed:

``` math
\begin{equation}
-\mathbf{c}_{\max}
\leq
\mathbf{C}_t^\top
\mathbf{w}_t
\leq
\mathbf{c}_{\max}.
\end{equation}
```

These constraints are particularly important in global equity portfolios where otherwise attractive signals may generate unintended country concentration.

#### Style Factor Neutrality

Let

``` math
\begin{equation}
\mathbf{F}_t
\in
\mathbb{R}^{N_t\times K}
\end{equation}
```

denote security exposures to $`K`$ style factors.

Possible factors include:

- size;

- value;

- momentum;

- quality;

- volatility;

- liquidity;

- leverage;

- growth.

Portfolio factor exposures are

``` math
\begin{equation}
\boxed{
\mathbf{f}_{p,t}
=
\mathbf{F}_t^\top
\mathbf{w}_t
\in
\mathbb{R}^{K}.
}
\end{equation}
```

Exact neutrality requires

``` math
\begin{equation}
\boxed{
\mathbf{F}_t^\top
\mathbf{w}_t
=
\mathbf{0}_{K}.
}
\end{equation}
```

More commonly,

``` math
\begin{equation}
-\mathbf{f}_{\max}
\leq
\mathbf{F}_t^\top
\mathbf{w}_t
\leq
\mathbf{f}_{\max}.
\end{equation}
```

##### Joint Exposure Constraints

Beta, industry, country, and style exposures can be combined into one matrix:

``` math
\begin{equation}
\boxed{
\mathbf{B}_t^{\mathrm{port}}
=
\begin{bmatrix}
\boldsymbol{\beta}_t
&
\mathbf{D}_t
&
\mathbf{C}_t
&
\mathbf{F}_t
\end{bmatrix}
\in
\mathbb{R}^{N_t\times K_{\mathrm{tot}}}.
}
\end{equation}
```

Then a generic exposure constraint is

``` math
\begin{equation}
\boxed{
\mathbf{l}_t
\leq
\left(
\mathbf{B}_t^{\mathrm{port}}
\right)^\top
\mathbf{w}_t
\leq
\mathbf{u}_t.
}
\end{equation}
```

#### Tracking Error Constraints

For benchmark-relative strategies, portfolio risk may be controlled through tracking error.

Let

``` math
\begin{equation}
\mathbf{w}_t^{B}
\in
\mathbb{R}^{N_t}
\end{equation}
```

denote benchmark weights.

Active weights are

``` math
\begin{equation}
\boxed{
\mathbf{a}_t
=
\mathbf{w}_t
-
\mathbf{w}_t^{B}.
}
\end{equation}
```

Ex-ante tracking-error variance is

``` math
\begin{equation}
\boxed{
TE_t^2
=
\mathbf{a}_t^\top
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{a}_t.
}
\end{equation}
```

Tracking error is therefore

``` math
\begin{equation}
\boxed{
TE_t
=
\sqrt{
\mathbf{a}_t^\top
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{a}_t
}.
}
\end{equation}
```

A maximum tracking-error constraint is

``` math
\begin{equation}
\boxed{
\mathbf{a}_t^\top
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{a}_t
\leq
TE_{\max}^{2}.
}
\end{equation}
```

##### Active vs. Absolute Risk

Tracking error measures risk relative to the benchmark, not absolute portfolio risk.

Thus,

``` math
\begin{equation}
\boxed{
\text{Portfolio Volatility}
\neq
\text{Tracking Error}.
}
\end{equation}
```

A portfolio may have high absolute volatility while maintaining low tracking error if its exposures closely resemble the benchmark.

#### Turnover Constraints

Let

``` math
\begin{equation}
\mathbf{w}_{t^-}
\end{equation}
```

denote portfolio weights immediately before rebalancing.

The desired weight change is

``` math
\begin{equation}
\Delta\mathbf{w}_t
=
\mathbf{w}_t
-
\mathbf{w}_{t^-}.
\end{equation}
```

Total traded notional in weight space is

``` math
\begin{equation}
\boxed{
TO_t^{\mathrm{gross}}
=
\sum_{i=1}^{N_t}
|\Delta w_{i,t}|.
}
\end{equation}
```

A hard turnover constraint is

``` math
\begin{equation}
\boxed{
\sum_{i=1}^{N_t}
|w_{i,t}-w_{i,t^-}|
\leq
TO_{\max}.
}
\end{equation}
```

If the half-turnover convention is used,

``` math
\begin{equation}
TO_t^{1/2}
=
\frac{1}{2}
\sum_i
|w_{i,t}-w_{i,t^-}|,
\end{equation}
```

the corresponding limit must be defined consistently.

##### Security-Level Trade Limits

One may also impose

``` math
\begin{equation}
\boxed{
|w_{i,t}-w_{i,t^-}|
\leq
\Delta w_{i,t}^{\max}.
}
\end{equation}
```

This prevents excessively large trades in individual securities even if total portfolio turnover remains below its overall limit.

#### Liquidity and ADV Constraints

Portfolio weights must be compatible with the amount of liquidity available in the market.

Let

``` math
\begin{equation}
A_t
\end{equation}
```

denote portfolio NAV.

The desired currency notional trade in security $`i`$ is

``` math
\begin{equation}
\boxed{
Q_{i,t}
=
A_t
|w_{i,t}-w_{i,t^-}|.
}
\end{equation}
```

Let

``` math
\begin{equation}
\mathrm{ADV}_{i,t}
\end{equation}
```

denote Average Daily Volume in the same currency.

The participation rate is

``` math
\begin{equation}
\boxed{
PR_{i,t}
=
\frac{
A_t
|w_{i,t}-w_{i,t^-}|
}{
\mathrm{ADV}_{i,t}
}.
}
\end{equation}
```

A maximum participation-rate constraint is

``` math
\begin{equation}
\boxed{
PR_{i,t}
\leq
PR_{\max}.
}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
\boxed{
|w_{i,t}-w_{i,t^-}|
\leq
PR_{\max}
\frac{
\mathrm{ADV}_{i,t}
}{
A_t
}.
}
\end{equation}
```

##### Position Capacity Constraint

Liquidity may also constrain total position size rather than only daily trade size.

Suppose the maximum desired position represents no more than $`H`$ days of ADV:

``` math
\begin{equation}
A_t|w_{i,t}|
\leq
H
\,
\mathrm{ADV}_{i,t}.
\end{equation}
```

Then

``` math
\begin{equation}
\boxed{
|w_{i,t}|
\leq
H
\frac{
\mathrm{ADV}_{i,t}
}{
A_t
}.
}
\end{equation}
```

##### AUM Dependence

Because

``` math
\begin{equation}
|w_{i,t}-w_{i,t^-}|_{\max}
\propto
\frac{1}{A_t},
\end{equation}
```

the feasible portfolio becomes more restrictive as AUM increases.

Thus,

``` math
\begin{equation}
\boxed{
A_t\uparrow
\quad\Rightarrow\quad
\text{Liquidity Constraints Tighten}.
}
\end{equation}
```

This establishes the direct link between portfolio constraints and strategy capacity.

#### Short Availability Constraints

A negative desired weight is implementable only if the corresponding security can be borrowed.

Let

``` math
\begin{equation}
H_{i,t}^{\mathrm{short}}
\in
\{0,1\}
\end{equation}
```

denote short availability.

If

``` math
\begin{equation}
H_{i,t}^{\mathrm{short}}=0,
\end{equation}
```

then the portfolio must satisfy

``` math
\begin{equation}
\boxed{
w_{i,t}
\geq
0.
}
\end{equation}
```

##### Borrow Quantity Constraint

Suppose

``` math
\begin{equation}
B_{i,t}^{\$}
\end{equation}
```

denotes the maximum currency notional available to borrow.

Then

``` math
\begin{equation}
A_t
\max(-w_{i,t},0)
\leq
B_{i,t}^{\$}.
\end{equation}
```

Equivalently,

``` math
\begin{equation}
\boxed{
w_{i,t}
\geq
-
\frac{
B_{i,t}^{\$}
}{
A_t
}.
}
\end{equation}
```

##### Borrow-Cost Constraints

If the borrow fee is

``` math
\begin{equation}
b_{i,t},
\end{equation}
```

the strategy may exclude short positions when

``` math
\begin{equation}
b_{i,t}>b_{\max}.
\end{equation}
```

This can be expressed as

``` math
\begin{equation}
b_{i,t}>b_{\max}
\quad\Rightarrow\quad
w_{i,t}\geq0.
\end{equation}
```

Alternatively, borrow cost may remain in the optimization objective rather than being imposed as a hard exclusion.

Thus,

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Borrow Availability}
&\rightarrow
\text{Hard Feasibility Constraint},
\\
\text{Borrow Cost}
&\rightarrow
\text{Constraint or Cost Penalty}.
\end{aligned}
}
\end{equation}
```

##### Combined Feasible Set

The complete feasible set can now be represented schematically as

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathcal{W}_t
=
\Bigg\{
\mathbf{w}\in\mathbb{R}^{N_t}
:\;
&
\|\mathbf{w}\|_1
\leq
G_{\max},
\\
&
N_{\min}
\leq
\mathbf{1}^{\top}\mathbf{w}
\leq
N_{\max},
\\
&
\mathbf{w}^{\min}
\leq
\mathbf{w}
\leq
\mathbf{w}^{\max},
\\
&
\mathbf{l}_B
\leq
\mathbf{B}_t^\top\mathbf{w}
\leq
\mathbf{u}_B,
\\
&
\left(
\mathbf{w}-\mathbf{w}^{B}
\right)^\top
\widehat{\boldsymbol{\Sigma}}_t
\left(
\mathbf{w}-\mathbf{w}^{B}
\right)
\leq
TE_{\max}^{2},
\\
&
\left\|
\mathbf{w}
-
\mathbf{w}_{t^-}
\right\|_1
\leq
TO_{\max},
\\
&
A_t
|w_i-w_{i,t^-}|
\leq
PR_{\max}
\mathrm{ADV}_{i,t},
\quad
\forall i,
\\
&
\text{short-availability constraints hold}
\Bigg\}.
\end{aligned}
}
\end{equation}
```

Not every strategy requires all of these constraints.

The feasible set should contain only restrictions that correspond to actual economic, regulatory, mandate, or implementation requirements.

##### Constraint Interactions and Feasibility

Constraints cannot always be considered independently.

For example, simultaneously requiring

``` math
\begin{equation}
\mathbf{1}^{\top}\mathbf{w}=0,
\end{equation}
```

``` math
\begin{equation}
\boldsymbol{\beta}_t^\top\mathbf{w}=0,
\end{equation}
```

``` math
\begin{equation}
\mathbf{D}_t^\top\mathbf{w}=0,
\end{equation}
```

and very tight position limits may leave no feasible portfolio.

Thus,

``` math
\begin{equation}
\boxed{
\mathcal{W}_t
=
\varnothing
}
\end{equation}
```

is possible.

The backtester must therefore explicitly verify feasibility before solving the optimization problem.

##### Constraint Hierarchy

In practical implementations, it is useful to distinguish between:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Hard Constraints}
&:
\quad
\text{must never be violated},
\\
\text{Soft Constraints}
&:
\quad
\text{may be relaxed at a cost}.
\end{aligned}
}
\end{equation}
```

Hard constraints may include:

- legal shortability;

- mandate leverage limits;

- absolute position limits.

Soft constraints may include:

- preferred factor-neutrality bands;

- turnover targets;

- benchmark-relative sector limits.

A soft constraint can be incorporated using a slack variable.

For example,

``` math
\begin{equation}
-\beta_{\max}-\xi_t
\leq
\boldsymbol{\beta}_t^\top\mathbf{w}_t
\leq
\beta_{\max}+\xi_t,
\end{equation}
```

with

``` math
\begin{equation}
\xi_t\geq0,
\end{equation}
```

and a penalty

``` math
\begin{equation}
-\lambda_{\xi}\xi_t
\end{equation}
```

in the optimization objective.

This preserves feasibility while penalizing departures from the preferred constraint.

##### Constraint Diagnostics

For each optimized portfolio, the backtester should record:

- gross exposure;

- net exposure;

- long and short gross budgets;

- maximum absolute position;

- portfolio beta;

- industry exposures;

- country exposures;

- style-factor exposures;

- ex-ante tracking error;

- portfolio turnover;

- maximum ADV participation rate;

- number of short-constrained securities.

It is also useful to identify which constraints are binding.

For constraint

``` math
\begin{equation}
g_j(\mathbf{w}_t)\leq c_j,
\end{equation}
```

the constraint is binding when

``` math
\begin{equation}
\boxed{
g_j(\mathbf{w}_t)
\approx
c_j.
}
\end{equation}
```

A large number of persistently binding constraints may indicate that the portfolio specification is excessively restrictive or that the raw signal is poorly aligned with the investment mandate.

##### Position in the Portfolio-Construction Pipeline

At this stage, the portfolio engine has defined:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{s}_t^{\mathrm{final}}
&\in
\mathbb{R}^{N_t},
&&
\text{signal},
\\
\widehat{\boldsymbol{\Sigma}}_t
&\in
\mathbb{R}^{N_t\times N_t},
&&
\text{risk model},
\\
\mathcal{J}_t(\mathbf{w})
&&&
\text{optimization objective},
\\
\mathcal{W}_t
&&&
\text{feasible portfolio set}.
\end{aligned}
}
\end{equation}
```

The target portfolio is therefore fully characterized by

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{target}}
=
\underset{\mathbf{w}\in\mathcal{W}_t}{\arg\max}
\;
\mathcal{J}_t(\mathbf{w}).
}
\end{equation}
```

The next stages of the backtester determine how these target weights are scaled, rebalanced, converted into executable trades, and ultimately transformed into realized portfolio returns.

