### Data Cleaning

Once the point-in-time investment universe has been constructed, the raw observations associated with each eligible security must be transformed into a consistent and economically meaningful dataset.

Let

``` math
\begin{equation}
\mathcal{D}_t^{\mathrm{raw}}
\end{equation}
```

denote the point-in-time data available for the investment universe at time $`t`$. The cleaning operator may be represented abstractly as

``` math
\begin{equation}
\boxed{
\mathcal{D}_t^{\mathrm{clean}}
=
\mathcal{C}
\left(
\mathcal{D}_t^{\mathrm{raw}}
\right),
}
\end{equation}
```

where $`\mathcal{C}`$ denotes the collection of deterministic data-validation and cleaning rules.

The objective of this stage is not to improve the apparent statistical properties of the data. Rather, it is to ensure that observations entering subsequent calculations have a valid economic interpretation.

A robust cleaning pipeline should satisfy several principles:

1.  **Determinism:** identical inputs and cleaning rules must produce identical outputs.

2.  **Causality:** cleaning at time $`t`$ must not use information unavailable at time $`t`$.

3.  **Traceability:** modifications and exclusions should be identifiable and auditable.

4.  **Minimal intervention:** observations should not be modified unless there is a clearly defined reason.

5.  **Separation of concerns:** invalid-data treatment, missing-data treatment, and outlier treatment should remain conceptually distinct.

In particular,

``` math
\begin{equation}
\boxed{
\text{Missing}
\neq
\text{Invalid}
\neq
\text{Stale}
\neq
\text{Extreme}.
}
\end{equation}
```

An extreme but economically valid observation should not automatically be removed during data cleaning. Statistical treatment of extreme observations is developed separately in the outlier-handling section.

#### Duplicate Observations

The first requirement of a panel dataset is that its observational key be well-defined.

Suppose the intended security-level key is

``` math
\begin{equation}
K
=
(i,t),
\end{equation}
```

where $`i`$ identifies the security and $`t`$ the observation timestamp.

The dataset should satisfy

``` math
\begin{equation}
\boxed{
\#\left\{
j:
K_j=(i,t)
\right\}
\leq 1
}
\end{equation}
```

for every $`(i,t)`$ pair, unless multiple observations at the same timestamp are explicitly part of the data model.

##### Exact Duplicates

Two rows may be identical across all fields:

``` math
\begin{equation}
D_j=D_k.
\end{equation}
```

If the duplication is known to result from ingestion or concatenation, retaining a single observation is generally sufficient.

##### Conflicting Duplicates

The more difficult case occurs when

``` math
\begin{equation}
(i_j,t_j)
=
(i_k,t_k)
\end{equation}
```

but

``` math
\begin{equation}
X_j
\neq
X_k.
\end{equation}
```

For example, the same security and timestamp may appear with two different prices.

Such observations should not be resolved through an arbitrary operation such as

``` math
\begin{equation}
\texttt{drop\_duplicates(keep="last")}
\end{equation}
```

unless the ordering itself has a documented economic meaning.

A deterministic priority rule should instead be defined. Possible criteria include:

- vendor revision timestamp;

- source priority;

- exchange or listing priority;

- data-quality flag;

- observation status;

- ingestion version.

If no defensible rule exists, the observation should be flagged for investigation rather than silently selected.

##### Uniqueness Invariant

After duplicate resolution, the pipeline should verify

``` math
\begin{equation}
\boxed{
\operatorname{Unique}
\left(
\mathrm{SecurityID},
\mathrm{Timestamp}
\right)
=
\mathrm{True}.
}
\end{equation}
```

The same principle applies to other datasets, although their keys differ. For example,

``` math
\begin{equation}
(\mathrm{CompanyID},
\mathrm{FiscalPeriod},
\mathrm{Vintage})
\end{equation}
```

may be appropriate for fundamental data, while analyst-level data may require

``` math
\begin{equation}
(\mathrm{CompanyID},
\mathrm{AnalystID},
\mathrm{ForecastPeriod},
\mathrm{Timestamp}).
\end{equation}
```

#### Missing Values

Missing observations are unavoidable in financial datasets.

Let

``` math
\begin{equation}
M_{i,t}^{(k)}
=
\begin{cases}
1,
&
X_{i,t}^{(k)}
\text{ is missing},
\\
0,
&
\text{otherwise},
\end{cases}
\end{equation}
```

denote the missingness indicator for variable $`k`$.

A crucial principle is that

``` math
\begin{equation}
\boxed{
X_{i,t}=\mathrm{NA}
}
\end{equation}
```

is not itself an instruction describing how the observation should be treated.

##### Sources of Missingness

A value may be missing because:

- the security did not yet exist;

- the market was closed;

- trading was suspended;

- the variable had not yet been published;

- the variable is economically not applicable;

- the vendor failed to collect the observation;

- security coverage is incomplete;

- the observation failed a previous validation rule.

These situations are economically different and should not automatically receive identical treatment.

##### Missingness State

Whenever possible, the pipeline should preserve not only the missing value but also its reason.

Conceptually,

``` math
\begin{equation}
\boxed{
\mathrm{MissingState}_{i,t}
\in
\left\{
\begin{array}{l}
\mathrm{NotListed},\\
\mathrm{MarketClosed},\\
\mathrm{Suspended},\\
\mathrm{NotReported},\\
\mathrm{NotApplicable},\\
\mathrm{VendorMissing},\\
\mathrm{Invalidated},\\
\mathrm{Unknown}
\end{array}
\right\}.
}
\end{equation}
```

This distinction becomes particularly important when missing values are later used in feature construction or machine-learning models.

##### Dropping Observations

A complete-case procedure retains security $`i`$ only when all required variables are observed:

``` math
\begin{equation}
\boxed{
\sum_{k=1}^{K}
M_{i,t}^{(k)}
=
0.
}
\end{equation}
```

Although simple, this approach can substantially modify the investment universe if missingness is correlated with size, liquidity, geography, analyst coverage, or firm age.

##### Forward Filling

For slowly changing variables, a previous observation may sometimes be carried forward.

Define

``` math
\begin{equation}
\tau_i^*(t)
=
\max
\left\{
\tau\leq t:
X_{i,\tau}
\text{ observed}
\right\}.
\end{equation}
```

Then

``` math
\begin{equation}
X_{i,t}^{\mathrm{ffill}}
=
X_{i,\tau_i^*(t)}.
\end{equation}
```

However, forward filling is valid only when the previous observation remains economically meaningful.

A maximum staleness condition should generally be imposed:

``` math
\begin{equation}
\boxed{
t-\tau_i^*(t)
\leq
L_{\max}.
}
\end{equation}
```

Otherwise,

``` math
\begin{equation}
X_{i,t}^{\mathrm{ffill}}
=
\mathrm{NA}.
\end{equation}
```

##### Interpolation

Time-series interpolation such as

``` math
\begin{equation}
\widetilde{X}_{i,t}
=
\lambda X_{i,t_1}
+
(1-\lambda)X_{i,t_2},
\qquad
t_1<t<t_2,
\end{equation}
```

is dangerous in predictive backtesting whenever $`X_{i,t_2}`$ was not known at time $`t`$.

In that case,

``` math
\begin{equation}
\boxed{
\text{Interpolation using future observations}
\Rightarrow
\text{Look-Ahead Bias}.
}
\end{equation}
```

Interpolation should therefore not be treated as an innocuous data-cleaning operation.

##### Imputation

Statistical imputation belongs conceptually closer to feature preprocessing than to raw data cleaning.

For example, replacing a missing feature with a cross-sectional median,

``` math
\begin{equation}
X_{i,t}^{\mathrm{imp}}
=
\operatorname{Median}_{j\in\mathcal{U}_t}
X_{j,t},
\end{equation}
```

changes the information supplied to the predictive model.

Such transformations should therefore be explicit, fitted only on admissible information, and documented as part of feature preprocessing rather than hidden inside the raw cleaning layer.

#### Stale Prices

A recorded price may be numerically valid while failing to represent a recent market transaction.

This situation is referred to as a stale price.

Let

``` math
\begin{equation}
t_{i}^{\mathrm{lasttrade}}(t)
\end{equation}
```

denote the timestamp of the most recent valid trade observed for security $`i`$ as of time $`t`$.

Define price age as

``` math
\begin{equation}
\boxed{
A_{i,t}^{P}
=
t
-
t_{i}^{\mathrm{lasttrade}}(t).
}
\end{equation}
```

A price may be classified as stale if

``` math
\begin{equation}
A_{i,t}^{P}
>
A_{\max}^{P}.
\end{equation}
```

##### Repeated Prices

A simple diagnostic is the number of consecutive observations with an unchanged price.

Define

``` math
\begin{equation}
Z_{i,t}
=
\begin{cases}
1,
&
P_{i,t}=P_{i,t-1},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

A long sequence

``` math
\begin{equation}
Z_{i,t}
=
Z_{i,t-1}
=
\cdots
=
1
\end{equation}
```

may indicate stale data.

However,

``` math
\begin{equation}
\boxed{
P_{i,t}=P_{i,t-1}
\not\Rightarrow
\text{Stale Price}.
}
\end{equation}
```

A security can genuinely close at the same price on consecutive days. Additional information such as trading volume, number of trades, quotes, and market status should therefore be considered.

##### Zero Return and Zero Volume

A stronger warning signal is

``` math
\begin{equation}
R_{i,t}=0
\qquad\text{and}\qquad
V_{i,t}=0.
\end{equation}
```

Even this condition does not uniquely identify an error: the market may have been closed or the security may have been suspended.

Staleness detection should therefore distinguish

``` math
\begin{equation}
\boxed{
\text{No Price Movement}
\neq
\text{No Trading}
\neq
\text{Missing Observation}.
}
\end{equation}
```

##### Effect on Backtests

Stale prices can distort:

- return calculations;

- volatility estimates;

- covariance matrices;

- beta estimates;

- momentum signals;

- liquidity measures;

- portfolio valuations.

For example, repeated stale prices artificially generate

``` math
\begin{equation}
R_{i,t}=0,
\end{equation}
```

which can mechanically reduce estimated volatility.

The correct treatment depends on the cause of staleness and should be determined before risk and signal calculations are performed.

#### Invalid Observations

An invalid observation violates a known logical, economic, or structural constraint.

Unlike an outlier, an invalid observation is not merely unusual: it is inconsistent with the definition of the variable or the data-generating process.

##### Hard Validation Rules

Examples include

``` math
\begin{equation}
P_{i,t}\leq0,
\end{equation}
```

``` math
\begin{equation}
V_{i,t}<0,
\end{equation}
```

or, for OHLC data,

``` math
\begin{equation}
P_{i,t}^{\mathrm{high}}
<
P_{i,t}^{\mathrm{low}}.
\end{equation}
```

Additional consistency conditions include

``` math
\begin{equation}
P_{i,t}^{\mathrm{high}}
\geq
\max
\left(
P_{i,t}^{\mathrm{open}},
P_{i,t}^{\mathrm{close}}
\right),
\end{equation}
```

and

``` math
\begin{equation}
P_{i,t}^{\mathrm{low}}
\leq
\min
\left(
P_{i,t}^{\mathrm{open}},
P_{i,t}^{\mathrm{close}}
\right).
\end{equation}
```

If bid and ask quotes are used, one would normally expect

``` math
\begin{equation}
P_{i,t}^{\mathrm{bid}}
\leq
P_{i,t}^{\mathrm{ask}}.
\end{equation}
```

##### Cross-Field Consistency

Validation should not be restricted to individual variables.

Suppose

``` math
\begin{equation}
\mathrm{DollarVolume}_{i,t}
\end{equation}
```

is provided directly by the vendor.

It can be compared with an approximate reconstructed value

``` math
\begin{equation}
\widehat{\mathrm{DollarVolume}}_{i,t}
=
P_{i,t}V_{i,t}.
\end{equation}
```

Large discrepancies may indicate inconsistent units, adjustment conventions, or data errors.

##### Hard Errors vs. Extreme Observations

Consider a one-day return of

``` math
\begin{equation}
R_{i,t}=+150\%.
\end{equation}
```

This observation is extreme but not necessarily invalid.

It may result from:

- genuine market movement;

- an acquisition;

- a corporate restructuring;

- an unadjusted stock split;

- a data error.

Therefore,

``` math
\begin{equation}
\boxed{
\text{Large Magnitude}
\not\Rightarrow
\text{Invalid Observation}.
}
\end{equation}
```

The pipeline should first investigate structural explanations, particularly corporate actions, before treating the observation statistically.

##### Validation Flags

Rather than immediately deleting suspicious observations, a robust system may attach validation flags:

``` math
\begin{equation}
F_{i,t}^{\mathrm{valid}}
\in
\{
\mathrm{Valid},
\mathrm{Warning},
\mathrm{Invalid}
\}.
\end{equation}
```

This preserves the original observation and allows the downstream policy to be defined separately from detection.

#### Corporate Action Adjustments

Corporate actions create discontinuities in prices, shares outstanding, and other security-level variables that must be distinguished from genuine economic returns.

Let

``` math
\begin{equation}
A_{i,t}
\end{equation}
```

denote the cumulative adjustment factor applied to the raw price.

An adjusted price may be represented as

``` math
\begin{equation}
\boxed{
P_{i,t}^{\mathrm{adj}}
=
A_{i,t}
P_{i,t}^{\mathrm{raw}}.
}
\end{equation}
```

##### Stock Splits

Consider an $`m`$-for-$`n`$ split.

The split ratio is

``` math
\begin{equation}
s
=
\frac{m}{n}.
\end{equation}
```

Ignoring market movements,

``` math
\begin{equation}
P_{i,t}^{\mathrm{after}}
=
\frac{1}{s}
P_{i,t^-}^{\mathrm{before}},
\end{equation}
```

while

``` math
\begin{equation}
Q_{i,t}^{\mathrm{after}}
=
s
Q_{i,t^-}^{\mathrm{before}}.
\end{equation}
```

Thus,

``` math
\begin{equation}
P_{i,t}^{\mathrm{after}}
Q_{i,t}^{\mathrm{after}}
=
P_{i,t^-}^{\mathrm{before}}
Q_{i,t^-}^{\mathrm{before}}.
\end{equation}
```

If the price series is not adjusted, a split may incorrectly appear as a large investment return.

##### Dividends

For a cash dividend $`D_{i,t}`$, total return is

``` math
\begin{equation}
\boxed{
R_{i,t}^{\mathrm{total}}
=
\frac{
P_{i,t}
+
D_{i,t}
}{
P_{i,t-1}
}
-1.
}
\end{equation}
```

Using only

``` math
\begin{equation}
\frac{P_{i,t}}{P_{i,t-1}}-1
\end{equation}
```

would incorrectly interpret the mechanical ex-dividend price decline as an economic loss.

##### Adjustment Consistency

A particularly important engineering rule is that adjustment conventions must be internally consistent.

For example, combining

``` math
\begin{equation}
P_{i,t}^{\mathrm{adj}}
\end{equation}
```

with unadjusted shares outstanding or unadjusted volume can produce inconsistent quantities.

For a split factor $`s_{i,t}`$, if historical prices are multiplied by an adjustment factor, historical share quantities generally require the inverse economic treatment.

Thus, variables such as

``` math
\begin{equation}
P,
\qquad
V,
\qquad
N^{\mathrm{shares}},
\qquad
\mathrm{MCap}
\end{equation}
```

must be checked for consistent adjustment conventions.

##### Avoiding Double Adjustment

If a vendor already provides a total-return or fully adjusted series, applying corporate-action adjustments again will double count the event.

Therefore,

``` math
\begin{equation}
\boxed{
\text{Vendor-Adjusted Data}
+
\text{Manual Adjustment}
\not\equiv
\text{Correctly Adjusted Data}.
}
\end{equation}
```

The pipeline should explicitly record which variables are raw and which are already adjusted.

#### Currency Conversion

For multi-country strategies, monetary quantities must be expressed under a consistent currency convention.

Let

``` math
\begin{equation}
C_0
\end{equation}
```

denote the portfolio base currency.

Suppose

``` math
\begin{equation}
X_{i,t}^{(C_i)}
\end{equation}
```

is a monetary quantity expressed in local currency $`C_i`$.

Let

``` math
\begin{equation}
FX_t^{C_i\rightarrow C_0}
\end{equation}
```

denote the number of units of base currency obtained for one unit of local currency.

Then

``` math
\begin{equation}
\boxed{
X_{i,t}^{(C_0)}
=
X_{i,t}^{(C_i)}
FX_t^{C_i\rightarrow C_0}.
}
\end{equation}
```

##### Quotation Convention

FX quotation conventions must be explicit.

If instead the database stores

``` math
\begin{equation}
FX_t^{C_0/C_i}
\end{equation}
```

as units of local currency per unit of base currency, conversion requires

``` math
\begin{equation}
X_{i,t}^{(C_0)}
=
\frac{
X_{i,t}^{(C_i)}
}{
FX_t^{C_0/C_i}
}.
\end{equation}
```

Confusing these two conventions creates multiplicative errors that may not be obvious from the resulting dataset.

##### Prices vs. Returns

Currency conversion of price levels and currency conversion of returns are different operations.

For returns,

``` math
\begin{equation}
1+R_{i,t}^{C_0}
=
\left(
1+R_{i,t}^{C_i}
\right)
\left(
1+R_{FX,t}^{C_i\rightarrow C_0}
\right).
\end{equation}
```

Hence,

``` math
\begin{equation}
\boxed{
R_{i,t}^{C_0}
=
R_{i,t}^{C_i}
+
R_{FX,t}^{C_i\rightarrow C_0}
+
R_{i,t}^{C_i}
R_{FX,t}^{C_i\rightarrow C_0}.
}
\end{equation}
```

The cross-product term should not be discarded when exact returns are required.

##### Currency Metadata

Every monetary variable should ideally carry an explicit currency identifier:

``` math
\begin{equation}
\boxed{
\left(
X_{i,t},
C_{i,t}
\right).
}
\end{equation}
```

This is especially important for fundamentals because reporting currencies can change through time.

Currency should therefore be treated as data rather than inferred permanently from a company’s country.

#### Frequency Alignment

Quantitative strategies frequently combine variables observed at different frequencies.

For example,

``` math
\begin{equation}
\begin{aligned}
\text{Market Data}
&:\quad
\text{Daily or Intraday},
\\
\text{Fundamentals}
&:\quad
\text{Quarterly or Semi-Annual},
\\
\text{Analyst Estimates}
&:\quad
\text{Irregular},
\\
\text{Macroeconomic Data}
&:\quad
\text{Monthly or Quarterly}.
\end{aligned}
\end{equation}
```

These observations must ultimately be mapped to a common set of strategy decision times

``` math
\begin{equation}
\mathcal{T}^{D}
=
\left\{
t_1,t_2,\ldots,t_T
\right\}.
\end{equation}
```

##### Downsampling

Suppose daily returns are converted into monthly returns.

If month $`m`$ contains trading days

``` math
\begin{equation}
\mathcal{T}_m,
\end{equation}
```

the correct simple monthly return is obtained geometrically:

``` math
\begin{equation}
\boxed{
R_{i,m}
=
\prod_{t\in\mathcal{T}_m}
(1+R_{i,t})
-1.
}
\end{equation}
```

In general,

``` math
\begin{equation}
R_{i,m}
\neq
\sum_{t\in\mathcal{T}_m}
R_{i,t}.
\end{equation}
```

For log returns, however,

``` math
\begin{equation}
r_{i,m}
=
\sum_{t\in\mathcal{T}_m}
r_{i,t}.
\end{equation}
```

##### Aggregation Depends on Variable Type

Different variables require different aggregation operators.

For example:

``` math
\begin{equation}
\boxed{
\begin{array}{lll}
\text{Returns}
&
\rightarrow
&
\text{Geometric Compounding},
\\
\text{Volume}
&
\rightarrow
&
\text{Summation or Average},
\\
\text{Closing Price}
&
\rightarrow
&
\text{Last Valid Observation},
\\
\text{Volatility}
&
\rightarrow
&
\text{Model-Dependent Aggregation},
\\
\text{Fundamental State}
&
\rightarrow
&
\text{Latest Available Observation}.
\end{array}
}
\end{equation}
```

A generic resampling operation should therefore not apply the same aggregation function to every column.

##### Upsampling

Lower-frequency variables are often mapped onto higher-frequency decision grids.

For example, a quarterly accounting variable may be carried forward to daily dates:

``` math
\begin{equation}
X_{i,t}
=
X_{i,\tau^*(t)},
\end{equation}
```

where

``` math
\begin{equation}
\tau^*(t)
=
\max
\left\{
\tau:
t_{\tau}^{\mathrm{avail}}
\leq t
\right\}.
\end{equation}
```

This is fundamentally an as-of operation, not interpolation.

No value from the next reporting period should enter before its availability date.

##### Information Frequency vs. Trading Frequency

The frequency of the input data does not determine the portfolio rebalancing frequency.

A strategy may use daily information but rebalance monthly:

``` math
\begin{equation}
\boxed{
f_{\mathrm{data}}
\neq
f_{\mathrm{signal}}
\neq
f_{\mathrm{rebalance}}.
}
\end{equation}
```

These frequencies should be represented separately in the backtesting architecture.

#### Trading Calendar Alignment

Financial datasets do not necessarily share the same calendar.

Different exchanges may have different:

- weekends;

- public holidays;

- exceptional closures;

- trading suspensions;

- market opening and closing times;

- daylight-saving conventions.

Let

``` math
\begin{equation}
\mathcal{T}_i
\end{equation}
```

denote the valid trading calendar associated with security $`i`$.

##### Local Trading Calendars

For a single-market strategy, a master calendar may be defined as

``` math
\begin{equation}
\mathcal{T}
=
\left\{
t:
\text{the relevant exchange is open at }t
\right\}.
\end{equation}
```

For a multi-market strategy, however,

``` math
\begin{equation}
\mathcal{T}_i
\neq
\mathcal{T}_j
\end{equation}
```

may hold for securities listed in different countries.

##### Union and Intersection Calendars

A global backtester may construct either the union

``` math
\begin{equation}
\mathcal{T}^{\cup}
=
\bigcup_i
\mathcal{T}_i
\end{equation}
```

or the intersection

``` math
\begin{equation}
\mathcal{T}^{\cap}
=
\bigcap_i
\mathcal{T}_i.
\end{equation}
```

The union retains every date on which at least one market is open, whereas the intersection retains only dates on which all relevant markets are open.

Neither choice is universally correct.

For global portfolios, the union calendar is often necessary for accurate NAV accounting, but individual securities must retain their own tradability status.

##### Market Closure vs. Missing Data

Suppose market $`M`$ is closed on day $`t`$.

Then the absence of a new price is not equivalent to a vendor data error.

Define

``` math
\begin{equation}
O_{i,t}
=
\begin{cases}
1,
&
\text{security }i\text{'s market is open at }t,
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

Then

``` math
\begin{equation}
O_{i,t}=0
\end{equation}
```

and

``` math
\begin{equation}
P_{i,t}=\mathrm{NA}
\end{equation}
```

may be completely valid.

The cleaning pipeline should therefore distinguish

``` math
\begin{equation}
\boxed{
\text{Scheduled Market Closure}
\neq
\text{Missing Market Observation}.
}
\end{equation}
```

##### Month-End Alignment

Calendar month-end and trading month-end are not necessarily identical.

Let

``` math
\begin{equation}
T_m^{\mathrm{cal}}
\end{equation}
```

denote the final calendar day of month $`m`$, and

``` math
\begin{equation}
T_m^{\mathrm{trade}}
=
\max
\left\{
t\in\mathcal{T}:
t\leq T_m^{\mathrm{cal}}
\right\}
\end{equation}
```

the final valid trading day.

Then a month-end strategy should normally operate on

``` math
\begin{equation}
\boxed{
T_m^{\mathrm{trade}}
}
\end{equation}
```

rather than mechanically requiring an observation on the final calendar day.

##### Time Zones

For global or intraday strategies, timestamps should be stored in an unambiguous time-zone convention.

A robust architecture may store timestamps internally in UTC,

``` math
\begin{equation}
t^{UTC},
\end{equation}
```

while retaining the corresponding local exchange timestamp

``` math
\begin{equation}
t^{\mathrm{local}}.
\end{equation}
```

The mapping depends on the exchange time zone and daylight-saving regime.

This becomes essential when determining whether information from one market was available before a trading decision in another.

##### Tradability Matrix

For multi-market strategies, it is useful to define a tradability indicator

``` math
\begin{equation}
H_{i,t}
=
\begin{cases}
1,
&
\text{security }i\text{ can be traded at }t,
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

Collecting these indicators across securities produces the tradability matrix

``` math
\begin{equation}
\boxed{
H
=
\left[
H_{i,t}
\right]_{i,t}.
}
\end{equation}
```

Portfolio implementation must respect

``` math
\begin{equation}
H_{i,t}=0
\quad\Rightarrow\quad
\Delta q_{i,t}=0,
\end{equation}
```

where $`\Delta q_{i,t}`$ denotes the requested trade in security $`i`$.

A security may therefore remain part of the portfolio while being temporarily untradable.

#### Cleaning Pipeline and Validation Invariants

The individual cleaning operations should be organized into a deterministic pipeline.

A possible ordering is

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Raw PIT Data}
&\rightarrow
\text{Key Validation}
\rightarrow
\text{Duplicate Resolution}
\\[0.1cm]
&\rightarrow
\text{Structural Validation}
\rightarrow
\text{Corporate-Action Adjustment}
\\[0.1cm]
&\rightarrow
\text{Currency Normalization}
\rightarrow
\text{Calendar Alignment}
\\[0.1cm]
&\rightarrow
\text{Frequency Alignment}
\rightarrow
\text{Missing/Stale Flags}.
\end{aligned}
}
\end{equation}
```

The exact ordering may depend on the dataset, but dependencies between operations must be explicit.

For example, an apparent $`-50\%`$ price return should not be classified as a statistical anomaly before verifying whether a two-for-one stock split occurred.

##### Validation Invariants

At the output of the cleaning layer, a set of invariants should hold.

For example:

``` math
\begin{equation}
\boxed{
\begin{aligned}
&\text{Unique observational keys},\\
&\text{No structurally impossible prices or volumes},\\
&\text{Consistent corporate-action adjustments},\\
&\text{Explicit currency units},\\
&\text{Valid trading-calendar mapping},\\
&\text{Explicit missingness and staleness states},\\
&\text{No use of information after the decision timestamp}.
\end{aligned}
}
\end{equation}
```

##### Audit Trail

Cleaning should ideally be non-destructive.

Let

``` math
\begin{equation}
X_{i,t}^{\mathrm{raw}}
\end{equation}
```

denote the original observation and

``` math
\begin{equation}
X_{i,t}^{\mathrm{clean}}
\end{equation}
```

the value exposed to the downstream research pipeline.

The system should retain, whenever feasible,

``` math
\begin{equation}
\boxed{
\left(
X_{i,t}^{\mathrm{raw}},
X_{i,t}^{\mathrm{clean}},
F_{i,t}^{\mathrm{clean}},
R_{i,t}^{\mathrm{clean}}
\right),
}
\end{equation}
```

where:

- $`F_{i,t}^{\mathrm{clean}}`$ identifies the cleaning action;

- $`R_{i,t}^{\mathrm{clean}}`$ records the reason for that action.

This makes it possible to distinguish an original vendor observation from a value that has been adjusted, invalidated, carried forward, or otherwise modified.

##### Output of the Cleaning Layer

The output of this stage should be a validated but not yet statistically transformed dataset:

``` math
\begin{equation}
\boxed{
\mathcal{D}_t^{\mathrm{clean}}
=
\mathcal{C}
\left(
\mathcal{D}_t^{\mathrm{PIT}},
\mathcal{U}_t
\right).
}
\end{equation}
```

The distinction between cleaning and subsequent statistical preprocessing is fundamental:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Cleaning}
&:
\text{ Is the observation economically and structurally valid?}
\\[0.15cm]
\text{Outlier Treatment}
&:
\text{ How should valid extreme observations be handled?}
\\[0.15cm]
\text{Feature Engineering}
&:
\text{ How should valid data be transformed into predictors?}
\end{aligned}
}
\end{equation}
```

Thus, the core data path becomes

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathcal{D}^{\mathrm{raw}}
&\rightarrow
\mathcal{D}^{\mathrm{PIT}}
\rightarrow
\mathcal{U}_t
\rightarrow
\mathcal{D}_t^{\mathrm{clean}}
\\[0.1cm]
&\rightarrow
\text{Outlier Treatment}
\rightarrow
\text{Feature Engineering}
\rightarrow
\text{Signal Construction}.
\end{aligned}
}
\end{equation}
```

