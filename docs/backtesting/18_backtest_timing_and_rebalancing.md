### Backtest Timing and Rebalancing

The first responsibility of the simulation engine is to define the chronological relationship between information, portfolio decisions, execution, and realized returns.

A backtest must ensure that the portfolio earning a return was fully determined before that return became observable.

The general timing structure is

``` math
\begin{equation}
\boxed{
\text{Available Information}
\rightarrow
\text{Portfolio Decision}
\rightarrow
\text{Execution}
\rightarrow
\text{Holding Period}
\rightarrow
\text{Realized Return}.
}
\end{equation}
```

#### Decision, Execution, and Holding Timeline

Let

``` math
\begin{equation}
t_d
\end{equation}
```

denote the portfolio decision time,

``` math
\begin{equation}
t_e
\end{equation}
```

the execution time, and

``` math
\begin{equation}
[t_e,t_e')
\end{equation}
```

the subsequent holding interval.

A valid chronology requires

``` math
\begin{equation}
\boxed{
t_d
\leq
t_e
<
t_e'.
}
\end{equation}
```

The final desired portfolio is constructed using only information available at $`t_d`$:

``` math
\begin{equation}
\boxed{
\mathbf{w}_{t_d}^{\mathrm{final}}
=
f
\left(
\mathcal{I}_{t_d}
\right),
}
\end{equation}
```

where $`\mathcal{I}_{t_d}`$ denotes the point-in-time information set.

The portfolio return must then be generated using price changes occurring after the simulated execution.

#### Execution Lags

A strategy cannot generally assume that information observed at a given instant can be traded at a price that occurred before the information was available.

If a signal requires the closing price at date $`t`$, for example,

``` math
\begin{equation}
P_{i,t}^{\mathrm{close}},
\end{equation}
```

then the resulting portfolio decision is formed only after that close is known.

A conservative timing convention may therefore be

``` math
\begin{equation}
\boxed{
\text{Close}_t
\rightarrow
\text{Portfolio Decision}
\rightarrow
\text{Execution at Open}_{t+1}.
}
\end{equation}
```

Alternatively,

``` math
\begin{equation}
\boxed{
\text{Close}_t
\rightarrow
\text{Portfolio Decision}
\rightarrow
\text{Execution at Close}_{t+1}.
}
\end{equation}
```

The appropriate lag depends on the assumed execution mechanism.

The lag should be modeled explicitly rather than being introduced accidentally through DataFrame alignment.

##### Avoiding Double Lags

Suppose weights computed from information at date $`t-1`$ are already stored at date $`t`$.

If those weights are then shifted again before multiplying by date-$`t`$ returns, the backtester may unintentionally introduce an additional period of delay.

Thus,

``` math
\begin{equation}
\boxed{
\text{The economic decision should be lagged exactly once.}
}
\end{equation}
```

The correct implementation depends on the timestamp convention used for both weights and returns.

#### Rebalancing Schedule

Let

``` math
\begin{equation}
\mathcal{T}^{R}
=
\left\{
t_1^{R},
t_2^{R},
\ldots
\right\}
\end{equation}
```

denote the set of portfolio rebalance dates.

Possible schedules include:

- daily;

- weekly;

- monthly;

- quarterly;

- event-driven;

- threshold-triggered.

The signal calculation frequency and portfolio rebalance frequency need not be identical.

Thus,

``` math
\begin{equation}
\boxed{
f_{\mathrm{signal}}
\neq
f_{\mathrm{rebalance}}
}
\end{equation}
```

in general.

For example, signals may be updated daily while the portfolio is rebalanced only weekly.

#### Holding Period

Following execution at time $`t_e`$, the implemented portfolio is held until the next rebalance or liquidation event.

The holding interval is

``` math
\begin{equation}
\boxed{
[t_e,t_e').
}
\end{equation}
```

If the portfolio is represented at discrete times, the implemented weights at $`t`$ earn the subsequent return:

``` math
\begin{equation}
\boxed{
R_{p,t\rightarrow t+1}^{\mathrm{gross}}
=
\left(
\mathbf{w}_t^{\mathrm{implemented}}
\right)^\top
\mathbf{R}_{t\rightarrow t+1}.
}
\end{equation}
```

The fundamental requirement is

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{implemented}}
\text{ must be determined before }
\mathbf{R}_{t\rightarrow t+1}
\text{ is observed}.
}
\end{equation}
```

#### Timing Integrity and Look-Ahead Prevention

Timing integrity must hold throughout the complete portfolio simulation.

At each date, the backtester should verify that:

- all signal inputs were available before the decision;

- all model parameters were estimated using admissible historical data;

- risk estimates were available before portfolio construction;

- target weights were computed before the returns attributed to them;

- execution prices occurred no earlier than the simulated execution time;

- transaction-cost inputs were available at the relevant decision or execution time.

Thus, the simulation chronology must always satisfy

``` math
\begin{equation}
\boxed{
\mathcal{I}_t
\rightarrow
\mathbf{w}_t^{\mathrm{final}}
\rightarrow
\text{Execution}
\rightarrow
\mathbf{w}_t^{\mathrm{implemented}}
\rightarrow
\text{Future Returns}.
}
\end{equation}
```

