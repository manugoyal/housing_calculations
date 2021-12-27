from params import *

market_params = MarketParams(
    buyers_fee_percentage=1,
    sellers_fee_percentage=6,
    sellers_fee_base=3000,
    home_appreciation_rate_annual=3,
    marginal_tax_rate_percentage=32,
    property_tax_percentage_annual=1.25,
    stock_market_growth_percentage_annual=5,
    capital_gains_rate_percentage=15,
    home_profit_tax_exclusion_amount=250000,
    downpayment_discount=0)

loan_params_30 = LoanParams(
    downpayment_percentage=20,
    maximum_loan_amount=822000,
    loan_period_months=360,
    interest_rate_percentage_annual=3.125)

jumbo_loan_params_30 = LoanParams(
    downpayment_percentage=25,
    maximum_loan_amount=float('inf'),
    loan_period_months=360,
    interest_rate_percentage_annual=2.99)

loan_params_15 = LoanParams(
    downpayment_percentage=20,
    maximum_loan_amount=822000,
    loan_period_months=180,
    interest_rate_percentage_annual=2.75)

jumbo_loan_params_15 = LoanParams(
    downpayment_percentage=25,
    maximum_loan_amount=float('inf'),
    loan_period_months=180,
    interest_rate_percentage_annual=2.75)

condo_params = HomeClassParams(
    home_insurance_percentage_annual=0.02,
    home_maintenance_annual=2500)

sfh_params = HomeClassParams(
    home_insurance_percentage_annual=0.4,
    home_maintenance_annual=5000)

mira_params = HomeParams(
    address='280 Spear St Unit 3402',
    home_value=1265000,
    hoa_monthly=1115.79,
    rental_monthly=4000,
    finishing_costs=30000)

mira_loan_params = LoanParams(
    downpayment_percentage=25,
    maximum_loan_amount=float('inf'),
    loan_period_months=360,
    interest_rate_percentage_annual=2.95)
