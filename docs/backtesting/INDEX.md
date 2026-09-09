# Backtesting Methodology Index

This file is the routing table for the backtesting methodology.

**Do not read the complete `BACKTESTING_GUIDE.md` during normal development.**

Identify the methodological topic affected by the task and read only the corresponding files below.

The complete original specification remains available at:

`docs/BACKTESTING_GUIDE.md`

---

## Methodology Map

| Topic | Specification |
|---|---|
| Problem Definition and Backtest Conventions | [`01_problem_definition_and_backtest_conventions.md`](./01_problem_definition_and_backtest_conventions.md) |
| Backtesting Biases and Research Integrity | [`02_backtesting_biases_and_research_integrity.md`](./02_backtesting_biases_and_research_integrity.md) |
| Raw Data Acquisition | [`03_raw_data_acquisition.md`](./03_raw_data_acquisition.md) |
| Point-in-Time Data Construction | [`04_point_in_time_data_construction.md`](./04_point_in_time_data_construction.md) |
| Investment Universe Construction | [`05_investment_universe_construction.md`](./05_investment_universe_construction.md) |
| Data Cleaning | [`06_data_cleaning.md`](./06_data_cleaning.md) |
| Outlier Detection and Treatment | [`07_outlier_detection_and_treatment.md`](./07_outlier_detection_and_treatment.md) |
| From Firm-Level Characteristics to Raw Scores | [`08_from_firm_level_characteristics_to_raw_scores.md`](./08_from_firm_level_characteristics_to_raw_scores.md) |
| Model-Based Signal Construction | [`09_model_based_signal_construction.md`](./09_model_based_signal_construction.md) |
| Signal Neutralization | [`10_signal_neutralization.md`](./10_signal_neutralization.md) |
| Final Signal Construction | [`11_final_signal_construction.md`](./11_final_signal_construction.md) |
| Signal Diagnostics | [`12_signal_diagnostics.md`](./12_signal_diagnostics.md) |
| From Signals to Portfolio Weights | [`13_from_signals_to_portfolio_weights.md`](./13_from_signals_to_portfolio_weights.md) |
| Portfolio Risk Model | [`14_portfolio_risk_model.md`](./14_portfolio_risk_model.md) |
| Portfolio Optimization | [`15_portfolio_optimization.md`](./15_portfolio_optimization.md) |
| Portfolio Constraints | [`16_portfolio_constraints.md`](./16_portfolio_constraints.md) |
| Portfolio-Level Risk Scaling | [`17_portfolio_level_risk_scaling.md`](./17_portfolio_level_risk_scaling.md) |
| Backtest Timing and Rebalancing | [`18_backtest_timing_and_rebalancing.md`](./18_backtest_timing_and_rebalancing.md) |
| Portfolio Implementation | [`19_portfolio_implementation.md`](./19_portfolio_implementation.md) |
| Transaction Costs and Market Frictions | [`20_transaction_costs_and_market_frictions.md`](./20_transaction_costs_and_market_frictions.md) |
| Portfolio Accounting and P&L | [`21_portfolio_accounting_and_pandl.md`](./21_portfolio_accounting_and_pandl.md) |
| Backtest Return Construction | [`22_backtest_return_construction.md`](./22_backtest_return_construction.md) |
| Performance Assessment | [`23_performance_assessment.md`](./23_performance_assessment.md) |
| Benchmark and Factor-Adjusted Performance | [`24_benchmark_and_factor_adjusted_performance.md`](./24_benchmark_and_factor_adjusted_performance.md) |
| Performance Attribution | [`25_performance_attribution.md`](./25_performance_attribution.md) |
| Robustness and Sensitivity Analysis | [`26_robustness_and_sensitivity_analysis.md`](./26_robustness_and_sensitivity_analysis.md) |
| Statistical Inference | [`27_statistical_inference.md`](./27_statistical_inference.md) |
| Reproducibility and Production Architecture | [`28_reproducibility_and_production_architecture.md`](./28_reproducibility_and_production_architecture.md) |
| From Research Idea to Investment Strategy | [`29_from_research_idea_to_investment_strategy.md`](./29_from_research_idea_to_investment_strategy.md) |
| Mathematical Notation | [`30_mathematical_notation.md`](./30_mathematical_notation.md) |
| Portfolio and Matrix Algebra | [`31_portfolio_and_matrix_algebra.md`](./31_portfolio_and_matrix_algebra.md) |
| Regression and Neutralization Derivations | [`32_regression_and_neutralization_derivations.md`](./32_regression_and_neutralization_derivations.md) |
| Risk Model Derivations | [`33_risk_model_derivations.md`](./33_risk_model_derivations.md) |
| Portfolio Optimization Derivations | [`34_portfolio_optimization_derivations.md`](./34_portfolio_optimization_derivations.md) |
| Performance Metric Derivations | [`35_performance_metric_derivations.md`](./35_performance_metric_derivations.md) |
| Statistical Tests | [`36_statistical_tests.md`](./36_statistical_tests.md) |
| Implementation Pseudocode | [`37_implementation_pseudocode.md`](./37_implementation_pseudocode.md) |
| Backtesting Checklist | [`38_backtesting_checklist.md`](./38_backtesting_checklist.md) |

---

## Detailed Contents

### [Problem Definition and Backtest Conventions](./01_problem_definition_and_backtest_conventions.md)

- Problem Definition and Backtest Conventions
  - Investment Objective
  - Investment Universe and Asset Class
  - Prediction Target and Investment Horizon
  - Rebalancing Frequency and Holding Period
  - Long-Only and Long–Short Strategies
  - Benchmark Definition
  - Information Sets and Timing Conventions
  - Execution Assumptions
  - Gross Exposure, Net Exposure, and Leverage
  - Risk and Volatility Targets
  - Transaction Cost Assumptions
  - The Complete Backtesting Timeline

### [Backtesting Biases and Research Integrity](./02_backtesting_biases_and_research_integrity.md)

- Backtesting Biases and Research Integrity
  - Look-Ahead Bias
  - Survivorship Bias
  - Selection Bias
  - Data Snooping and Multiple Testing
  - Publication and Restatement Bias
  - Universe Reconstruction Bias
  - Data Leakage
  - Overfitting
  - Unrealistic Trading and Cost Assumptions
  - Research Integrity and Backtest Governance

### [Raw Data Acquisition](./03_raw_data_acquisition.md)

- Raw Data Acquisition
  - Market Data
  - Fundamental Data
  - Analyst Estimates
  - Alternative Data
  - Risk Factors and Market Variables
  - Industry and Country Classifications
  - Corporate Actions
  - Liquidity, Borrowing, and Transaction Cost Data
  - Raw Data Architecture

### [Point-in-Time Data Construction](./04_point_in_time_data_construction.md)

- Point-in-Time Data Construction
  - Observation Dates, Publication Dates, and Effective Dates
  - Reporting Lags
  - Restatements
  - As-Of Joins
  - Historical Universe Membership
  - Delisted Securities
  - Preventing Look-Ahead Bias

### [Investment Universe Construction](./05_investment_universe_construction.md)

- Investment Universe Construction
  - Geographical and Exchange Filters
  - Security Type Filters
  - Market Capitalization Filters
  - Liquidity Filters
  - Price Filters
  - Listing History Requirements
  - Data Availability Requirements
  - Shortability Constraints
  - Dynamic Universe Construction

### [Data Cleaning](./06_data_cleaning.md)

- Data Cleaning
  - Duplicate Observations
  - Missing Values
  - Stale Prices
  - Invalid Observations
  - Corporate Action Adjustments
  - Currency Conversion
  - Frequency Alignment
  - Trading Calendar Alignment
  - Cleaning Pipeline and Validation Invariants

### [Outlier Detection and Treatment](./07_outlier_detection_and_treatment.md)

- Outlier Detection and Treatment
  - Definition of an Outlier
  - Cross-Sectional vs. Time-Series Outliers
  - Quantile-Based Winsorization
  - MAD-Based Methods
  - Robust Z-Scores
  - Truncation, Winsorization, and Observation Removal
  - Economic Sanity Checks
  - Point-in-Time Outlier Treatment
  - Outlier-Treatment Diagnostics
  - Output of the Outlier Layer

### [From Firm-Level Characteristics to Raw Scores](./08_from_firm_level_characteristics_to_raw_scores.md)

- From Firm-Level Characteristics to Raw Scores
  - Definition of a Firm-Level Characteristic
  - Cross-Sectional vs. Time-Series Transformations
  - Z-Score Transformation
  - Robust Z-Score Transformation
  - Rank Transformation
  - Percentile Transformation
  - Quantile and Decile Scores
  - Gaussian Rank Transformation
  - Direction and Sign Convention
  - Score Clipping and Bounding
  - Combining Multiple Characteristics
  - Final Raw Score

### [Model-Based Signal Construction](./09_model_based_signal_construction.md)

- Model-Based Signal Construction
  - General Predictive Framework
  - Target Variable Definition
  - Input Characteristics and Design Matrix
  - Econometric Models
  - Machine Learning Models
  - Deep Learning Models
  - Regression, Classification, and Ranking Objectives
  - Training, Validation, and Test Samples
  - Expanding and Rolling Estimation Windows
  - Walk-Forward Validation
  - Embargo and Leakage Prevention
  - Hyperparameter Selection
  - Model Refitting
  - Prediction-to-Score Transformation
  - Final Model-Based Raw Score

### [Signal Neutralization](./10_signal_neutralization.md)

- Signal Neutralization
  - Motivation for Neutralization
  - General Exposure Matrix
  - Cross-Sectional Regression Framework
  - Beta Neutralization
  - Industry and Sector Neutralization
  - Country Neutralization
  - Size Neutralization
  - Volatility Neutralization
  - Momentum and Style Factor Neutralization
  - Joint vs. Sequential Neutralization
  - Weighted Neutralization
  - Residualized Signal Interpretation

### [Final Signal Construction](./11_final_signal_construction.md)

- Final Signal Construction
  - Post-Neutralization Standardization
  - Multiple-Signal Combination
  - Signal Smoothing
  - Turnover-Aware Signal Adjustments
  - Confidence Weighting
  - Final Investable Signal

### [Signal Diagnostics](./12_signal_diagnostics.md)

- Signal Diagnostics
  - Cross-Sectional Signal Distribution
  - Information Coefficient
  - Rank Information Coefficient
  - Information Coefficient Information Ratio
  - Quantile and Decile Returns
  - Long–Short Spread
  - Monotonicity
  - Hit Rate
  - Signal Persistence and Autocorrelation
  - Signal Turnover
  - Factor Exposure Diagnostics
  - Cross-Sectional and Temporal Stability

### [From Signals to Portfolio Weights](./13_from_signals_to_portfolio_weights.md)

- From Signals to Portfolio Weights
  - Signal-to-Weight Mapping Functions
  - Direct Pure Alpha Construction and Risk Scaling
  - Equal-Weighted Quantile Portfolios
  - Top/Bottom $`N`$ Portfolios
  - Rank-Weighted Portfolios
  - Linear Signal Mapping
  - Nonlinear Signal Mapping
  - Threshold-Based Mapping
  - Conviction-Weighted Portfolios

### [Portfolio Risk Model](./14_portfolio_risk_model.md)

- Portfolio Risk Model
  - Portfolio Variance and Covariance
  - Historical Covariance Estimation
  - Shrinkage Estimators
  - Factor Risk Models
  - Systematic and Specific Risk
  - Beta Estimation
  - Factor Exposure Estimation
  - Volatility Forecasting

### [Portfolio Optimization](./15_portfolio_optimization.md)

- Portfolio Optimization
  - General Optimization Framework
  - Expected Return Maximization
  - Mean–Variance Optimization
  - Risk-Adjusted Optimization
  - Transaction-Cost-Aware Optimization
  - Turnover-Aware Optimization
  - Regularization of Portfolio Weights

### [Portfolio Constraints](./16_portfolio_constraints.md)

- Portfolio Constraints
  - Gross Exposure
  - Net Exposure
  - Long and Short Budgets
  - Leverage Constraints
  - Position Limits
  - Beta Neutrality
  - Industry and Sector Neutrality
  - Country Neutrality
  - Style Factor Neutrality
  - Tracking Error Constraints
  - Turnover Constraints
  - Liquidity and ADV Constraints
  - Short Availability Constraints

### [Portfolio-Level Risk Scaling](./17_portfolio_level_risk_scaling.md)

- Portfolio-Level Risk Scaling
  - Portfolio Direction and Portfolio Scale
  - Volatility Targeting
  - Leverage Caps and Scaling Limits
  - Interaction with Portfolio Constraints
  - Final Target Weights

### [Backtest Timing and Rebalancing](./18_backtest_timing_and_rebalancing.md)

- Backtest Timing and Rebalancing
  - Decision, Execution, and Holding Timeline
  - Execution Lags
  - Rebalancing Schedule
  - Holding Period
  - Timing Integrity and Look-Ahead Prevention

### [Portfolio Implementation](./19_portfolio_implementation.md)

- Portfolio Implementation
  - Target vs. Current Portfolio
  - Portfolio Drift
  - Required Trades
  - Order Generation
  - Execution Price Assumptions
  - Partial Execution and Partial Rebalancing
  - Position Rounding
  - Implemented Portfolio

### [Transaction Costs and Market Frictions](./20_transaction_costs_and_market_frictions.md)

- Transaction Costs and Market Frictions
  - General Transaction-Cost Model
  - Commissions and Explicit Fees
  - Bid–Ask Spread
  - Slippage
  - Market Impact
  - Short Borrowing Costs
  - Financing Costs
  - Liquidity and Capacity Effects

### [Portfolio Accounting and P&L](./21_portfolio_accounting_and_pandl.md)

- Portfolio Accounting and P&L
  - Portfolio State Representation
  - Positions and Market Values
  - Cash Account
  - Mark-to-Market Valuation
  - Daily Profit and Loss
  - NAV Evolution

### [Backtest Return Construction](./22_backtest_return_construction.md)

- Backtest Return Construction
  - Gross Portfolio Return
  - Trading-Cost Deduction
  - Financing and Borrowing-Cost Deduction
  - Net Portfolio Return
  - Cumulative Performance

### [Performance Assessment](./23_performance_assessment.md)

- Performance Assessment
  - Annualized Return
  - Annualized Volatility
  - Sharpe Ratio
  - Sortino Ratio
  - Maximum Drawdown
  - Calmar Ratio
  - Hit Ratio
  - Skewness and Kurtosis
  - Value at Risk
  - Expected Shortfall
  - Turnover
  - Capacity
  - Gross vs. Net Performance

### [Benchmark and Factor-Adjusted Performance](./24_benchmark_and_factor_adjusted_performance.md)

- Benchmark and Factor-Adjusted Performance
  - Benchmark Excess Returns
  - Tracking Error
  - Information Ratio
  - CAPM Alpha and Beta
  - Multifactor Regression
  - Style Factor Exposures
  - Factor-Adjusted Alpha

### [Performance Attribution](./25_performance_attribution.md)

- Performance Attribution
  - Attribution Framework
  - Long vs. Short Attribution
  - Security-Level Attribution
  - Sector and Industry Attribution
  - Country Attribution
  - Factor Attribution
  - Signal Attribution
  - Model Attribution
  - Beta vs. Pure Alpha
  - Gross Alpha vs. Implementation Costs
  - Transaction Cost Attribution
  - Financing and Borrowing Cost Attribution

### [Robustness and Sensitivity Analysis](./26_robustness_and_sensitivity_analysis.md)

- Robustness and Sensitivity Analysis
  - Subperiod Analysis
  - Market Regime Analysis
  - Alternative Investment Universes
  - Alternative Rebalancing Frequencies
  - Alternative Holding Periods
  - Signal Lag Sensitivity
  - Outlier Treatment Sensitivity
  - Neutralization Sensitivity
  - Portfolio Mapping Sensitivity
  - Transaction Cost Sensitivity
  - Hyperparameter and Parameter Perturbation
  - Placebo and Randomization Tests

### [Statistical Inference](./27_statistical_inference.md)

- Statistical Inference
  - Mean Return Tests and $`t`$-Statistics
  - Serial Dependence and Heteroskedasticity
  - Newey–West Standard Errors
  - Bootstrap Methods
  - Multiple Hypothesis Testing
  - Data Snooping Adjustments
  - Deflated Sharpe Ratio
  - Probability of Backtest Overfitting

### [Reproducibility and Production Architecture](./28_reproducibility_and_production_architecture.md)

- Reproducibility and Production Architecture
  - Research vs. Production Environments
  - Configuration Management
  - Code Versioning
  - Data Versioning
  - Model Versioning
  - Experiment Tracking
  - Random Seeds
  - Logging
  - Unit Tests
  - Integration Tests
  - Reproducible Environments
  - Backtest–Live Trading Parity

### [From Research Idea to Investment Strategy](./29_from_research_idea_to_investment_strategy.md)

- From Research Idea to Investment Strategy
  - Summary of the Complete Pipeline
  - Interactions Between Signal, Risk, and Portfolio Construction
  - Research and Backtest Validation Checklist
  - From Backtesting to Live Implementation

### [Mathematical Notation](./30_mathematical_notation.md)

- Mathematical Notation

### [Portfolio and Matrix Algebra](./31_portfolio_and_matrix_algebra.md)

- Portfolio and Matrix Algebra

### [Regression and Neutralization Derivations](./32_regression_and_neutralization_derivations.md)

- Regression and Neutralization Derivations

### [Risk Model Derivations](./33_risk_model_derivations.md)

- Risk Model Derivations

### [Portfolio Optimization Derivations](./34_portfolio_optimization_derivations.md)

- Portfolio Optimization Derivations

### [Performance Metric Derivations](./35_performance_metric_derivations.md)

- Performance Metric Derivations

### [Statistical Tests](./36_statistical_tests.md)

- Statistical Tests

### [Implementation Pseudocode](./37_implementation_pseudocode.md)

- Implementation Pseudocode

### [Backtesting Checklist](./38_backtesting_checklist.md)

- Backtesting Checklist

