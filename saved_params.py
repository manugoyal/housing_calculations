from params import *

market_params = MarketParams(
    buyers_fee_percentage=1,
    sellers_fee_percentage=7,
    sellers_fee_base=3000,
    home_appreciation_rate_annual=3,
    marginal_tax_rate_percentage=32,
    property_tax_percentage_annual=1,
    stock_market_growth_percentage_annual=5,
    capital_gains_rate_percentage=15)

loan_params_30 = LoanParams(
    downpayment_percentage=20,
    loan_period_months=360,
    interest_rate_percentage_annual=2.99)

loan_params_15 = LoanParams(
    downpayment_percentage=20,
    loan_period_months=180,
    interest_rate_percentage_annual=2.75)

condo_params = HomeClassParams(
    home_insurance_percentage_annual=0.1,
    home_maintenance_annual=5000)

home_params_201_lumina = HomeParams(
    address='201 Folsom St Lumina',
    home_value=1098000,
    hoa_monthly=1125,
    rental_monthly=3499)

home_params_346_1st = HomeParams(
    address='346 1st St',
    home_value=880000,
    hoa_monthly=575,
    rental_monthly=3200)

home_params_423_vermont = HomeParams(
    address='426 Vermont',
    home_value=1295000,
    hoa_monthly=535,
    rental_monthly=7000)

home_params_280_spear_3u = HomeParams(
    address='280 Spear St Apt 3U',
    home_value=795000,
    hoa_monthly=1078,
    rental_monthly=3000)
