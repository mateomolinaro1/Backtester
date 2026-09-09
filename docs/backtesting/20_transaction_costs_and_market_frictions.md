### Transaction Costs and Market Frictions

Trading changes portfolio holdings but also generates implementation costs.

Let

``` math
\begin{equation}
\Delta\mathbf{w}_t
\end{equation}
```

denote the executed portfolio trade.

Total implementation cost may be represented generically as

``` math
\begin{equation}
\boxed{
TC_t
=
C_t
\left(
\Delta\mathbf{w}_t,
\mathrm{Liquidity}_t,
\mathrm{Spread}_t,
\mathrm{Volatility}_t,
A_t,
\ldots
\right).
}
\end{equation}
```

#### General Transaction-Cost Model

A useful decomposition is

``` math
\begin{equation}
\boxed{
TC_t
=
TC_t^{\mathrm{fees}}
+
TC_t^{\mathrm{spread}}
+
TC_t^{\mathrm{slippage}}
+
TC_t^{\mathrm{impact}}.
}
\end{equation}
```

Holding-related costs such as borrow and financing are treated separately because they accrue through time rather than only when a trade occurs.

#### Commissions and Explicit Fees

Let

``` math
\begin{equation}
c_{i,t}^{\mathrm{fee}}
\end{equation}
```

denote explicit cost per unit of traded notional.

Then

``` math
\begin{equation}
\boxed{
TC_t^{\mathrm{fees}}
=
\sum_i
c_{i,t}^{\mathrm{fee}}
|\Delta w_{i,t}|.
}
\end{equation}
```

These costs may include commissions, exchange fees, taxes, and regulatory fees.

#### Bid–Ask Spread

Let

``` math
\begin{equation}
P_{i,t}^{\mathrm{bid}}
\qquad\text{and}\qquad
P_{i,t}^{\mathrm{ask}}
\end{equation}
```

denote contemporaneous bid and ask prices.

The mid-price is

``` math
\begin{equation}
P_{i,t}^{\mathrm{mid}}
=
\frac{
P_{i,t}^{\mathrm{bid}}
+
P_{i,t}^{\mathrm{ask}}
}{2}.
\end{equation}
```

The proportional half-spread is approximately

``` math
\begin{equation}
\boxed{
c_{i,t}^{\mathrm{spread}}
=
\frac{
P_{i,t}^{\mathrm{ask}}
-
P_{i,t}^{\mathrm{bid}}
}{
2P_{i,t}^{\mathrm{mid}}
}.
}
\end{equation}
```

A trade crossing the spread therefore generates approximately

``` math
\begin{equation}
TC_t^{\mathrm{spread}}
=
\sum_i
c_{i,t}^{\mathrm{spread}}
|\Delta w_{i,t}|.
\end{equation}
```

#### Slippage

Slippage captures the difference between the reference price assumed when the portfolio decision is made and the actual execution price.

For security $`i`$,

``` math
\begin{equation}
\boxed{
\mathrm{Slippage}_{i,t}
=
\frac{
P_{i,t}^{\mathrm{exec}}
-
P_{i,t}^{\mathrm{reference}}
}{
P_{i,t}^{\mathrm{reference}}
}
}
\end{equation}
```

with sign conventions adjusted according to trade direction.

Slippage may reflect price movement during the delay between decision and execution, order-book dynamics, and execution uncertainty.

#### Market Impact

Large orders may move market prices.

A generic impact model can be written as

``` math
\begin{equation}
\boxed{
TC_{i,t}^{\mathrm{impact}}
=
\eta_{i,t}
|\Delta w_{i,t}|^{p},
\qquad
p>1.
}
\end{equation}
```

A more implementation-oriented model may depend on trade size relative to ADV:

``` math
\begin{equation}
TC_{i,t}^{\mathrm{impact}}
=
g
\left(
\frac{
A_t|\Delta w_{i,t}|
}{
\mathrm{ADV}_{i,t}
},
\sigma_{i,t},
\ldots
\right).
\end{equation}
```

Market impact therefore introduces an explicit dependence of strategy costs on portfolio AUM.

#### Short Borrowing Costs

Short positions require borrowing the underlying securities.

Let

``` math
\begin{equation}
b_{i,t}
\end{equation}
```

denote the annualized borrow rate.

For a short position with notional

``` math
\begin{equation}
A_t|w_{i,t}|,
\end{equation}
```

the approximate borrow cost over a time fraction $`\Delta t`$ is

``` math
\begin{equation}
\boxed{
BC_{i,t}
=
A_t
|w_{i,t}|
b_{i,t}
\Delta t.
}
\end{equation}
```

Borrow costs accrue while the short position is held and should therefore be distinguished from one-off transaction costs.

#### Financing Costs

Leveraged portfolios may require external financing.

Let

``` math
\begin{equation}
F_t
\end{equation}
```

denote the financed amount and

``` math
\begin{equation}
r_t^{\mathrm{fin}}
\end{equation}
```

the applicable annualized financing rate.

Over period $`\Delta t`$,

``` math
\begin{equation}
\boxed{
FC_t
=
F_t
r_t^{\mathrm{fin}}
\Delta t.
}
\end{equation}
```

The precise financing convention depends on portfolio structure, instrument type, collateral, and cash treatment.

#### Liquidity and Capacity Effects

Implementation costs depend on strategy size.

Let

``` math
\begin{equation}
A_t
\end{equation}
```

denote portfolio AUM.

For fixed portfolio weights,

``` math
\begin{equation}
Q_{i,t}^{\$}
=
A_t|\Delta w_{i,t}|.
\end{equation}
```

Therefore,

``` math
\begin{equation}
A_t\uparrow
\quad\Rightarrow\quad
Q_{i,t}^{\$}\uparrow.
\end{equation}
```

Larger AUM may increase participation rates, market impact, execution time, and the number of binding liquidity constraints.

Thus,

``` math
\begin{equation}
\boxed{
\text{Backtest Performance}
=
f(\text{AUM})
}
\end{equation}
```

whenever transaction costs and market impact are modeled realistically.

