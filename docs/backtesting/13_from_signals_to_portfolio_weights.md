### From Signals to Portfolio Weights

The previous parts of the backtester transformed raw information into a final investable signal

``` math
\begin{equation}
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
\mathbb{R}^{N_t}.
\end{equation}
```

The signal describes the relative attractiveness of securities, but it does not yet determine how much capital should be allocated to each security.

Portfolio construction begins by defining a mapping from signals to portfolio weights:

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{final}}
\quad
\longrightarrow
\quad
\mathbf{w}_t^{\mathrm{target}}.
}
\end{equation}
```

Let

``` math
\begin{equation}
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
\mathbb{R}^{N_t}
\end{equation}
```

denote the target portfolio weights immediately after the rebalance at time $`t`$.

A positive weight represents a long position,

``` math
\begin{equation}
w_{i,t}^{\mathrm{target}}>0,
\end{equation}
```

a negative weight represents a short position,

``` math
\begin{equation}
w_{i,t}^{\mathrm{target}}<0,
\end{equation}
```

and

``` math
\begin{equation}
w_{i,t}^{\mathrm{target}}=0
\end{equation}
```

means that no position is desired in security $`i`$.

At this stage, the objective is to study direct signal-to-weight mappings. Portfolio-level risk optimization, factor constraints, leverage constraints, turnover penalties, and implementation costs will be introduced subsequently.

Thus, the current section focuses on

``` math
\begin{equation}
\boxed{
\text{Signal Strength}
\rightarrow
\text{Desired Relative Position Size}.
}
\end{equation}
```

#### Signal-to-Weight Mapping Functions

Let

``` math
\begin{equation}
\mathcal{G}_t
\end{equation}
```

denote a signal-to-weight mapping.

In its most general form,

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{raw}}
=
\mathcal{G}_t
\left(
\mathbf{s}_t^{\mathrm{final}}
\right),
}
\end{equation}
```

where

``` math
\begin{equation}
\mathbf{w}_t^{\mathrm{raw}}
\in
\mathbb{R}^{N_t}
\end{equation}
```

denotes the portfolio weights implied directly by the signal before subsequent portfolio-level constraints or risk adjustments.

The mapping may depend only on the ordering of the signal, or it may use its numerical magnitude.

##### Ordinal vs. Cardinal Mapping

If the signal is ordinal, only relative ordering is economically meaningful.

For example,

``` math
\begin{equation}
s_{i,t}^{\mathrm{final}}
>
s_{j,t}^{\mathrm{final}}
\end{equation}
```

means that security $`i`$ is preferred to security $`j`$, but the difference

``` math
\begin{equation}
s_{i,t}^{\mathrm{final}}
-
s_{j,t}^{\mathrm{final}}
\end{equation}
```

need not have a meaningful economic interpretation.

Suitable mappings therefore include:

- quantile portfolios;

- top/bottom $`N`$ portfolios;

- rank-based portfolios.

If the signal is cardinal, its magnitude contains information that may be used directly for position sizing.

Examples include:

- standardized alpha scores;

- calibrated expected returns;

- confidence-adjusted expected returns.

In this case, linear or nonlinear mappings may be appropriate.

Hence,

``` math
\begin{equation}
\boxed{
\text{Nature of Signal}
\rightarrow
\text{Choice of Mapping Function}.
}
\end{equation}
```

##### Raw and Normalized Weights

It is useful to distinguish the raw output of the mapping function from the subsequently normalized portfolio.

Let

``` math
\begin{equation}
\widetilde{\mathbf{w}}_t
=
\mathcal{G}_t
\left(
\mathbf{s}_t^{\mathrm{final}}
\right)
\end{equation}
```

denote unnormalized desired positions.

A normalization operator $`\mathcal{N}`$ can then produce

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{raw}}
=
\mathcal{N}
\left(
\widetilde{\mathbf{w}}_t
\right).
}
\end{equation}
```

For example, a unit-gross normalization is

``` math
\begin{equation}
\boxed{
w_{i,t}^{\mathrm{raw}}
=
\frac{
\widetilde{w}_{i,t}
}{
\sum_{j=1}^{N_t}
\left|
\widetilde{w}_{j,t}
\right|
}.
}
\end{equation}
```

Then

``` math
\begin{equation}
\sum_{i=1}^{N_t}
\left|
w_{i,t}^{\mathrm{raw}}
\right|
=
1.
\end{equation}
```

The desired gross and net exposure conventions will be treated explicitly in a later section.

#### Direct Pure Alpha Construction and Risk Scaling

The signal-to-weight mappings introduced above can be used directly to construct a long–short *Pure Alpha* portfolio without requiring a numerical portfolio optimizer.

This provides an important alternative to optimization-based portfolio construction.

Let

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{final}}
\in
\mathbb{R}^{N_t}
\end{equation}
```

denote the final cross-sectional signal after the transformations and neutralizations developed previously.

A mapping function

``` math
\begin{equation}
\mathcal{G}_t:
\mathbb{R}^{N_t}
\rightarrow
\mathbb{R}^{N_t}
\end{equation}
```

can transform this signal directly into Pure Alpha portfolio weights:

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{PA}
=
\mathcal{G}_t
\left(
\mathbf{s}_t^{\mathrm{final}}
\right),
}
\end{equation}
```

where

``` math
\begin{equation}
\mathbf{w}_t^{PA}
=
\begin{bmatrix}
w_{1,t}^{PA}\\
\vdots\\
w_{N_t,t}^{PA}
\end{bmatrix}
\in
\mathbb{R}^{N_t}.
\end{equation}
```

The superscript $`PA`$ denotes *Pure Alpha*.

The mapping $`\mathcal{G}_t(\cdot)`$ may correspond, for example, to a linear signal mapping, rank weighting, quantile portfolios, or another deterministic mapping rule. These alternatives are developed in the following subsections.

If the signal and mapping procedure have already been designed to satisfy the desired exposure properties, the resulting portfolio can be constructed directly without solving an optimization problem.

Conceptually,

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{final}}
\rightarrow
\mathcal{G}_t
\rightarrow
\mathbf{w}_t^{PA}.
}
\end{equation}
```

##### Direct Construction Without Numerical Optimization

A particularly simple example is a linear mapping.

Suppose that the final signal satisfies

``` math
\begin{equation}
\mathbf{1}^{\top}
\mathbf{s}_t^{\mathrm{final}}
=
0.
\end{equation}
```

A gross-normalized Pure Alpha portfolio can be defined as

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{PA}
=
G^{PA}
\frac{
\mathbf{s}_t^{\mathrm{final}}
}{
\left\|
\mathbf{s}_t^{\mathrm{final}}
\right\|_1
},
}
\end{equation}
```

where

``` math
\begin{equation}
G^{PA}>0
\end{equation}
```

is the desired gross exposure.

By construction,

``` math
\begin{equation}
\left\|
\mathbf{w}_t^{PA}
\right\|_1
=
G^{PA}.
\end{equation}
```

Moreover, because the signal sums to zero,

``` math
\begin{equation}
\mathbf{1}^{\top}
\mathbf{w}_t^{PA}
=
0.
\end{equation}
```

The portfolio is therefore dollar neutral.

More generally, deterministic transformations can be used to impose the desired portfolio structure analytically whenever closed-form mappings are available.

This can be attractive in large-scale backtests because it avoids solving a numerical optimization problem at every rebalance date.

Thus, portfolio construction does not necessarily imply portfolio optimization:

``` math
\begin{equation}
\boxed{
\text{Signal}
\rightarrow
\text{Closed-Form Mapping}
\rightarrow
\text{Pure Alpha Portfolio}
}
\end{equation}
```

may itself constitute a complete portfolio-construction procedure.

##### Alpha-Level Volatility Scaling

The risk of the resulting Pure Alpha portfolio may vary substantially through time even if its gross exposure is kept constant.

Let

``` math
\begin{equation}
\widehat{\boldsymbol{\Sigma}}_t
\in
\mathbb{R}^{N_t\times N_t}
\end{equation}
```

denote the point-in-time covariance estimate.

The ex-ante volatility of the Pure Alpha portfolio is

``` math
\begin{equation}
\boxed{
\widehat{\sigma}_{PA,t}
=
\sqrt{
\left(
\mathbf{w}_t^{PA}
\right)^{\top}
\widehat{\boldsymbol{\Sigma}}_t
\mathbf{w}_t^{PA}
}.
}
\end{equation}
```

Let

``` math
\begin{equation}
\sigma_{PA}^{*}>0
\end{equation}
```

denote the desired Pure Alpha volatility.

An optional isovol scaling coefficient is

``` math
\begin{equation}
\boxed{
\lambda_t^{PA}
=
\frac{
\sigma_{PA}^{*}
}{
\widehat{\sigma}_{PA,t}
}.
}
\end{equation}
```

The risk-scaled Pure Alpha portfolio is then

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{PA,\mathrm{iso}}
=
\lambda_t^{PA}
\mathbf{w}_t^{PA}.
}
\end{equation}
```

Because $`\lambda_t^{PA}`$ is a common scalar applied to all securities, this operation changes the overall scale of the Pure Alpha portfolio without changing its relative composition:

``` math
\begin{equation}
\frac{
w_{i,t}^{PA,\mathrm{iso}}
}{
w_{j,t}^{PA,\mathrm{iso}}
}
=
\frac{
w_{i,t}^{PA}
}{
w_{j,t}^{PA}
}.
\end{equation}
```

The direct Pure Alpha construction may therefore be summarized as

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{final}}
\rightarrow
\mathbf{w}_t^{PA}
\rightarrow
\mathbf{w}_t^{PA,\mathrm{iso}},
}
\end{equation}
```

where the final isovol step is optional.

##### Preservation of Neutrality

Common volatility scaling preserves homogeneous zero-exposure constraints.

Suppose the Pure Alpha portfolio satisfies

``` math
\begin{equation}
\mathbf{B}_t^\top
\mathbf{w}_t^{PA}
=
\mathbf{0},
\end{equation}
```

where

``` math
\begin{equation}
\mathbf{B}_t
\in
\mathbb{R}^{N_t\times K}
\end{equation}
```

contains the exposures against which neutrality is required.

Then

``` math
\begin{equation}
\begin{aligned}
\mathbf{B}_t^\top
\mathbf{w}_t^{PA,\mathrm{iso}}
&=
\mathbf{B}_t^\top
\left(
\lambda_t^{PA}
\mathbf{w}_t^{PA}
\right)
\\
&=
\lambda_t^{PA}
\mathbf{B}_t^\top
\mathbf{w}_t^{PA}
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
\text{Isovol Scaling}
\quad\text{preserves exact zero-exposure constraints}.
}
\end{equation}
```

This includes, when already satisfied by the Pure Alpha weights, dollar neutrality, beta neutrality, industry neutrality, country neutrality, and style-factor neutrality.

##### Pure Alpha as a Standalone Portfolio

The risk-scaled Pure Alpha portfolio may itself be the final strategy.

In this case,

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{final}}
=
\mathbf{w}_t^{PA,\mathrm{iso}},
}
\end{equation}
```

and no optimization engine is required.

This architecture is particularly useful when the desired portfolio can be constructed through simple and transparent closed-form rules:

``` math
\begin{equation}
\boxed{
\text{Final Signal}
\rightarrow
\text{Direct L/S Mapping}
\rightarrow
\text{Optional Isovol}
\rightarrow
\text{Final Pure Alpha Portfolio}.
}
\end{equation}
```

##### Pure Alpha as an Input to a Subsequent Optimizer

Alternatively, the Pure Alpha construction can represent an intermediate research object rather than the final investable portfolio.

For example, the objective may be to translate a long–short Pure Alpha signal into a constrained long-only portfolio.

Information contained in the Pure Alpha strategy can then be used to define an expected-return vector

``` math
\begin{equation}
\widehat{\boldsymbol{\mu}}_t
\in
\mathbb{R}^{N_t}
\end{equation}
```

that subsequently enters the portfolio optimization engine.

Schematically,

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{s}_t^{\mathrm{final}}
&\rightarrow
\mathbf{w}_t^{PA}
\\
&\rightarrow
\text{Pure Alpha Information}
\\
&\rightarrow
\widehat{\boldsymbol{\mu}}_t
\\
&\rightarrow
\text{Constrained Portfolio Optimization}
\\
&\rightarrow
\mathbf{w}_t^{\mathrm{target}}.
\end{aligned}
}
\end{equation}
```

For example, a simple calibration may take the form

``` math
\begin{equation}
\boxed{
\widehat{\boldsymbol{\mu}}_t
=
\kappa_t
\mathbf{w}_t^{PA},
}
\end{equation}
```

where $`\kappa_t`$ converts the relative Pure Alpha direction into expected-return units.

However, an important distinction must be maintained between the *cross-sectional alpha information* and the *risk scaling* applied to the Pure Alpha portfolio.

Indeed,

``` math
\begin{equation}
\mathbf{w}_t^{PA,\mathrm{iso}}
=
\lambda_t^{PA}
\mathbf{w}_t^{PA},
\end{equation}
```

where $`\lambda_t^{PA}`$ depends on forecast portfolio volatility.

The fact that the Pure Alpha portfolio receives more leverage when forecast volatility is low does not, by itself, imply that individual expected returns are proportionally larger.

Therefore, when the Pure Alpha object is used to construct expected returns for a subsequent optimizer, the alpha direction and its portfolio-level risk scale should be conceptually distinguished.

##### Two Different Roles of Isovol Scaling

It is useful to distinguish the alpha-level isovol operation introduced here from the final portfolio-level volatility scaling developed later.

The first operates on the directly constructed Pure Alpha portfolio:

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{PA}
\rightarrow
\mathbf{w}_t^{PA,\mathrm{iso}}.
}
\end{equation}
```

Its purpose is to normalize the risk of the Pure Alpha strategy itself.

The second operates on the target portfolio produced after the complete portfolio-construction process:

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{target}}
\rightarrow
\mathbf{w}_t^{\mathrm{final}}.
}
\end{equation}
```

Its purpose is to control the absolute risk of the final investable portfolio.

These two operations need not both be performed.

If the directly constructed Pure Alpha portfolio is itself the final portfolio, alpha-level isovol may already provide the desired risk scaling.

If a subsequent optimizer materially changes the portfolio composition, however, the volatility of the optimized portfolio generally differs from that of the original Pure Alpha portfolio. A new portfolio-level risk forecast may therefore be required.

Thus,

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Alpha-Level Isovol}
&:
&
\mathbf{w}_t^{PA}
&\rightarrow
\mathbf{w}_t^{PA,\mathrm{iso}},
\\[3pt]
\text{Final Portfolio Isovol}
&:
&
\mathbf{w}_t^{\mathrm{target}}
&\rightarrow
\mathbf{w}_t^{\mathrm{final}}.
\end{aligned}
}
\end{equation}
```

The appropriate architecture depends on whether the Pure Alpha portfolio is used directly as the investment strategy or as an intermediate input to a subsequent portfolio-construction problem.

#### Equal-Weighted Quantile Portfolios

One of the simplest mappings is to divide the investment universe into quantiles according to the final signal.

Let

``` math
\begin{equation}
\mathcal{Q}_{q,t}
\subseteq
\mathcal{U}_t,
\qquad
q=1,\ldots,Q,
\end{equation}
```

denote quantile $`q`$, where $`\mathcal{Q}_{1,t}`$ contains the lowest-signal securities and $`\mathcal{Q}_{Q,t}`$ contains the highest-signal securities.

For a long-only top-quantile portfolio,

``` math
\begin{equation}
\boxed{
w_{i,t}
=
\begin{cases}
\dfrac{1}{|\mathcal{Q}_{Q,t}|},
&
i\in\mathcal{Q}_{Q,t},
\\[0.25cm]
0,
&
\text{otherwise}.
\end{cases}
}
\end{equation}
```

##### Long–Short Quantile Portfolio

A simple dollar-neutral long–short portfolio can buy the highest quantile and short the lowest quantile.

If each side is allocated gross exposure $`G_t/2`$, then

``` math
\begin{equation}
\boxed{
w_{i,t}
=
\begin{cases}
\dfrac{G_t/2}{|\mathcal{Q}_{Q,t}|},
&
i\in\mathcal{Q}_{Q,t},
\\[0.30cm]
-\dfrac{G_t/2}{|\mathcal{Q}_{1,t}|},
&
i\in\mathcal{Q}_{1,t},
\\[0.30cm]
0,
&
\text{otherwise}.
\end{cases}
}
\end{equation}
```

The long-leg gross exposure is

``` math
\begin{equation}
\sum_{i:w_{i,t}>0}w_{i,t}
=
\frac{G_t}{2},
\end{equation}
```

while the absolute short-leg exposure is

``` math
\begin{equation}
\sum_{i:w_{i,t}<0}|w_{i,t}|
=
\frac{G_t}{2}.
\end{equation}
```

Therefore,

``` math
\begin{equation}
\sum_i |w_{i,t}|=G_t
\end{equation}
```

and

``` math
\begin{equation}
\sum_i w_{i,t}=0.
\end{equation}
```

For example, if

``` math
\begin{equation}
G_t=2,
\end{equation}
```

the portfolio is $`100\%`$ long and $`100\%`$ short.

##### Properties

Equal-weighted quantile portfolios are:

- simple;

- transparent;

- relatively insensitive to extreme signal magnitudes;

- appropriate for ordinal signals.

However, all selected securities receive identical weights regardless of the strength of their signals.

#### Top/Bottom $`N`$ Portfolios

Instead of selecting a fixed fraction of the universe, the strategy may select a fixed number of securities.

Let

``` math
\begin{equation}
\mathcal{L}_t^{N}
\end{equation}
```

denote the set containing the $`N_L`$ highest-signal securities and

``` math
\begin{equation}
\mathcal{S}_t^{N}
\end{equation}
```

the set containing the $`N_S`$ lowest-signal securities.

An equal-weighted long–short specification is

``` math
\begin{equation}
\boxed{
w_{i,t}
=
\begin{cases}
\dfrac{G_t/2}{N_L},
&
i\in\mathcal{L}_t^{N},
\\[0.30cm]
-\dfrac{G_t/2}{N_S},
&
i\in\mathcal{S}_t^{N},
\\[0.30cm]
0,
&
\text{otherwise}.
\end{cases}
}
\end{equation}
```

Unlike quantile selection, the number of positions remains constant when the size of the investment universe changes.

##### Concentration Trade-Off

A smaller $`N`$ produces a more concentrated portfolio:

``` math
\begin{equation}
N\downarrow
\quad\Rightarrow\quad
\text{Higher Concentration}.
\end{equation}
```

This may increase exposure to the strongest signals but also increases idiosyncratic risk and sensitivity to individual-security errors.

Conversely,

``` math
\begin{equation}
N\uparrow
\quad\Rightarrow\quad
\text{Greater Diversification},
\end{equation}
```

but potentially weaker average signal strength among selected securities.

#### Rank-Weighted Portfolios

Equal-weighted portfolios use the signal to select securities but ignore differences in relative rank once selection has occurred.

Rank-weighted portfolios preserve more information about the ordering of securities without relying directly on the magnitude of the original signal.

Let

``` math
\begin{equation}
r_{i,t}
\in
\{1,\ldots,N_t\}
\end{equation}
```

denote the cross-sectional rank of security $`i`$, with larger ranks corresponding to more attractive securities.

A centered rank score can be defined as

``` math
\begin{equation}
\boxed{
\widetilde{r}_{i,t}
=
r_{i,t}
-
\frac{N_t+1}{2}.
}
\end{equation}
```

Then

``` math
\begin{equation}
\sum_{i=1}^{N_t}
\widetilde{r}_{i,t}
=
0.
\end{equation}
```

A rank-weighted portfolio can be constructed as

``` math
\begin{equation}
\boxed{
w_{i,t}
=
G_t
\frac{
\widetilde{r}_{i,t}
}{
\sum_{j=1}^{N_t}
|\widetilde{r}_{j,t}|
}.
}
\end{equation}
```

Therefore,

``` math
\begin{equation}
\sum_i |w_{i,t}|=G_t,
\end{equation}
```

while

``` math
\begin{equation}
\sum_i w_{i,t}=0.
\end{equation}
```

##### Percentile Representation

Alternatively, define the percentile rank

``` math
\begin{equation}
p_{i,t}
=
\frac{
r_{i,t}-1
}{
N_t-1
}
\in[0,1].
\end{equation}
```

A centered percentile score is

``` math
\begin{equation}
\boxed{
q_{i,t}
=
p_{i,t}
-
\frac{1}{2}.
}
\end{equation}
```

Weights may then be defined proportionally to $`q_{i,t}`$.

This representation is convenient because its scale does not depend directly on the number of securities in the universe.

#### Linear Signal Mapping

If signal magnitude is meaningful, the simplest cardinal mapping assigns positions directly proportional to the signal:

``` math
\begin{equation}
\boxed{
\widetilde{w}_{i,t}
=
\kappa_t
s_{i,t}^{\mathrm{final}},
}
\end{equation}
```

where $`\kappa_t>0`$ is a scaling parameter.

If only relative weights matter before normalization, $`\kappa_t`$ can be omitted:

``` math
\begin{equation}
\widetilde{w}_{i,t}
=
s_{i,t}^{\mathrm{final}}.
\end{equation}
```

Under unit-gross normalization,

``` math
\begin{equation}
\boxed{
w_{i,t}
=
\frac{
s_{i,t}^{\mathrm{final}}
}{
\sum_{j=1}^{N_t}
|s_{j,t}^{\mathrm{final}}|
}.
}
\end{equation}
```

More generally, for target gross exposure $`G_t`$,

``` math
\begin{equation}
\boxed{
w_{i,t}
=
G_t
\frac{
s_{i,t}^{\mathrm{final}}
}{
\sum_{j=1}^{N_t}
|s_{j,t}^{\mathrm{final}}|
}.
}
\end{equation}
```

##### Net Exposure

Notice that gross normalization alone does not guarantee

``` math
\begin{equation}
\sum_i w_{i,t}=0.
\end{equation}
```

Indeed,

``` math
\begin{equation}
\sum_i w_{i,t}
=
G_t
\frac{
\sum_i s_{i,t}^{\mathrm{final}}
}{
\sum_i |s_{i,t}^{\mathrm{final}}|
}.
\end{equation}
```

Thus, a zero-net portfolio is obtained automatically only if

``` math
\begin{equation}
\boxed{
\sum_i s_{i,t}^{\mathrm{final}}=0.
}
\end{equation}
```

Otherwise, the signal must be centered or the resulting weights must be adjusted if dollar neutrality is required.

##### Interpretation

Linear mapping preserves relative differences in signal magnitude:

``` math
\begin{equation}
\frac{
w_{i,t}
}{
w_{j,t}
}
=
\frac{
s_{i,t}^{\mathrm{final}}
}{
s_{j,t}^{\mathrm{final}}
}
\end{equation}
```

for two securities with non-zero signals before additional constraints.

This is appropriate only when such magnitude differences have a meaningful interpretation.

#### Nonlinear Signal Mapping

A nonlinear mapping applies a function

``` math
\begin{equation}
g:\mathbb{R}\rightarrow\mathbb{R}
\end{equation}
```

to each signal:

``` math
\begin{equation}
\boxed{
\widetilde{w}_{i,t}
=
g
\left(
s_{i,t}^{\mathrm{final}}
\right).
}
\end{equation}
```

Normalized weights are then

``` math
\begin{equation}
\boxed{
w_{i,t}
=
G_t
\frac{
g(s_{i,t}^{\mathrm{final}})
}{
\sum_{j=1}^{N_t}
|g(s_{j,t}^{\mathrm{final}})|
}.
}
\end{equation}
```

##### Power Mapping

One example is the signed power transformation

``` math
\begin{equation}
\boxed{
g(s)
=
\operatorname{sign}(s)
|s|^{p},
}
\end{equation}
```

where

``` math
\begin{equation}
p>0.
\end{equation}
```

If

``` math
\begin{equation}
p>1,
\end{equation}
```

the mapping increases the relative importance of extreme signals.

If

``` math
\begin{equation}
0<p<1,
\end{equation}
```

the mapping compresses differences between large and small signals.

The linear mapping is recovered when

``` math
\begin{equation}
p=1.
\end{equation}
```

##### Bounded Mapping

A bounded function may be used to prevent extreme signals from generating disproportionately large raw positions.

For example,

``` math
\begin{equation}
\boxed{
g(s)
=
\tanh(\kappa s),
}
\end{equation}
```

where $`\kappa>0`$ controls the steepness of the transformation.

For small values of $`s`$,

``` math
\begin{equation}
\tanh(\kappa s)
\approx
\kappa s,
\end{equation}
```

so the mapping is approximately linear.

For large positive or negative signals,

``` math
\begin{equation}
\tanh(\kappa s)
\rightarrow
\pm1.
\end{equation}
```

Thus, the marginal effect of increasingly extreme signals decreases.

##### Exponential Mapping

For a long-only strategy, an exponential transformation may be used:

``` math
\begin{equation}
\widetilde{w}_{i,t}
=
\exp
\left(
\kappa s_{i,t}^{\mathrm{final}}
\right).
\end{equation}
```

Normalized weights become

``` math
\begin{equation}
\boxed{
w_{i,t}
=
\frac{
\exp(\kappa s_{i,t}^{\mathrm{final}})
}{
\sum_{j=1}^{N_t}
\exp(\kappa s_{j,t}^{\mathrm{final}})
}.
}
\end{equation}
```

This is equivalent to a softmax mapping.

The parameter $`\kappa`$ controls concentration:

``` math
\begin{equation}
\kappa\rightarrow0
\quad\Rightarrow\quad
w_{i,t}\rightarrow\frac{1}{N_t},
\end{equation}
```

whereas larger values of $`\kappa`$ increasingly concentrate the portfolio in high-signal securities.

#### Threshold-Based Mapping

A strategy may choose to hold positions only when the signal exceeds a minimum conviction threshold.

Let

``` math
\begin{equation}
\tau_t>0
\end{equation}
```

denote the threshold.

A simple symmetric rule is

``` math
\begin{equation}
\boxed{
\widetilde{w}_{i,t}
=
\begin{cases}
s_{i,t}^{\mathrm{final}},
&
|s_{i,t}^{\mathrm{final}}|>\tau_t,
\\[0.20cm]
0,
&
|s_{i,t}^{\mathrm{final}}|\leq\tau_t.
\end{cases}
}
\end{equation}
```

The surviving positions can subsequently be normalized to the desired gross exposure.

##### Binary Threshold Mapping

A more aggressive simplification ignores signal magnitude once the threshold is crossed:

``` math
\begin{equation}
\boxed{
\widetilde{w}_{i,t}
=
\begin{cases}
+1,
&
s_{i,t}^{\mathrm{final}}>\tau_t,
\\
0,
&
-\tau_t
\leq
s_{i,t}^{\mathrm{final}}
\leq
\tau_t,
\\
-1,
&
s_{i,t}^{\mathrm{final}}<-\tau_t.
\end{cases}
}
\end{equation}
```

This creates three regions:

``` math
\begin{equation}
\boxed{
\text{Short}
\qquad
\text{No Position}
\qquad
\text{Long}.
}
\end{equation}
```

##### Soft Thresholding

Instead of introducing a discontinuity at $`\tau_t`$, one may use

``` math
\begin{equation}
\boxed{
g(s)
=
\operatorname{sign}(s)
\max
\left(
|s|-\tau_t,
0
\right).
}
\end{equation}
```

Thus,

``` math
\begin{equation}
\widetilde{w}_{i,t}
=
g
\left(
s_{i,t}^{\mathrm{final}}
\right).
\end{equation}
```

Small signals are mapped to zero, while larger signals increase continuously beyond the threshold.

##### Economic Motivation

Thresholding can be useful when small signals are believed to contain little economic information.

It may also reduce the number of positions and avoid trading on weak changes in estimated attractiveness.

However, thresholding introduces an additional parameter and can create instability around the threshold.

A security moving from

``` math
\begin{equation}
s_{i,t}
=
\tau_t-\epsilon
\end{equation}
```

to

``` math
\begin{equation}
s_{i,t+1}
=
\tau_t+\epsilon
\end{equation}
```

may suddenly enter the portfolio despite an economically negligible change in the underlying signal.

Such discontinuities can contribute to turnover.

#### Conviction-Weighted Portfolios

A conviction-weighted portfolio explicitly allocates more capital to securities for which the investment signal is stronger.

In its simplest form,

``` math
\begin{equation}
\boxed{
|\widetilde{w}_{i,t}|
=
g
\left(
|s_{i,t}^{\mathrm{final}}|
\right),
}
\end{equation}
```

where $`g(\cdot)`$ is increasing.

The sign of the position is determined by the sign of the signal:

``` math
\begin{equation}
\boxed{
\widetilde{w}_{i,t}
=
\operatorname{sign}
\left(
s_{i,t}^{\mathrm{final}}
\right)
g
\left(
|s_{i,t}^{\mathrm{final}}|
\right).
}
\end{equation}
```

##### Conviction Within Selected Tails

Conviction weighting can also be combined with quantile or top/bottom selection.

Suppose

``` math
\begin{equation}
\mathcal{L}_t
\end{equation}
```

and

``` math
\begin{equation}
\mathcal{S}_t
\end{equation}
```

denote the selected long and short sets.

For the long leg,

``` math
\begin{equation}
\boxed{
w_{i,t}^{L}
=
\frac{G_t^{L}
g(s_{i,t}^{\mathrm{final}})}
{
\sum_{j\in\mathcal{L}_t}
g(s_{j,t}^{\mathrm{final}})
},
\qquad
i\in\mathcal{L}_t,
}
\end{equation}
```

where

``` math
\begin{equation}
G_t^{L}>0
\end{equation}
```

is the desired long gross exposure.

For the short leg, using a positive conviction function of signal magnitude,

``` math
\begin{equation}
\boxed{
w_{i,t}^{S}
=
-
\frac{
G_t^{S}
g(|s_{i,t}^{\mathrm{final}}|)
}{
\sum_{j\in\mathcal{S}_t}
g(|s_{j,t}^{\mathrm{final}}|)
},
\qquad
i\in\mathcal{S}_t,
}
\end{equation}
```

where

``` math
\begin{equation}
G_t^{S}>0
\end{equation}
```

denotes the absolute short gross exposure.

Then

``` math
\begin{equation}
\sum_{i\in\mathcal{L}_t}
w_{i,t}^{L}
=
G_t^{L},
\end{equation}
```

and

``` math
\begin{equation}
\sum_{i\in\mathcal{S}_t}
|w_{i,t}^{S}|
=
G_t^{S}.
\end{equation}
```

##### Signal Strength vs. Forecast Confidence

Conviction should not necessarily be identified with signal magnitude alone.

A large signal may have low estimation confidence.

Suppose

``` math
\begin{equation}
c_{i,t}\in[0,1]
\end{equation}
```

denotes a confidence measure.

One may define effective conviction as

``` math
\begin{equation}
\boxed{
\chi_{i,t}
=
c_{i,t}
\left|
s_{i,t}^{\mathrm{final}}
\right|.
}
\end{equation}
```

Then

``` math
\begin{equation}
\widetilde{w}_{i,t}
=
\operatorname{sign}
\left(
s_{i,t}^{\mathrm{final}}
\right)
g(\chi_{i,t}).
\end{equation}
```

This distinguishes

``` math
\begin{equation}
\boxed{
\text{Strength of Investment View}
}
\end{equation}
```

from

``` math
\begin{equation}
\boxed{
\text{Confidence in the Investment View}.
}
\end{equation}
```

##### Comparison of Direct Mapping Approaches

The main direct signal-to-weight mappings can be summarized as

``` math
\begin{equation}
\boxed{
\begin{array}{lll}
\text{Quantile Mapping}
&
\rightarrow
&
\text{Group membership determines position},
\\[0.15cm]
\text{Top/Bottom }N
&
\rightarrow
&
\text{Fixed number of extreme securities},
\\[0.15cm]
\text{Rank Mapping}
&
\rightarrow
&
\text{Relative ordering determines position size},
\\[0.15cm]
\text{Linear Mapping}
&
\rightarrow
&
w_i\propto s_i,
\\[0.15cm]
\text{Nonlinear Mapping}
&
\rightarrow
&
w_i\propto g(s_i),
\\[0.15cm]
\text{Threshold Mapping}
&
\rightarrow
&
\text{Weak signals receive zero weight},
\\[0.15cm]
\text{Conviction Mapping}
&
\rightarrow
&
\text{Position size increases with conviction}.
\end{array}
}
\end{equation}
```

There is no universally optimal mapping.

The appropriate choice depends on the economic meaning of the signal, its predictive relationship with future returns, its stability, and the intended portfolio architecture.

##### From Raw Mapped Weights to Portfolio Construction

The mappings developed in this section produce a first portfolio representation

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{final}}
\quad
\overset{\mathcal{G}_t}{\longrightarrow}
\quad
\mathbf{w}_t^{\mathrm{raw}}.
}
\end{equation}
```

However,

``` math
\begin{equation}
\mathbf{w}_t^{\mathrm{raw}}
\end{equation}
```

should not necessarily be interpreted as the final implemented portfolio.

It may still need to satisfy requirements concerning:

- long and short gross exposure;

- net exposure;

- leverage;

- individual position limits;

- sector, country, beta, and factor exposures;

- portfolio volatility;

- diversification;

- liquidity;

- turnover;

- transaction costs.

The portfolio-construction problem therefore continues from

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{final}}
\rightarrow
\mathbf{w}_t^{\mathrm{raw}}
\rightarrow
\mathbf{w}_t^{\mathrm{target}}
\rightarrow
\mathbf{w}_t^{\mathrm{implemented}}.
}
\end{equation}
```

The next sections determine how the raw signal-implied positions should be scaled, constrained, and optimized before they become actual portfolio holdings.

