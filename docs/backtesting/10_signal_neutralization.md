### Signal Neutralization

The raw investment score

``` math
\begin{equation}
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
\mathbb{R}^{N_t}
\end{equation}
```

may contain unintended exposures to systematic characteristics such as:

- market beta;

- industry or sector membership;

- country;

- size;

- volatility;

- momentum;

- other style factors.

For example, a valuation score may unintentionally assign systematically higher scores to small-cap stocks, or an analyst-revision signal may be concentrated in particular industries.

Signal neutralization attempts to remove these systematic components before the signal is mapped into portfolio weights.

The generic objective is

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{raw}}
\rightarrow
\mathbf{s}_t^{\mathrm{neutral}},
}
\end{equation}
```

where the neutralized score has zero exposure, according to the chosen neutralization metric, to a predefined set of variables.

The distinction between signal neutralization and portfolio neutralization is fundamental:

``` math
\begin{equation}
\boxed{
\text{Signal Neutralization}
\neq
\text{Portfolio Neutralization}.
}
\end{equation}
```

Signal neutralization modifies the alpha signal before portfolio construction. Portfolio neutralization instead imposes constraints directly on final portfolio weights.

Both may be used in the same strategy, but they operate at different stages of the investment process.

#### Motivation for Neutralization

Suppose the raw signal is predictive because

``` math
\begin{equation}
\mathbb{E}
\left[
R_{i,t+1}
\mid
s_{i,t}^{\mathrm{raw}}
\right]
\end{equation}
```

varies across securities.

However, assume that the signal is correlated with a systematic factor exposure

``` math
\begin{equation}
b_{i,t}.
\end{equation}
```

Then part of the apparent predictive power of the signal may simply reflect exposure to that factor.

For example,

``` math
\begin{equation}
\operatorname{Corr}_t
\left(
s_{i,t}^{\mathrm{raw}},
\beta_{i,t}
\right)
\neq
0.
\end{equation}
```

A strategy that buys high-score stocks and shorts low-score stocks may therefore generate a portfolio with systematic market-beta exposure even if the original objective was to capture stock-specific alpha.

##### Signal Decomposition

A simple decomposition is

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{raw}}
=
\mathbf{B}_t
\boldsymbol{\gamma}_t
+
\boldsymbol{\varepsilon}_t,
}
\end{equation}
```

where:

- $`\mathbf{B}_t`$ contains systematic exposures;

- $`\boldsymbol{\gamma}_t`$ measures the component of the raw score associated with those exposures;

- $`\boldsymbol{\varepsilon}_t`$ is the residual component.

The neutralized score is then defined as

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{neutral}}
=
\boldsymbol{\varepsilon}_t.
}
\end{equation}
```

The purpose of neutralization is therefore to preserve the component of the signal that cannot be explained by the selected systematic exposures.

##### Economic Interpretation

Neutralization answers the question:

``` math
\begin{equation}
\boxed{
\begin{aligned}
&\text{How attractive is security }i
\\
&\text{after controlling for its systematic characteristics?}
\end{aligned}
}
\end{equation}
```

For example, industry-neutral value does not compare a bank directly with a technology company according to raw valuation levels. Instead, it attempts to identify securities that are attractive relative to what would be expected given their industry characteristics.

#### General Exposure Matrix

Let

``` math
\begin{equation}
K_t
\end{equation}
```

denote the number of exposures that should be removed at time $`t`$.

For security $`i`$, define

``` math
\begin{equation}
\mathbf{b}_{i,t}
=
\begin{bmatrix}
b_{i,t}^{(1)}
\\
\vdots
\\
b_{i,t}^{(K_t)}
\end{bmatrix}
\in
\mathbb{R}^{K_t}.
\end{equation}
```

Stacking the exposures across securities gives the exposure matrix

``` math
\begin{equation}
\boxed{
\mathbf{B}_t
=
\begin{bmatrix}
(\mathbf{b}_{1,t})^\top
\\
\vdots
\\
(\mathbf{b}_{N_t,t})^\top
\end{bmatrix}
\in
\mathbb{R}^{N_t\times K_t}.
}
\end{equation}
```

Possible columns of $`\mathbf{B}_t`$ include:

``` math
\begin{equation}
\mathbf{B}_t
=
\begin{bmatrix}
\mathbf{1}
&
\boldsymbol{\beta}_t
&
\mathbf{D}_t^{\mathrm{industry}}
&
\log(\mathbf{MCap}_t)
&
\boldsymbol{\sigma}_t
&
\mathbf{F}_t^{\mathrm{style}}
\end{bmatrix}.
\end{equation}
```

The exact matrix depends on the desired neutralization.

##### Intercept

An intercept column

``` math
\begin{equation}
\mathbf{1}
=
\begin{bmatrix}
1\\
\vdots\\
1
\end{bmatrix}
\end{equation}
```

is frequently included.

Then the residualized signal satisfies

``` math
\begin{equation}
\mathbf{1}^{\top}
\mathbf{s}_t^{\mathrm{neutral}}
=
0
\end{equation}
```

under ordinary least squares.

Thus, the cross-sectional mean of the residual signal is zero.

##### Continuous and Categorical Exposures

Continuous exposures may include

``` math
\begin{equation}
\beta_{i,t},
\qquad
\log(\mathrm{MCap}_{i,t}),
\qquad
\sigma_{i,t}.
\end{equation}
```

Categorical variables such as industry membership are represented through dummy variables.

If there are $`G`$ industries,

``` math
\begin{equation}
D_{i,g,t}
=
\begin{cases}
1,
&
\text{if security }i\text{ belongs to industry }g,
\\
0,
&
\text{otherwise}.
\end{cases}
\end{equation}
```

The corresponding matrix is

``` math
\begin{equation}
\mathbf{D}_t
\in
\mathbb{R}^{N_t\times G}.
\end{equation}
```

##### Dummy Variable Collinearity

If an intercept is included together with all mutually exclusive industry dummy variables,

``` math
\begin{equation}
\mathbf{1}
=
\sum_{g=1}^{G}
\mathbf{D}_{g,t}.
\end{equation}
```

The design matrix is therefore perfectly collinear.

One category must be omitted, or another identification convention must be used.

For example,

``` math
\begin{equation}
\mathbf{B}_t
=
\begin{bmatrix}
\mathbf{1}
&
\mathbf{D}_{1,t}
&
\cdots
&
\mathbf{D}_{G-1,t}
\end{bmatrix}.
\end{equation}
```

#### Cross-Sectional Regression Framework

The standard neutralization method is a cross-sectional regression performed independently at each decision date $`t`$.

The model is

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{raw}}
=
\mathbf{B}_t
\boldsymbol{\gamma}_t
+
\boldsymbol{\varepsilon}_t.
}
\end{equation}
```

Under Ordinary Least Squares,

``` math
\begin{equation}
\widehat{\boldsymbol{\gamma}}_t
=
\left(
\mathbf{B}_t^\top
\mathbf{B}_t
\right)^{-1}
\mathbf{B}_t^\top
\mathbf{s}_t^{\mathrm{raw}},
\end{equation}
```

assuming the matrix is invertible.

The fitted systematic component is

``` math
\begin{equation}
\widehat{\mathbf{s}}_t^{\mathrm{systematic}}
=
\mathbf{B}_t
\widehat{\boldsymbol{\gamma}}_t.
\end{equation}
```

The neutralized score is

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{neutral}}
=
\mathbf{s}_t^{\mathrm{raw}}
-
\mathbf{B}_t
\widehat{\boldsymbol{\gamma}}_t.
}
\end{equation}
```

##### Projection-Matrix Representation

Define the projection matrix onto the column space of $`\mathbf{B}_t`$:

``` math
\begin{equation}
\boxed{
\mathbf{P}_{B,t}
=
\mathbf{B}_t
\left(
\mathbf{B}_t^\top
\mathbf{B}_t
\right)^{-1}
\mathbf{B}_t^\top.
}
\end{equation}
```

Then

``` math
\begin{equation}
\widehat{\mathbf{s}}_t^{\mathrm{systematic}}
=
\mathbf{P}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}.
\end{equation}
```

Define the residual-maker matrix

``` math
\begin{equation}
\boxed{
\mathbf{M}_{B,t}
=
\mathbf{I}
-
\mathbf{P}_{B,t}.
}
\end{equation}
```

The neutralized score is therefore

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{neutral}}
=
\mathbf{M}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}.
}
\end{equation}
```

##### Orthogonality Property

OLS residuals satisfy

``` math
\begin{equation}
\boxed{
\mathbf{B}_t^\top
\mathbf{s}_t^{\mathrm{neutral}}
=
\mathbf{0}.
}
\end{equation}
```

Thus, the neutralized score is orthogonal to every column of the exposure matrix under the Euclidean inner product.

This is the mathematical basis of regression-based neutralization.

##### Geometric Interpretation

The raw signal can be decomposed as

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{raw}}
=
\underbrace{
\mathbf{P}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}
}_{\text{component explained by exposures}}
+
\underbrace{
\mathbf{M}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}
}_{\text{orthogonal component}}.
}
\end{equation}
```

Neutralization removes the projection of the signal onto the subspace spanned by the unwanted exposures.

#### Beta Neutralization

Suppose

``` math
\begin{equation}
\boldsymbol{\beta}_t
=
\begin{bmatrix}
\beta_{1,t}
\\
\vdots
\\
\beta_{N_t,t}
\end{bmatrix}
\end{equation}
```

denotes the vector of stock-level market betas.

A beta-neutralized signal can be obtained from

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{raw}}
=
\alpha_t
+
\gamma_{\beta,t}
\beta_{i,t}
+
\varepsilon_{i,t}.
}
\end{equation}
```

In matrix form,

``` math
\begin{equation}
\mathbf{B}_t
=
\begin{bmatrix}
\mathbf{1}
&
\boldsymbol{\beta}_t
\end{bmatrix}.
\end{equation}
```

The neutralized score is

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\beta\text{-neutral}}
=
\widehat{\boldsymbol{\varepsilon}}_t.
}
\end{equation}
```

By construction,

``` math
\begin{equation}
\boldsymbol{\beta}_t^\top
\mathbf{s}_t^{\beta\text{-neutral}}
=
0
\end{equation}
```

under OLS.

##### Interpretation

Suppose high-score securities systematically have high market beta.

Then

``` math
\begin{equation}
\gamma_{\beta,t}>0.
\end{equation}
```

Beta neutralization removes the component of the raw score that can be explained linearly by beta.

The residual score therefore represents relative attractiveness conditional on market beta.

##### Signal Beta Neutrality vs. Portfolio Beta Neutrality

The condition

``` math
\begin{equation}
\boldsymbol{\beta}_t^\top
\mathbf{s}_t^{\mathrm{neutral}}
=
0
\end{equation}
```

does not automatically imply

``` math
\begin{equation}
\boldsymbol{\beta}_t^\top
\mathbf{w}_t
=
0.
\end{equation}
```

This is because the subsequent signal-to-weight mapping may be nonlinear or may introduce constraints and scaling.

Therefore,

``` math
\begin{equation}
\boxed{
\text{Beta-Neutral Signal}
\not\Rightarrow
\text{Beta-Neutral Portfolio}.
}
\end{equation}
```

Portfolio beta neutrality must be checked or imposed separately during portfolio construction.

#### Industry and Sector Neutralization

Industry neutralization removes systematic differences in signal levels across industries or sectors.

Suppose there are $`G`$ industries.

The raw score may be modeled as

``` math
\begin{equation}
s_{i,t}^{\mathrm{raw}}
=
\alpha_t
+
\sum_{g=1}^{G-1}
\gamma_{g,t}
D_{i,g,t}
+
\varepsilon_{i,t}.
\end{equation}
```

The residual

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{industry\text{-}neutral}}
=
\widehat{\varepsilon}_{i,t}
}
\end{equation}
```

measures the security’s score relative to the systematic level associated with its industry.

##### Group-Demeaning Interpretation

If the model contains only industry dummies and no additional continuous variables, industry neutralization is closely related to subtracting the industry mean.

For industry $`g`$,

``` math
\begin{equation}
\bar{s}_{g,t}
=
\frac{
1
}{
N_{g,t}
}
\sum_{i:g(i,t)=g}
s_{i,t}^{\mathrm{raw}}.
\end{equation}
```

Then a simple industry-demeaned score is

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{neutral}}
=
s_{i,t}^{\mathrm{raw}}
-
\bar{s}_{g(i,t),t}.
}
\end{equation}
```

Thus, a security is evaluated relative to peers in the same industry rather than relative to the entire market.

##### Sector vs. Industry Granularity

Neutralization may be performed at different hierarchical levels:

``` math
\begin{equation}
\text{Sector}
\rightarrow
\text{Industry Group}
\rightarrow
\text{Industry}
\rightarrow
\text{Sub-Industry}.
\end{equation}
```

A finer classification removes more granular systematic variation but leaves fewer securities within each group.

Thus,

``` math
\begin{equation}
\boxed{
\text{Finer Neutralization}
\rightarrow
\text{Less Cross-Sectional Information Per Group}.
}
\end{equation}
```

#### Country Neutralization

In international strategies, raw scores may differ systematically across countries because of:

- accounting conventions;

- sector composition;

- macroeconomic regimes;

- valuation levels;

- local market structure.

Let

``` math
\begin{equation}
C_{i,c,t}
\end{equation}
```

denote country dummy $`c`$.

The regression becomes

``` math
\begin{equation}
s_{i,t}^{\mathrm{raw}}
=
\alpha_t
+
\sum_{c=1}^{C-1}
\gamma_{c,t}^{C}
C_{i,c,t}
+
\varepsilon_{i,t}.
\end{equation}
```

The country-neutral score is

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{country\text{-}neutral}}
=
\widehat{\varepsilon}_{i,t}.
}
\end{equation}
```

This prevents systematic differences in country-level signal distributions from dominating the stock-selection process.

#### Size Neutralization

Many firm characteristics are correlated with company size.

A standard size variable is

``` math
\begin{equation}
\boxed{
z_{i,t}^{\mathrm{size}}
=
\log
\left(
\mathrm{MCap}_{i,t}
\right).
}
\end{equation}
```

The logarithm is typically preferred because market capitalization is highly right-skewed.

A size-neutralization regression is

``` math
\begin{equation}
s_{i,t}^{\mathrm{raw}}
=
\alpha_t
+
\gamma_{\mathrm{size},t}
\log
\left(
\mathrm{MCap}_{i,t}
\right)
+
\varepsilon_{i,t}.
\end{equation}
```

The residual is

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{size\text{-}neutral}}
=
\widehat{\varepsilon}_{i,t}.
}
\end{equation}
```

##### Nonlinear Size Effects

The relationship between a raw signal and size need not be linear.

A more flexible specification may include

``` math
\begin{equation}
\left[
\log(\mathrm{MCap}_{i,t})
\right]^2,
\end{equation}
```

or other basis functions.

For example,

``` math
\begin{equation}
s_{i,t}^{\mathrm{raw}}
=
\alpha_t
+
\gamma_{1,t}
\log(\mathrm{MCap}_{i,t})
+
\gamma_{2,t}
\left[
\log(\mathrm{MCap}_{i,t})
\right]^2
+
\varepsilon_{i,t}.
\end{equation}
```

Neutralization removes only the functional relationship explicitly included in the regression.

#### Volatility Neutralization

Signals may also be systematically related to stock-level risk.

Let

``` math
\begin{equation}
\sigma_{i,t}
\end{equation}
```

denote an ex-ante volatility estimate.

A volatility-neutralization regression is

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{raw}}
=
\alpha_t
+
\gamma_{\sigma,t}
\sigma_{i,t}
+
\varepsilon_{i,t}.
}
\end{equation}
```

The residual signal is orthogonal to the included volatility measure.

This can be useful when the strategy intends to separate alpha information from a low-volatility or high-volatility tilt.

##### Choice of Volatility Measure

Possible measures include:

- realized historical volatility;

- exponentially weighted volatility;

- idiosyncratic volatility;

- risk-model forecast volatility.

The choice determines the exposure being removed.

For example,

``` math
\begin{equation}
\sigma_{i,t}^{\mathrm{total}}
\end{equation}
```

and

``` math
\begin{equation}
\sigma_{i,t}^{\mathrm{idiosyncratic}}
\end{equation}
```

represent economically different risk concepts.

#### Momentum and Style Factor Neutralization

The same framework extends naturally to additional style characteristics.

Suppose

``` math
\begin{equation}
\mathbf{f}_{i,t}^{\mathrm{style}}
=
\begin{bmatrix}
f_{i,t}^{\mathrm{momentum}}
\\
f_{i,t}^{\mathrm{value}}
\\
f_{i,t}^{\mathrm{quality}}
\\
f_{i,t}^{\mathrm{lowvol}}
\\
\vdots
\end{bmatrix}.
\end{equation}
```

Then

``` math
\begin{equation}
s_{i,t}^{\mathrm{raw}}
=
\alpha_t
+
\left(
\mathbf{f}_{i,t}^{\mathrm{style}}
\right)^\top
\boldsymbol{\gamma}_t
+
\varepsilon_{i,t}.
\end{equation}
```

The residual

``` math
\begin{equation}
\boxed{
s_{i,t}^{\mathrm{style\text{-}neutral}}
=
\widehat{\varepsilon}_{i,t}
}
\end{equation}
```

represents the component of the signal orthogonal to the included style exposures.

##### Avoiding Mechanical Removal of the Alpha

Neutralization should be applied only to exposures that are genuinely unwanted.

If the alpha hypothesis itself is a momentum strategy, neutralizing the signal against momentum may remove the intended source of return.

Thus,

``` math
\begin{equation}
\boxed{
\text{Neutralization Variable}
\neq
\text{Automatically Desirable Control}.
}
\end{equation}
```

Every exposure included in the neutralization matrix should therefore have a clear economic justification.

“‘latex

#### Joint vs. Sequential Neutralization

When several groups of exposures must be removed from a raw signal, two broad approaches may be considered:

``` math
\begin{equation}
\boxed{
\text{Joint Neutralization}
\qquad\text{or}\qquad
\text{Sequential Neutralization}.
}
\end{equation}
```

The distinction must be handled carefully. A naive sequential residualization is generally not equivalent to a joint regression. However, a properly constructed sequential procedure based on the *Frisch–Waugh–Lovell theorem* is exactly equivalent to joint neutralization.

Let

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{raw}}
\in
\mathbb{R}^{N_t}
\end{equation}
```

denote the raw cross-sectional signal at time $`t`$, where $`N_t`$ is the number of securities in the investment universe.

Suppose the exposures to be removed are divided into two blocks:

``` math
\begin{equation}
\mathbf{B}_{1,t}
\in
\mathbb{R}^{N_t\times K_1},
\end{equation}
```

and

``` math
\begin{equation}
\mathbf{B}_{2,t}
\in
\mathbb{R}^{N_t\times K_2},
\end{equation}
```

where $`K_1`$ and $`K_2`$ denote the number of exposures in the first and second blocks respectively.

Examples could be:

``` math
\begin{equation}
\mathbf{B}_{1,t}
=
\begin{bmatrix}
\mathbf{1}
&
\boldsymbol{\beta}_t
\end{bmatrix},
\end{equation}
```

and

``` math
\begin{equation}
\mathbf{B}_{2,t}
=
\begin{bmatrix}
\mathbf{D}_t^{\mathrm{industry}}
&
\log(\mathbf{MCap}_t)
\end{bmatrix}.
\end{equation}
```

##### Joint Neutralization

Define the complete exposure matrix

``` math
\begin{equation}
\boxed{
\mathbf{B}_t
=
\begin{bmatrix}
\mathbf{B}_{1,t}
&
\mathbf{B}_{2,t}
\end{bmatrix}
\in
\mathbb{R}^{N_t\times(K_1+K_2)}.
}
\end{equation}
```

Joint neutralization estimates the cross-sectional regression

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{raw}}
=
\mathbf{B}_{1,t}
\boldsymbol{\gamma}_{1,t}
+
\mathbf{B}_{2,t}
\boldsymbol{\gamma}_{2,t}
+
\boldsymbol{\varepsilon}_t,
}
\end{equation}
```

where

``` math
\begin{equation}
\boldsymbol{\gamma}_{1,t}
\in
\mathbb{R}^{K_1},
\qquad
\boldsymbol{\gamma}_{2,t}
\in
\mathbb{R}^{K_2},
\end{equation}
```

and

``` math
\begin{equation}
\boldsymbol{\varepsilon}_t
\in
\mathbb{R}^{N_t}.
\end{equation}
```

Equivalently,

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{raw}}
=
\mathbf{B}_t
\boldsymbol{\gamma}_t
+
\boldsymbol{\varepsilon}_t,
\end{equation}
```

with

``` math
\begin{equation}
\boldsymbol{\gamma}_t
=
\begin{bmatrix}
\boldsymbol{\gamma}_{1,t}
\\
\boldsymbol{\gamma}_{2,t}
\end{bmatrix}
\in
\mathbb{R}^{K_1+K_2}.
\end{equation}
```

Under Ordinary Least Squares,

``` math
\begin{equation}
\widehat{\boldsymbol{\gamma}}_t
=
\left(
\mathbf{B}_t^\top
\mathbf{B}_t
\right)^{-1}
\mathbf{B}_t^\top
\mathbf{s}_t^{\mathrm{raw}},
\end{equation}
```

assuming full column rank.

The joint-neutralized signal is

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{joint}}
=
\mathbf{s}_t^{\mathrm{raw}}
-
\mathbf{B}_t
\widehat{\boldsymbol{\gamma}}_t.
}
\end{equation}
```

Define the projection matrix onto the column space of $`\mathbf{B}_t`$ as

``` math
\begin{equation}
\mathbf{P}_{B,t}
=
\mathbf{B}_t
\left(
\mathbf{B}_t^\top
\mathbf{B}_t
\right)^{-1}
\mathbf{B}_t^\top
\in
\mathbb{R}^{N_t\times N_t},
\end{equation}
```

and the corresponding residual-maker matrix as

``` math
\begin{equation}
\boxed{
\mathbf{M}_{B,t}
=
\mathbf{I}_{N_t}
-
\mathbf{P}_{B,t}.
}
\end{equation}
```

Then

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{joint}}
=
\mathbf{M}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}.
}
\end{equation}
```

The OLS normal equations imply

``` math
\begin{equation}
\boxed{
\mathbf{B}_{1,t}^\top
\mathbf{s}_t^{\mathrm{joint}}
=
\mathbf{0}_{K_1},
}
\end{equation}
```

and

``` math
\begin{equation}
\boxed{
\mathbf{B}_{2,t}^\top
\mathbf{s}_t^{\mathrm{joint}}
=
\mathbf{0}_{K_2}.
}
\end{equation}
```

Hence, the resulting signal is simultaneously orthogonal to every exposure included in both blocks.

##### Naive Sequential Neutralization

A seemingly natural alternative is to neutralize the signal against the first block and then neutralize the resulting residual against the second block.

Define

``` math
\begin{equation}
\mathbf{P}_{1,t}
=
\mathbf{B}_{1,t}
\left(
\mathbf{B}_{1,t}^\top
\mathbf{B}_{1,t}
\right)^{-1}
\mathbf{B}_{1,t}^\top,
\end{equation}
```

and

``` math
\begin{equation}
\boxed{
\mathbf{M}_{1,t}
=
\mathbf{I}_{N_t}
-
\mathbf{P}_{1,t}.
}
\end{equation}
```

The first-stage residual is

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{(1)}
=
\mathbf{M}_{1,t}
\mathbf{s}_t^{\mathrm{raw}}.
}
\end{equation}
```

By construction,

``` math
\begin{equation}
\mathbf{B}_{1,t}^\top
\mathbf{s}_t^{(1)}
=
\mathbf{0}_{K_1}.
\end{equation}
```

Now define similarly

``` math
\begin{equation}
\mathbf{P}_{2,t}
=
\mathbf{B}_{2,t}
\left(
\mathbf{B}_{2,t}^\top
\mathbf{B}_{2,t}
\right)^{-1}
\mathbf{B}_{2,t}^\top,
\end{equation}
```

and

``` math
\begin{equation}
\mathbf{M}_{2,t}
=
\mathbf{I}_{N_t}
-
\mathbf{P}_{2,t}.
\end{equation}
```

A naive second step gives

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{naive}}
=
\mathbf{M}_{2,t}
\mathbf{M}_{1,t}
\mathbf{s}_t^{\mathrm{raw}}.
}
\end{equation}
```

This procedure is generally *not* equivalent to joint neutralization.

##### Why Naive Sequential Neutralization Is Order Dependent

In general,

``` math
\begin{equation}
\boxed{
\mathbf{M}_{2,t}
\mathbf{M}_{1,t}
\neq
\mathbf{M}_{1,t}
\mathbf{M}_{2,t}.
}
\end{equation}
```

Therefore, reversing the order of the two neutralizations generally produces a different final signal.

Moreover, although

``` math
\begin{equation}
\mathbf{B}_{1,t}^\top
\mathbf{s}_t^{(1)}
=
0,
\end{equation}
```

after the second projection one generally has

``` math
\begin{equation}
\boxed{
\mathbf{B}_{1,t}^\top
\mathbf{s}_t^{\mathrm{naive}}
\neq
0.
}
\end{equation}
```

Thus, the second projection can reintroduce exposure to the first block.

The reason is that $`\mathbf{B}_{2,t}`$ may contain components lying in the column space of $`\mathbf{B}_{1,t}`$.

##### Frisch–Waugh–Lovell Theorem

The correct sequential procedure is given by the *Frisch–Waugh–Lovell theorem*.

The theorem states that, in the joint regression

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{raw}}
=
\mathbf{B}_{1,t}
\boldsymbol{\gamma}_{1,t}
+
\mathbf{B}_{2,t}
\boldsymbol{\gamma}_{2,t}
+
\boldsymbol{\varepsilon}_t,
\end{equation}
```

the coefficient on $`\mathbf{B}_{2,t}`$ can be obtained by:

1.  residualizing the dependent variable with respect to $`\mathbf{B}_{1,t}`$;

2.  residualizing every column of $`\mathbf{B}_{2,t}`$ with respect to $`\mathbf{B}_{1,t}`$;

3.  regressing the residualized dependent variable on the residualized second exposure block.

The first residualized object is

``` math
\begin{equation}
\boxed{
\widetilde{\mathbf{s}}_t
=
\mathbf{M}_{1,t}
\mathbf{s}_t^{\mathrm{raw}}
\in
\mathbb{R}^{N_t}.
}
\end{equation}
```

The second exposure block must also be residualized:

``` math
\begin{equation}
\boxed{
\widetilde{\mathbf{B}}_{2,t}
=
\mathbf{M}_{1,t}
\mathbf{B}_{2,t}
\in
\mathbb{R}^{N_t\times K_2}.
}
\end{equation}
```

Thus, the relevant second-stage regression is not

``` math
\begin{equation}
\widetilde{\mathbf{s}}_t
\text{ on }
\mathbf{B}_{2,t},
\end{equation}
```

but rather

``` math
\begin{equation}
\boxed{
\widetilde{\mathbf{s}}_t
=
\widetilde{\mathbf{B}}_{2,t}
\boldsymbol{\gamma}_{2,t}
+
\boldsymbol{\varepsilon}_t.
}
\end{equation}
```

The Frisch–Waugh–Lovell theorem guarantees that

``` math
\begin{equation}
\boxed{
\widehat{\boldsymbol{\gamma}}_{2,t}^{FWL}
=
\widehat{\boldsymbol{\gamma}}_{2,t}^{\mathrm{joint}}.
}
\end{equation}
```

##### FWL-Consistent Sequential Neutralization

Define the projection matrix onto the residualized exposure block

``` math
\begin{equation}
\widetilde{\mathbf{B}}_{2,t}
=
\mathbf{M}_{1,t}
\mathbf{B}_{2,t}
\end{equation}
```

as

``` math
\begin{equation}
\mathbf{P}_{\widetilde{B}_2,t}
=
\widetilde{\mathbf{B}}_{2,t}
\left(
\widetilde{\mathbf{B}}_{2,t}^{\top}
\widetilde{\mathbf{B}}_{2,t}
\right)^{-1}
\widetilde{\mathbf{B}}_{2,t}^{\top}.
\end{equation}
```

The associated residual-maker matrix is

``` math
\begin{equation}
\boxed{
\mathbf{M}_{\widetilde{B}_2,t}
=
\mathbf{I}_{N_t}
-
\mathbf{P}_{\widetilde{B}_2,t}.
}
\end{equation}
```

The correctly sequentially neutralized signal is then

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{FWL}
=
\mathbf{M}_{\widetilde{B}_2,t}
\mathbf{M}_{1,t}
\mathbf{s}_t^{\mathrm{raw}}.
}
\end{equation}
```

The Frisch–Waugh–Lovell theorem implies

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{FWL}
=
\mathbf{s}_t^{\mathrm{joint}}.
}
\end{equation}
```

Equivalently,

``` math
\begin{equation}
\boxed{
\mathbf{M}_{\widetilde{B}_2,t}
\mathbf{M}_{1,t}
\mathbf{s}_t^{\mathrm{raw}}
=
\mathbf{M}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}.
}
\end{equation}
```

Hence, properly constructed sequential neutralization is exactly equivalent to joint neutralization.

##### Geometric Interpretation

The exposure matrix

``` math
\begin{equation}
\mathbf{B}_{2,t}
\end{equation}
```

may contain two components:

``` math
\begin{equation}
\boxed{
\mathbf{B}_{2,t}
=
\mathbf{P}_{1,t}
\mathbf{B}_{2,t}
+
\mathbf{M}_{1,t}
\mathbf{B}_{2,t}.
}
\end{equation}
```

The first component,

``` math
\begin{equation}
\mathbf{P}_{1,t}
\mathbf{B}_{2,t},
\end{equation}
```

already lies in the space spanned by $`\mathbf{B}_{1,t}`$.

The second component,

``` math
\begin{equation}
\boxed{
\mathbf{M}_{1,t}
\mathbf{B}_{2,t},
}
\end{equation}
```

is orthogonal to $`\mathbf{B}_{1,t}`$ and represents the genuinely new directions added by the second exposure block.

Therefore,

``` math
\begin{equation}
\boxed{
\operatorname{Col}
\left(
\begin{bmatrix}
\mathbf{B}_{1,t}
&
\mathbf{B}_{2,t}
\end{bmatrix}
\right)
=
\operatorname{Col}
\left(
\begin{bmatrix}
\mathbf{B}_{1,t}
&
\mathbf{M}_{1,t}\mathbf{B}_{2,t}
\end{bmatrix}
\right),
}
\end{equation}
```

where $`\operatorname{Col}(\cdot)`$ denotes the column space.

This is the geometric intuition behind the Frisch–Waugh–Lovell result.

##### Connection with Gram–Schmidt Orthogonalization

The same procedure can be interpreted as a block version of Gram–Schmidt orthogonalization.

The first exposure block is retained as

``` math
\begin{equation}
\widetilde{\mathbf{B}}_{1,t}
=
\mathbf{B}_{1,t}.
\end{equation}
```

The second block is replaced by its component orthogonal to the first:

``` math
\begin{equation}
\widetilde{\mathbf{B}}_{2,t}
=
\mathbf{M}_{1,t}
\mathbf{B}_{2,t}.
\end{equation}
```

The joint exposure space can then be written as

``` math
\begin{equation}
\operatorname{Col}(\mathbf{B}_t)
=
\operatorname{Col}
\left(
\widetilde{\mathbf{B}}_{1,t},
\widetilde{\mathbf{B}}_{2,t}
\right).
\end{equation}
```

Sequentially removing these orthogonalized exposure blocks therefore removes exactly the same subspace as the original joint regression.

##### Special Case: Orthogonal Exposure Blocks

Suppose the two exposure blocks are already orthogonal:

``` math
\begin{equation}
\boxed{
\mathbf{B}_{1,t}^{\top}
\mathbf{B}_{2,t}
=
\mathbf{0}_{K_1\times K_2}.
}
\end{equation}
```

Then

``` math
\begin{equation}
\mathbf{P}_{1,t}
\mathbf{B}_{2,t}
=
0,
\end{equation}
```

and therefore

``` math
\begin{equation}
\boxed{
\mathbf{M}_{1,t}
\mathbf{B}_{2,t}
=
\mathbf{B}_{2,t}.
}
\end{equation}
```

In this special case, the raw second exposure block is already equal to its FWL-residualized version.

Therefore,

``` math
\begin{equation}
\mathbf{M}_{2,t}
\mathbf{M}_{1,t}
=
\mathbf{M}_{1,t}
\mathbf{M}_{2,t},
\end{equation}
```

and naive sequential neutralization becomes equivalent to joint neutralization.

##### Extension to More Than Two Exposure Blocks

The same logic extends to $`J`$ exposure blocks

``` math
\begin{equation}
\mathbf{B}_{1,t},
\mathbf{B}_{2,t},
\ldots,
\mathbf{B}_{J,t}.
\end{equation}
```

The second block is orthogonalized with respect to the first:

``` math
\begin{equation}
\widetilde{\mathbf{B}}_{2,t}
=
\mathbf{M}_{B_1,t}
\mathbf{B}_{2,t}.
\end{equation}
```

The third block must be orthogonalized with respect to the entire space already removed:

``` math
\begin{equation}
\widetilde{\mathbf{B}}_{3,t}
=
\mathbf{M}_{[B_1,B_2],t}
\mathbf{B}_{3,t}.
\end{equation}
```

More generally,

``` math
\begin{equation}
\boxed{
\widetilde{\mathbf{B}}_{j,t}
=
\mathbf{M}_{[B_1,\ldots,B_{j-1}],t}
\mathbf{B}_{j,t}.
}
\end{equation}
```

Sequential projection onto these orthogonalized exposure blocks reproduces the residual from the joint regression containing all exposures.

##### Practical Implication for Signal Neutralization

It is therefore important to distinguish three procedures:

``` math
\begin{equation}
\boxed{
\begin{aligned}
\text{Joint Regression}
&:
\quad
[\mathbf{B}_{1,t},\mathbf{B}_{2,t}]
\text{ included simultaneously},
\\[0.15cm]
\text{Naive Sequential}
&:
\quad
\mathbf{M}_{2,t}\mathbf{M}_{1,t}
\mathbf{s}_t^{\mathrm{raw}},
\\[0.15cm]
\text{FWL Sequential}
&:
\quad
\mathbf{M}_{\widetilde{B}_2,t}
\mathbf{M}_{1,t}
\mathbf{s}_t^{\mathrm{raw}}.
\end{aligned}
}
\end{equation}
```

In general,

``` math
\begin{equation}
\boxed{
\text{Naive Sequential Neutralization}
\neq
\text{Joint Neutralization},
}
\end{equation}
```

whereas

``` math
\begin{equation}
\boxed{
\text{FWL-Consistent Sequential Neutralization}
=
\text{Joint Neutralization}.
}
\end{equation}
```

For implementation purposes, a single joint regression is usually the simplest and least error-prone approach when all exposures are known simultaneously.

Sequential neutralization is mathematically equivalent only when each new exposure block is first residualized with respect to all exposure blocks that have already been removed.

#### Weighted Neutralization

Ordinary Least Squares gives every security equal importance in the cross-sectional regression.

In some applications, a weighted neutralization may be preferable.

Let

``` math
\begin{equation}
\mathbf{W}_t
=
\operatorname{diag}
\left(
\omega_{1,t},
\ldots,
\omega_{N_t,t}
\right),
\end{equation}
```

with

``` math
\begin{equation}
\omega_{i,t}>0.
\end{equation}
```

The Weighted Least Squares estimator is

``` math
\begin{equation}
\boxed{
\widehat{\boldsymbol{\gamma}}_t^{WLS}
=
\left(
\mathbf{B}_t^\top
\mathbf{W}_t
\mathbf{B}_t
\right)^{-1}
\mathbf{B}_t^\top
\mathbf{W}_t
\mathbf{s}_t^{\mathrm{raw}}.
}
\end{equation}
```

The residualized signal is

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{neutral}}
=
\mathbf{s}_t^{\mathrm{raw}}
-
\mathbf{B}_t
\widehat{\boldsymbol{\gamma}}_t^{WLS}.
}
\end{equation}
```

##### Weighted Orthogonality

WLS residuals satisfy

``` math
\begin{equation}
\boxed{
\mathbf{B}_t^\top
\mathbf{W}_t
\mathbf{s}_t^{\mathrm{neutral}}
=
\mathbf{0}.
}
\end{equation}
```

Notice that this is weighted orthogonality.

In general,

``` math
\begin{equation}
\mathbf{B}_t^\top
\mathbf{s}_t^{\mathrm{neutral}}
\neq
0.
\end{equation}
```

Thus, WLS neutralization changes the definition of neutrality.

##### Possible Weighting Schemes

Possible weights include:

- market capitalization;

- square-root market capitalization;

- liquidity;

- inverse variance;

- portfolio relevance;

- data-quality confidence.

For example,

``` math
\begin{equation}
\omega_{i,t}
=
\sqrt{
\mathrm{MCap}_{i,t}
}
\end{equation}
```

gives greater influence to larger securities without allowing the largest firms to dominate as strongly as full market-cap weighting.

##### Economic Meaning of the Metric

The choice of $`\mathbf{W}_t`$ defines the inner product

``` math
\begin{equation}
\langle
\mathbf{x},
\mathbf{y}
\rangle_W
=
\mathbf{x}^{\top}
\mathbf{W}_t
\mathbf{y}.
\end{equation}
```

Neutralization therefore depends not only on the exposure matrix but also on the metric under which orthogonality is defined.

This distinction becomes important when comparing equal-weight and capitalization-weighted neutralization.

#### Residualized Signal Interpretation

After neutralization,

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{neutral}}
=
\mathbf{M}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}
}
\end{equation}
```

under OLS, or its weighted analogue under WLS.

The residual signal should be interpreted as the component of the original score that is unexplained by the chosen exposure matrix.

##### Not Necessarily Pure Alpha

It is tempting to interpret the residual as “pure alpha.”

This interpretation should be used cautiously.

The residual is orthogonal only to the variables explicitly included in

``` math
\begin{equation}
\mathbf{B}_t.
\end{equation}
```

It may remain exposed to omitted factors.

Thus,

``` math
\begin{equation}
\boxed{
\text{Residualized Signal}
\neq
\text{Guaranteed Pure Alpha}.
}
\end{equation}
```

More precisely,

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{neutral}}
=
\text{component unexplained by the specified controls}.
}
\end{equation}
```

##### Loss of Signal Magnitude

Because part of the raw signal is removed,

``` math
\begin{equation}
\left\|
\mathbf{s}_t^{\mathrm{neutral}}
\right\|_2
\leq
\left\|
\mathbf{s}_t^{\mathrm{raw}}
\right\|_2
\end{equation}
```

under an orthogonal OLS projection.

Indeed,

``` math
\begin{equation}
\left\|
\mathbf{s}_t^{\mathrm{raw}}
\right\|_2^2
=
\left\|
\mathbf{P}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}
\right\|_2^2
+
\left\|
\mathbf{M}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}
\right\|_2^2.
\end{equation}
```

Therefore,

``` math
\begin{equation}
\boxed{
\left\|
\mathbf{s}_t^{\mathrm{neutral}}
\right\|_2^2
=
\left\|
\mathbf{s}_t^{\mathrm{raw}}
\right\|_2^2
-
\left\|
\mathbf{s}_t^{\mathrm{systematic}}
\right\|_2^2.
}
\end{equation}
```

Neutralization mechanically reduces signal variation whenever the raw score is correlated with the controlled exposures.

##### Explained Fraction of the Signal

The cross-sectional regression $`R^2`$ provides a useful diagnostic:

``` math
\begin{equation}
\boxed{
R_t^2
=
1
-
\frac{
\sum_i
\left(
s_{i,t}^{\mathrm{neutral}}
\right)^2
}{
\sum_i
\left(
s_{i,t}^{\mathrm{raw}}
-
\bar{s}_t^{\mathrm{raw}}
\right)^2
}.
}
\end{equation}
```

A high

``` math
\begin{equation}
R_t^2
\end{equation}
```

indicates that a large fraction of the raw signal is explained by the neutralization variables.

If

``` math
\begin{equation}
R_t^2
\approx
1,
\end{equation}
```

the chosen neutralization removes almost all cross-sectional variation in the signal.

This may indicate that the supposed alpha is largely a disguised systematic exposure.

##### Preserving the Raw and Neutralized Signals

The backtesting architecture should preserve both

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{raw}}
\end{equation}
```

and

``` math
\begin{equation}
\mathbf{s}_t^{\mathrm{neutral}}.
\end{equation}
```

This allows direct comparison of:

- predictive performance;

- factor exposures;

- cross-sectional dispersion;

- turnover;

- portfolio performance;

- performance attribution.

The complete signal path is therefore

``` math
\begin{equation}
\boxed{
\begin{aligned}
\mathbf{s}_t^{\mathrm{raw}}
&=
\underbrace{
\mathbf{P}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}
}_{\text{controlled component}}
+
\underbrace{
\mathbf{M}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}
}_{\text{residual component}}
\\[0.15cm]
&\rightarrow
\mathbf{s}_t^{\mathrm{neutral}}
=
\mathbf{M}_{B,t}
\mathbf{s}_t^{\mathrm{raw}}.
\end{aligned}
}
\end{equation}
```

##### Interface with Final Signal Construction

The neutralized score is not necessarily the final signal used for portfolio construction.

Further transformations may include:

- re-standardization;

- combination with other neutralized signals;

- temporal smoothing;

- turnover-aware adjustments;

- confidence weighting.

Thus,

``` math
\begin{equation}
\boxed{
\mathbf{s}_t^{\mathrm{raw}}
\rightarrow
\mathbf{s}_t^{\mathrm{neutral}}
\rightarrow
\mathbf{s}_t^{\mathrm{final}}
\rightarrow
\mathbf{w}_t.
}
\end{equation}
```

The neutralization layer therefore acts as the interface between alpha generation and the construction of the final investable signal.

