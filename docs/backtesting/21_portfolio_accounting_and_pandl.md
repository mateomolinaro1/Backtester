### Portfolio Accounting and P&L

Once trades have been executed, the backtester must maintain the evolving state of the simulated portfolio.

The accounting engine converts security quantities, prices, and cash flows into portfolio NAV and profit and loss.

#### Portfolio State Representation

A convenient portfolio state representation is

``` math
\begin{equation}
\boxed{
\mathcal{P}_t
=
\left(
\mathbf{q}_t,
\mathbf{P}_t,
C_t,
NAV_t
\right),
}
\end{equation}
```

where

``` math
\begin{equation}
\mathbf{q}_t
\in
\mathbb{R}^{N_t}
\end{equation}
```

denotes security quantities,

``` math
\begin{equation}
\mathbf{P}_t
\in
\mathbb{R}^{N_t}
\end{equation}
```

denotes valuation prices,

``` math
\begin{equation}
C_t
\end{equation}
```

denotes cash, and

``` math
\begin{equation}
NAV_t
\end{equation}
```

denotes portfolio net asset value.

#### Positions and Market Values

The market value of security $`i`$ is

``` math
\begin{equation}
\boxed{
MV_{i,t}
=
q_{i,t}
P_{i,t}.
}
\end{equation}
```

Positive market value represents a long position and negative market value a short position.

Portfolio security value is

``` math
\begin{equation}
\boxed{
MV_t
=
\sum_i
q_{i,t}
P_{i,t}.
}
\end{equation}
```

#### Cash Account

Trading changes the cash account.

Ignoring costs temporarily,

``` math
\begin{equation}
\boxed{
C_t^{\mathrm{post}}
=
C_t^{\mathrm{pre}}
-
\sum_i
\Delta q_{i,t}
P_{i,t}^{\mathrm{exec}}.
}
\end{equation}
```

Purchases reduce cash, whereas sales increase cash.

Transaction costs and other cash flows are subsequently deducted or credited according to the accounting convention.

#### Mark-to-Market Valuation

At valuation time $`t`$,

``` math
\begin{equation}
\boxed{
NAV_t
=
C_t
+
\sum_i
q_{i,t}
P_{i,t}.
}
\end{equation}
```

As market prices change, portfolio NAV changes even in the absence of trading.

This mark-to-market process creates the realized P&L of the portfolio.

#### Daily Profit and Loss

Ignoring external capital flows, portfolio P&L between two valuation times is

``` math
\begin{equation}
\boxed{
PnL_{t\rightarrow t+1}
=
NAV_{t+1}
-
NAV_t.
}
\end{equation}
```

A useful decomposition is

``` math
\begin{equation}
\boxed{
PnL_t^{\mathrm{net}}
=
PnL_t^{\mathrm{market}}
-
TC_t
-
BC_t
-
FC_t,
}
\end{equation}
```

where:

- $`PnL_t^{\mathrm{market}}`$ is the mark-to-market trading P&L;

- $`TC_t`$ denotes transaction costs;

- $`BC_t`$ denotes short-borrowing costs;

- $`FC_t`$ denotes financing costs.

#### NAV Evolution

If

``` math
\begin{equation}
R_{p,t+1}^{\mathrm{net}}
\end{equation}
```

denotes the net portfolio return, then

``` math
\begin{equation}
\boxed{
NAV_{t+1}
=
NAV_t
\left(
1+
R_{p,t+1}^{\mathrm{net}}
\right).
}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
\boxed{
R_{p,t+1}^{\mathrm{net}}
=
\frac{
NAV_{t+1}
-
NAV_t
}{
NAV_t
}.
}
\end{equation}
```

