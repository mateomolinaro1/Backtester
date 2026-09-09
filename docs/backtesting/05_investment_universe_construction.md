### Investment Universe Construction

Before constructing investment signals, the backtester must determine which securities are eligible to participate in the strategy at each decision date.

Let

``` math
\begin{equation}
\mathcal{U}_t^{\mathrm{raw}}
\end{equation}
```

denote the complete set of securities represented in the point-in-time database at time $`t`$.

The investment universe is obtained by applying a collection of eligibility rules:

``` math
\begin{equation}
\boxed{
\mathcal{U}_t
=
\left\{
i\in\mathcal{U}_t^{\mathrm{raw}}
:
E_{i,t}=1
\right\},
}
\end{equation}
```

where

``` math
\begin{equation}
E_{i,t}
\in
\{0,1\}
\end{equation}
```

is the overall eligibility indicator for security $`i`$.

If the universe is defined through $`K`$ individual filters, let

``` math
\begin{equation}
E_{i,t}^{(k)}
\in
\{0,1\},
\qquad
k=1,\ldots,K,
\end{equation}
```

denote whether security $`i`$ satisfies eligibility condition $`k`$.

If all conditions are required simultaneously,

``` math
\begin{equation}
\boxed{
E_{i,t}
=
\prod_{k=1}^{K}
E_{i,t}^{(k)}.
}
\end{equation}
```

Thus,

``` math
\begin{equation}
E_{i,t}=1
\end{equation}
```

if and only if security $`i`$ satisfies every required eligibility condition.

Typical filters concern:

- geography and exchange;

- security type;

- market capitalization;

- liquidity;

- price;

- listing history;

- data availability;

- shortability.

The investment universe must be reconstructed dynamically using only point-in-time information. Universe construction is therefore itself part of the investment process rather than a static preprocessing operation.

A crucial distinction is

``` math
\begin{equation}
\boxed{
\text{Eligible Security}
\neq
\text{Selected Security}.
}
\end{equation}
```

Universe construction determines which securities *may* enter the strategy. Signal construction and portfolio construction subsequently determine which eligible securities actually receive non-zero portfolio weights.

#### Geographical and Exchange Filters

A strategy may restrict its investment universe according to geographical exposure, listing location, or trading venue.

Let

``` math
\begin{equation}
C_{i,t}
\end{equation}
```

denote the relevant country classification of security $`i`$ at time $`t`$ and let

``` math
\begin{equation}
\mathcal{C}^{\mathrm{eligible}}
\end{equation}
```

denote the set of eligible countries.

The geographical eligibility indicator is

``` math
\begin{equation}
E_{i,t}^{\mathrm{geo}}
=
\begin{cases}
1,
&
C_{i,t}\in\mathcal{C}^{\mathrm{eligible}},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

For example, a European equity strategy might define

``` math
\begin{equation}
\mathcal{C}^{\mathrm{eligible}}
=
\{
\text{France},
\text{Germany},
\text{Italy},
\text{Spain},
\ldots
\}.
\end{equation}
```

However, the definition of country is not unique.

Possible conventions include:

- country of incorporation;

- headquarters location;

- country of primary listing;

- provider-defined country;

- country of dominant economic exposure.

The convention should be specified explicitly and applied consistently.

##### Exchange Filters

The strategy may additionally restrict securities to approved exchanges.

Let

``` math
\begin{equation}
X_{i,t}
\end{equation}
```

denote the exchange on which security $`i`$ is listed and let

``` math
\begin{equation}
\mathcal{X}^{\mathrm{eligible}}
\end{equation}
```

denote the set of eligible exchanges.

Then

``` math
\begin{equation}
E_{i,t}^{\mathrm{exchange}}
=
\begin{cases}
1,
&
X_{i,t}\in\mathcal{X}^{\mathrm{eligible}},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

Exchange filters may be useful for excluding securities traded on venues with insufficient liquidity, unreliable data, limited accessibility, or different market structures.

For securities with multiple listings, the backtester should define whether the strategy operates on:

- the primary listing;

- the most liquid listing;

- a predefined preferred listing;

- all eligible listings.

Care must be taken to avoid representing the same underlying economic exposure multiple times unintentionally.

#### Security Type Filters

Historical security databases may contain instruments that are not part of the intended investment universe.

Depending on the strategy, these may include:

- ordinary common shares;

- preferred shares;

- depositary receipts;

- ETFs;

- closed-end funds;

- REITs;

- units;

- warrants;

- rights;

- convertible securities;

- other structured instruments.

Let

``` math
\begin{equation}
S_{i,t}^{\mathrm{type}}
\end{equation}
```

denote the security type and let

``` math
\begin{equation}
\mathcal{S}^{\mathrm{eligible}}
\end{equation}
```

denote the admissible set.

Then

``` math
\begin{equation}
E_{i,t}^{\mathrm{type}}
=
\begin{cases}
1,
&
S_{i,t}^{\mathrm{type}}
\in
\mathcal{S}^{\mathrm{eligible}},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

For a conventional common-equity strategy, one may for example restrict the universe to ordinary common shares.

The precise rule depends on the investment mandate and should be defined before examining strategy performance.

#### Market Capitalization Filters

Market capitalization filters are commonly used to exclude securities that are too small to trade realistically or that fall outside the intended investment segment.

The equity market capitalization of company $`i`$ can be written as

``` math
\begin{equation}
\boxed{
\mathrm{MCap}_{i,t}
=
P_{i,t}
N_{i,t}^{\mathrm{shares}},
}
\end{equation}
```

where $`N_{i,t}^{\mathrm{shares}}`$ denotes the relevant number of shares outstanding.

A minimum capitalization rule is

``` math
\begin{equation}
E_{i,t}^{\mathrm{MCap}}
=
\begin{cases}
1,
&
\mathrm{MCap}_{i,t}
\geq
M_{\min},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

##### Full vs. Free-Float Market Capitalization

For investability purposes, free-float capitalization may be more informative than total capitalization.

Let

``` math
\begin{equation}
f_{i,t}^{\mathrm{float}}
\in[0,1]
\end{equation}
```

denote the fraction of shares considered freely tradable.

Then

``` math
\begin{equation}
\boxed{
\mathrm{FFMCap}_{i,t}
=
f_{i,t}^{\mathrm{float}}
\mathrm{MCap}_{i,t}.
}
\end{equation}
```

A strategy may therefore impose

``` math
\begin{equation}
\mathrm{FFMCap}_{i,t}
\geq
M_{\min}^{\mathrm{float}}.
\end{equation}
```

##### Absolute and Relative Thresholds

A capitalization filter need not use a fixed monetary threshold.

A relative rule may retain, for example, securities above a given cross-sectional percentile:

``` math
\begin{equation}
\mathrm{MCap}_{i,t}
\geq
Q_{q,t}^{\mathrm{MCap}},
\end{equation}
```

where

``` math
\begin{equation}
Q_{q,t}^{\mathrm{MCap}}
\end{equation}
```

is the $`q`$-th percentile of the point-in-time market-capitalization distribution.

Alternatively, the strategy may retain the $`N`$ largest eligible securities.

All quantities used in the ranking must be computed using the historical cross-section available at time $`t`$.

#### Liquidity Filters

Market capitalization alone does not guarantee that a security can be traded efficiently.

Liquidity filters attempt to remove securities for which realistic execution would be difficult or excessively costly.

A common measure is Average Daily Volume in currency units:

``` math
\begin{equation}
\mathrm{ADV}_{i,t}^{\$}
=
\frac{1}{L}
\sum_{\ell=1}^{L}
P_{i,t-\ell}
V_{i,t-\ell}.
\end{equation}
```

A minimum-liquidity rule is

``` math
\begin{equation}
E_{i,t}^{\mathrm{ADV}}
=
\begin{cases}
1,
&
\mathrm{ADV}_{i,t}^{\$}
\geq
ADV_{\min},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

Notice that the window above ends at $`t-1`$. This is appropriate when the universe is constructed before trading on day $`t`$ and the complete trading volume of day $`t`$ is not yet observable.

##### Alternative Liquidity Measures

Other liquidity filters may use:

- median daily traded notional;

- turnover ratio;

- bid–ask spread;

- number of trading days;

- percentage of zero-return days;

- quoted depth;

- Amihud-type illiquidity measures.

For example, the Amihud illiquidity measure over $`L`$ observations can be written as

``` math
\begin{equation}
\boxed{
\mathrm{ILLIQ}_{i,t}
=
\frac{1}{L}
\sum_{\ell=1}^{L}
\frac{
|R_{i,t-\ell}|
}{
\mathrm{DollarVolume}_{i,t-\ell}
}.
}
\end{equation}
```

Higher values indicate greater price movement per unit of traded notional and therefore lower liquidity.

##### Universe Filter vs. Portfolio Constraint

Liquidity can enter the investment process at two distinct stages.

First, a universe filter may impose

``` math
\begin{equation}
\mathrm{ADV}_{i,t}^{\$}
\geq
ADV_{\min}.
\end{equation}
```

Second, portfolio construction may impose a position- or trade-size constraint such as

``` math
\begin{equation}
\frac{
|\Delta w_{i,t}|A_t
}{
\mathrm{ADV}_{i,t}^{\$}
}
\leq
PR_{\max}.
\end{equation}
```

These operations should not be confused.

The first determines whether the security is eligible at all. The second determines how much of an eligible security may realistically be traded.

#### Price Filters

Strategies may exclude securities whose prices fall below a minimum threshold.

Let

``` math
\begin{equation}
P_{i,t}^{\mathrm{filter}}
\end{equation}
```

denote the price observable at the universe-construction time.

A simple rule is

``` math
\begin{equation}
E_{i,t}^{\mathrm{price}}
=
\begin{cases}
1,
&
P_{i,t}^{\mathrm{filter}}
\geq
P_{\min},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

Low-priced securities may exhibit:

- larger proportional bid–ask spreads;

- stronger price discreteness;

- lower institutional capacity;

- greater sensitivity to microstructure effects.

The threshold should be expressed in the appropriate local or common currency, depending on the design of the universe.

Care must also be taken when using historical prices around stock splits. A price filter should represent the actual economically relevant price at the historical date rather than an improperly adjusted value that incorporates future corporate actions.

#### Listing History Requirements

Newly listed securities may not possess sufficient historical information for signal estimation, risk estimation, or portfolio construction.

Let

``` math
\begin{equation}
t_i^{\mathrm{list}}
\end{equation}
```

denote the historical listing date of security $`i`$.

Its listing age at decision date $`t`$ is

``` math
\begin{equation}
\boxed{
A_{i,t}^{\mathrm{listing}}
=
t-t_i^{\mathrm{list}}.
}
\end{equation}
```

A minimum-history rule may require

``` math
\begin{equation}
A_{i,t}^{\mathrm{listing}}
\geq
L_{\min}.
\end{equation}
```

Equivalently,

``` math
\begin{equation}
E_{i,t}^{\mathrm{history}}
=
\begin{cases}
1,
&
A_{i,t}^{\mathrm{listing}}
\geq
L_{\min},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

##### Calendar History vs. Valid Observations

Listing age alone may be insufficient.

A stock listed for one year may have experienced trading suspensions or missing observations.

It may therefore be preferable to require a minimum number of valid historical observations:

``` math
\begin{equation}
\boxed{
N_{i,t}^{\mathrm{valid}}
\geq
N_{\min}.
}
\end{equation}
```

For example, estimating a rolling beta over 252 trading days may require a minimum number of valid return observations within that window rather than merely requiring that the stock was listed 252 calendar days ago.

##### IPO Treatment

A minimum listing-history rule implicitly excludes recent IPOs.

This may be necessary because:

- historical returns are insufficient;

- accounting histories may be incomplete;

- liquidity may be unstable immediately after listing;

- certain rolling features cannot yet be computed.

However, such exclusions also modify the economic universe of the strategy and should therefore be documented explicitly.

#### Data Availability Requirements

A security may satisfy all economic and liquidity criteria while lacking the data required by the investment model.

Let the signal require $`K`$ inputs

``` math
\begin{equation}
X_{i,t}^{(1)},
\ldots,
X_{i,t}^{(K)}.
\end{equation}
```

A strict complete-case eligibility rule is

``` math
\begin{equation}
E_{i,t}^{\mathrm{data}}
=
\begin{cases}
1,
&
X_{i,t}^{(k)}
\text{ is available for all }
k=1,\ldots,K,
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
\boxed{
E_{i,t}^{\mathrm{data}}
=
\prod_{k=1}^{K}
\mathbbm{1}
\left(
X_{i,t}^{(k)}
\text{ available}
\right).
}
\end{equation}
```

##### Core vs. Optional Variables

Not every missing variable necessarily requires removing a security.

The feature set can be divided into:

``` math
\begin{equation}
\mathcal{K}
=
\mathcal{K}^{\mathrm{required}}
\cup
\mathcal{K}^{\mathrm{optional}}.
\end{equation}
```

Eligibility then requires only

``` math
\begin{equation}
X_{i,t}^{(k)}
\text{ available}
\qquad
\forall
k\in
\mathcal{K}^{\mathrm{required}}.
\end{equation}
```

Optional variables may subsequently be treated through an explicitly defined missing-data procedure.

##### Missingness as a Selection Mechanism

Data-availability filters can themselves create selection effects.

For example, small or recently listed firms may have:

- fewer analyst estimates;

- shorter accounting histories;

- poorer alternative-data coverage.

Therefore,

``` math
\begin{equation}
\boxed{
\text{Missing Data}
\not\Rightarrow
\text{Random Missingness}.
}
\end{equation}
```

Requiring complete observations can systematically alter the economic characteristics of the universe.

The number and characteristics of securities excluded because of missing data should therefore be monitored.

#### Shortability Constraints

For long–short strategies, eligibility on the long side does not necessarily imply eligibility on the short side.

Define

``` math
\begin{equation}
\mathcal{U}_t^{L}
\end{equation}
```

and

``` math
\begin{equation}
\mathcal{U}_t^{S}
\end{equation}
```

as the long-eligible and short-eligible universes respectively.

Typically,

``` math
\begin{equation}
\boxed{
\mathcal{U}_t^{S}
\subseteq
\mathcal{U}_t^{L}
}
\end{equation}
```

or, more generally, both are subsets of a common investment universe.

##### Borrow Availability

Let

``` math
\begin{equation}
B_{i,t}^{\mathrm{avail}}
\end{equation}
```

denote the number or notional amount of shares available to borrow.

A minimum borrow-availability condition may be written as

``` math
\begin{equation}
B_{i,t}^{\mathrm{avail}}
\geq
B_{\min}.
\end{equation}
```

##### Borrow Cost

Let

``` math
\begin{equation}
b_{i,t}
\end{equation}
```

denote the annualized borrow fee.

A strategy may exclude securities satisfying

``` math
\begin{equation}
b_{i,t}
>
b_{\max}.
\end{equation}
```

The short-eligibility indicator can therefore combine both conditions:

``` math
\begin{equation}
E_{i,t}^{\mathrm{short}}
=
\begin{cases}
1,
&
B_{i,t}^{\mathrm{avail}}
\geq
B_{\min}
\quad\text{and}\quad
b_{i,t}
\leq
b_{\max},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

##### Filter vs. Cost Treatment

A high borrow fee does not necessarily imply that a security should be excluded.

Two different approaches are possible:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Hard Constraint:}
&\quad
b_{i,t}>b_{\max}
\Rightarrow
i\notin\mathcal{U}_t^{S},
\\[0.15cm]
\text{Soft Treatment:}
&\quad
i\in\mathcal{U}_t^{S},
\text{ but borrow cost enters expected net return.}
\end{aligned}
}
\end{equation}
```

The appropriate choice depends on the portfolio-construction framework and availability of reliable securities-lending data.

##### Asymmetric Long and Short Universes

The distinction between long and short eligibility becomes important when interpreting a long–short strategy.

For example, the raw signal may rank a difficult-to-borrow security as one of the strongest short candidates.

If that security cannot actually be borrowed, the theoretical short portfolio and implementable short portfolio differ.

Thus,

``` math
\begin{equation}
\boxed{
\text{Predictive Opportunity Set}
\neq
\text{Implementable Short Opportunity Set}.
}
\end{equation}
```

#### Dynamic Universe Construction

The investment universe should generally be reconstructed at every relevant decision date rather than defined once over the complete historical sample.

Let

``` math
\begin{equation}
\mathcal{U}_t^{(0)}
\end{equation}
```

denote the point-in-time raw universe.

A sequential representation of the filtering process is

``` math
\begin{equation}
\begin{aligned}
\mathcal{U}_t^{(1)}
&=
\mathcal{F}_{\mathrm{geo}}
\left(
\mathcal{U}_t^{(0)}
\right),
\\
\mathcal{U}_t^{(2)}
&=
\mathcal{F}_{\mathrm{type}}
\left(
\mathcal{U}_t^{(1)}
\right),
\\
\mathcal{U}_t^{(3)}
&=
\mathcal{F}_{\mathrm{MCap}}
\left(
\mathcal{U}_t^{(2)}
\right),
\\
\mathcal{U}_t^{(4)}
&=
\mathcal{F}_{\mathrm{liq}}
\left(
\mathcal{U}_t^{(3)}
\right),
\\
&\vdots
\\
\mathcal{U}_t
&=
\mathcal{F}_{K}
\left(
\mathcal{U}_t^{(K-1)}
\right).
\end{aligned}
\end{equation}
```

Equivalently, the final universe can be expressed directly as

``` math
\begin{equation}
\boxed{
\mathcal{U}_t
=
\left\{
i\in\mathcal{U}_t^{\mathrm{raw}}
:
E_{i,t}^{\mathrm{geo}}
E_{i,t}^{\mathrm{exchange}}
E_{i,t}^{\mathrm{type}}
E_{i,t}^{\mathrm{MCap}}
E_{i,t}^{\mathrm{liq}}
E_{i,t}^{\mathrm{price}}
E_{i,t}^{\mathrm{history}}
E_{i,t}^{\mathrm{data}}
=1
\right\}.
}
\end{equation}
```

Short eligibility may then be imposed separately.

##### Universe Evolution

Because eligibility characteristics change through time,

``` math
\begin{equation}
\boxed{
\mathcal{U}_t
\neq
\mathcal{U}_{t+1}
}
\end{equation}
```

in general.

A security may enter the universe because:

- it completes an IPO and satisfies the minimum-history requirement;

- its capitalization exceeds the required threshold;

- its liquidity improves;

- sufficient fundamental or alternative data become available.

A security may leave because:

- it delists;

- its capitalization falls below the threshold;

- liquidity deteriorates;

- its price falls below the minimum;

- required data become unavailable;

- its security or geographical classification changes.

##### Universe Reconstitution Frequency

The universe does not necessarily need to be reconstructed every day.

Let

``` math
\begin{equation}
\mathcal{T}^{U}
=
\left\{
t_1^{U},
t_2^{U},
\ldots
\right\}
\end{equation}
```

denote universe-reconstitution dates.

Possible frequencies include:

- daily;

- weekly;

- monthly;

- quarterly;

- index-reconstitution dates.

Between two reconstitution dates, the universe may either remain fixed or be updated for exceptional events such as delistings and trading suspensions.

This convention should be specified explicitly.

##### Buffer Rules and Universe Turnover

Hard thresholds can generate excessive universe turnover.

Suppose the minimum market capitalization is

``` math
\begin{equation}
M_{\min}.
\end{equation}
```

A security whose capitalization fluctuates repeatedly around this threshold may enter and leave the universe frequently.

One solution is to introduce separate entry and exit thresholds:

``` math
\begin{equation}
M_{\mathrm{entry}}
>
M_{\mathrm{exit}}.
\end{equation}
```

A security outside the universe enters only if

``` math
\begin{equation}
\mathrm{MCap}_{i,t}
\geq
M_{\mathrm{entry}},
\end{equation}
```

whereas an existing constituent remains eligible provided

``` math
\begin{equation}
\mathrm{MCap}_{i,t}
\geq
M_{\mathrm{exit}}.
\end{equation}
```

Hence,

``` math
\begin{equation}
\boxed{
M_{\mathrm{entry}}
>
M_{\mathrm{exit}}
}
\end{equation}
```

creates a buffer region that reduces mechanical universe turnover.

Similar buffer rules can be applied to liquidity, rankings, and other eligibility criteria.

##### Universe Diagnostics

Universe construction should be treated as an observable component of the backtest rather than as an invisible preprocessing step.

At each date $`t`$, useful diagnostics include:

- number of securities in the raw universe;

- number removed by each filter;

- final universe size;

- median and distribution of market capitalization;

- median and distribution of liquidity;

- sector and country composition;

- number of shortable securities;

- universe entries and exits.

Let

``` math
\begin{equation}
N_t
=
|\mathcal{U}_t|
\end{equation}
```

denote the number of eligible securities.

The time series

``` math
\begin{equation}
\left\{
N_t
\right\}_{t=1}^{T}
\end{equation}
```

should be monitored for unexpected discontinuities that may reveal data or filtering errors.

##### Final Point-in-Time Universe

The final investment universe should depend exclusively on information available at the universe-construction time.

Formally,

``` math
\begin{equation}
\boxed{
\mathcal{U}_t
=
G
\left(
\mathcal{I}_t;
\theta^{U}
\right),
}
\end{equation}
```

where:

- $`\mathcal{I}_t`$ is the point-in-time information set;

- $`G(\cdot)`$ is the universe-construction procedure;

- $`\theta^{U}`$ contains the predefined eligibility parameters.

The resulting universe is then passed to the subsequent stages of the investment process:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathcal{I}_t
&\rightarrow
\mathcal{U}_t
\rightarrow
\text{Data Cleaning}
\rightarrow
\text{Feature Construction}
\\[0.15cm]
&\rightarrow
\text{Signal}
\rightarrow
\text{Portfolio Construction}.
\end{aligned}
}
\end{equation}
```

Universe construction therefore acts as the bridge between the complete point-in-time database and the cross-section on which the quantitative investment strategy is actually defined.

