### Model-Based Signal Construction

A characteristic-based strategy directly transforms one or several firm-level characteristics into investment scores. A model-based strategy instead estimates a predictive relationship between a set of characteristics and a future target.

The general architecture is

``` math
\begin{equation}
\boxed{
\mathbf{X}_t
\rightarrow
\widehat{\mathbf{y}}_{t+h|t}
\rightarrow
\mathbf{s}_t^{\mathrm{raw}},
}
\end{equation}
```

where:

- $`\mathbf{X}_t`$ denotes the information available at time $`t`$;

- $`\widehat{\mathbf{y}}_{t+h|t}`$ denotes model predictions for horizon $`t+h`$ formed using information available at $`t`$;

- $`\mathbf{s}_t^{\mathrm{raw}}`$ denotes the final model-based raw investment score.

The fundamental distinction from direct characteristic scoring is therefore

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Characteristic-Based:}
&\quad
x_{i,t}
\rightarrow
s_{i,t}^{\mathrm{raw}},
\\[0.15cm]
\text{Model-Based:}
&\quad
\mathbf{x}_{i,t}
\rightarrow
\widehat{y}_{i,t+h|t}
\rightarrow
s_{i,t}^{\mathrm{raw}}.
\end{aligned}
}
\end{equation}
```

Once $`\mathbf{s}_t^{\mathrm{raw}}`$ has been produced, the downstream neutralization and portfolio-construction engine is identical in both cases.

#### General Predictive Framework

Let

``` math
\begin{equation}
\mathbf{x}_{i,t}
=
\begin{bmatrix}
x_{i,t}^{(1)}
&
\cdots
&
x_{i,t}^{(K)}
\end{bmatrix}^{\top}
\in
\mathbb{R}^{K}
\end{equation}
```

denote the vector of $`K`$ characteristics available for security $`i`$ at time $`t`$.

Let

``` math
\begin{equation}
y_{i,t+h}
\end{equation}
```

denote the future target variable over prediction horizon $`h`$.

The general predictive problem is

``` math
\begin{equation}
\boxed{
y_{i,t+h}
=
f
\left(
\mathbf{x}_{i,t};
\theta
\right)
+
\varepsilon_{i,t+h},
}
\end{equation}
```

where:

- $`f(\cdot)`$ is the predictive model;

- $`\theta`$ denotes model parameters;

- $`\varepsilon_{i,t+h}`$ denotes the prediction error.

At decision time $`t`$, model parameters must be estimated using only data available before or at that time:

``` math
\begin{equation}
\widehat{\theta}_t
=
\mathcal{A}
\left(
\mathcal{D}_t^{\mathrm{train}}
\right),
\end{equation}
```

where $`\mathcal{A}`$ denotes the estimation algorithm.

The prediction is then

``` math
\begin{equation}
\boxed{
\widehat{y}_{i,t+h|t}
=
f
\left(
\mathbf{x}_{i,t};
\widehat{\theta}_t
\right).
}
\end{equation}
```

The notation

``` math
\begin{equation}
\widehat{y}_{i,t+h|t}
\end{equation}
```

explicitly emphasizes that the prediction concerns time $`t+h`$ but is formed using information available at time $`t`$.

#### Target Variable Definition

The target variable determines what the model is attempting to predict.

For return-prediction strategies, a natural target is the future simple return

``` math
\begin{equation}
\boxed{
y_{i,t+h}
=
R_{i,t\rightarrow t+h}.
}
\end{equation}
```

However, alternative targets may include:

- future excess return;

- benchmark-relative return;

- market- or factor-adjusted return;

- future return rank;

- future return sign;

- probability of outperforming;

- future volatility;

- future drawdown;

- future risk-adjusted return.

##### Absolute vs. Relative Targets

An absolute return target is

``` math
\begin{equation}
y_{i,t+h}
=
R_{i,t\rightarrow t+h}.
\end{equation}
```

A benchmark-relative target is

``` math
\begin{equation}
\boxed{
y_{i,t+h}
=
R_{i,t\rightarrow t+h}
-
R_{B,t\rightarrow t+h}.
}
\end{equation}
```

A cross-sectionally demeaned target may be defined as

``` math
\begin{equation}
y_{i,t+h}
=
R_{i,t\rightarrow t+h}
-
\frac{1}{N_t}
\sum_{j=1}^{N_t}
R_{j,t\rightarrow t+h}.
\end{equation}
```

Relative targets may be more closely aligned with cross-sectional stock selection because they remove part of the common market component.

##### Continuous vs. Discrete Targets

For regression,

``` math
\begin{equation}
y_{i,t+h}
\in
\mathbb{R}.
\end{equation}
```

For binary classification,

``` math
\begin{equation}
y_{i,t+h}
=
\mathbb{I}
\left(
R_{i,t\rightarrow t+h}>0
\right).
\end{equation}
```

For relative classification,

``` math
\begin{equation}
y_{i,t+h}
=
\mathbb{I}
\left(
R_{i,t\rightarrow t+h}
>
R_{B,t\rightarrow t+h}
\right).
\end{equation}
```

For ranking problems, the target may instead be

``` math
\begin{equation}
y_{i,t+h}
=
\operatorname{Rank}_t
\left(
R_{i,t\rightarrow t+h}
\right).
\end{equation}
```

##### Prediction Horizon

The target horizon $`h`$ should correspond to the economic horizon of the strategy.

A mismatch between target horizon and portfolio implementation can materially affect both the statistical and economic interpretation of the model.

For example, predicting

``` math
\begin{equation}
R_{i,t\rightarrow t+20}
\end{equation}
```

while rebuilding the portfolio every day generates overlapping target periods.

This creates dependence across training observations and must be considered in validation and inference.

#### Input Characteristics and Design Matrix

Suppose $`K`$ firm-level characteristics are available.

For security $`i`$ at time $`t`$,

``` math
\begin{equation}
\mathbf{x}_{i,t}
=
\begin{bmatrix}
x_{i,t}^{(1)}
\\
\vdots
\\
x_{i,t}^{(K)}
\end{bmatrix}.
\end{equation}
```

Across the $`N_t`$ securities observed at time $`t`$, the design matrix is

``` math
\begin{equation}
\boxed{
\mathbf{X}_t
=
\begin{bmatrix}
(\mathbf{x}_{1,t})^\top
\\
\vdots
\\
(\mathbf{x}_{N_t,t})^\top
\end{bmatrix}
\in
\mathbb{R}^{N_t\times K}.
}
\end{equation}
```

The corresponding target vector is

``` math
\begin{equation}
\mathbf{y}_{t+h}
=
\begin{bmatrix}
y_{1,t+h}
\\
\vdots
\\
y_{N_t,t+h}
\end{bmatrix}.
\end{equation}
```

##### Panel Representation

Across multiple dates, observations may be stacked into a panel:

``` math
\begin{equation}
\mathcal{P}
=
\left\{
(\mathbf{x}_{i,t},y_{i,t+h})
:
i\in\mathcal{U}_t,
\;
t\in\mathcal{T}
\right\}.
\end{equation}
```

The corresponding stacked design matrix can be represented as

``` math
\begin{equation}
\mathbf{X}
\in
\mathbb{R}^{M\times K},
\end{equation}
```

where

``` math
\begin{equation}
M
=
\sum_t N_t
\end{equation}
```

is the total number of security-date observations.

##### Preprocessing Parameters

Some models require feature transformations such as scaling or centering.

If feature $`k`$ is standardized using training-sample parameters,

``` math
\begin{equation}
\widetilde{x}_{i,t}^{(k)}
=
\frac{
x_{i,t}^{(k)}
-
\widehat{\mu}_{k,\mathrm{train}}
}{
\widehat{\sigma}_{k,\mathrm{train}}
}.
\end{equation}
```

Crucially,

``` math
\begin{equation}
\boxed{
\widehat{\mu}_{k,\mathrm{train}},
\widehat{\sigma}_{k,\mathrm{train}}
}
\end{equation}
```

must be estimated exclusively from the corresponding training sample.

Preprocessing is therefore part of the fitted model pipeline rather than an operation that may be estimated once using the entire dataset.

#### Econometric Models

Econometric models specify an explicit parametric relationship between the target and explanatory characteristics.

##### Linear Regression

A cross-sectional or pooled linear model takes the form

``` math
\begin{equation}
\boxed{
y_{i,t+h}
=
\alpha
+
\mathbf{x}_{i,t}^{\top}\beta
+
\varepsilon_{i,t+h}.
}
\end{equation}
```

Stacking observations gives

``` math
\begin{equation}
\mathbf{y}
=
\mathbf{X}\beta
+
\varepsilon,
\end{equation}
```

after incorporating an intercept into the design matrix if required.

The Ordinary Least Squares estimator is

``` math
\begin{equation}
\boxed{
\widehat{\beta}^{OLS}
=
\left(
\mathbf{X}^{\top}\mathbf{X}
\right)^{-1}
\mathbf{X}^{\top}\mathbf{y},
}
\end{equation}
```

when $`\mathbf{X}^{\top}\mathbf{X}`$ is invertible.

##### Weighted Least Squares

Observations may receive different estimation weights.

Let

``` math
\begin{equation}
\mathbf{W}
=
\operatorname{diag}
\left(
\omega_1,\ldots,\omega_M
\right).
\end{equation}
```

Then

``` math
\begin{equation}
\boxed{
\widehat{\beta}^{WLS}
=
\left(
\mathbf{X}^{\top}
\mathbf{W}
\mathbf{X}
\right)^{-1}
\mathbf{X}^{\top}
\mathbf{W}
\mathbf{y}.
}
\end{equation}
```

Weights may reflect:

- recency;

- market capitalization;

- observation reliability;

- volatility;

- sampling design.

##### Regularized Linear Models

Ridge regression solves

``` math
\begin{equation}
\boxed{
\widehat{\beta}^{\mathrm{Ridge}}
=
\underset{\beta}{\arg\min}
\left[
\|\mathbf{y}-\mathbf{X}\beta\|_2^2
+
\lambda
\|\beta\|_2^2
\right].
}
\end{equation}
```

Lasso regression solves

``` math
\begin{equation}
\boxed{
\widehat{\beta}^{\mathrm{Lasso}}
=
\underset{\beta}{\arg\min}
\left[
\|\mathbf{y}-\mathbf{X}\beta\|_2^2
+
\lambda
\|\beta\|_1
\right].
}
\end{equation}
```

Elastic Net combines both penalties:

``` math
\begin{equation}
\boxed{
\widehat{\beta}^{EN}
=
\underset{\beta}{\arg\min}
\left[
\|\mathbf{y}-\mathbf{X}\beta\|_2^2
+
\lambda
\left(
\alpha\|\beta\|_1
+
(1-\alpha)\|\beta\|_2^2
\right)
\right].
}
\end{equation}
```

Regularization can reduce estimation variance and improve stability when characteristics are numerous or highly correlated.

##### Panel Models

Panel regressions may incorporate entity or time effects:

``` math
\begin{equation}
y_{i,t+h}
=
\alpha_i
+
\gamma_t
+
\mathbf{x}_{i,t}^{\top}\beta
+
\varepsilon_{i,t+h},
\end{equation}
```

where:

- $`\alpha_i`$ denotes security-specific effects;

- $`\gamma_t`$ denotes time-specific effects.

The appropriate specification depends on whether the objective is prediction, economic interpretation, or both.

#### Machine Learning Models

Machine-learning models relax the assumption of a fixed linear functional form.

The general prediction remains

``` math
\begin{equation}
\widehat{y}_{i,t+h|t}
=
f
\left(
\mathbf{x}_{i,t};
\widehat{\theta}_t
\right),
\end{equation}
```

but $`f(\cdot)`$ may be nonlinear and contain interactions that are not specified manually.

##### Decision Trees

A regression tree partitions the feature space into regions

``` math
\begin{equation}
\mathcal{R}_1,
\ldots,
\mathcal{R}_M
\end{equation}
```

and predicts

``` math
\begin{equation}
\widehat{y}(x)
=
\sum_{m=1}^{M}
c_m
\mathbb{I}
\left(
x\in\mathcal{R}_m
\right).
\end{equation}
```

Trees naturally capture nonlinearities and feature interactions.

##### Random Forests

A Random Forest combines $`B`$ trees:

``` math
\begin{equation}
\boxed{
\widehat{y}(x)
=
\frac{1}{B}
\sum_{b=1}^{B}
\widehat{f}_b(x).
}
\end{equation}
```

Bootstrap sampling and random feature selection reduce correlation between individual trees and can improve generalization.

##### Gradient Boosting

Boosting constructs an additive model:

``` math
\begin{equation}
\boxed{
\widehat{f}_M(x)
=
\sum_{m=1}^{M}
\eta
f_m(x),
}
\end{equation}
```

where:

- $`f_m`$ is typically a weak learner;

- $`\eta`$ is the learning rate.

Each new learner is chosen to reduce the residual error of the existing ensemble.

Gradient-boosted trees are particularly common in tabular financial prediction because they can capture nonlinearities while remaining relatively efficient.

##### Model Complexity

Unlike linear models, machine-learning models may contain a large number of effective degrees of freedom.

Their economic usefulness therefore depends critically on:

- temporal validation;

- regularization;

- hyperparameter control;

- sufficient sample size;

- robustness across periods.

Higher in-sample predictive power does not necessarily imply higher out-of-sample investment performance.

#### Deep Learning Models

Deep-learning models represent a particularly flexible class of nonlinear predictive functions.

A feed-forward neural network can be written recursively as

``` math
\begin{equation}
\mathbf{h}^{(1)}
=
\phi
\left(
\mathbf{W}^{(1)}\mathbf{x}
+
\mathbf{b}^{(1)}
\right),
\end{equation}
```

and

``` math
\begin{equation}
\mathbf{h}^{(\ell)}
=
\phi
\left(
\mathbf{W}^{(\ell)}
\mathbf{h}^{(\ell-1)}
+
\mathbf{b}^{(\ell)}
\right),
\end{equation}
```

for hidden layers $`\ell=2,\ldots,L`$.

The final prediction may be

``` math
\begin{equation}
\boxed{
\widehat{y}
=
\mathbf{W}^{(L+1)}
\mathbf{h}^{(L)}
+
\mathbf{b}^{(L+1)}.
}
\end{equation}
```

##### Sequential Models

When the complete historical path is an input, the model may receive

``` math
\begin{equation}
\mathbf{X}_{i,t}^{\mathrm{seq}}
=
\left[
\mathbf{x}_{i,t-L+1},
\ldots,
\mathbf{x}_{i,t}
\right].
\end{equation}
```

Architectures may then include recurrent networks, temporal convolutional models, or attention-based models.

##### Cross-Sectional Models

Deep-learning models may also process the entire cross-section jointly:

``` math
\begin{equation}
\mathbf{X}_t
\rightarrow
\widehat{\mathbf{y}}_{t+h|t}.
\end{equation}
```

Such models can potentially learn interactions across securities, but require particular care because the cross-sectional universe changes through time.

##### Higher Capacity and Overfitting

Deep models generally have substantially greater representational capacity than simple econometric models.

Consequently,

``` math
\begin{equation}
\boxed{
\text{Model Capacity}
\uparrow
\quad\Rightarrow\quad
\text{Need for Regularization and Validation}
\uparrow.
}
\end{equation}
```

Appropriate controls may include:

- weight decay;

- dropout;

- early stopping;

- architecture constraints;

- temporal cross-validation;

- ensembling.

#### Regression, Classification, and Ranking Objectives

The model objective should be aligned with the economic decision the strategy ultimately makes.

##### Regression

For continuous return prediction, a common loss is Mean Squared Error:

``` math
\begin{equation}
\boxed{
\mathcal{L}_{MSE}
=
\frac{1}{M}
\sum_{j=1}^{M}
\left(
y_j-\widehat{y}_j
\right)^2.
}
\end{equation}
```

Alternatively,

``` math
\begin{equation}
\mathcal{L}_{MAE}
=
\frac{1}{M}
\sum_{j=1}^{M}
|y_j-\widehat{y}_j|.
\end{equation}
```

##### Classification

For binary classification,

``` math
\begin{equation}
y_j\in\{0,1\},
\end{equation}
```

and the model predicts

``` math
\begin{equation}
p_j
=
P(y_j=1|\mathbf{x}_j).
\end{equation}
```

Binary cross-entropy is

``` math
\begin{equation}
\boxed{
\mathcal{L}_{BCE}
=
-
\frac{1}{M}
\sum_{j=1}^{M}
\left[
y_j\log(p_j)
+
(1-y_j)\log(1-p_j)
\right].
}
\end{equation}
```

##### Ranking

For cross-sectional stock selection, the exact numerical return prediction may be less important than the ordering of securities.

The objective may therefore emphasize

``` math
\begin{equation}
\operatorname{Rank}
\left(
\widehat{y}_{i,t+h|t}
\right)
\end{equation}
```

relative to

``` math
\begin{equation}
\operatorname{Rank}
\left(
y_{i,t+h}
\right).
\end{equation}
```

A rank-based evaluation metric is the cross-sectional Spearman correlation:

``` math
\begin{equation}
\boxed{
IC_t^{\mathrm{rank}}
=
\operatorname{Corr}_{\mathrm{Spearman}}
\left(
\widehat{\mathbf{y}}_{t+h|t},
\mathbf{y}_{t+h}
\right).
}
\end{equation}
```

Ranking losses may be pairwise or listwise and attempt to optimize ordering directly.

##### Statistical Loss vs. Investment Objective

The statistical training objective need not coincide with the final portfolio objective.

For example,

``` math
\begin{equation}
\mathcal{L}_{MSE}
\end{equation}
```

optimizes squared prediction errors, whereas the investment process may care primarily about:

- cross-sectional ranking;

- long–short spread;

- turnover;

- transaction costs;

- net Sharpe ratio.

Thus,

``` math
\begin{equation}
\boxed{
\text{Statistical Accuracy}
\neq
\text{Economic Performance}.
}
\end{equation}
```

The connection between predictions and portfolio performance is therefore evaluated only after the complete downstream portfolio-construction process has been applied.

#### Training, Validation, and Test Samples

Model estimation and model evaluation must be separated temporally.

Let the full historical sample be divided into:

``` math
\begin{equation}
\boxed{
\mathcal{D}^{\mathrm{train}},
\qquad
\mathcal{D}^{\mathrm{val}},
\qquad
\mathcal{D}^{\mathrm{test}}.
}
\end{equation}
```

These datasets serve different roles.

##### Training Sample

The training sample is used to estimate model parameters:

``` math
\begin{equation}
\widehat{\theta}
=
\mathcal{A}
\left(
\mathcal{D}^{\mathrm{train}}
\right).
\end{equation}
```

##### Validation Sample

The validation sample is used for:

- hyperparameter selection;

- model selection;

- early stopping;

- architecture selection;

- feature-selection decisions.

##### Test Sample

The test sample is reserved for final evaluation.

It should not influence:

``` math
\begin{equation}
\widehat{\theta},
\qquad
\lambda,
\qquad
\text{feature selection},
\qquad
\text{model architecture}.
\end{equation}
```

Repeatedly using test performance to modify the model converts the test sample into another validation sample.

##### Chronological Ordering

For financial prediction,

``` math
\begin{equation}
\boxed{
\mathcal{T}^{\mathrm{train}}
<
\mathcal{T}^{\mathrm{val}}
<
\mathcal{T}^{\mathrm{test}}.
}
\end{equation}
```

Random train-test splitting is generally inappropriate when it allows future observations to influence models evaluated on earlier periods.

#### Expanding and Rolling Estimation Windows

Model parameters may be estimated using either expanding or rolling historical windows.

##### Expanding Window

Let the first training observation occur at $`t_0`$.

At decision time $`t`$, an expanding training set is

``` math
\begin{equation}
\boxed{
\mathcal{D}_t^{\mathrm{train,exp}}
=
\left\{
(\mathbf{x}_{i,\tau},y_{i,\tau+h})
:
t_0
\leq
\tau
\leq
t-h
\right\}.
}
\end{equation}
```

As $`t`$ increases, the training sample grows.

The corresponding estimator is

``` math
\begin{equation}
\widehat{\theta}_t^{\mathrm{exp}}
=
\mathcal{A}
\left(
\mathcal{D}_t^{\mathrm{train,exp}}
\right).
\end{equation}
```

##### Rolling Window

For a fixed window length $`L`$,

``` math
\begin{equation}
\boxed{
\mathcal{D}_t^{\mathrm{train,roll}}
=
\left\{
(\mathbf{x}_{i,\tau},y_{i,\tau+h})
:
t-L
\leq
\tau
\leq
t-h
\right\}.
}
\end{equation}
```

Older observations are discarded as new ones enter.

##### Trade-Off

Expanding windows use more observations and may reduce estimation variance.

Rolling windows may adapt more quickly to structural change.

Thus,

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Expanding Window}
&\rightarrow
\text{More Data, Greater Historical Memory},
\\
\text{Rolling Window}
&\rightarrow
\text{Less Data, Greater Adaptability}.
\end{aligned}
}
\end{equation}
```

#### Walk-Forward Validation

Walk-forward validation reproduces the chronological process through which a model would have been estimated and deployed historically.

Let

``` math
\begin{equation}
t_1,
t_2,
\ldots,
t_M
\end{equation}
```

denote successive prediction dates.

For each date $`t_m`$:

1.  construct the admissible training sample;

2.  estimate preprocessing parameters;

3.  fit the model;

4.  optionally select hyperparameters using historical validation data;

5.  generate predictions for $`t_m`$;

6.  move forward to $`t_{m+1}`$.

The resulting predictions are

``` math
\begin{equation}
\boxed{
\left\{
\widehat{\mathbf{y}}_{t_m+h|t_m}
\right\}_{m=1}^{M}.
}
\end{equation}
```

Each prediction is therefore genuinely out of sample relative to its own estimation window.

##### Pseudo-Out-of-Sample Predictions

The sequence

``` math
\begin{equation}
\widehat{\mathbf{y}}_{t+h|t}
\end{equation}
```

is often referred to as a pseudo-out-of-sample prediction because the model is evaluated historically under the same information restrictions that would have applied in real time.

#### Embargo and Leakage Prevention

When targets overlap in time, simply ending the training sample immediately before the prediction date may still create leakage.

Suppose the target is

``` math
\begin{equation}
y_{i,\tau+h}
=
R_{i,\tau\rightarrow\tau+h}.
\end{equation}
```

An observation whose feature date is $`\tau<t`$ may nevertheless have a target period extending beyond the decision date $`t`$.

To prevent this, the training sample should contain only observations whose targets are fully realized and admissible before the model is estimated.

##### Embargo

Let $`E`$ denote an embargo interval.

The last admissible training observation may be restricted to

``` math
\begin{equation}
\boxed{
\tau+h
\leq
t-E.
}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
\tau
\leq
t-E-h.
\end{equation}
```

The embargo introduces a temporal buffer between training outcomes and the prediction date.

##### Purging Overlapping Labels

If training and validation observations contain overlapping target intervals, observations whose labels overlap the validation period may be removed.

This is particularly relevant when

``` math
\begin{equation}
h
\end{equation}
```

is long relative to the rebalancing frequency.

##### Preprocessing Leakage

All data-dependent preprocessing must be estimated inside the training window.

This includes:

- feature means;

- feature standard deviations;

- imputation parameters;

- dimensionality reduction;

- feature selection;

- learned embeddings.

Thus,

``` math
\begin{equation}
\boxed{
\text{Fit preprocessing on train}
\rightarrow
\text{Apply unchanged to validation/test}.
}
\end{equation}
```

#### Hyperparameter Selection

Many models depend on hyperparameters that are not estimated directly through the primary training objective.

Let

``` math
\begin{equation}
\lambda
\in
\Lambda
\end{equation}
```

denote a hyperparameter configuration.

Examples include:

- Ridge penalty;

- Lasso penalty;

- tree depth;

- number of trees;

- learning rate;

- neural-network architecture;

- dropout rate;

- regularization strength.

Hyperparameter selection can be expressed as

``` math
\begin{equation}
\boxed{
\lambda_t^*
=
\underset{\lambda\in\Lambda}{\arg\min}
\;
\mathcal{L}_{\mathrm{val},t}(\lambda).
}
\end{equation}
```

Alternatively, if a higher evaluation metric is better,

``` math
\begin{equation}
\lambda_t^*
=
\underset{\lambda\in\Lambda}{\arg\max}
\;
M_{\mathrm{val},t}(\lambda).
\end{equation}
```

##### Statistical vs. Economic Selection Metrics

Possible validation criteria include:

- RMSE;

- MAE;

- classification accuracy;

- cross-entropy;

- Pearson IC;

- rank IC;

- validation long–short spread;

- validation net Sharpe ratio.

If an economic performance metric is used, the complete validation portfolio construction and cost model must itself remain strictly inside the validation procedure.

##### Nested Selection

When hyperparameter tuning is intensive, an inner validation loop may be used inside each outer walk-forward period.

Conceptually,

``` math
\begin{equation}
\boxed{
\text{Outer Training Window}
\supset
\left[
\text{Inner Train}
+
\text{Inner Validation}
\right].
}
\end{equation}
```

The outer prediction date remains untouched until the final selected model is applied.

#### Model Refitting

The model does not necessarily need to be re-estimated at every portfolio rebalance.

Let

``` math
\begin{equation}
\mathcal{T}^{\mathrm{refit}}
=
\left\{
t_1^{R},
t_2^{R},
\ldots
\right\}
\end{equation}
```

denote model-refitting dates.

Between two refitting dates,

``` math
\begin{equation}
t_m^{R}
\leq
t
<
t_{m+1}^{R},
\end{equation}
```

the parameters may remain fixed:

``` math
\begin{equation}
\boxed{
\widehat{\theta}_t
=
\widehat{\theta}_{t_m^{R}}.
}
\end{equation}
```

##### Refit Frequency vs. Prediction Frequency

The following frequencies are distinct:

``` math
\begin{equation}
\boxed{
f_{\mathrm{refit}}
\neq
f_{\mathrm{prediction}}
\neq
f_{\mathrm{rebalance}}.
}
\end{equation}
```

For example, a model may:

- refit monthly;

- generate predictions daily;

- rebalance weekly.

##### Full Refitting vs. Parameter Updates

A refit may involve:

- re-estimating model parameters only;

- re-estimating preprocessing parameters;

- reselecting hyperparameters;

- reselecting features;

- retraining the complete model architecture.

These choices should be distinguished because they imply different levels of adaptation and computational cost.

#### Prediction-to-Score Transformation

The model prediction

``` math
\begin{equation}
\widehat{y}_{i,t+h|t}
\end{equation}
```

is not necessarily used directly as the investment score.

The prediction vector is

``` math
\begin{equation}
\widehat{\mathbf{y}}_{t+h|t}
=
\begin{bmatrix}
\widehat{y}_{1,t+h|t}
\\
\vdots
\\
\widehat{y}_{N_t,t+h|t}
\end{bmatrix}.
\end{equation}
```

A scoring transformation produces

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{raw}}
=
\mathcal{P}_t
\left(
\widehat{y}_{i,t+h|t}
\right).
}
\end{equation}
```

##### Direct Prediction Score

The simplest choice is

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{raw}}
=
\widehat{y}_{i,t+h|t}.
}
\end{equation}
```

This preserves the model’s predicted magnitude.

##### Cross-Sectional Standardization

Predictions may instead be standardized:

``` math
\begin{equation}
s_{i,t}^{\mathrm{raw}}
=
\frac{
\widehat{y}_{i,t+h|t}
-
\widehat{\mu}_t
}{
\widehat{\sigma}_t
},
\end{equation}
```

where

``` math
\begin{equation}
\widehat{\mu}_t
=
\frac{1}{N_t}
\sum_i
\widehat{y}_{i,t+h|t}.
\end{equation}
```

##### Rank-Based Prediction Score

Alternatively,

``` math
\begin{equation}
r_{i,t}^{\mathrm{pred}}
=
\operatorname{Rank}_t
\left(
\widehat{y}_{i,t+h|t}
\right),
\end{equation}
```

followed by

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{raw}}
=
2
\frac{
r_{i,t}^{\mathrm{pred}}-1
}{
N_t-1
}
-1.
}
\end{equation}
```

This discards predicted magnitude and retains only ordering.

##### Classification Probabilities

For a classifier predicting

``` math
\begin{equation}
p_{i,t}
=
P
\left(
y_{i,t+h}=1
\mid
\mathbf{x}_{i,t}
\right),
\end{equation}
```

a centered score may be

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{raw}}
=
2p_{i,t}-1.
}
\end{equation}
```

Then

``` math
\begin{equation}
s_{i,t}^{\mathrm{raw}}
\in
[-1,1].
\end{equation}
```

##### Prediction Calibration

The numerical magnitude of model predictions should not automatically be interpreted as economically calibrated expected returns.

For example,

``` math
\begin{equation}
\widehat{y}_{i,t+h|t}=0.02
\end{equation}
```

does not necessarily imply that the true expected return is exactly $`2\%`$.

Models optimized for ranking may produce useful cross-sectional ordering even when prediction magnitudes are poorly calibrated.

Thus,

``` math
\begin{equation}
\boxed{
\text{Predictive Ranking Quality}
\neq
\text{Prediction Calibration}.
}
\end{equation}
```

#### Final Model-Based Raw Score

The final output of the model-based signal layer is

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{raw}}
=
\begin{bmatrix}
s_{1,t}^{\mathrm{raw}}
\\
\vdots
\\
s_{N_t,t}^{\mathrm{raw}}
\end{bmatrix}
\in
\mathbb{R}^{N_t}.
}
\end{equation}
```

The complete model-based pipeline can therefore be represented as

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathcal{D}_t^{\mathrm{PIT}}
&\rightarrow
\mathbf{X}_t
\rightarrow
\widehat{\theta}_t
\\[0.1cm]
&\rightarrow
\widehat{\mathbf{y}}_{t+h|t}
\rightarrow
\mathcal{P}_t
\left(
\widehat{\mathbf{y}}_{t+h|t}
\right)
\rightarrow
\mathbf{s}_t^{\mathrm{raw}}.
\end{aligned}
}
\end{equation}
```

The estimation operator itself depends only on historical admissible data:

``` math
\begin{equation}
\widehat{\theta}_t
=
\mathcal{A}
\left(
\mathcal{D}_t^{\mathrm{train}}
\right),
\end{equation}
```

so that

``` math
\begin{equation}
\boxed{
\widehat{\theta}_t
\in
\mathcal{I}_t.
}
\end{equation}
```

##### Unified Signal Interface

The characteristic-based route produces

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{raw}}
=
\mathcal{S}
\left(
\mathbf{X}_t
\right),
\end{equation}
```

while the model-based route produces

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{raw}}
=
\mathcal{P}
\left[
f
\left(
\mathbf{X}_t;
\widehat{\theta}_t
\right)
\right].
\end{equation}
```

In both cases, the downstream engine receives exactly the same mathematical object:

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{raw}}
\in
\mathbb{R}^{N_t}.
}
\end{equation}
```

The subsequent processing is therefore model agnostic:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{s}_t^{\mathrm{raw}}
&\rightarrow
\text{Signal Neutralization}
\rightarrow
\mathbf{s}_t^{\mathrm{neutral}}
\\[0.1cm]
&\rightarrow
\text{Final Signal Construction}
\rightarrow
\mathbf{s}_t^{\mathrm{final}}
\\[0.1cm]
&\rightarrow
\text{Portfolio Construction}
\rightarrow
\mathbf{w}_t.
\end{aligned}
}
\end{equation}
```

##### Backtest Invariant

At every historical prediction date $`t`$, the model-based engine should satisfy

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{raw}}
=
g
\left(
\mathcal{I}_t
\right).
}
\end{equation}
```

No characteristic transformation, model parameter, hyperparameter, preprocessing statistic, or model-selection decision used to generate the raw score may depend on information outside the historical information set $`\mathcal{I}_t`$.

This condition is the fundamental invariant of model-based signal generation. “‘

“‘latex

# Signal Neutralization and Final Signal

