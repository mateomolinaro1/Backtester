### Backtesting Biases and Research Integrity

A backtest is only meaningful if the simulated investment process could have been implemented using the information and market conditions that were actually available at each historical date.

Backtesting errors generally arise when the historical simulation benefits from information, securities, parameter choices, or trading conditions that would not have been available to an investor in real time.

These errors can be grouped into several broad categories:

- information-timing biases;

- universe-construction biases;

- sample-selection biases;

- model-selection and multiple-testing biases;

- data-processing leakage;

- unrealistic implementation assumptions.

The fundamental principle remains the information-set condition introduced in Section <a href="#sec:problem_definition" data-reference-type="ref" data-reference="sec:problem_definition">1</a>. If $`\mathcal{I}_t`$ denotes all information available to an investor at time $`t`$, then every investment decision must satisfy

``` math
\begin{equation}
\boxed{
w_t=f(\mathcal{I}_t).
}
\end{equation}
```

Any backtest in which $`w_t`$ depends directly or indirectly on information revealed after $`t`$ is contaminated by future information.

However, avoiding explicit future variables is not sufficient. Bias can also enter through the investment universe, data preprocessing, hyperparameter selection, model comparison, transaction-cost assumptions, or even through the researcher’s decision to continue or abandon a strategy after observing its historical performance.

This section describes the principal sources of bias and establishes a set of research-integrity principles that should be enforced throughout the complete backtesting pipeline.

#### Look-Ahead Bias

Look-ahead bias occurs whenever a portfolio decision at time $`t`$ uses information that was not yet available at that time.

Formally, if the portfolio is

``` math
\begin{equation}
w_t
=
f(X_t),
\end{equation}
```

then every component of $`X_t`$ must be measurable with respect to $`\mathcal{I}_t`$.

A look-ahead violation occurs if

``` math
\begin{equation}
X_t
=
g
\left(
\mathcal{I}_t,
Z_{t+h}
\right),
\qquad
h>0,
\end{equation}
```

where $`Z_{t+h}`$ denotes information that becomes observable only after time $`t`$.

A trivial example would be constructing today’s portfolio using tomorrow’s return:

``` math
\begin{equation}
w_{i,t}
=
f
\left(
R_{i,t\rightarrow t+1}
\right).
\end{equation}
```

Such an error is obvious. In practice, however, look-ahead bias often enters the research pipeline in more subtle ways.

##### Price Timing

Suppose a signal is computed using the closing price on day $`t`$:

``` math
\begin{equation}
s_t
=
f
\left(
P_t^{\mathrm{close}}
\right).
\end{equation}
```

If the closing price is not fully known until the market close, the strategy cannot generally assume that it simultaneously executes the resulting trade at that exact same closing price.

A more defensible sequence is

``` math
\begin{equation}
P_t^{\mathrm{close}}
\rightarrow
s_t
\rightarrow
w_t
\rightarrow
P_{t+1}^{\mathrm{exec}}.
\end{equation}
```

Alternatively, same-day execution may be valid if the strategy uses information available before the execution window. The critical requirement is that the timing assumption matches the actual information and trading process.

##### Fundamental Data

Accounting variables illustrate another common source of look-ahead bias.

Suppose a firm’s fiscal-year earnings correspond to December 31 but are published on March 15 of the following year.

The accounting value cannot be used on January 1 simply because its fiscal period ended on December 31.

Let

``` math
\begin{equation}
t_i^{\mathrm{period}}
\end{equation}
```

denote the economic reference date of observation $`i`$, and

``` math
\begin{equation}
t_i^{\mathrm{available}}
\end{equation}
```

denote the date on which it becomes observable.

A valid backtest must satisfy

``` math
\begin{equation}
\boxed{
t
\geq
t_i^{\mathrm{available}}
}
\end{equation}
```

before the observation can enter $`\mathcal{I}_t`$.

The relevant backtesting date is therefore the information-availability date, not necessarily the fiscal or economic reference date.

##### Rolling Statistics

Look-ahead bias can also enter through incorrectly constructed rolling statistics.

Suppose volatility is estimated as

``` math
\begin{equation}
\widehat{\sigma}_{i,t}
=
\operatorname{Std}
\left(
R_{i,t-L+1},
\ldots,
R_{i,t}
\right).
\end{equation}
```

This estimator is valid if $`R_{i,t}`$ is already observable when the portfolio decision is made.

However, using

``` math
\begin{equation}
\operatorname{Std}
\left(
R_{i,t-L+2},
\ldots,
R_{i,t+1}
\right)
\end{equation}
```

to construct the portfolio at time $`t`$ introduces future information.

The same issue applies to:

- moving averages;

- rolling betas;

- rolling correlations;

- volatility estimates;

- rolling z-scores;

- rolling normalization parameters.

##### Prevention

The strongest protection against look-ahead bias is to define the backtest as an explicit chronological process:

``` math
\begin{equation}
\boxed{
\mathcal{I}_t
\rightarrow
\text{data processing}
\rightarrow
\text{signal}
\rightarrow
\text{portfolio}
\rightarrow
\text{execution}
\rightarrow
R_{t\rightarrow t+1}.
}
\end{equation}
```

At every stage of the pipeline, one should be able to answer the question:

> Could this quantity have been computed using only information that was available at this exact historical time?

#### Survivorship Bias

Survivorship bias arises when the historical universe contains only securities that survive until a later date.

Suppose the current investment universe is

``` math
\begin{equation}
\mathcal{U}_{T},
\end{equation}
```

where $`T`$ denotes the present date.

Using this same universe throughout the historical backtest,

``` math
\begin{equation}
\mathcal{U}_t
=
\mathcal{U}_T
\qquad
\forall t<T,
\end{equation}
```

implicitly assumes that the investor knew which firms would survive until $`T`$.

This systematically removes securities that subsequently:

- went bankrupt;

- were delisted;

- were acquired;

- ceased trading;

- became financially distressed;

- left the relevant index or market.

The resulting sample tends to contain firms with better ex-post outcomes than the true historical opportunity set.

A valid universe must therefore be reconstructed dynamically:

``` math
\begin{equation}
\boxed{
\mathcal{U}_t
=
\left\{
i:
I_{i,t}^{\mathrm{eligible}}=1
\right\},
}
\end{equation}
```

where eligibility is determined using only information available at time $`t`$.

Survivorship bias is particularly dangerous in equity strategies based on financial distress, value, profitability, or momentum, since securities that eventually disappear may have extreme characteristics before their exit.

##### Delisting Returns

Simply retaining delisted securities in the historical database is not always sufficient to eliminate survivorship bias. A security disappearing from the database or investment universe does not imply that the corresponding investment position disappears without an economic gain or loss.

Suppose security $`i`$ has its last regular trading observation at time $`T_i-1`$ and is subsequently delisted at time $`T_i`$. The investor may receive a terminal economic payoff resulting from bankruptcy, liquidation, acquisition, merger, privatization, or another corporate event.

Let

``` math
\begin{equation}
P_{i,T_i-1}
\end{equation}
```

denote the last relevant market price before delisting and let

``` math
\begin{equation}
V_{i,T_i}^{\mathrm{terminal}}
\end{equation}
```

denote the terminal economic value received by the shareholder. A simplified delisting return can then be defined as

``` math
\begin{equation}
\boxed{
R_{i,T_i}^{\mathrm{delist}}
=
\frac{
V_{i,T_i}^{\mathrm{terminal}}
}{
P_{i,T_i-1}
}
-1.
}
\end{equation}
```

The terminal value may correspond, depending on the event, to cash proceeds, liquidation proceeds, the value of securities received in a merger, or another form of economic compensation.

###### Bankruptcy Example.

Suppose a security is purchased at a price of

``` math
\begin{equation}
P_{i,t}=10.
\end{equation}
```

Before being delisted, its last observed market price falls to

``` math
\begin{equation}
P_{i,T_i-1}=8.
\end{equation}
```

If the company subsequently goes bankrupt and shareholders receive nothing, then

``` math
\begin{equation}
V_{i,T_i}^{\mathrm{terminal}}=0.
\end{equation}
```

The final delisting return is therefore

``` math
\begin{equation}
R_{i,T_i}^{\mathrm{delist}}
=
\frac{0}{8}-1
=
-100\%.
\end{equation}
```

If the database simply stops the return series at the last observed price of $`8`$, the backtest records only the decline

``` math
\begin{equation}
\frac{8}{10}-1
=
-20\%.
\end{equation}
```

However, the investor’s true cumulative economic return is

``` math
\begin{equation}
\frac{0}{10}-1
=
-100\%.
\end{equation}
```

The correct economic path is therefore

``` math
\begin{equation}
\boxed{
10
\longrightarrow
8
\longrightarrow
0,
}
\end{equation}
```

rather than

``` math
\begin{equation}
10
\longrightarrow
8
\longrightarrow
\mathrm{NA}.
\end{equation}
```

Treating the missing observation as the disappearance of the position would therefore substantially overstate portfolio performance.

###### Acquisition Example.

A delisting does not necessarily generate a negative return.

Suppose a company trades at

``` math
\begin{equation}
P_{i,T_i-1}=80
\end{equation}
```

immediately before being acquired for

``` math
\begin{equation}
V_{i,T_i}^{\mathrm{terminal}}=100
\end{equation}
```

per share.

The corresponding delisting return is

``` math
\begin{equation}
R_{i,T_i}^{\mathrm{delist}}
=
\frac{100}{80}-1
=
25\%.
\end{equation}
```

If the historical price series simply terminates at $`80`$, the backtest would fail to capture the $`25\%`$ terminal gain received by the shareholder.

Delisting returns should therefore not be interpreted exclusively as bankruptcy losses. More generally, they represent the final economic payoff associated with the disappearance of a security from regular trading.

###### Portfolio-Level Consequences.

The distinction becomes particularly important when translating security-level returns into portfolio returns.

Suppose the portfolio holds security $`i`$ immediately before its delisting with weight

``` math
\begin{equation}
w_{i,T_i-1}=2\%.
\end{equation}
```

If the delisting return is

``` math
\begin{equation}
R_{i,T_i}^{\mathrm{delist}}=-100\%,
\end{equation}
```

then the contribution of the security to the portfolio return over the delisting event is approximately

``` math
\begin{equation}
w_{i,T_i-1}
R_{i,T_i}^{\mathrm{delist}}
=
0.02\times(-1)
=
-2\%.
\end{equation}
```

Simply removing the security from the portfolio and setting

``` math
\begin{equation}
w_{i,T_i}=0
\end{equation}
```

without first accounting for the delisting return would incorrectly eliminate this loss. Economically, such a procedure would implicitly assume that the position could be liquidated at its previous valuation immediately before disappearing.

The correct sequence is instead

``` math
\begin{equation}
\boxed{
\text{Position at }T_i-1
\rightarrow
R_{i,T_i}^{\mathrm{delist}}
\rightarrow
V_{i,T_i}^{\mathrm{terminal}}
\rightarrow
\text{Position removed from the portfolio}.
}
\end{equation}
```

Thus, the removal of a security from the investment universe and the economic liquidation of the corresponding position are two distinct operations.

A historical return series should conceptually contain

``` math
\begin{equation}
\boxed{
R_{i,1},
R_{i,2},
\ldots,
R_{i,T_i-1},
R_{i,T_i}^{\mathrm{delist}},
}
\end{equation}
```

rather than

``` math
\begin{equation}
R_{i,1},
R_{i,2},
\ldots,
R_{i,T_i-1},
\mathrm{NA}.
\end{equation}
```

Only after the terminal economic payoff has been incorporated should the security disappear from the portfolio and subsequent investment universe.

This issue is particularly important for strategies exposed to distressed, small-cap, value, or otherwise financially fragile securities, since the probability of delisting may be systematically related to the investment signal itself. Ignoring delisting returns can therefore introduce not only a general upward bias in performance, but also a bias that is correlated with the characteristics being studied.

#### Selection Bias

Selection bias occurs when the sample used for research is selected using information related to subsequent performance.

Suppose the true historical population is

``` math
\begin{equation}
\mathcal{P}_t,
\end{equation}
```

but the researcher constructs a sample

``` math
\begin{equation}
\mathcal{S}_t
\subset
\mathcal{P}_t
\end{equation}
```

according to criteria that depend, directly or indirectly, on future outcomes.

Then the estimated relationship

``` math
\begin{equation}
\mathbb{E}
\left[
R_{t+1}
\mid
X_t,
i\in\mathcal{S}_t
\right]
\end{equation}
```

need not correspond to the relationship that would have existed in the true investable population.

Selection bias may arise through:

- choosing markets that historically performed well;

- selecting factors after inspecting historical results;

- restricting the sample to companies with complete future histories;

- excluding periods in which the strategy performed poorly;

- choosing a backtest start date after examining results;

- studying only strategies that survived internal research.

An important distinction is that an economically motivated universe filter is not necessarily selection bias.

For example, imposing at time $`t`$

``` math
\begin{equation}
\mathrm{ADV}_{i,t}
>
\mathrm{ADV}_{\min}
\end{equation}
```

may be economically justified because the strategy cannot realistically trade illiquid securities.

The problem arises when the filtering rule itself is chosen ex post because it improves historical performance.

Research decisions should therefore be motivated by economic reasoning, implementation constraints, or hypotheses defined independently of the backtest outcome whenever possible.

#### Data Snooping and Multiple Testing

Quantitative research typically involves evaluating many candidate signals, models, hyperparameters, universes, and portfolio-construction rules.

Suppose the researcher evaluates $`M`$ strategies:

``` math
\begin{equation}
S_1,
S_2,
\ldots,
S_M.
\end{equation}
```

Even if every strategy has zero true alpha,

``` math
\begin{equation}
\mathbb{E}[R^{S_j}]=0
\qquad
\forall j,
\end{equation}
```

sampling noise implies that some strategies will exhibit strong historical performance purely by chance.

If the researcher selects

``` math
\begin{equation}
S^*
=
\underset{j=1,\ldots,M}{\arg\max}
\;
\widehat{\mathrm{Sharpe}}_j,
\end{equation}
```

then

``` math
\begin{equation}
\widehat{\mathrm{Sharpe}}_{S^*}
\end{equation}
```

is upward biased as an estimate of the strategy’s true Sharpe ratio.

The bias generally increases with the number of experiments performed.

##### Repeated Hypothesis Testing

Suppose each independent hypothesis test is conducted at significance level $`\alpha`$.

For a single null hypothesis,

``` math
\begin{equation}
P(\text{false rejection})=\alpha.
\end{equation}
```

If $`M`$ independent null hypotheses are tested, the probability of obtaining at least one false positive is

``` math
\begin{equation}
\boxed{
P(\text{at least one false positive})
=
1-(1-\alpha)^M.
}
\end{equation}
```

For example, with

``` math
\begin{equation}
\alpha=5\%,
\qquad
M=20,
\end{equation}
```

the probability becomes

``` math
\begin{equation}
1-0.95^{20}
\approx
64\%.
\end{equation}
```

Thus, observing one apparently significant result among many experiments provides substantially weaker evidence than observing the same result when only one hypothesis was tested.

##### Hidden Multiple Testing

The number of effective tests is often much larger than the number of models reported in the final paper or research note.

Researcher degrees of freedom may include:

- alternative signal definitions;

- different winsorization thresholds;

- different lags;

- different holding periods;

- alternative universes;

- different neutralization procedures;

- different model architectures;

- different hyperparameters;

- alternative transaction-cost assumptions;

- different portfolio mappings.

All of these decisions constitute implicit experiments if they are adjusted after observing backtest performance.

##### Mitigation

Possible safeguards include:

- keeping a genuinely untouched test sample;

- walk-forward validation;

- predefining the research hypothesis;

- recording all experiments;

- correcting for multiple testing;

- evaluating economic rather than purely statistical significance;

- testing robustness across independent markets and periods;

- using techniques such as the Deflated Sharpe Ratio.

The purpose is not to eliminate experimentation. Experimentation is central to quantitative research. The objective is instead to recognize that repeated experimentation changes the statistical interpretation of the best observed backtest.

#### Publication and Restatement Bias

Historical databases frequently contain the latest corrected or restated value of an economic or accounting variable rather than the value that was originally available to investors.

Suppose a firm initially reports

``` math
\begin{equation}
X_{i,t}^{(0)}
\end{equation}
```

and later restates the same accounting item as

``` math
\begin{equation}
X_{i,t}^{(1)}.
\end{equation}
```

If the backtest uses

``` math
\begin{equation}
X_{i,t}^{(1)}
\end{equation}
```

at a historical date when investors could observe only

``` math
\begin{equation}
X_{i,t}^{(0)},
\end{equation}
```

then future information has implicitly entered the strategy.

The same issue appears in macroeconomic data.

For example, GDP, inflation, employment, and other economic statistics may be revised several times after their initial release.

The value stored today,

``` math
\begin{equation}
X_t^{\mathrm{final}},
\end{equation}
```

may therefore differ from the real-time value

``` math
\begin{equation}
X_t^{\mathrm{vintage}}.
\end{equation}
```

For a historically realistic backtest, one ideally requires point-in-time or vintage data:

``` math
\begin{equation}
\boxed{
X_t^{\mathrm{backtest}}
=
X_t^{\mathrm{available\ at\ }t}.
}
\end{equation}
```

Using final revised data may materially overstate the predictability available to a real-time investor.

#### Universe Reconstruction Bias

Universe reconstruction bias is related to, but broader than, survivorship bias.

A historical investment universe should reproduce the securities that would actually have satisfied the strategy’s eligibility rules at each date.

Let the universe-selection function be

``` math
\begin{equation}
\mathcal{U}_t
=
g
\left(
\mathcal{I}_t
\right).
\end{equation}
```

The universe itself is therefore part of the investment decision process.

Errors can arise when historical membership is reconstructed using information that was not available contemporaneously.

Examples include:

- using today’s index constituents historically;

- applying today’s sector classification to past observations;

- using future market capitalization;

- using future liquidity measures;

- excluding securities that later delist;

- incorrectly handling IPO entry dates;

- applying filters using future data availability.

##### Index Membership

Suppose a strategy trades constituents of an index.

The correct universe is

``` math
\begin{equation}
\mathcal{U}_t
=
\text{index constituents known at }t,
\end{equation}
```

not

``` math
\begin{equation}
\mathcal{U}_t
=
\text{current constituents}.
\end{equation}
```

Moreover, index changes are often announced before their effective date. The researcher must therefore specify whether the strategy trades using the announcement date, the effective date, or another operational convention.

##### Universe Filters

Suppose a minimum market-capitalization threshold is imposed:

``` math
\begin{equation}
\mathrm{MCap}_{i,t}
>
M_{\min}.
\end{equation}
```

The market capitalization used must be based on information available at $`t`$.

Similarly, a liquidity filter such as

``` math
\begin{equation}
\mathrm{ADV}_{i,t}^{(L)}
>
ADV_{\min}
\end{equation}
```

must use trailing rather than future volume.

The universe-selection function must therefore obey exactly the same information-set discipline as the signal itself.

#### Data Leakage

Data leakage occurs when information from outside the training information set influences model estimation, preprocessing, feature construction, or hyperparameter selection.

Leakage is particularly important for econometric, machine-learning, and deep-learning strategies.

##### Preprocessing Leakage

Consider standardizing a feature:

``` math
\begin{equation}
Z_{i,t}
=
\frac{
X_{i,t}-\mu_X
}{
\sigma_X
}.
\end{equation}
```

If $`\mu_X`$ and $`\sigma_X`$ are estimated using the entire dataset, including future observations, then the transformed training data contain information about the future.

Instead, preprocessing parameters must be estimated from the training sample:

``` math
\begin{equation}
\widehat{\mu}_{X,\mathrm{train}}
=
\frac{1}{N_{\mathrm{train}}}
\sum_{j\in\mathrm{train}}
X_j,
\end{equation}
```

and

``` math
\begin{equation}
\widehat{\sigma}_{X,\mathrm{train}}
=
\operatorname{Std}
\left(
X_j:
j\in\mathrm{train}
\right).
\end{equation}
```

Validation and test observations are then transformed using these fixed training parameters:

``` math
\begin{equation}
Z_j^{\mathrm{test}}
=
\frac{
X_j^{\mathrm{test}}
-
\widehat{\mu}_{X,\mathrm{train}}
}{
\widehat{\sigma}_{X,\mathrm{train}}
}.
\end{equation}
```

##### Feature-Selection Leakage

Suppose features are selected by computing their relationship with the target over the entire dataset:

``` math
\begin{equation}
\rho_j
=
\operatorname{Corr}
\left(
X_j,
Y
\right).
\end{equation}
```

Selecting features with the largest $`|\rho_j|`$ before splitting the data causes future target information to influence the model.

Feature selection must instead be performed entirely inside the training procedure.

##### Hyperparameter Leakage

Suppose hyperparameters $`\theta`$ are chosen as

``` math
\begin{equation}
\theta^*
=
\underset{\theta}{\arg\max}
\;
\mathrm{Performance}_{\mathrm{test}}(\theta).
\end{equation}
```

The test sample is then no longer a true out-of-sample sample.

The proper structure is

``` math
\begin{equation}
\boxed{
\text{Train}
\rightarrow
\text{Validation}
\rightarrow
\text{Test}.
}
\end{equation}
```

Training data estimate model parameters. Validation data select models and hyperparameters. Test data are used only for final evaluation.

For time-series applications, these sets must also respect chronology.

##### Cross-Sectional vs. Temporal Leakage

In panel datasets, leakage can occur along both the time and asset dimensions.

A random train-test split may place observations from the same economic period in both training and testing samples.

For financial prediction, a chronological split is generally preferable:

``` math
\begin{equation}
\underbrace{
\{1,\ldots,T_{\mathrm{train}}\}
}_{\text{training}}
<
\underbrace{
\{T_{\mathrm{train}}+1,\ldots,T_{\mathrm{val}}\}
}_{\text{validation}}
<
\underbrace{
\{T_{\mathrm{val}}+1,\ldots,T_{\mathrm{test}}\}
}_{\text{testing}}.
\end{equation}
```

Walk-forward validation will be developed in detail in the model-training section.

#### Overfitting

Overfitting occurs when a model captures idiosyncratic patterns in the historical sample rather than persistent economic relationships.

Suppose observed returns satisfy

``` math
\begin{equation}
Y
=
f^*(X)
+
\varepsilon,
\end{equation}
```

where $`f^*`$ denotes the true underlying relationship and $`\varepsilon`$ denotes noise.

A highly flexible model may estimate

``` math
\begin{equation}
\widehat{f}
\end{equation}
```

that fits both

``` math
\begin{equation}
f^*(X)
\end{equation}
```

and part of the sample-specific noise $`\varepsilon`$.

This may produce excellent in-sample performance:

``` math
\begin{equation}
\mathrm{Error}_{\mathrm{IS}}
\downarrow,
\end{equation}
```

while out-of-sample performance deteriorates:

``` math
\begin{equation}
\mathrm{Error}_{\mathrm{OOS}}
\uparrow.
\end{equation}
```

##### Backtest Overfitting

Overfitting is not restricted to predictive models.

An entire investment strategy can be overfit through repeated choices of:

- signal definitions;

- lookback windows;

- portfolio thresholds;

- neutralization factors;

- rebalancing frequencies;

- risk targets;

- transaction-cost assumptions;

- universes.

The final strategy may therefore be viewed as the result of a large implicit optimization:

``` math
\begin{equation}
\theta^*
=
\underset{\theta\in\Theta}{\arg\max}
\;
\widehat{S}(\theta),
\end{equation}
```

where $`\theta`$ represents all research choices and $`\widehat{S}`$ denotes an estimated performance statistic such as the Sharpe ratio.

The larger the effective parameter space $`\Theta`$, the greater the risk that

``` math
\begin{equation}
\widehat{S}(\theta^*)
\gg
S_{\mathrm{true}}(\theta^*).
\end{equation}
```

##### Signs of Overfitting

Potential warning signs include:

- very high in-sample Sharpe ratios;

- narrow optimal parameter regions;

- strong sensitivity to small parameter changes;

- performance concentrated in a short subperiod;

- performance driven by a small number of securities;

- poor performance across related markets;

- large degradation from validation to test samples;

- economically implausible signal mechanisms.

##### Mitigation

Overfitting can be reduced through:

- simple and economically interpretable hypotheses;

- regularization;

- walk-forward validation;

- strict separation of training, validation, and testing;

- parameter-stability analysis;

- robustness tests;

- independent datasets;

- realistic transaction costs;

- explicit accounting for the number of research trials.

The objective is not necessarily to choose the model with the highest historical performance, but rather the model whose performance is most likely to generalize beyond the historical sample.

#### Unrealistic Trading and Cost Assumptions

Even a statistically valid signal can produce an unrealistic backtest if the simulation assumes impossible or excessively favorable trading conditions.

The backtest must therefore distinguish between

``` math
\begin{equation}
\boxed{
\text{predictive performance}
}
\end{equation}
```

and

``` math
\begin{equation}
\boxed{
\text{economically implementable performance}.
}
\end{equation}
```

##### Execution Prices

A common unrealistic assumption is executing all trades at the closing price used to compute the signal.

If

``` math
\begin{equation}
s_t
=
f(P_t^{\mathrm{close}}),
\end{equation}
```

then execution at the same closing price may not be feasible.

Execution should instead respect the chronological sequence established in the backtest design.

##### Bid–Ask Spread

Assuming execution at the mid-price ignores the bid–ask spread.

For a security with bid and ask prices

``` math
\begin{equation}
P_{i,t}^{\mathrm{bid}}
\qquad\text{and}\qquad
P_{i,t}^{\mathrm{ask}},
\end{equation}
```

the mid-price is

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

A market buy generally occurs closer to the ask and a market sell closer to the bid.

The one-way spread cost relative to the mid-price is approximately

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

##### Market Impact

A backtest that assumes transaction costs are independent of portfolio size may substantially overstate strategy capacity.

Let

``` math
\begin{equation}
Q_{i,t}
\end{equation}
```

denote traded quantity and

``` math
\begin{equation}
\mathrm{ADV}_{i,t}
\end{equation}
```

denote Average Daily Volume.

The participation rate is

``` math
\begin{equation}
\boxed{
PR_{i,t}
=
\frac{
Q_{i,t}
}{
\mathrm{ADV}_{i,t}
}.
}
\end{equation}
```

As $`PR_{i,t}`$ increases, market impact generally increases.

A stylized impact function may take the form

``` math
\begin{equation}
c_{i,t}^{\mathrm{impact}}
=
\eta
\sigma_{i,t}
PR_{i,t}^{\gamma},
\end{equation}
```

where $`\eta>0`$ and typically

``` math
\begin{equation}
0<\gamma\leq 1.
\end{equation}
```

A strategy that appears highly profitable at small capital may therefore become unattractive at large scale.

##### Short-Selling Constraints

Backtests of long–short strategies frequently assume that every security can be shorted without restriction.

In reality, a short position may face:

- limited borrow availability;

- stock-loan fees;

- hard-to-borrow premiums;

- recalls;

- short-sale restrictions;

- position limits.

The cost and feasibility of shorting may also be correlated with the investment signal itself.

For example, distressed or highly shorted securities may simultaneously appear attractive to a short signal and be particularly expensive to borrow.

##### Liquidity Constraints

A realistic portfolio should constrain trading relative to available market liquidity.

For example,

``` math
\begin{equation}
Q_{i,t}
\leq
\kappa
\,
\mathrm{ADV}_{i,t},
\end{equation}
```

where $`\kappa`$ denotes the maximum acceptable participation rate.

Ignoring such constraints can result in hypothetical portfolios that could not have been executed in practice.

##### Financing and Leverage

Leveraged portfolios incur financing costs.

If leverage at time $`t`$ is denoted by

``` math
\begin{equation}
L_t,
\end{equation}
```

then the economic return of a leveraged strategy cannot generally be obtained simply by multiplying the unlevered return by $`L_t`$.

Financing spreads, collateral requirements, borrowing constraints, and margin rules must also be considered.

##### Capacity

The profitability of a strategy is generally a function of assets under management:

``` math
\begin{equation}
\Pi
=
\Pi(A),
\end{equation}
```

where $`A`$ denotes strategy capital.

Because transaction costs and market impact generally increase with traded notional,

``` math
\begin{equation}
\frac{\partial TC(A)}{\partial A}
>
0.
\end{equation}
```

Strategy capacity can therefore be interpreted as the level of assets at which the incremental economic attractiveness of the strategy becomes insufficient.

Capacity analysis will be developed in greater detail in the performance and implementation sections.

#### Research Integrity and Backtest Governance

The biases described above are not independent. A single research workflow may simultaneously contain survivorship bias, preprocessing leakage, repeated parameter tuning, and unrealistic implementation assumptions.

A robust quantitative research process should therefore impose systematic controls throughout the entire pipeline.

##### Chronological Integrity

Every transformation should preserve the chronological ordering

``` math
\begin{equation}
\boxed{
\text{information}
\rightarrow
\text{decision}
\rightarrow
\text{execution}
\rightarrow
\text{realized outcome}.
}
\end{equation}
```

Future observations must never influence earlier investment decisions.

##### Point-in-Time Integrity

Data used at time $`t`$ should reproduce the data that would genuinely have been available at that date:

``` math
\begin{equation}
\boxed{
\mathcal{D}_t
=
\mathcal{D}_t^{\mathrm{PIT}}.
}
\end{equation}
```

This includes:

- security membership;

- fundamental releases;

- analyst forecasts;

- classifications;

- corporate actions;

- macroeconomic vintages.

##### Out-of-Sample Integrity

All decisions involving model selection should be separated from final evaluation.

Conceptually,

``` math
\begin{equation}
\boxed{
\underbrace{\text{Training}}_{\text{parameter estimation}}
\rightarrow
\underbrace{\text{Validation}}_{\text{model selection}}
\rightarrow
\underbrace{\text{Testing}}_{\text{final evaluation}}.
}
\end{equation}
```

Repeatedly consulting the test sample gradually converts it into another validation sample.

##### Experiment Tracking

Every material research experiment should ideally record:

- data version;

- universe definition;

- signal definition;

- preprocessing parameters;

- model parameters;

- portfolio-construction parameters;

- transaction-cost assumptions;

- performance results;

- date of the experiment.

This helps quantify researcher degrees of freedom and prevents the final strategy from appearing as if it were the only hypothesis ever tested.

##### Economic Plausibility

Statistical performance alone is insufficient evidence of a robust investment strategy.

A credible strategy should ideally have an economic, behavioral, structural, or institutional explanation for why the predictive relationship may persist.

The relevant question is not only

``` math
\begin{equation}
\text{``Did it work historically?''}
\end{equation}
```

but also

``` math
\begin{equation}
\boxed{
\text{``Why should this relationship survive out of sample?''}
}
\end{equation}
```

##### Backtest Integrity Checklist

Before interpreting historical performance, the researcher should verify at least that:

- no future information enters signal construction;

- preprocessing parameters are estimated using only admissible data;

- the historical investment universe is reconstructed point-in-time;

- delisted and disappeared securities are treated correctly;

- model selection is separated from final testing;

- the number of experiments and parameter searches is recognized;

- execution timing is feasible;

- transaction costs include both purchases and sales;

- spread, market impact, borrowing, and financing are modeled when economically relevant;

- portfolio size is consistent with market liquidity;

- robustness is evaluated across alternative periods and reasonable parameter choices.

A backtest should therefore not be interpreted as a direct estimate of future performance. It is better understood as a controlled historical experiment designed to determine whether an investment hypothesis remains economically and statistically plausible after accounting for realistic information, implementation, and research constraints.

# Data Engineering

