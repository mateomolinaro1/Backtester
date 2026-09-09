### Point-in-Time Data Construction

Raw historical databases generally describe what is known *today* about past observations. A backtest, however, requires a different object: the information that would actually have been available to an investor at each historical date.

The objective of point-in-time construction is therefore to transform the complete historical database

``` math
\begin{equation}
\mathcal{D}
\end{equation}
```

into a sequence of historical information sets

``` math
\begin{equation}
\boxed{
\mathcal{D}
\longrightarrow
\left\{
\mathcal{I}_t
\right\}_{t=1}^{T},
}
\end{equation}
```

where $`\mathcal{I}_t`$ contains only observations that were genuinely observable by the investment process at time $`t`$.

For any data observation $`j`$, define its availability time as

``` math
\begin{equation}
t_j^{\mathrm{avail}}.
\end{equation}
```

Then observation $`j`$ may enter the information set at time $`t`$ only if

``` math
\begin{equation}
\boxed{
t_j^{\mathrm{avail}}
\leq
t.
}
\end{equation}
```

Thus,

``` math
\begin{equation}
\boxed{
\mathcal{I}_t
=
\left\{
D_j\in\mathcal{D}
:
t_j^{\mathrm{avail}}
\leq t
\right\}.
}
\end{equation}
```

This condition is the fundamental rule underlying point-in-time data engineering.

Its practical implementation requires careful treatment of dates, reporting lags, revisions, entity membership, and historical joins.

#### Observation Dates, Publication Dates, and Effective Dates

A single financial observation may be associated with several different dates. These dates describe different economic concepts and should not be treated as interchangeable.

For observation $`j`$, define:

``` math
\begin{equation}
t_j^{\mathrm{obs}},
\qquad
t_j^{\mathrm{pub}},
\qquad
t_j^{\mathrm{eff}},
\qquad
t_j^{\mathrm{avail}}.
\end{equation}
```

These correspond respectively to:

- $`t_j^{\mathrm{obs}}`$: the date or period to which the observation economically refers;

- $`t_j^{\mathrm{pub}}`$: the date on which the information is officially published or announced;

- $`t_j^{\mathrm{eff}}`$: the date on which an event or classification becomes economically or operationally effective;

- $`t_j^{\mathrm{avail}}`$: the earliest date and time at which the investment process could actually have used the information.

These dates may coincide for some datasets but differ substantially for others.

##### Market Data Example

For a daily closing price,

``` math
\begin{equation}
P_{i,t}^{\mathrm{close}},
\end{equation}
```

the observation date and publication date may both correspond approximately to trading day $`t`$.

However, the information becomes usable only after the closing price has actually been observed.

Hence,

``` math
\begin{equation}
t^{\mathrm{obs}}
=
t,
\end{equation}
```

but the exact

``` math
\begin{equation}
t^{\mathrm{avail}}
\end{equation}
```

depends on the timestamp of the signal and execution process.

##### Fundamental Data Example

Suppose a company reports financial results for the fiscal year ending on December 31.

Then

``` math
\begin{equation}
t^{\mathrm{obs}}
=
\text{December 31}.
\end{equation}
```

Suppose the results are released on March 15 of the following year.

Then

``` math
\begin{equation}
t^{\mathrm{pub}}
=
\text{March 15}.
\end{equation}
```

The value cannot be used by the strategy between December 31 and March 14, even though the accounting observation refers economically to December 31.

Thus,

``` math
\begin{equation}
\boxed{
t^{\mathrm{obs}}
<
t^{\mathrm{pub}}
\leq
t^{\mathrm{avail}}.
}
\end{equation}
```

##### Corporate Action Example

Suppose an index provider announces on June 1 that stock $`i`$ will enter the index on June 10.

Then

``` math
\begin{equation}
t^{\mathrm{pub}}
=
\text{June 1},
\end{equation}
```

while

``` math
\begin{equation}
t^{\mathrm{eff}}
=
\text{June 10}.
\end{equation}
```

The investor may know on June 1 that the future membership change will occur, but the security does not become an index constituent until June 10.

Publication and effective dates therefore answer different questions.

##### General Principle

For every dataset, the backtester should identify the date corresponding to the question

``` math
\begin{equation}
\boxed{
\text{When could the strategy first have used this observation?}
}
\end{equation}
```

This date is $`t^{\mathrm{avail}}`$.

The point-in-time dataset should then be indexed primarily by availability rather than purely by economic reference date.

#### Reporting Lags

Many variables become observable only after a delay relative to the period they describe.

Define the reporting lag of observation $`j`$ as

``` math
\begin{equation}
\boxed{
L_j
=
t_j^{\mathrm{avail}}
-
t_j^{\mathrm{obs}}.
}
\end{equation}
```

For fundamental information, this lag can be substantial.

For example, a quarterly accounting observation may correspond to

``` math
\begin{equation}
t_j^{\mathrm{obs}}
=
\text{March 31},
\end{equation}
```

but only become available on

``` math
\begin{equation}
t_j^{\mathrm{avail}}
=
\text{May 5}.
\end{equation}
```

The reporting lag is therefore approximately

``` math
\begin{equation}
L_j
=
35\text{ days}.
\end{equation}
```

##### Actual vs. Assumed Reporting Lags

The preferred approach is to use the true historical publication or availability timestamp for each observation.

If these timestamps are unavailable, a conservative lag may be imposed artificially.

For example,

``` math
\begin{equation}
X_{i,\tau}
\text{ becomes usable at }
\tau+L,
\end{equation}
```

where $`L`$ is a predefined reporting lag.

The backtesting rule becomes

``` math
\begin{equation}
\boxed{
X_{i,\tau}
\in
\mathcal{I}_t
\quad
\Longleftrightarrow
\quad
\tau+L
\leq
t.
}
\end{equation}
```

This approach is less precise than using historical release dates but is preferable to assuming that accounting data were known at the fiscal period-end date.

##### Cross-Sectional Variation in Reporting Lags

Reporting lags need not be identical across companies.

Firm $`i`$ may report after

``` math
\begin{equation}
L_i=25\text{ days},
\end{equation}
```

while firm $`j`$ may report after

``` math
\begin{equation}
L_j=55\text{ days}.
\end{equation}
```

Applying a common lag to both companies can therefore distort the historical information set.

Whenever available, observation-specific timestamps are preferable:

``` math
\begin{equation}
\boxed{
L_{i,\tau}
=
t_{i,\tau}^{\mathrm{avail}}
-
t_{i,\tau}^{\mathrm{obs}}.
}
\end{equation}
```

##### Intraday Reporting Lags

For higher-frequency strategies, dates alone may be insufficient.

Suppose an earnings announcement occurs on day $`t`$ at 17:30, after the market close.

A daily database may record only

``` math
\begin{equation}
t^{\mathrm{pub}}=t,
\end{equation}
```

but a strategy trading at the close of day $`t`$ could not have used the announcement.

In such applications, availability should be represented by a timestamp:

``` math
\begin{equation}
\boxed{
t^{\mathrm{avail}}
=
(\text{date},\text{time},\text{timezone}).
}
\end{equation}
```

Ignoring intraday timestamps can create look-ahead bias even when calendar dates appear correct.

#### Restatements

Historical observations may be revised after their initial publication.

This is common for:

- accounting statements;

- macroeconomic releases;

- index and classification data;

- analyst databases;

- corporate-action records.

Suppose a company initially reports accounting value

``` math
\begin{equation}
X_{i,\tau}^{(0)}
\end{equation}
```

at time

``` math
\begin{equation}
t_{i,\tau}^{(0)}.
\end{equation}
```

The same observation is later restated as

``` math
\begin{equation}
X_{i,\tau}^{(1)}
\end{equation}
```

at time

``` math
\begin{equation}
t_{i,\tau}^{(1)}
>
t_{i,\tau}^{(0)}.
\end{equation}
```

Then the historically correct value depends on the backtest date:

``` math
\begin{equation}
X_{i,\tau}^{\mathrm{PIT}}(t)
=
\begin{cases}
\text{unavailable},
&
t<t_{i,\tau}^{(0)},
\\[0.2cm]
X_{i,\tau}^{(0)},
&
t_{i,\tau}^{(0)}
\leq
t
<
t_{i,\tau}^{(1)},
\\[0.2cm]
X_{i,\tau}^{(1)},
&
t
\geq
t_{i,\tau}^{(1)}.
\end{cases}
\end{equation}
```

More generally, if an observation has revisions

``` math
\begin{equation}
X_j^{(0)},
X_j^{(1)},
\ldots,
X_j^{(M)}
\end{equation}
```

with availability times

``` math
\begin{equation}
t_j^{(0)}
<
t_j^{(1)}
<
\cdots
<
t_j^{(M)},
\end{equation}
```

the valid value at time $`t`$ is

``` math
\begin{equation}
\boxed{
X_j^{\mathrm{PIT}}(t)
=
X_j^{(m^*)},
\qquad
m^*
=
\max
\left\{
m:
t_j^{(m)}
\leq
t
\right\}.
}
\end{equation}
```

##### Vintage Data

A database containing all historical versions of an observation is commonly referred to as a vintage or point-in-time database.

Conceptually,

``` math
\begin{equation}
\boxed{
\text{Observation}
+
\text{Revision Version}
+
\text{Availability Timestamp}.
}
\end{equation}
```

Using the latest value stored today,

``` math
\begin{equation}
X_j^{\mathrm{latest}},
\end{equation}
```

for all historical dates incorrectly gives the backtest information from future revisions.

##### Restatement Policy

The backtester should therefore establish an explicit restatement policy.

The preferred rule is:

``` math
\begin{equation}
\boxed{
\text{At time }t,
\text{ use the latest version that was available at }t.
}
\end{equation}
```

If historical vintages are unavailable, the limitation should be documented explicitly, since the resulting backtest may contain restatement bias.

#### As-Of Joins

Point-in-time datasets frequently combine observations recorded at different frequencies.

For example:

- prices may be daily;

- fundamentals may be quarterly;

- analyst estimates may change irregularly;

- classifications may change occasionally.

A standard equality join,

``` math
\begin{equation}
t_X=t_Y,
\end{equation}
```

is therefore generally inappropriate.

Instead, the backtester often requires an *as-of join*.

For security $`i`$ and portfolio date $`t`$, define the latest admissible observation time as

``` math
\begin{equation}
\boxed{
\tau_i^*(t)
=
\max
\left\{
\tau:
t_{i,\tau}^{\mathrm{avail}}
\leq
t
\right\}.
}
\end{equation}
```

The point-in-time value used by the strategy is then

``` math
\begin{equation}
\boxed{
X_{i,t}^{\mathrm{PIT}}
=
X_{i,\tau_i^*(t)}.
}
\end{equation}
```

Thus, the as-of join answers the question:

``` math
\begin{equation}
\boxed{
\text{What was the most recent observation available as of time }t?
}
\end{equation}
```

##### Backward As-Of Join

For predictive backtesting, the join direction should normally be backward:

``` math
\begin{equation}
\boxed{
t^{\mathrm{source}}
\leq
t^{\mathrm{decision}}.
}
\end{equation}
```

A forward join,

``` math
\begin{equation}
t^{\mathrm{source}}
>
t^{\mathrm{decision}},
\end{equation}
```

would introduce future information.

##### Example

Suppose a company reports quarterly earnings on

``` math
\begin{equation}
t_1=\text{May 5}
\end{equation}
```

and subsequently on

``` math
\begin{equation}
t_2=\text{August 4}.
\end{equation}
```

For every backtest date satisfying

``` math
\begin{equation}
\text{May 5}
\leq
t
<
\text{August 4},
\end{equation}
```

the valid fundamental observation is the May 5 release.

Thus,

``` math
\begin{equation}
X_{i,t}^{\mathrm{PIT}}
=
X_{i,t_1}.
\end{equation}
```

Only from August 4 onward may the newer observation replace it.

##### Maximum Staleness

The fact that an observation is the latest historically available value does not necessarily mean that it remains economically usable indefinitely.

A maximum age may therefore be imposed.

Let

``` math
\begin{equation}
A_{i,t}
=
t
-
t_{i,\tau_i^*(t)}^{\mathrm{avail}}
\end{equation}
```

denote data age.

Then one may require

``` math
\begin{equation}
\boxed{
A_{i,t}
\leq
A_{\max}.
}
\end{equation}
```

Otherwise the observation is treated as stale or missing.

This prevents an extremely old fundamental, estimate, or classification record from being carried forward indefinitely.

##### Entity Keys

An as-of join must generally be performed within the appropriate entity.

For example,

``` math
\begin{equation}
\boxed{
\text{Join Key}
=
(\mathrm{SecurityID},t)
}
\end{equation}
```

for security-level data, while company-level fundamental data may require

``` math
\begin{equation}
\boxed{
\text{CompanyID}
\longrightarrow
\text{SecurityID}
}
\end{equation}
```

before being joined to market observations.

Entity resolution and temporal alignment are therefore jointly necessary.

#### Historical Universe Membership

The investment universe itself must be reconstructed point-in-time.

Let

``` math
\begin{equation}
I_{i,t}^{\mathrm{member}}
=
\begin{cases}
1,
&
\text{if security }i
\text{ belongs to the relevant universe at }t,
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
\boxed{
\mathcal{U}_t
=
\left\{
i:
I_{i,t}^{\mathrm{member}}=1
\right\}.
}
\end{equation}
```

Historical membership can vary because of:

- IPOs;

- delistings;

- mergers and acquisitions;

- index additions and deletions;

- changes in exchange eligibility;

- changes in liquidity or size requirements;

- changes in security type;

- shortability constraints.

##### Entry and Exit Intervals

A convenient representation stores a membership interval for each security:

``` math
\begin{equation}
\left[
t_i^{\mathrm{entry}},
t_i^{\mathrm{exit}}
\right).
\end{equation}
```

Then

``` math
\begin{equation}
I_{i,t}^{\mathrm{member}}
=
\begin{cases}
1,
&
t_i^{\mathrm{entry}}
\leq
t
<
t_i^{\mathrm{exit}},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

##### Index Membership

If a strategy trades an index universe, current constituents must not be projected backward through history.

Instead,

``` math
\begin{equation}
\boxed{
\mathcal{U}_t
=
\text{constituents valid at time }t.
}
\end{equation}
```

A distinction may also be required between announcement and effective dates.

Suppose an addition is announced at

``` math
\begin{equation}
t^{\mathrm{announce}}
\end{equation}
```

and becomes effective at

``` math
\begin{equation}
t^{\mathrm{effective}}.
\end{equation}
```

Then whether the security can enter the strategy before the effective date depends on whether the strategy is explicitly designed to trade announced future index changes.

The rule should be defined ex ante and applied consistently.

##### Rule-Based Universes

For a rule-based universe, membership may itself be computed from historical variables.

Suppose securities must satisfy

``` math
\begin{equation}
\mathrm{MCap}_{i,t}
>
M_{\min}
\end{equation}
```

and

``` math
\begin{equation}
\mathrm{ADV}_{i,t}
>
ADV_{\min}.
\end{equation}
```

Then

``` math
\begin{equation}
I_{i,t}^{\mathrm{eligible}}
=
\mathbbm{1}
\left(
\mathrm{MCap}_{i,t}>M_{\min}
\right)
\mathbbm{1}
\left(
\mathrm{ADV}_{i,t}>ADV_{\min}
\right).
\end{equation}
```

Every variable entering the eligibility rule must itself be point-in-time.

Thus, universe construction satisfies the same information constraint as signal construction:

``` math
\begin{equation}
\boxed{
\mathcal{U}_t
=
g(\mathcal{I}_t).
}
\end{equation}
```

#### Delisted Securities

Delisted securities require special treatment because their disappearance affects both historical universe membership and portfolio accounting.

A delisted security should not simply disappear retrospectively from the historical database.

Before delisting,

``` math
\begin{equation}
i\in\mathcal{U}_t.
\end{equation}
```

After the delisting becomes effective,

``` math
\begin{equation}
i\notin\mathcal{U}_t.
\end{equation}
```

The transition must occur at the historically correct date.

##### Universe Treatment

Suppose security $`i`$ delists at time $`T_i`$.

Its historical membership may be represented as

``` math
\begin{equation}
I_{i,t}^{\mathrm{member}}
=
\begin{cases}
1,
&
t<T_i,
\\
0,
&
t\geq T_i.
\end{cases}
\end{equation}
```

However, removing the security from future universes does not by itself solve the portfolio-accounting problem.

##### Economic Payoff Before Removal

If the strategy holds the security immediately before delisting, the terminal economic payoff must first be incorporated.

As established in Section <a href="#subsubsec:delisting_returns" data-reference-type="ref" data-reference="subsubsec:delisting_returns">2.2.1</a>,

``` math
\begin{equation}
\boxed{
\text{Existing Position}
\rightarrow
R_{i,T_i}^{\mathrm{delist}}
\rightarrow
\text{Terminal Proceeds}
\rightarrow
\text{Position Removal}.
}
\end{equation}
```

The historical data pipeline should therefore retain:

- the final tradable price;

- the delisting or terminal return, when available;

- the delisting date;

- the reason or event type, when relevant.

Replacing the delisting event with a missing value can materially bias historical returns.

##### Missing Delisting Information

In some datasets, the final economic payoff is unavailable.

The backtester must then adopt an explicit policy rather than silently dropping the observation.

Possible treatments depend on the database and research objective, but any assumption should be documented because the resulting performance may be sensitive to the treatment of missing terminal returns.

#### Preventing Look-Ahead Bias

The complete purpose of point-in-time construction is to guarantee that no future information enters a historical investment decision.

Let $`X_{i,t}^{(k)}`$ denote feature input $`k`$ used for security $`i`$ at time $`t`$.

The fundamental validity condition is

``` math
\begin{equation}
\boxed{
t_{i}^{(k),\mathrm{avail}}
\leq
t
\qquad
\forall i,k.
}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
X_t
\in
\sigma(\mathcal{I}_t),
\end{equation}
```

where $`\sigma(\mathcal{I}_t)`$ denotes the information generated by observations available up to time $`t`$.

##### Point-in-Time Construction Rule

For each required variable, the backtester should conceptually execute:

``` math
\begin{equation}
\boxed{
X_{i,t}^{\mathrm{PIT}}
=
\text{latest valid version of }
X_i
\text{ whose availability time satisfies }
t^{\mathrm{avail}}\leq t.
}
\end{equation}
```

This single rule simultaneously governs:

- fundamental data;

- analyst estimates;

- alternative data;

- classifications;

- macroeconomic variables;

- corporate-action information;

- universe membership.

##### Decision Time vs. Calendar Date

A calendar date alone may not define the information set sufficiently.

Let

``` math
\begin{equation}
t^{\mathrm{decision}}
\end{equation}
```

denote the exact decision timestamp.

Then the admissibility rule becomes

``` math
\begin{equation}
\boxed{
t_j^{\mathrm{avail}}
\leq
t^{\mathrm{decision}}.
}
\end{equation}
```

For example, information released after the market close on day $`t`$ may belong to the information set for day $`t+1`$, but not to a strategy executed at the close of day $`t`$.

##### Safe Pipeline Ordering

A robust backtesting process should preserve the chronological order

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Raw Observation}
&\rightarrow
\text{Availability Timestamp}
\rightarrow
\text{Point-in-Time Join}
\\[0.15cm]
&\rightarrow
\text{Feature Construction}
\rightarrow
\text{Signal}
\rightarrow
\text{Portfolio Decision}
\end{aligned}
}
\end{equation}
```

Crucially, point-in-time filtering should occur *before* any operation that could combine past and future observations.

##### Common Point-in-Time Failures

Common implementation errors include:

- joining fundamentals by fiscal-period date rather than publication date;

- forward-filling observations before imposing availability dates;

- using the latest restated accounting value historically;

- using today’s industry classification throughout history;

- using current index constituents for past dates;

- including a security before its historical listing or eligibility date;

- removing securities retrospectively because they later delisted;

- using macroeconomic values after revisions rather than real-time vintages;

- performing nearest-date joins that select future observations;

- ignoring intraday release timestamps when the strategy trades at intraday or close-to-close frequency.

##### Point-in-Time Validation Tests

Because point-in-time errors can be difficult to detect from performance alone, the data pipeline should include explicit validation tests.

For every joined observation $`j`$ used at decision time $`t`$,

``` math
\begin{equation}
\boxed{
t_j^{\mathrm{avail}}
\leq
t
}
\end{equation}
```

should hold programmatically.

One may define the violation indicator

``` math
\begin{equation}
V_j
=
\begin{cases}
1,
&
t_j^{\mathrm{avail}}
>
t_j^{\mathrm{decision}},
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

A valid dataset should satisfy

``` math
\begin{equation}
\boxed{
\sum_j V_j
=
0.
}
\end{equation}
```

Additional validation checks should verify that:

- source observations are sorted chronologically;

- as-of joins always operate backward;

- revisions are selected according to historical availability;

- entity mappings are valid at the historical date;

- no security enters the universe before its eligibility date;

- delisted securities remain present until their historical exit date;

- stale observations are identified according to predefined rules.

##### The Point-in-Time Information Set

After all temporal filters, revisions, memberships, and joins have been resolved, the final point-in-time dataset at decision date $`t`$ can be written abstractly as

``` math
\begin{equation}
\boxed{
\mathcal{D}_t^{\mathrm{PIT}}
=
\left\{
D_j:
t_j^{\mathrm{avail}}
\leq
t,
\;
D_j
\text{ is the historically valid version at }t
\right\}.
}
\end{equation}
```

The investment process can then safely construct features as

``` math
\begin{equation}
X_t
=
g
\left(
\mathcal{D}_t^{\mathrm{PIT}}
\right),
\end{equation}
```

signals as

``` math
\begin{equation}
s_t
=
f(X_t),
\end{equation}
```

and portfolio weights as

``` math
\begin{equation}
w_t
=
\phi(s_t).
\end{equation}
```

Thus,

``` math
\begin{equation}
\boxed{
\mathcal{D}
\rightarrow
\mathcal{D}_t^{\mathrm{PIT}}
\rightarrow
X_t
\rightarrow
s_t
\rightarrow
w_t
}
\end{equation}
```

preserves the fundamental information constraint

``` math
\begin{equation}
\boxed{
w_t=f(\mathcal{I}_t).
}
\end{equation}
```

Point-in-time construction therefore represents the temporal firewall between the historical database known today and the historical information set that could genuinely have been used by the strategy.

