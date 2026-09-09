### Raw Data Acquisition

Data constitute the first operational input of a quantitative investment process. Before signals can be constructed, the backtester must collect the historical information required to reproduce the investment decisions that could have been made at each point in time.

Let the complete collection of raw data available to the research system be denoted by

``` math
\begin{equation}
\mathcal{D}.
\end{equation}
```

This collection may contain several heterogeneous data sources:

``` math
\begin{equation}
\boxed{
\mathcal{D}
=
\left\{
\mathcal{D}^{\mathrm{market}},
\mathcal{D}^{\mathrm{fund}},
\mathcal{D}^{\mathrm{est}},
\mathcal{D}^{\mathrm{alt}},
\mathcal{D}^{\mathrm{risk}},
\mathcal{D}^{\mathrm{class}},
\mathcal{D}^{\mathrm{corp}},
\mathcal{D}^{\mathrm{impl}}
\right\}.
}
\end{equation}
```

where the superscripts correspond respectively to market data, fundamental data, analyst estimates, alternative data, risk and market variables, classifications, corporate actions, and implementation-related data.

These sources may differ substantially in:

- observation frequency;

- historical coverage;

- entity granularity;

- timestamp conventions;

- identifiers;

- revision policies;

- data quality;

- point-in-time availability.

Consequently, raw data acquisition should not be viewed as the construction of a single homogeneous table. Rather, it consists of collecting a set of heterogeneous historical sources that will subsequently be aligned into a consistent point-in-time information set.

A useful distinction is

``` math
\begin{equation}
\boxed{
\text{Raw Data}
\neq
\text{Point-in-Time Data}
\neq
\text{Model-Ready Data}.
}
\end{equation}
```

Raw data correspond to observations obtained from the original data sources. Point-in-time data reconstruct the information that was genuinely available at each historical date. Model-ready data are subsequently cleaned, aligned, transformed, and converted into features suitable for signal construction.

The present section focuses exclusively on the nature of the raw inputs.

#### Market Data

Market data describe the observable trading history of financial securities.

For equity security $`i`$, a standard daily record may contain

``` math
\begin{equation}
\boxed{
\left(
P_{i,t}^{\mathrm{open}},
P_{i,t}^{\mathrm{high}},
P_{i,t}^{\mathrm{low}},
P_{i,t}^{\mathrm{close}},
V_{i,t}
\right),
}
\end{equation}
```

where:

- $`P_{i,t}^{\mathrm{open}}`$ denotes the opening price;

- $`P_{i,t}^{\mathrm{high}}`$ denotes the highest traded price;

- $`P_{i,t}^{\mathrm{low}}`$ denotes the lowest traded price;

- $`P_{i,t}^{\mathrm{close}}`$ denotes the closing price;

- $`V_{i,t}`$ denotes trading volume.

Depending on the strategy and data provider, market data may additionally contain:

- VWAP;

- number of trades;

- traded notional;

- intraday trades;

- quotes;

- order-book information;

- trading venue;

- exchange status.

Detailed liquidity measures such as bid–ask spreads, market depth, ADV, and participation rates are treated separately in Section <a href="#subsec:liquidity_borrowing_transaction_cost_data" data-reference-type="ref" data-reference="subsec:liquidity_borrowing_transaction_cost_data">1.8</a>.

##### Prices and Returns

Given a sequence of prices, the simple return of security $`i`$ between $`t-1`$ and $`t`$ is

``` math
\begin{equation}
R_{i,t}
=
\frac{P_{i,t}}{P_{i,t-1}}-1.
\end{equation}
```

The corresponding logarithmic return is

``` math
\begin{equation}
r_{i,t}
=
\log(P_{i,t})
-
\log(P_{i,t-1}).
\end{equation}
```

The two quantities satisfy

``` math
\begin{equation}
r_{i,t}
=
\log(1+R_{i,t}),
\end{equation}
```

and

``` math
\begin{equation}
R_{i,t}
=
e^{r_{i,t}}-1.
\end{equation}
```

For small returns,

``` math
\begin{equation}
r_{i,t}
\approx
R_{i,t}.
\end{equation}
```

Price returns do not necessarily represent the complete economic return earned by an investor.

If $`D_{i,t}`$ denotes cash distributions received during the period, a simplified total return is

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

The treatment of dividends, splits, mergers, and other events is developed in Section <a href="#subsec:corporate_actions" data-reference-type="ref" data-reference="subsec:corporate_actions">1.7</a>.

##### Raw and Adjusted Prices

Historical databases frequently provide both raw and adjusted prices.

Let

``` math
\begin{equation}
P_{i,t}^{\mathrm{raw}}
\end{equation}
```

denote the observed market price and

``` math
\begin{equation}
P_{i,t}^{\mathrm{adj}}
\end{equation}
```

an adjusted price.

A generic relationship is

``` math
\begin{equation}
P_{i,t}^{\mathrm{adj}}
=
A_{i,t}
P_{i,t}^{\mathrm{raw}},
\end{equation}
```

where $`A_{i,t}`$ denotes an adjustment factor.

Whenever possible, the research system should retain separately

``` math
\begin{equation}
\boxed{
P_{i,t}^{\mathrm{raw}},
\qquad
A_{i,t},
\qquad
P_{i,t}^{\mathrm{adj}}.
}
\end{equation}
```

This allows the historical transformation to remain auditable rather than depending exclusively on vendor-preprocessed series.

##### Data Frequency

Market data may be observed at different frequencies:

``` math
\begin{equation}
\boxed{
\text{Tick}
\rightarrow
\text{Intraday}
\rightarrow
\text{Daily}
\rightarrow
\text{Weekly}
\rightarrow
\text{Monthly}.
}
\end{equation}
```

The required frequency depends on both signal horizon and execution horizon.

For example, a monthly equity strategy may still require daily prices to construct signals or simulate execution, whereas an intraday strategy may require individual transactions and quotes.

##### Security Identifiers

A security should not generally be identified exclusively by its ticker.

Tickers may:

- change through time;

- be reused;

- differ across exchanges;

- refer to different share classes.

A robust architecture should therefore use persistent identifiers whenever possible.

Conceptually,

``` math
\begin{equation}
\boxed{
\text{Company}
\longleftrightarrow
\text{Security}
\longleftrightarrow
\text{Listing}
\longleftrightarrow
\text{Ticker}.
}
\end{equation}
```

These objects are distinct. A company may issue multiple securities, and one security may be associated with multiple listings or trading venues.

#### Fundamental Data

Fundamental data describe the accounting and economic characteristics of companies.

They are commonly extracted from:

- income statements;

- balance sheets;

- cash-flow statements;

- regulatory filings;

- annual and interim reports;

- company disclosures.

For company $`i`$ and accounting period $`\tau`$, let

``` math
\begin{equation}
F_{i,\tau}
=
\begin{bmatrix}
F_{i,\tau}^{(1)}\\
\vdots\\
F_{i,\tau}^{(K)}
\end{bmatrix}
\in
\mathbb{R}^{K}
\end{equation}
```

denote a vector of $`K`$ fundamental variables.

##### Main Accounting Variables

Typical income-statement variables include:

- revenue;

- gross profit;

- EBITDA;

- EBIT;

- operating income;

- interest expense;

- taxes;

- net income;

- earnings per share.

Typical balance-sheet variables include:

- cash;

- inventories;

- receivables;

- total assets;

- short- and long-term debt;

- total liabilities;

- shareholders’ equity;

- book value.

Typical cash-flow variables include:

- operating cash flow;

- capital expenditures;

- investing cash flow;

- financing cash flow;

- free cash flow;

- dividends;

- share repurchases.

##### Stock and Flow Variables

Accounting variables differ according to whether they are measured at a date or over a period.

A stock variable, such as total assets, is measured at a particular date:

``` math
\begin{equation}
\mathrm{Assets}_{i,\tau}.
\end{equation}
```

A flow variable, such as revenue, is accumulated over an interval:

``` math
\begin{equation}
\mathrm{Revenue}_{i,[\tau_0,\tau_1]}.
\end{equation}
```

This distinction matters when constructing financial ratios.

For example,

``` math
\begin{equation}
ROA_i
=
\frac{
\mathrm{NetIncome}_{i,[\tau_0,\tau_1]}
}{
\frac{1}{2}
\left(
\mathrm{Assets}_{i,\tau_0}
+
\mathrm{Assets}_{i,\tau_1}
\right)
}.
\end{equation}
```

The numerator is measured over a period, whereas the denominator approximates the average balance-sheet stock over that period.

##### Reporting Structure

Fundamental data may be reported annually, semi-annually, or quarterly, depending on the company, country, regulatory regime, and historical period.

Importantly, the accounting period to which an observation refers is not necessarily the date on which that observation becomes known to investors.

The precise distinction between reporting date, publication date, vendor timestamp, and information-availability date is deferred to the Point-in-Time Data Construction section.

#### Analyst Estimates

Sell-side analysts publish forecasts for future company fundamentals and other financial quantities.

For company $`i`$, analyst $`a`$, information date $`t`$, target fiscal period $`\tau`$, and forecasted variable $`k`$, an individual estimate can be represented as

``` math
\begin{equation}
E_{i,a,t}^{(\tau,k)}.
\end{equation}
```

Typical forecast variables include:

- revenue;

- EBITDA;

- EBIT;

- earnings per share;

- net income;

- free cash flow;

- target price.

##### Individual and Consensus Estimates

Suppose $`A_{i,t}`$ analysts provide estimates for company $`i`$.

A simple consensus estimate is

``` math
\begin{equation}
\boxed{
\bar{E}_{i,t}
=
\frac{1}{A_{i,t}}
\sum_{a=1}^{A_{i,t}}
E_{i,a,t}.
}
\end{equation}
```

Alternative aggregation methods may use:

- the median;

- trimmed means;

- recency weights;

- analyst-specific weights.

The number of contributing analysts,

``` math
\begin{equation}
A_{i,t},
\end{equation}
```

may itself be informative because coverage and forecast uncertainty often vary across securities.

##### Forecast Revisions and Dispersion

A simple revision over horizon $`h`$ is

``` math
\begin{equation}
\boxed{
\Delta E_{i,t}^{(h)}
=
E_{i,t}
-
E_{i,t-h}.
}
\end{equation}
```

A normalized revision may be written as

``` math
\begin{equation}
\Delta E_{i,t}^{\mathrm{rel}}
=
\frac{
E_{i,t}-E_{i,t-h}
}{
|E_{i,t-h}|
}.
\end{equation}
```

If individual analyst estimates are available, disagreement may be measured as

``` math
\begin{equation}
\mathrm{Dispersion}_{i,t}
=
\sqrt{
\frac{1}{A_{i,t}-1}
\sum_{a=1}^{A_{i,t}}
\left(
E_{i,a,t}
-
\bar{E}_{i,t}
\right)^2
}.
\end{equation}
```

Revisions measure changes in expectations, whereas dispersion measures cross-sectional disagreement among analysts.

##### Actuals

Once the corresponding realized accounting quantity becomes available, analyst forecasts can be compared with the realized value.

The timing of forecasts, revisions, and actual releases is essential and will be handled explicitly in the point-in-time construction stage rather than in the raw-data description.

#### Alternative Data

Alternative data refer broadly to information sources outside conventional market, accounting, and analyst-estimate databases.

Examples include:

- news;

- earnings-call transcripts;

- regulatory text;

- social-media activity;

- web traffic;

- job postings;

- credit-card transactions;

- satellite imagery;

- geolocation information;

- supply-chain information;

- product reviews;

- search activity.

Unlike conventional financial data, these sources may be:

- unstructured;

- high dimensional;

- irregularly sampled;

- event driven;

- noisy;

- difficult to associate with tradable securities.

##### Raw Data Representations

Alternative-data observations need not initially be numerical.

For example,

``` math
\begin{equation}
\text{Text Document},
\qquad
\text{Image},
\qquad
\text{Event},
\qquad
\text{Graph},
\qquad
\text{Transaction Record}
\end{equation}
```

may all constitute raw inputs.

Their conversion into numerical features belongs to the Feature Engineering section rather than to raw data acquisition.

##### Entity Mapping

Alternative datasets frequently refer to economic entities rather than directly to securities.

A generic mapping may therefore require

``` math
\begin{equation}
\boxed{
\text{Raw Entity}
\longrightarrow
\text{Company ID}
\longrightarrow
\text{Security ID}.
}
\end{equation}
```

Examples include mapping a product, brand, subsidiary, website, or executive to the corresponding publicly traded company.

The historical validity and timing of these mappings will be addressed in the point-in-time construction stage.

#### Risk Factors and Market Variables

Quantitative strategies frequently require market-wide variables in addition to security-specific information.

Let

``` math
\begin{equation}
F_t
=
\begin{bmatrix}
F_{1,t}\\
\vdots\\
F_{K,t}
\end{bmatrix}
\end{equation}
```

denote a vector of $`K`$ systematic factor returns.

##### Systematic Risk Factors

Possible factors include:

- market;

- size;

- value;

- momentum;

- profitability;

- investment;

- quality;

- low volatility;

- industry;

- country.

A linear factor model may be represented as

``` math
\begin{equation}
R_{i,t}^{e}
=
\alpha_i
+
\beta_i^\top F_t
+
\varepsilon_{i,t},
\end{equation}
```

where $`\beta_i`$ denotes the vector of factor exposures.

Such factors may later be used for:

- beta estimation;

- signal neutralization;

- portfolio constraints;

- risk modeling;

- performance attribution.

##### Risk-Free Rates and Macroeconomic Variables

Other relevant market-level inputs may include:

- risk-free rates;

- government bond yields;

- yield-curve slopes;

- credit spreads;

- implied volatility;

- inflation;

- economic growth;

- monetary-policy variables;

- foreign-exchange rates;

- commodity prices.

If $`R_{f,t}`$ denotes the relevant risk-free return, an excess return is

``` math
\begin{equation}
\boxed{
R_{i,t}^{e}
=
R_{i,t}-R_{f,t}.
}
\end{equation}
```

Macroeconomic variables may subsequently require vintage reconstruction because the values observed today may differ from the originally released values.

##### Currency Data

Foreign-exchange data are required when assets and portfolio NAV are expressed in different currencies.

Suppose an asset earns return $`R_{i,t}^{F}`$ in foreign currency $`F`$, while the foreign currency earns return $`R_{FX,t}`$ relative to domestic currency $`D`$.

Then

``` math
\begin{equation}
1+R_{i,t}^{D}
=
\left(
1+R_{i,t}^{F}
\right)
\left(
1+R_{FX,t}
\right),
\end{equation}
```

so that

``` math
\begin{equation}
\boxed{
R_{i,t}^{D}
=
R_{i,t}^{F}
+
R_{FX,t}
+
R_{i,t}^{F}R_{FX,t}.
}
\end{equation}
```

The exchange-rate quotation convention must be specified consistently.

#### Industry and Country Classifications

Industry, sector, and country classifications provide categorical information about securities and firms.

They may later be used for:

- universe construction;

- neutralization;

- portfolio constraints;

- risk modeling;

- performance attribution.

Let

``` math
\begin{equation}
g(i,t)
\end{equation}
```

denote the industry classification of security $`i`$ at time $`t`$.

##### Industry Representation

For $`K`$ mutually exclusive industries, define

``` math
\begin{equation}
D_{i,k,t}
=
\begin{cases}
1,
&
\text{if security }i
\text{ belongs to industry }k,
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

The classification matrix is therefore

``` math
\begin{equation}
\boxed{
D_t
\in
\mathbb{R}^{N_t\times K}.
}
\end{equation}
```

Industry classifications are often hierarchical:

``` math
\begin{equation}
\boxed{
\text{Sector}
\rightarrow
\text{Industry Group}
\rightarrow
\text{Industry}
\rightarrow
\text{Sub-Industry}.
}
\end{equation}
```

The appropriate level of granularity depends on the intended application.

##### Time Variation

Industry membership may vary through time:

``` math
\begin{equation}
g(i,t_1)
\neq
g(i,t_2).
\end{equation}
```

Changes may result from:

- changes in business activity;

- restructurings;

- mergers and acquisitions;

- classification-provider revisions.

Historical classification changes must therefore be retained rather than replaced by the latest classification.

##### Country Classification

Country assignment may also be defined in several ways, including:

- country of incorporation;

- headquarters location;

- country of primary listing;

- provider classification;

- dominant economic exposure.

The appropriate convention should be defined according to the economic purpose of the strategy.

#### Corporate Actions

Corporate actions modify the economic value, number, or identity of securities and must therefore be represented explicitly in the data architecture.

Relevant events include:

- cash dividends;

- special dividends;

- stock splits;

- reverse stock splits;

- stock dividends;

- rights issues;

- spin-offs;

- mergers;

- acquisitions;

- tender offers;

- share-class conversions;

- delistings.

##### Stock Splits

Suppose a company performs an $`m`$-for-$`n`$ stock split.

Ignoring other market movements,

``` math
\begin{equation}
Q_{i,t}^{\mathrm{after}}
=
Q_{i,t^-}
\frac{m}{n},
\end{equation}
```

while

``` math
\begin{equation}
P_{i,t}^{\mathrm{after}}
=
P_{i,t^-}
\frac{n}{m}.
\end{equation}
```

Hence,

``` math
\begin{equation}
Q_{i,t}^{\mathrm{after}}
P_{i,t}^{\mathrm{after}}
=
Q_{i,t^-}
P_{i,t^-}.
\end{equation}
```

The stock split changes the number of shares and quoted price but does not itself create shareholder wealth.

##### Cash Dividends

A cash dividend represents an economic distribution to shareholders.

If $`D_{i,t}`$ is paid during the period, the total return is

``` math
\begin{equation}
R_{i,t}^{\mathrm{total}}
=
\frac{
P_{i,t}+D_{i,t}
}{
P_{i,t-1}
}
-1.
\end{equation}
```

##### Mergers, Acquisitions, and Delistings

A corporate event may replace an existing security with:

- cash;

- another security;

- a combination of cash and securities.

The economic conversion must be represented before the original security is removed from portfolio accounting.

For delistings, the required sequence is

``` math
\begin{equation}
\boxed{
\text{Existing Position}
\rightarrow
\text{Terminal Economic Payoff}
\rightarrow
\text{Position Removal}.
}
\end{equation}
```

as discussed in Section <a href="#subsubsec:delisting_returns" data-reference-type="ref" data-reference="subsubsec:delisting_returns">2.2.1</a>.

##### Corporate-Action Event Table

A generic corporate-action record may contain

``` math
\begin{equation}
\boxed{
\left(
\mathrm{SecurityID},
\mathrm{EventType},
t^{\mathrm{announcement}},
t^{\mathrm{ex}},
t^{\mathrm{effective}},
t^{\mathrm{payment}},
\mathrm{Terms}
\right).
}
\end{equation}
```

These timestamps have distinct economic meanings and must therefore be stored separately.

#### Liquidity, Borrowing, and Transaction Cost Data

A predictive strategy is economically meaningful only if the resulting portfolio can be implemented under realistic trading conditions.

The raw-data layer should therefore include information describing:

- trading liquidity;

- execution conditions;

- securities lending;

- explicit market fees.

##### Liquidity Measures

Relevant variables include:

- traded volume;

- traded notional;

- Average Daily Volume;

- bid–ask spread;

- quoted depth;

- turnover ratio;

- number of trades.

Average Daily Volume in shares over lookback window $`L`$ may be defined as

``` math
\begin{equation}
\mathrm{ADV}_{i,t}^{\mathrm{shares}}
=
\frac{1}{L}
\sum_{\ell=0}^{L-1}
V_{i,t-\ell}.
\end{equation}
```

Currency-denominated ADV is

``` math
\begin{equation}
\boxed{
\mathrm{ADV}_{i,t}^{\$}
=
\frac{1}{L}
\sum_{\ell=0}^{L-1}
P_{i,t-\ell}
V_{i,t-\ell}.
}
\end{equation}
```

If the strategy trades notional $`Q_{i,t}^{\$}`$, its participation rate is

``` math
\begin{equation}
\boxed{
PR_{i,t}
=
\frac{
|Q_{i,t}^{\$}|
}{
\mathrm{ADV}_{i,t}^{\$}
}.
}
\end{equation}
```

##### Bid–Ask Data

Let

``` math
\begin{equation}
P_{i,t}^{\mathrm{bid}}
\qquad\text{and}\qquad
P_{i,t}^{\mathrm{ask}}
\end{equation}
```

denote the best bid and ask.

The mid-price is

``` math
\begin{equation}
P_{i,t}^{\mathrm{mid}}
=
\frac{
P_{i,t}^{\mathrm{ask}}
+
P_{i,t}^{\mathrm{bid}}
}{2}.
\end{equation}
```

The quoted spread is

``` math
\begin{equation}
\mathrm{Spread}_{i,t}
=
P_{i,t}^{\mathrm{ask}}
-
P_{i,t}^{\mathrm{bid}},
\end{equation}
```

and the relative quoted spread is

``` math
\begin{equation}
\boxed{
\mathrm{RelativeSpread}_{i,t}
=
\frac{
P_{i,t}^{\mathrm{ask}}
-
P_{i,t}^{\mathrm{bid}}
}{
P_{i,t}^{\mathrm{mid}}
}.
}
\end{equation}
```

Under the simplified assumption of execution at the best bid or ask, the one-way spread cost relative to the mid-price is approximately

``` math
\begin{equation}
c_{i,t}^{\mathrm{spread}}
\approx
\frac{1}{2}
\mathrm{RelativeSpread}_{i,t}.
\end{equation}
```

##### Securities-Lending Data

A short position generally requires borrowing the security before it can be sold.

Relevant variables include:

- borrow availability;

- available quantity;

- annualized borrow fee;

- utilization;

- hard-to-borrow status;

- recalls.

Let $`b_{i,t}`$ denote the annualized borrow rate.

For a short position with absolute market value $`V_{i,t}^{\mathrm{short}}`$ held for $`\Delta t`$ years, a simplified borrowing cost is

``` math
\begin{equation}
\boxed{
BC_{i,t}
\approx
b_{i,t}
V_{i,t}^{\mathrm{short}}
\Delta t.
}
\end{equation}
```

##### Transaction-Cost Inputs

Transaction costs themselves are outputs of an implementation model.

The raw data used to estimate them may include

``` math
\begin{equation}
\mathcal{D}_{i,t}^{TC}
=
\left\{
\mathrm{Spread}_{i,t},
\mathrm{ADV}_{i,t},
\sigma_{i,t},
\mathrm{Depth}_{i,t},
\mathrm{Fees}_{i,t},
\ldots
\right\}.
\end{equation}
```

The conceptual sequence is therefore

``` math
\begin{equation}
\boxed{
\underbrace{
\mathcal{D}_{i,t}^{TC}
}_{\text{Raw Implementation Data}}
\longrightarrow
\underbrace{
C_{i,t}(\cdot)
}_{\text{Transaction-Cost Model}}
\longrightarrow
\underbrace{
TC_{i,t}
}_{\text{Estimated Cost}}.
}
\end{equation}
```

The transaction-cost model itself will be developed in the portfolio implementation section.

##### Liquidity and Capacity

If portfolio NAV is $`A_t`$, a weight change $`\Delta w_{i,t}`$ corresponds to traded notional

``` math
\begin{equation}
Q_{i,t}^{\$}
=
A_t
|\Delta w_{i,t}|.
\end{equation}
```

Hence,

``` math
\begin{equation}
PR_{i,t}
=
\frac{
A_t|\Delta w_{i,t}|
}{
\mathrm{ADV}_{i,t}^{\$}
}.
\end{equation}
```

Thus, holding portfolio construction fixed,

``` math
\begin{equation}
\boxed{
A_t \uparrow
\quad\Rightarrow\quad
PR_{i,t} \uparrow
\quad\Rightarrow\quad
\text{Implementation Difficulty Typically Increases}.
}
\end{equation}
```

This establishes the direct connection between raw liquidity data and strategy capacity.

#### Raw Data Architecture

The raw-data layer combines observations measured at different entity levels:

``` math
\begin{equation}
\boxed{
\begin{array}{ccc}
\text{Market Data}
&
\rightarrow
&
\text{Security / Listing Level}
\\[0.15cm]
\text{Fundamentals}
&
\rightarrow
&
\text{Company / Accounting-Period Level}
\\[0.15cm]
\text{Analyst Estimates}
&
\rightarrow
&
\text{Company / Forecast-Horizon Level}
\\[0.15cm]
\text{Alternative Data}
&
\rightarrow
&
\text{Entity / Event Level}
\\[0.15cm]
\text{Risk Factors}
&
\rightarrow
&
\text{Market / Factor Level}
\\[0.15cm]
\text{Classifications}
&
\rightarrow
&
\text{Company / Security Level}
\\[0.15cm]
\text{Corporate Actions}
&
\rightarrow
&
\text{Security / Event Level}
\\[0.15cm]
\text{Implementation Data}
&
\rightarrow
&
\text{Security / Market Level}
\end{array}
}
\end{equation}
```

These sources cannot generally be merged through a simple equality join because they differ both in entity structure and in time representation.

A robust backtesting architecture must therefore preserve two dimensions:

``` math
\begin{equation}
\boxed{
\text{Entity Identity}
\qquad\text{and}\qquad
\text{Information Timing}.
}
\end{equation}
```

The raw-data stage answers the question

``` math
\begin{equation}
\boxed{
\text{What historical observations do we possess?}
}
\end{equation}
```

The next stage, Point-in-Time Data Construction, answers the distinct and more important backtesting question

``` math
\begin{equation}
\boxed{
\text{Which of these observations were actually available to the investor at time }t?
}
\end{equation}
```

