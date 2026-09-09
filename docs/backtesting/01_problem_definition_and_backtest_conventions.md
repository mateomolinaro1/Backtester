### Problem Definition and Backtest Conventions

A backtest is a numerical simulation of an investment strategy using historical data. Its objective is to estimate how a systematic investment process would have behaved if it had been implemented historically under a precisely defined set of information, portfolio construction, execution, and transaction-cost assumptions.

A quantitative investment strategy can be represented as a sequence of transformations:

``` math
\begin{equation}
\boxed{
\mathcal{D}_t
\longrightarrow
X_t
\longrightarrow
s_t
\longrightarrow
\widetilde{s}_t
\longrightarrow
w_t^{\mathrm{target}}
\longrightarrow
w_t
\longrightarrow
R_{p,t\rightarrow t+1}
}
\end{equation}
```

where:

- $`\mathcal{D}_t`$ denotes the raw data available to the investor at time $`t`$;

- $`X_t`$ denotes the set of features constructed from these data;

- $`s_t`$ denotes the raw investment signal;

- $`\widetilde{s}_t`$ denotes the final processed signal after operations such as standardization, ranking, combination, smoothing, or neutralization;

- $`w_t^{\mathrm{target}}`$ denotes the target portfolio produced by the portfolio-construction process;

- $`w_t`$ denotes the portfolio that is actually implemented after accounting for constraints, execution assumptions, and market frictions;

- $`R_{p,t\rightarrow t+1}`$ denotes the subsequent realized portfolio return over the holding period.

The central principle underlying the entire backtesting framework is that every investment decision made at time $`t`$ must depend exclusively on information that would have been available to the investor at that time.

Let $`\mathcal{I}_t`$ denote the investor’s information set at time $`t`$. The portfolio decision must satisfy

``` math
\begin{equation}
\boxed{
w_t = f(\mathcal{I}_t)
}
\end{equation}
```

for some portfolio-construction function $`f`$.

More formally, every input used in the portfolio decision must be $`\mathcal{I}_t`$-measurable. In particular,

``` math
\begin{equation}
X_t,
\qquad
s_t,
\qquad
\widetilde{s}_t,
\qquad
w_t
\end{equation}
```

must be functions exclusively of information contained in $`\mathcal{I}_t`$.

Future information must therefore not enter the decision rule:

``` math
\begin{equation}
\mathcal{I}_t
\cap
\left\{
\text{information revealed strictly after } t
\right\}
=
\varnothing.
\end{equation}
```

This apparently simple condition is one of the most important requirements of a valid backtest. Violations generate look-ahead bias and can substantially overstate the historical performance of an investment strategy.

Before constructing signals or portfolios, the investment problem and the backtesting conventions must therefore be explicitly defined.

#### Investment Objective

The first step consists of defining what the investment strategy is designed to achieve.

Depending on the application, the objective may be to:

- maximize absolute returns;

- maximize returns relative to a benchmark;

- maximize risk-adjusted returns;

- generate market-neutral alpha;

- minimize portfolio risk;

- track a benchmark while generating incremental alpha;

- maximize expected utility;

- maximize expected returns subject to risk, exposure, liquidity, turnover, or implementation constraints.

At a general level, portfolio construction can be represented as the optimization problem

``` math
\begin{equation}
w_t^*
=
\underset{w}{\arg\max}
\;
\mathcal{J}
\left(
w;
\mu_t,
\Sigma_t,
w_{t^-},
\mathcal{C}_t
\right),
\end{equation}
```

where:

- $`\mu_t \in \mathbb{R}^{N_t}`$ is the vector of expected asset returns;

- $`\Sigma_t \in \mathbb{R}^{N_t \times N_t}`$ is the estimated covariance matrix of asset returns;

- $`w_{t^-}`$ denotes the portfolio immediately before rebalancing at time $`t`$;

- $`\mathcal{C}_t`$ represents portfolio constraints and market frictions;

- $`N_t`$ denotes the number of investable securities at time $`t`$.

A common mean–variance specification augmented with implementation costs is

``` math
\begin{equation}
\boxed{
w_t^*
=
\underset{w}{\arg\max}
\left[
\mu_t^\top w
-
\frac{\lambda}{2}
w^\top \Sigma_t w
-
C_t(w,w_{t^-})
\right]
}
\end{equation}
```

subject to

``` math
\begin{equation}
w \in \mathcal{W}_t,
\end{equation}
```

where $`\lambda>0`$ is a risk-aversion parameter, $`C_t(w,w_{t^-})`$ represents expected implementation costs, and $`\mathcal{W}_t`$ denotes the feasible set of portfolios.

Importantly, not every systematic investment strategy requires explicit optimization. A strategy may instead directly transform cross-sectional signal values into portfolio weights.

For example,

``` math
\begin{equation}
w_{i,t}
=
\frac{s_{i,t}}
{\sum_{j=1}^{N_t}|s_{j,t}|}.
\end{equation}
```

Portfolio optimization should therefore be viewed as one possible signal-to-weight mapping rather than as a necessary component of every backtesting framework.

#### Investment Universe and Asset Class

Let

``` math
\begin{equation}
\mathcal{U}_t
=
\left\{
1,\ldots,N_t
\right\}
\end{equation}
```

denote the investment universe at time $`t`$.

The universe may vary through time:

``` math
\begin{equation}
\mathcal{U}_t
\neq
\mathcal{U}_{t+1}.
\end{equation}
```

This point is fundamental. Using the current investment universe throughout historical periods creates survivorship bias because securities that disappeared through bankruptcy, delisting, acquisition, or other corporate events are incorrectly excluded from historical observations.

The universe definition should specify at least:

- asset class;

- geographical coverage;

- eligible exchanges;

- eligible security types;

- minimum market capitalization;

- minimum liquidity;

- minimum security price;

- minimum trading history;

- data-availability requirements;

- shortability requirements for short portfolios.

The eligibility of security $`i`$ at time $`t`$ can be represented by the indicator

``` math
\begin{equation}
I_{i,t}^{\mathrm{eligible}}
=
\begin{cases}
1,
&
\text{if security } i
\text{ satisfies all eligibility conditions at } t,
\\[0.2cm]
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

The dynamic investment universe is therefore

``` math
\begin{equation}
\boxed{
\mathcal{U}_t
=
\left\{
i:
I_{i,t}^{\mathrm{eligible}}=1
\right\}.
}
\end{equation}
```

Importantly, the eligibility rule must itself respect the information set $`\mathcal{I}_t`$. For example, a future delisting cannot be used retrospectively to exclude a stock from today’s investment universe.

#### Prediction Target and Investment Horizon

For predictive strategies, the target variable must be precisely defined.

Let $`P_{i,t}`$ denote the price of asset $`i`$ at time $`t`$. The simple return between $`t`$ and $`t+h`$ is

``` math
\begin{equation}
R_{i,t\rightarrow t+h}
=
\frac{P_{i,t+h}}{P_{i,t}}-1.
\end{equation}
```

The corresponding logarithmic return is

``` math
\begin{equation}
r_{i,t\rightarrow t+h}
=
\log(P_{i,t+h})
-
\log(P_{i,t}).
\end{equation}
```

A predictive model may therefore estimate

``` math
\begin{equation}
\widehat{R}_{i,t\rightarrow t+h}
=
f(X_{i,t}),
\end{equation}
```

where $`X_{i,t}`$ contains exclusively information available at time $`t`$.

The target does not necessarily have to be the future raw return. Possible targets include:

- future absolute returns;

- future excess returns;

- benchmark-relative returns;

- market- or factor-adjusted returns;

- cross-sectional return ranks;

- return signs;

- probabilities of outperforming;

- future volatility;

- future risk-adjusted returns.

For example, a cross-sectional model may directly predict a relative return:

``` math
\begin{equation}
Y_{i,t+h}
=
R_{i,t\rightarrow t+h}
-
R_{B,t\rightarrow t+h},
\end{equation}
```

where $`R_{B,t\rightarrow t+h}`$ denotes the benchmark return over the same horizon.

Alternatively, the target may be a cross-sectional rank:

``` math
\begin{equation}
Y_{i,t+h}
=
\operatorname{Rank}
\left(
R_{i,t\rightarrow t+h}
\right).
\end{equation}
```

The prediction horizon $`h`$ should be economically consistent with the expected persistence of the underlying signal and the intended holding period.

However, the prediction horizon and the holding period need not be identical. This distinction becomes particularly important when overlapping forecasts or staggered portfolios are employed.

#### Rebalancing Frequency and Holding Period

Let

``` math
\begin{equation}
\mathcal{T}^{\mathrm{reb}}
=
\left\{
t_0,t_1,\ldots,t_K
\right\}
\end{equation}
```

denote the set of portfolio rebalancing dates.

Typical rebalancing frequencies include:

- daily;

- weekly;

- monthly;

- quarterly.

At each rebalancing date $`t_k`$, the strategy determines a new target portfolio

``` math
\begin{equation}
w_{t_k}^{\mathrm{target}}.
\end{equation}
```

If no trading occurs between $`t_k`$ and $`t_{k+1}`$, the *number of shares* held remains unchanged. The portfolio weights, however, generally drift because individual securities experience different returns.

If $`w_{i,t_k}`$ denotes the implemented weight immediately after rebalancing, the weight immediately before the next rebalance satisfies

``` math
\begin{equation}
w_{i,t_{k+1}^{-}}
=
\frac{
w_{i,t_k}
\left(
1+R_{i,t_k\rightarrow t_{k+1}}
\right)
}{
1+
R_{p,t_k\rightarrow t_{k+1}}
},
\end{equation}
```

in the simplified case of a fully invested long-only portfolio without cash flows or intermediate trading.

Thus,

``` math
\begin{equation}
w_{t_{k+1}^{-}}
\neq
w_{t_k}
\end{equation}
```

in general.

It is therefore important to distinguish:

``` math
\begin{equation}
\boxed{
w_{t_k}
\quad
\text{from}
\quad
w_{t_{k+1}^{-}}.
}
\end{equation}
```

The former denotes the portfolio immediately after rebalancing, while the latter denotes the portfolio obtained after market-driven weight drift and immediately before the next rebalance.

The rebalancing frequency and the prediction horizon are related but conceptually distinct.

For example, a model may predict one-month returns while the portfolio is rebalanced weekly. Successive predictions then correspond to overlapping forecast horizons.

This feature has implications for:

- portfolio construction;

- turnover;

- strategy capacity;

- autocorrelation of portfolio returns;

- statistical inference.

#### Long-Only and Long–Short Strategies

Let

``` math
\begin{equation}
w_t
=
\begin{bmatrix}
w_{1,t}
&
\cdots
&
w_{N_t,t}
\end{bmatrix}^{\top}
\in
\mathbb{R}^{N_t}
\end{equation}
```

denote the portfolio-weight vector.

For a long-only portfolio,

``` math
\begin{equation}
w_{i,t}\geq 0
\qquad
\forall i.
\end{equation}
```

A fully invested long-only portfolio generally satisfies

``` math
\begin{equation}
\sum_{i=1}^{N_t}
w_{i,t}
=
1.
\end{equation}
```

For a long–short portfolio,

``` math
\begin{equation}
w_{i,t}
\in
\mathbb{R},
\end{equation}
```

where positive weights represent long positions and negative weights represent short positions.

Define the total long exposure as

``` math
\begin{equation}
L_t
=
\sum_{i=1}^{N_t}
\max(w_{i,t},0),
\end{equation}
```

and the absolute short exposure as

``` math
\begin{equation}
S_t
=
\sum_{i=1}^{N_t}
\max(-w_{i,t},0).
\end{equation}
```

The gross exposure is

``` math
\begin{equation}
\boxed{
G_t
=
L_t+S_t
=
\sum_{i=1}^{N_t}
|w_{i,t}|
}
\end{equation}
```

while the net exposure is

``` math
\begin{equation}
\boxed{
E_t^{\mathrm{net}}
=
L_t-S_t
=
\sum_{i=1}^{N_t}
w_{i,t}.
}
\end{equation}
```

The notation $`E_t^{\mathrm{net}}`$ is used rather than $`N_t`$ to avoid confusion with $`N_t`$, the number of securities in the investment universe.

For example, a dollar-neutral portfolio with $`100\%`$ long exposure and $`100\%`$ short exposure satisfies

``` math
\begin{equation}
L_t=1,
\qquad
S_t=1.
\end{equation}
```

Consequently,

``` math
\begin{equation}
G_t=2,
\qquad
E_t^{\mathrm{net}}=0.
\end{equation}
```

The portfolio therefore has $`200\%`$ gross exposure while remaining dollar neutral.

#### Benchmark Definition

Let $`R_{B,t}`$ denote the return of the strategy benchmark.

The appropriate benchmark depends on the investment objective.

For an absolute-return or market-neutral strategy, the relevant benchmark may be cash or the risk-free rate.

For a benchmark-relative strategy, the active return is

``` math
\begin{equation}
R_t^{\mathrm{active}}
=
R_{p,t}
-
R_{B,t}.
\end{equation}
```

The active portfolio weights can similarly be defined as

``` math
\begin{equation}
w_t^{\mathrm{active}}
=
w_t-w_t^B,
\end{equation}
```

where $`w_t^B`$ denotes the benchmark portfolio weights.

For a fully invested portfolio and benchmark,

``` math
\begin{equation}
\mathbf{1}^{\top}w_t
=
1
\end{equation}
```

and

``` math
\begin{equation}
\mathbf{1}^{\top}w_t^B
=
1.
\end{equation}
```

Therefore,

``` math
\begin{equation}
\mathbf{1}^{\top}
w_t^{\mathrm{active}}
=
0.
\end{equation}
```

This distinction becomes particularly important when analyzing:

- excess returns;

- tracking error;

- information ratios;

- active risk;

- active factor exposures;

- performance attribution.

#### Information Sets and Timing Conventions

Timing conventions constitute one of the fundamental components of a valid backtest.

Let

``` math
\begin{equation}
\mathcal{I}_t
\end{equation}
```

denote all information that could realistically have been observed by the investor at decision time $`t`$.

Every quantity used to construct the portfolio must be measurable with respect to $`\mathcal{I}_t`$.

Therefore,

``` math
\begin{equation}
X_t,
\qquad
s_t,
\qquad
\widetilde{s}_t,
\qquad
w_t
\end{equation}
```

must all be $`\mathcal{I}_t`$-measurable.

By contrast, future returns are not observable at the decision date:

``` math
\begin{equation}
R_{t\rightarrow t+1}
\notin
\mathcal{I}_t.
\end{equation}
```

Hence, the fundamental backtesting sequence is

``` math
\begin{equation}
\boxed{
\mathcal{I}_t
\longrightarrow
X_t
\longrightarrow
s_t
\longrightarrow
w_t
\longrightarrow
R_{t\rightarrow t+1}.
}
\end{equation}
```

More generally, it is useful to distinguish four timestamps:

``` math
\begin{equation}
t^{\mathrm{data}}
\leq
t^{\mathrm{signal}}
\leq
t^{\mathrm{decision}}
\leq
t^{\mathrm{execution}}.
\end{equation}
```

These correspond respectively to:

- the time at which the latest required data become available;

- the time at which the signal can be computed;

- the time at which the portfolio decision is made;

- the time at which the corresponding trade is executed.

For example, suppose that a strategy uses the closing price on trading day $`t`$ to compute a momentum signal.

The signal cannot be known until the closing price itself has been observed. Therefore, assuming both

``` math
\begin{equation}
s_t
=
f(P_t^{\mathrm{close}})
\end{equation}
```

and execution at exactly $`P_t^{\mathrm{close}}`$ may introduce look-ahead bias unless the trading mechanism explicitly makes such execution feasible.

A conservative timing convention is

``` math
\begin{equation}
\boxed{
P_t^{\mathrm{close}}
\rightarrow
s_t
\rightarrow
w_t^{\mathrm{target}}
\rightarrow
\text{execution at } t+1.
}
\end{equation}
```

The exact convention depends on the trading process, data timestamp, order type, market, and assumed execution mechanism.

The same principle applies to fundamental data.

Suppose a firm’s annual accounting variable corresponds to the fiscal year ending on December 31 but the financial statement is released on March 15 of the following year.

The accounting information cannot enter $`\mathcal{I}_t`$ before March 15.

Thus,

``` math
\begin{equation}
\boxed{
\text{economic reference date}
\neq
\text{information availability date}.
}
\end{equation}
```

For backtesting purposes, the relevant date is generally the date at which the information became observable by market participants.

#### Execution Assumptions

A backtest must define the price at which hypothetical transactions are assumed to occur.

Common execution assumptions include:

- closing price;

- next-day opening price;

- Volume-Weighted Average Price (VWAP);

- Time-Weighted Average Price (TWAP);

- market mid-price plus an estimated execution cost.

Let

``` math
\begin{equation}
P_{i,t}^{\mathrm{exec}}
\end{equation}
```

denote the assumed execution price of security $`i`$.

If $`\Delta q_{i,t}`$ shares are traded at time $`t`$, the corresponding traded notional is

``` math
\begin{equation}
V_{i,t}^{\mathrm{trade}}
=
\Delta q_{i,t}
P_{i,t}^{\mathrm{exec}}.
\end{equation}
```

Execution assumptions must be compatible with the information timing convention.

In particular, an execution price that was already determined before the signal could have been computed cannot generally be used.

The backtest should therefore distinguish explicitly between

``` math
\begin{equation}
\boxed{
\text{signal price}
\neq
\text{execution price}
\neq
\text{valuation price},
}
\end{equation}
```

unless the investment process provides a valid economic and operational reason for these prices to coincide.

Execution assumptions become increasingly important as turnover increases and the strategy’s investment horizon decreases.

#### Gross Exposure, Net Exposure, and Leverage

Gross and net exposures characterize different dimensions of portfolio positioning.

Recall that

``` math
\begin{equation}
G_t
=
\sum_{i=1}^{N_t}
|w_{i,t}|
\end{equation}
```

and

``` math
\begin{equation}
E_t^{\mathrm{net}}
=
\sum_{i=1}^{N_t}
w_{i,t}.
\end{equation}
```

A portfolio can therefore have low net exposure while simultaneously carrying substantial gross exposure.

For example,

``` math
\begin{equation}
L_t=1.5,
\qquad
S_t=1.5
\end{equation}
```

implies

``` math
\begin{equation}
G_t=3,
\qquad
E_t^{\mathrm{net}}=0.
\end{equation}
```

The portfolio is dollar neutral but carries $`300\%`$ gross exposure.

This illustrates the important distinction

``` math
\begin{equation}
\boxed{
\text{Dollar neutrality}
\neq
\text{Low risk}
\neq
\text{Beta neutrality}.
}
\end{equation}
```

Suppose

``` math
\begin{equation}
\beta_t
=
\begin{bmatrix}
\beta_{1,t}\\
\vdots\\
\beta_{N_t,t}
\end{bmatrix}
\end{equation}
```

denotes the vector of individual security betas relative to a market factor.

Under the standard linear exposure approximation, the portfolio beta is

``` math
\begin{equation}
\boxed{
\beta_{p,t}
=
w_t^\top\beta_t.
}
\end{equation}
```

Dollar neutrality requires

``` math
\begin{equation}
\mathbf{1}^\top w_t
=
0,
\end{equation}
```

whereas beta neutrality requires

``` math
\begin{equation}
\beta_t^\top w_t
=
0.
\end{equation}
```

In general,

``` math
\begin{equation}
\boxed{
\mathbf{1}^\top w_t=0
\;\not\Rightarrow\;
\beta_t^\top w_t=0.
}
\end{equation}
```

A dollar-neutral portfolio may therefore retain significant systematic market risk.

Gross exposure, net exposure, beta exposure, factor exposures, and ex-ante portfolio volatility should consequently be treated as distinct quantities throughout portfolio construction and risk management.

#### Risk and Volatility Targets

Many systematic strategies target a predefined level of portfolio volatility.

Let

``` math
\begin{equation}
\widehat{\sigma}_{p,t}
\end{equation}
```

denote the ex-ante estimate of annualized portfolio volatility available at time $`t`$, and let

``` math
\begin{equation}
\sigma^{\mathrm{target}}
\end{equation}
```

denote the desired volatility target.

A simple volatility-scaling coefficient is

``` math
\begin{equation}
\lambda_t
=
\frac{
\sigma^{\mathrm{target}}
}{
\widehat{\sigma}_{p,t}
}.
\end{equation}
```

The scaled portfolio is then

``` math
\begin{equation}
\boxed{
w_t^{\mathrm{scaled}}
=
\lambda_t w_t.
}
\end{equation}
```

If the portfolio volatility is estimated using a covariance matrix,

``` math
\begin{equation}
\widehat{\sigma}_{p,t}
=
\sqrt{
w_t^\top
\widehat{\Sigma}_t
w_t
},
\end{equation}
```

where $`\widehat{\Sigma}_t`$ is an ex-ante covariance estimate constructed using information available at time $`t`$.

If $`\widehat{\Sigma}_t`$ represents a daily covariance matrix, annualized volatility can be written as

``` math
\begin{equation}
\widehat{\sigma}_{p,t}^{\mathrm{ann}}
=
\sqrt{
252
w_t^\top
\widehat{\Sigma}_t
w_t
}.
\end{equation}
```

Alternatively, volatility may be estimated directly from historical portfolio returns.

For example,

``` math
\begin{equation}
\widehat{\sigma}_{p,t}
=
g
\left(
R_{p,t},
R_{p,t-1},
\ldots,
R_{p,t-L+1}
\right).
\end{equation}
```

The estimator must satisfy the information constraint and must therefore not use future portfolio returns.

In practice, leverage caps are frequently combined with volatility targeting:

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
\lambda_{\max}
\right).
}
\end{equation}
```

This prevents the strategy from taking extreme leverage when estimated volatility becomes unusually low.

Additional smoothing or bounds may also be imposed on changes in leverage in order to avoid excessive turnover.

#### Transaction Cost Assumptions

A realistic backtest must account for the costs associated with implementing portfolio decisions. A strategy may exhibit attractive gross performance while becoming economically unattractive once trading costs, market impact, financing, and short-borrowing costs are taken into account.

It is useful to distinguish between two broad categories of implementation costs:

1.  **Trading costs**, which are generated when positions are bought or sold;

2.  **Holding and financing costs**, which arise from maintaining positions through time.

The distinction is important because trading costs are primarily related to changes in portfolio positions, whereas financing and borrowing costs depend primarily on the positions held and the duration for which they are maintained.

##### Portfolio Trades and Weight Changes

Let

``` math
\begin{equation}
w_{t^-}
\end{equation}
```

denote the vector of portfolio weights immediately before the rebalance at time $`t`$, after accounting for the drift of the existing portfolio, and let

``` math
\begin{equation}
w_t
\end{equation}
```

denote the implemented portfolio weights immediately after the rebalance.

The required change in portfolio weights is therefore

``` math
\begin{equation}
\boxed{
\Delta w_t
=
w_t-w_{t^-}.
}
\end{equation}
```

At the security level,

``` math
\begin{equation}
\Delta w_{i,t}
=
w_{i,t}-w_{i,t^-}.
\end{equation}
```

A positive value,

``` math
\begin{equation}
\Delta w_{i,t}>0,
\end{equation}
```

corresponds to a net purchase of security $`i`$, whereas

``` math
\begin{equation}
\Delta w_{i,t}<0
\end{equation}
```

corresponds to a net sale.

Define the purchased and sold notionals, expressed as fractions of portfolio net asset value, as

``` math
\begin{equation}
B_t
=
\sum_{i=1}^{N_t}
\max(\Delta w_{i,t},0),
\end{equation}
```

and

``` math
\begin{equation}
S_t^{\mathrm{trade}}
=
\sum_{i=1}^{N_t}
\max(-\Delta w_{i,t},0).
\end{equation}
```

The notation $`S_t^{\mathrm{trade}}`$ is used here to distinguish traded sales from the portfolio’s short exposure.

The total traded notional is therefore

``` math
\begin{equation}
\boxed{
T_t
=
B_t
+
S_t^{\mathrm{trade}}
=
\sum_{i=1}^{N_t}
|\Delta w_{i,t}|.
}
\end{equation}
```

##### One-Way Turnover and Total Traded Notional

Turnover is not uniquely defined in the literature or in industry practice. Two related conventions are commonly encountered.

The first reports the *total traded notional*:

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

This quantity counts both purchases and sales.

A second convention reports *one-way turnover*:

``` math
\begin{equation}
\boxed{
TO_t^{\mathrm{one\text{-}way}}
=
\frac{1}{2}
\sum_{i=1}^{N_t}
|\Delta w_{i,t}|.
}
\end{equation}
```

The origin of the factor $`1/2`$ can be seen directly for a fully invested portfolio.

Suppose that both the pre-rebalance and post-rebalance portfolios satisfy

``` math
\begin{equation}
\mathbf{1}^{\top}w_{t^-}
=
\mathbf{1}^{\top}w_t
=
1.
\end{equation}
```

Then

``` math
\begin{equation}
\sum_{i=1}^{N_t}\Delta w_{i,t}
=
\sum_{i=1}^{N_t}
\left(
w_{i,t}-w_{i,t^-}
\right)
=
0.
\end{equation}
```

Consequently, total purchases must equal total sales:

``` math
\begin{equation}
B_t
=
S_t^{\mathrm{trade}}.
\end{equation}
```

Since

``` math
\begin{equation}
\sum_{i=1}^{N_t}
|\Delta w_{i,t}|
=
B_t+S_t^{\mathrm{trade}},
\end{equation}
```

it follows that

``` math
\begin{equation}
\sum_{i=1}^{N_t}
|\Delta w_{i,t}|
=
2B_t
=
2S_t^{\mathrm{trade}}.
\end{equation}
```

Therefore,

``` math
\begin{equation}
\boxed{
\frac{1}{2}
\sum_{i=1}^{N_t}
|\Delta w_{i,t}|
=
B_t
=
S_t^{\mathrm{trade}}.
}
\end{equation}
```

The one-way turnover convention can thus be interpreted as the fraction of the portfolio that has been replaced, whereas total traded notional measures the sum of all purchases and sales.

For example, suppose that $`50\%`$ of a portfolio is sold and the proceeds are used to purchase new securities. Then

``` math
\begin{equation}
B_t=0.5,
\qquad
S_t^{\mathrm{trade}}=0.5.
\end{equation}
```

Hence,

``` math
\begin{equation}
TO_t^{\mathrm{gross}}
=
0.5+0.5
=
1,
\end{equation}
```

whereas

``` math
\begin{equation}
TO_t^{\mathrm{one\text{-}way}}
=
\frac{1}{2}(1)
=
0.5.
\end{equation}
```

The strategy can therefore be described as having replaced $`50\%`$ of its portfolio while having traded an aggregate notional equal to $`100\%`$ of its net asset value.

The factor $`1/2`$ is consequently a *turnover reporting convention*. It does not imply that only one side of a transaction generates implementation costs.

##### Proportional Transaction Costs

Both purchases and sales generally generate transaction costs. Therefore, if $`c`$ denotes the proportional cost per unit of traded notional and costs are assumed to be symmetric between purchases and sales, transaction costs are

``` math
\begin{equation}
\boxed{
TC_t
=
c
\sum_{i=1}^{N_t}
|\Delta w_{i,t}|.
}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
TC_t
=
c
\left(
B_t+S_t^{\mathrm{trade}}
\right).
\end{equation}
```

The factor $`1/2`$ should therefore *not* be introduced into this expression when $`c`$ represents the cost per unit of actual traded notional.

For example, suppose that a portfolio sells $`50\%`$ of its NAV and purchases another $`50\%`$, such that

``` math
\begin{equation}
\sum_i |\Delta w_{i,t}|=1.
\end{equation}
```

If the assumed transaction cost is $`10`$ basis points per unit of traded notional,

``` math
\begin{equation}
c=0.001,
\end{equation}
```

then

``` math
\begin{equation}
TC_t
=
0.001\times 1
=
0.001,
\end{equation}
```

corresponding to a $`10`$ basis-point reduction in portfolio NAV.

Using one-way turnover without adjusting the cost convention would instead produce

``` math
\begin{equation}
0.001\times 0.5
=
0.0005,
\end{equation}
```

or only $`5`$ basis points, thereby understating the true assumed trading cost.

If transaction costs vary across securities, the model becomes

``` math
\begin{equation}
\boxed{
TC_t
=
\sum_{i=1}^{N_t}
c_{i,t}
|\Delta w_{i,t}|.
}
\end{equation}
```

##### Asymmetric Buy and Sell Costs

Transaction costs need not be symmetric between purchases and sales.

Let

``` math
\begin{equation}
c_{i,t}^{\mathrm{buy}}
\end{equation}
```

and

``` math
\begin{equation}
c_{i,t}^{\mathrm{sell}}
\end{equation}
```

denote the proportional costs associated respectively with buying and selling security $`i`$.

A more general transaction-cost model is then

``` math
\begin{equation}
\boxed{
TC_t
=
\sum_{i=1}^{N_t}
\left[
c_{i,t}^{\mathrm{buy}}
\max(\Delta w_{i,t},0)
+
c_{i,t}^{\mathrm{sell}}
\max(-\Delta w_{i,t},0)
\right].
}
\end{equation}
```

If

``` math
\begin{equation}
c_{i,t}^{\mathrm{buy}}
=
c_{i,t}^{\mathrm{sell}}
=
c_{i,t},
\end{equation}
```

the expression reduces to

``` math
\begin{equation}
TC_t
=
\sum_{i=1}^{N_t}
c_{i,t}
|\Delta w_{i,t}|.
\end{equation}
```

Allowing asymmetric costs can be important when taxes, exchange fees, market microstructure, or other institutional features affect purchases and sales differently.

##### Components of Trading Costs

The proportional coefficient $`c_{i,t}`$ is itself a simplified representation of several distinct implementation costs.

Trading costs can broadly be decomposed as

``` math
\begin{equation}
\boxed{
TC_t
=
TC_t^{\mathrm{commission}}
+
TC_t^{\mathrm{spread}}
+
TC_t^{\mathrm{slippage}}
+
TC_t^{\mathrm{impact}}
+
TC_t^{\mathrm{tax}}
+
TC_t^{\mathrm{fees}}.
}
\end{equation}
```

These components have different economic origins.

###### Commissions.

Broker commissions and explicit execution fees may be charged as a fixed amount per order, per share, or as a proportion of traded notional.

A simple proportional representation is

``` math
\begin{equation}
TC_t^{\mathrm{commission}}
=
\sum_i
c_{i,t}^{\mathrm{commission}}
|\Delta w_{i,t}|.
\end{equation}
```

###### Bid–Ask Spread.

A buyer generally executes closer to the ask price, while a seller executes closer to the bid price.

Let

``` math
\begin{equation}
P_{i,t}^{\mathrm{mid}}
=
\frac{
P_{i,t}^{\mathrm{ask}}
+
P_{i,t}^{\mathrm{bid}}
}{2}
\end{equation}
```

denote the mid-price and

``` math
\begin{equation}
\mathrm{Spread}_{i,t}
=
P_{i,t}^{\mathrm{ask}}
-
P_{i,t}^{\mathrm{bid}}
\end{equation}
```

the quoted bid–ask spread.

Under the simplified assumption that a market order executes at the best bid or ask, the cost relative to the mid-price is approximately one half of the spread:

``` math
\begin{equation}
c_{i,t}^{\mathrm{spread}}
\approx
\frac{
P_{i,t}^{\mathrm{ask}}
-
P_{i,t}^{\mathrm{bid}}
}{
2P_{i,t}^{\mathrm{mid}}
}.
\end{equation}
```

Both purchases and sales therefore incur spread costs relative to the mid-price.

###### Slippage.

Slippage captures the difference between the theoretical or expected execution price and the price actually obtained.

It may result from price movements between signal formation and execution, order delays, limited liquidity, or execution uncertainty.

###### Market Impact.

Large orders may move market prices against the investor. Market impact therefore generally increases nonlinearly with order size.

A generic market-impact model can be represented as

``` math
\begin{equation}
TC_{i,t}^{\mathrm{impact}}
=
f
\left(
|\Delta w_{i,t}|,
\mathrm{ADV}_{i,t},
\sigma_{i,t},
\ldots
\right),
\end{equation}
```

where $`\mathrm{ADV}_{i,t}`$ denotes Average Daily Volume and $`\sigma_{i,t}`$ denotes a measure of asset volatility.

A commonly used stylized specification relates impact to participation in daily volume:

``` math
\begin{equation}
TC_{i,t}^{\mathrm{impact}}
\propto
\sigma_{i,t}
\left(
\frac{
Q_{i,t}
}{
\mathrm{ADV}_{i,t}
}
\right)^{\gamma},
\end{equation}
```

where $`Q_{i,t}`$ is the traded quantity and typically

``` math
\begin{equation}
0<\gamma\leq 1.
\end{equation}
```

###### Taxes and Exchange Fees.

Certain markets impose transaction taxes, stamp duties, exchange fees, or regulatory fees. These costs may be asymmetric and may apply only to purchases or only to sales.

They should therefore be modeled separately when economically material.

##### Trading Costs vs. Holding Costs

Trading costs should be distinguished from costs generated by maintaining positions.

Trading costs are primarily functions of portfolio changes:

``` math
\begin{equation}
TC_t
=
C(\Delta w_t).
\end{equation}
```

By contrast, holding and financing costs depend primarily on the positions maintained through time:

``` math
\begin{equation}
FC_{t\rightarrow t+1}
=
F
\left(
w_t,
t\rightarrow t+1
\right).
\end{equation}
```

For a long–short strategy, relevant holding costs may include:

- short-stock borrowing fees;

- financing costs associated with leverage;

- financing spreads;

- other position-specific carrying costs.

A short sale therefore involves two conceptually different types of costs.

First, initiating or modifying the short position generates a trading cost, just as buying or selling a long position does.

Second, maintaining the short position may generate an ongoing stock-borrow cost.

These costs should not be combined indiscriminately because they depend on different economic quantities.

##### General Transaction-Cost Function

A realistic transaction-cost function may therefore depend on several security-level and market-level variables:

``` math
\begin{equation}
\boxed{
TC_t
=
C
\left(
\Delta w_t,
\mathrm{Spread}_t,
\mathrm{ADV}_t,
\mathrm{Volatility}_t,
\mathrm{Liquidity}_t,
\mathrm{ParticipationRate}_t,
\ldots
\right).
}
\end{equation}
```

At the simplest level, a backtest may assume a constant proportional cost:

``` math
\begin{equation}
TC_t
=
c
\sum_i |\Delta w_{i,t}|.
\end{equation}
```

At a more sophisticated level, costs may vary across securities, dates, directions, and trade sizes:

``` math
\begin{equation}
TC_t
=
\sum_i
C_{i,t}
\left(
\Delta w_{i,t},
\mathrm{Spread}_{i,t},
\mathrm{ADV}_{i,t},
\sigma_{i,t},
\ldots
\right).
\end{equation}
```

The appropriate level of complexity depends on the strategy. Transaction-cost modeling is particularly important for high-turnover strategies, strategies trading less-liquid securities, and portfolios whose size represents a significant fraction of available market liquidity.

##### Gross and Net Portfolio Returns

If the portfolio is formed at time $`t`$ and subsequently earns returns over $`[t,t+1]`$, gross portfolio performance is

``` math
\begin{equation}
R_{p,t\rightarrow t+1}^{\mathrm{gross}}
=
w_t^\top
R_{t\rightarrow t+1},
\end{equation}
```

under the simplified assumption of no intra-period trading.

The corresponding net return can be represented schematically as

``` math
\begin{equation}
\boxed{
R_{p,t\rightarrow t+1}^{\mathrm{net}}
=
R_{p,t\rightarrow t+1}^{\mathrm{gross}}
-
TC_t
-
FC_{t\rightarrow t+1}.
}
\end{equation}
```

Here,

- $`TC_t`$ represents costs generated by the trades required to establish the portfolio at time $`t`$;

- $`FC_{t\rightarrow t+1}`$ represents financing, stock-borrowing, and other holding costs incurred while maintaining the portfolio over $`[t,t+1]`$.

This decomposition emphasizes the distinction

``` math
\begin{equation}
\boxed{
\underbrace{TC_t}_{\text{cost of changing positions}}
\qquad\text{vs.}\qquad
\underbrace{FC_{t\rightarrow t+1}}_{\text{cost of holding positions}}.
}
\end{equation}
```

The precise portfolio accounting, transaction-cost models, financing conventions, and treatment of market impact will be developed in greater detail in the portfolio implementation and backtest return construction sections.

#### The Complete Backtesting Timeline

The conventions introduced above can be summarized through the complete investment timeline.

At time $`t`$, the investor observes the information set

``` math
\begin{equation}
\mathcal{I}_t.
\end{equation}
```

The raw point-in-time data available to the investor satisfy

``` math
\begin{equation}
\mathcal{D}_t
\subseteq
\mathcal{I}_t.
\end{equation}
```

These data are transformed into features:

``` math
\begin{equation}
X_t
=
g(\mathcal{D}_t).
\end{equation}
```

A systematic investment rule or predictive model generates a raw signal:

``` math
\begin{equation}
s_t
=
f(X_t).
\end{equation}
```

Depending on the strategy, this signal may originate from:

- a directly constructed firm-level characteristic;

- several combined characteristics;

- an econometric model;

- a machine-learning model;

- a deep-learning model.

The raw signal is subsequently transformed into a final signal:

``` math
\begin{equation}
\widetilde{s}_t
=
h
\left(
s_t,
Z_t
\right),
\end{equation}
```

where $`Z_t`$ may include variables required for transformations such as industry, beta, size, or factor neutralization.

Portfolio construction maps the final signal into target weights:

``` math
\begin{equation}
w_t^{\mathrm{target}}
=
\phi
\left(
\widetilde{s}_t,
\widehat{\Sigma}_t,
w_{t^-},
\mathcal{C}_t
\right).
\end{equation}
```

The target portfolio may subsequently be modified because of implementation constraints, tradability, rounding, short availability, or other market frictions, producing the implemented portfolio

``` math
\begin{equation}
w_t.
\end{equation}
```

The portfolio then experiences future asset returns

``` math
\begin{equation}
R_{t\rightarrow t+1}
=
\begin{bmatrix}
R_{1,t\rightarrow t+1}\\
\vdots\\
R_{N_t,t\rightarrow t+1}
\end{bmatrix}.
\end{equation}
```

Ignoring intra-period trading, portfolio cash flows, and weight-drift complications for the moment, the gross portfolio return is

``` math
\begin{equation}
\boxed{
R_{p,t\rightarrow t+1}^{\mathrm{gross}}
=
w_t^\top
R_{t\rightarrow t+1}.
}
\end{equation}
```

After implementation costs,

``` math
\begin{equation}
\boxed{
R_{p,t\rightarrow t+1}^{\mathrm{net}}
=
w_t^\top
R_{t\rightarrow t+1}
-
TC_t
-
FC_{t\rightarrow t+1}.
}
\end{equation}
```

The complete backtesting pipeline can therefore be summarized as

``` math
\begin{equation}
\boxed{
\mathcal{I}_t
\rightarrow
\mathcal{D}_t
\rightarrow
X_t
\rightarrow
s_t
\rightarrow
\widetilde{s}_t
\rightarrow
w_t^{\mathrm{target}}
\rightarrow
w_t
\rightarrow
R_{t\rightarrow t+1}
\rightarrow
R_{p,t\rightarrow t+1}^{\mathrm{net}}.
}
\end{equation}
```

Equivalently, at a higher conceptual level,

``` math
\begin{equation}
\boxed{
\text{Information}
\rightarrow
\text{Data}
\rightarrow
\text{Features}
\rightarrow
\text{Signal}
\rightarrow
\text{Portfolio}
\rightarrow
\text{Execution}
\rightarrow
\text{Performance}.
}
\end{equation}
```

This sequence provides the conceptual backbone of the entire backtesting framework developed in the following sections.

Each subsequent chapter studies one or several of these transformations in detail while maintaining the fundamental constraint that every investment decision made at time $`t`$ must depend exclusively on the information available at time $`t`$.

