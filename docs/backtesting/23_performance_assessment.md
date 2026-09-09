### Performance Assessment

Let

``` math
\begin{equation}
R_{p,t},
\qquad
t=1,\ldots,T,
\end{equation}
```

denote the portfolio return series at the evaluation frequency.

Unless otherwise stated, performance should preferably be evaluated using net returns,

``` math
\begin{equation}
R_{p,t}
=
R_{p,t}^{\mathrm{net}}.
\end{equation}
```

Let

``` math
\begin{equation}
A
\end{equation}
```

denote the number of return observations per year. Typical conventions are

``` math
\begin{equation}
A=
\begin{cases}
252, & \text{daily returns},\\
52, & \text{weekly returns},\\
12, & \text{monthly returns}.
\end{cases}
\end{equation}
```

#### Annualized Return

The arithmetic mean periodic return is

``` math
\begin{equation}
\bar{R}_p
=
\frac{1}{T}
\sum_{t=1}^{T}
R_{p,t}.
\end{equation}
```

A simple arithmetic annualization is

``` math
\begin{equation}
\boxed{
\mu_p^{\mathrm{ann}}
=
A\bar{R}_p.
}
\end{equation}
```

For cumulative investment performance, however, geometric compounding is generally more appropriate.

Let

``` math
\begin{equation}
V_T
=
V_0
\prod_{t=1}^{T}
(1+R_{p,t}).
\end{equation}
```

The compound annual growth rate is

``` math
\begin{equation}
\boxed{
CAGR
=
\left(
\frac{V_T}{V_0}
\right)^{A/T}
-1.
}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
\boxed{
CAGR
=
\left[
\prod_{t=1}^{T}
(1+R_{p,t})
\right]^{A/T}
-1.
}
\end{equation}
```

The distinction between arithmetic annualized return and CAGR should always be made explicit.

#### Annualized Volatility

The sample volatility of periodic returns is

``` math
\begin{equation}
\widehat{\sigma}_p
=
\sqrt{
\frac{1}{T-1}
\sum_{t=1}^{T}
\left(
R_{p,t}-\bar{R}_p
\right)^2
}.
\end{equation}
```

Under the standard square-root-of-time convention, annualized volatility is

``` math
\begin{equation}
\boxed{
\widehat{\sigma}_p^{\mathrm{ann}}
=
\sqrt{A}
\widehat{\sigma}_p.
}
\end{equation}
```

This scaling assumes that the relevant return variance aggregates approximately linearly through time. Serial correlation, volatility clustering, and other time-series dependencies may cause the simple square-root-of-time approximation to be imperfect.

#### Sharpe Ratio

Let

``` math
\begin{equation}
R_{f,t}
\end{equation}
```

denote the risk-free return over period $`t`$ and define excess returns as

``` math
\begin{equation}
R_{p,t}^{e}
=
R_{p,t}-R_{f,t}.
\end{equation}
```

The annualized Sharpe ratio is

``` math
\begin{equation}
\boxed{
SR
=
\sqrt{A}
\frac{
\overline{R_p^{e}}
}{
\widehat{\sigma}(R_p^{e})
}.
}
\end{equation}
```

When the risk-free rate is negligible relative to the strategy return, a common approximation is

``` math
\begin{equation}
SR
\approx
\sqrt{A}
\frac{
\bar{R}_p
}{
\widehat{\sigma}_p
}.
\end{equation}
```

For market-neutral or leveraged strategies, the financing convention should be consistent with the return construction developed previously.

#### Sortino Ratio

The Sortino ratio penalizes downside variation rather than total volatility.

For a minimum acceptable periodic return $`MAR`$, define downside deviation as

``` math
\begin{equation}
\widehat{\sigma}_{\mathrm{down}}
=
\sqrt{
\frac{1}{T}
\sum_{t=1}^{T}
\min
\left(
R_{p,t}-MAR,
0
\right)^2
}.
\end{equation}
```

The annualized Sortino ratio can then be written as

``` math
\begin{equation}
\boxed{
\mathrm{Sortino}
=
\sqrt{A}
\frac{
\bar{R}_p-MAR
}{
\widehat{\sigma}_{\mathrm{down}}
}.
}
\end{equation}
```

The definition of $`MAR`$ and its frequency must be stated explicitly.

#### Maximum Drawdown

Let

``` math
\begin{equation}
V_t
=
V_0
\prod_{\tau=1}^{t}
(1+R_{p,\tau})
\end{equation}
```

denote the portfolio wealth process.

The running historical peak is

``` math
\begin{equation}
H_t
=
\max_{0\leq u\leq t}
V_u.
\end{equation}
```

The drawdown at time $`t`$ is

``` math
\begin{equation}
\boxed{
DD_t
=
\frac{V_t}{H_t}-1.
}
\end{equation}
```

Hence,

``` math
\begin{equation}
DD_t\leq0.
\end{equation}
```

Maximum drawdown is

``` math
\begin{equation}
\boxed{
MDD
=
-\min_t DD_t.
}
\end{equation}
```

Under this convention, $`MDD`$ is reported as a positive loss magnitude.

#### Calmar Ratio

The Calmar ratio compares compounded annual performance with maximum drawdown:

``` math
\begin{equation}
\boxed{
\mathrm{Calmar}
=
\frac{
CAGR
}{
MDD
}.
}
\end{equation}
```

Unlike the Sharpe ratio, the Calmar ratio directly penalizes the largest historical peak-to-trough loss.

#### Hit Ratio

A simple portfolio-level hit ratio measures the fraction of periods with positive returns:

``` math
\begin{equation}
\boxed{
HR
=
\frac{1}{T}
\sum_{t=1}^{T}
\mathbb{I}
\left(
R_{p,t}>0
\right).
}
\end{equation}
```

More generally, a benchmark or required-return threshold $`c_t`$ may be used:

``` math
\begin{equation}
HR(c)
=
\frac{1}{T}
\sum_{t=1}^{T}
\mathbb{I}
\left(
R_{p,t}>c_t
\right).
\end{equation}
```

Hit ratio should not be interpreted independently of payoff magnitude. A strategy may have a low hit ratio and remain profitable if winning periods are substantially larger than losing periods, or conversely.

#### Skewness and Kurtosis

The standardized third central moment measures return skewness:

``` math
\begin{equation}
\boxed{
\widehat{\mathrm{Skew}}
=
\frac{
\frac{1}{T}
\sum_{t=1}^{T}
(R_{p,t}-\bar{R}_p)^3
}{
\widehat{\sigma}_p^3
}.
}
\end{equation}
```

Positive skewness indicates a relatively longer right tail, while negative skewness indicates a relatively longer left tail.

The standardized fourth central moment is

``` math
\begin{equation}
\boxed{
\widehat{\mathrm{Kurt}}
=
\frac{
\frac{1}{T}
\sum_{t=1}^{T}
(R_{p,t}-\bar{R}_p)^4
}{
\widehat{\sigma}_p^4
}.
}
\end{equation}
```

For a Gaussian distribution,

``` math
\begin{equation}
\mathrm{Kurt}=3.
\end{equation}
```

Excess kurtosis is therefore

``` math
\begin{equation}
\boxed{
\mathrm{ExKurt}
=
\widehat{\mathrm{Kurt}}-3.
}
\end{equation}
```

Large positive excess kurtosis indicates heavier tails than under the Gaussian benchmark.

#### Value at Risk

For confidence level $`\alpha`$, Value at Risk is defined through the lower quantile of the portfolio return distribution.

Let

``` math
\begin{equation}
q_{1-\alpha}(R_p)
\end{equation}
```

denote the $`(1-\alpha)`$ return quantile.

Then

``` math
\begin{equation}
\boxed{
VaR_{\alpha}
=
-
q_{1-\alpha}(R_p).
}
\end{equation}
```

For example,

``` math
\begin{equation}
VaR_{95\%}
=
-
q_{5\%}(R_p).
\end{equation}
```

Historical VaR can be estimated directly from the empirical distribution of backtest returns.

VaR describes a loss threshold but does not measure the magnitude of losses beyond that threshold.

#### Expected Shortfall

Expected Shortfall addresses this limitation by measuring the average loss in the tail beyond the VaR threshold.

Under a continuous return distribution,

``` math
\begin{equation}
\boxed{
ES_{\alpha}
=
-
\mathbb{E}
\left[
R_p
\mid
R_p
\leq
q_{1-\alpha}(R_p)
\right].
}
\end{equation}
```

For example, $`ES_{95\%}`$ measures the average loss conditional on returns lying in approximately the worst $`5\%`$ of the distribution.

Expected Shortfall therefore contains information about tail severity that is not captured by VaR alone.

#### Turnover

Turnover measures the amount of portfolio trading required to implement the strategy.

Using the one-sided convention developed previously,

``` math
\begin{equation}
\boxed{
TO_t
=
\frac{1}{2}
\sum_{i=1}^{N_t}
\left|
w_{i,t}^{\mathrm{final}}
-
w_{i,t^-}
\right|.
}
\end{equation}
```

If implemented rather than desired trades are available, realized turnover should preferably be computed from executed changes.

Average turnover is

``` math
\begin{equation}
\boxed{
\overline{TO}
=
\frac{1}{T}
\sum_{t=1}^{T}
TO_t.
}
\end{equation}
```

If turnover is annualized, the exact scaling convention and rebalance frequency must be stated explicitly.

Turnover is not itself a performance measure, but it is an essential indicator of implementation intensity and the sensitivity of gross alpha to trading costs.

#### Capacity

Capacity measures how much capital can be deployed in the strategy before liquidity constraints and market impact materially degrade its performance.

Let

``` math
\begin{equation}
A
\end{equation}
```

denote strategy AUM.

Because traded dollar notional scales with AUM,

``` math
\begin{equation}
Q_{i,t}^{\$}(A)
=
A
|\Delta w_{i,t}|,
\end{equation}
```

transaction costs generally become functions of portfolio size:

``` math
\begin{equation}
TC_t
=
TC_t(A).
\end{equation}
```

Consequently,

``` math
\begin{equation}
\boxed{
R_{p,t}^{\mathrm{net}}
=
R_{p,t}^{\mathrm{gross}}
-
TC_t(A)
-
FC_t(A)
-
BC_t(A).
}
\end{equation}
```

A capacity curve may therefore be constructed as

``` math
\begin{equation}
\boxed{
A
\longmapsto
\mathrm{Performance}^{\mathrm{net}}(A).
}
\end{equation}
```

For example, one may examine

``` math
\begin{equation}
A
\longmapsto
SR^{\mathrm{net}}(A)
\end{equation}
```

or

``` math
\begin{equation}
A
\longmapsto
CAGR^{\mathrm{net}}(A).
\end{equation}
```

A practical capacity threshold may then be defined as the largest AUM satisfying a chosen economic condition, such as

``` math
\begin{equation}
SR^{\mathrm{net}}(A)
\geq
SR_{\min}.
\end{equation}
```

Capacity is therefore not a single universal number. It depends on the transaction-cost model, execution assumptions, liquidity constraints, required performance threshold, and portfolio implementation process.

#### Gross vs. Net Performance

A strategy should generally be evaluated both before and after implementation costs.

Let

``` math
\begin{equation}
R_{p,t}^{\mathrm{gross}}
\end{equation}
```

denote gross strategy return and

``` math
\begin{equation}
R_{p,t}^{\mathrm{net}}
\end{equation}
```

denote return after the modeled costs.

The difference

``` math
\begin{equation}
\boxed{
D_t^{\mathrm{implementation}}
=
R_{p,t}^{\mathrm{gross}}
-
R_{p,t}^{\mathrm{net}}
}
\end{equation}
```

measures the return drag associated with implementation.

Under the cost decomposition introduced previously,

``` math
\begin{equation}
\boxed{
D_t^{\mathrm{implementation}}
=
TC_t
+
FC_t
+
BC_t.
}
\end{equation}
```

Comparing gross and net performance is particularly important for high-turnover signals, less liquid universes, leveraged strategies, and short portfolios.

A strategy with attractive gross performance but weak net performance is not necessarily economically implementable.

