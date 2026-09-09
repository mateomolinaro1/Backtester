### Portfolio Implementation

The portfolio-construction engine specifies what the strategy would ideally like to hold.

The implementation engine determines the trades required to move from the portfolio currently held to that desired portfolio.

The central objects are therefore

``` math
\begin{equation}
\boxed{
\mathbf{w}_{t^-}
\qquad\text{and}\qquad
\mathbf{w}_t^{\mathrm{final}},
}
\end{equation}
```

where $`\mathbf{w}_{t^-}`$ denotes portfolio weights immediately before the rebalance.

#### Target vs. Current Portfolio

The required portfolio adjustment is

``` math
\begin{equation}
\boxed{
\Delta\mathbf{w}_t
=
\mathbf{w}_t^{\mathrm{final}}
-
\mathbf{w}_{t^-}.
}
\end{equation}
```

For security $`i`$,

``` math
\begin{equation}
\Delta w_{i,t}
=
w_{i,t}^{\mathrm{final}}
-
w_{i,t^-}.
\end{equation}
```

If

``` math
\begin{equation}
\Delta w_{i,t}>0,
\end{equation}
```

the strategy must increase its exposure to security $`i`$.

If

``` math
\begin{equation}
\Delta w_{i,t}<0,
\end{equation}
```

the strategy must reduce its exposure.

#### Portfolio Drift

The current portfolio immediately before rebalance is generally not equal to the weights established at the previous rebalance.

Suppose the portfolio initially holds weights

``` math
\begin{equation}
w_{i,t-1}^{\mathrm{implemented}}
\end{equation}
```

and securities subsequently realize returns

``` math
\begin{equation}
R_{i,t}.
\end{equation}
```

Ignoring intermediate cash flows, pre-rebalance weights become

``` math
\begin{equation}
\boxed{
w_{i,t^-}
=
\frac{
w_{i,t-1}^{\mathrm{implemented}}
(1+R_{i,t})
}{
1+R_{p,t}
}.
}
\end{equation}
```

Therefore,

``` math
\begin{equation}
\boxed{
\mathbf{w}_{t^-}
\neq
\mathbf{w}_{t-1}^{\mathrm{implemented}}
}
\end{equation}
```

in general.

This phenomenon is referred to as *portfolio drift*.

The correct trade calculation must therefore compare the new desired portfolio with the drifted portfolio, not mechanically with the previous target weights.

#### Required Trades

Let

``` math
\begin{equation}
A_t
\end{equation}
```

denote portfolio NAV immediately before the rebalance.

The desired currency notional trade in security $`i`$ is approximately

``` math
\begin{equation}
\boxed{
Q_{i,t}^{\$}
=
A_t
\Delta w_{i,t}.
}
\end{equation}
```

Positive values correspond to purchases and negative values to sales.

If the execution price is

``` math
\begin{equation}
P_{i,t}^{\mathrm{exec}},
\end{equation}
```

the corresponding desired share quantity is

``` math
\begin{equation}
\boxed{
\Delta q_{i,t}^{\mathrm{desired}}
=
\frac{
A_t\Delta w_{i,t}
}{
P_{i,t}^{\mathrm{exec}}
}.
}
\end{equation}
```

The exact conversion may depend on contract multipliers, currency conversion, and instrument type.

#### Order Generation

The desired quantity changes must be translated into executable orders.

For each security,

``` math
\begin{equation}
\Delta q_{i,t}>0
\end{equation}
```

generates a buy order, while

``` math
\begin{equation}
\Delta q_{i,t}<0
\end{equation}
```

generates a sell order.

An order can be represented schematically as

``` math
\begin{equation}
\boxed{
\mathcal{O}_{i,t}
=
\left(
i,
\mathrm{Side}_{i,t},
|\Delta q_{i,t}|,
\mathrm{OrderType}_{i,t},
t
\right).
}
\end{equation}
```

The simulation may use simple market orders or more detailed assumptions about execution algorithms.

#### Execution Price Assumptions

The execution price determines the price at which simulated trades are assumed to occur.

Possible conventions include:

- next open;

- next close;

- VWAP;

- TWAP;

- arrival price;

- mid-price plus modeled spread and slippage.

The execution-price convention must be consistent with the information and execution timeline.

For example,

``` math
\begin{equation}
\boxed{
\text{Signal requiring Close}_t
\not\Rightarrow
\text{execution at the same Close}_t
}
\end{equation}
```

unless the strategy is known and executable before the closing auction under the assumed model.

#### Partial Execution and Partial Rebalancing

The desired trade need not always be fully executed.

Let

``` math
\begin{equation}
\phi_{i,t}
\in
[0,1]
\end{equation}
```

denote the fraction of the desired trade that can be executed.

Then

``` math
\begin{equation}
\boxed{
\Delta q_{i,t}^{\mathrm{executed}}
=
\phi_{i,t}
\Delta q_{i,t}^{\mathrm{desired}}.
}
\end{equation}
```

The executed portfolio therefore moves only partially toward the desired target.

Partial execution may result from:

- liquidity constraints;

- participation-rate limits;

- unavailable borrow;

- trading halts;

- order-size limits;

- deliberate partial-rebalancing rules.

#### Position Rounding

Real portfolios generally trade discrete quantities.

If security $`i`$ must be traded in lot size

``` math
\begin{equation}
L_i,
\end{equation}
```

the executed quantity may be rounded as

``` math
\begin{equation}
\boxed{
\Delta q_{i,t}^{\mathrm{rounded}}
=
L_i
\cdot
\operatorname{Round}
\left(
\frac{
\Delta q_{i,t}^{\mathrm{desired}}
}{
L_i
}
\right).
}
\end{equation}
```

For ordinary equities,

``` math
\begin{equation}
L_i=1
\end{equation}
```

may represent whole-share trading.

Rounding means that implemented portfolio weights need not exactly equal the desired weights.

#### Implemented Portfolio

After execution, the portfolio contains quantities

``` math
\begin{equation}
\boxed{
q_{i,t}^{\mathrm{implemented}}
=
q_{i,t^-}
+
\Delta q_{i,t}^{\mathrm{executed}}.
}
\end{equation}
```

The resulting implemented weights are

``` math
\begin{equation}
\boxed{
w_{i,t}^{\mathrm{implemented}}
=
\frac{
q_{i,t}^{\mathrm{implemented}}
P_{i,t}^{\mathrm{exec}}
}{
NAV_t^{\mathrm{post}}
}.
}
\end{equation}
```

Thus,

``` math
\begin{equation}
\boxed{
\mathbf{w}_t^{\mathrm{implemented}}
\neq
\mathbf{w}_t^{\mathrm{final}}
}
\end{equation}
```

in general.

The difference

``` math
\begin{equation}
\boxed{
\mathbf{e}_t^{\mathrm{implementation}}
=
\mathbf{w}_t^{\mathrm{implemented}}
-
\mathbf{w}_t^{\mathrm{final}}
}
\end{equation}
```

can be interpreted as implementation error.

