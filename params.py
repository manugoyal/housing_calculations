from collections import namedtuple

# These paramaters pertain to current market conditions.
MarketParams = namedtuple(
    'MarketParams',
    [
        'buyers_fee_percentage',
        'sellers_fee_percentage',
        'sellers_fee_base',
        'home_appreciation_rate_annual',
        'marginal_tax_rate_percentage',
        'property_tax_percentage_annual',
        'stock_market_growth_percentage_annual',
        'capital_gains_rate_percentage',
        'home_profit_tax_exclusion_amount',
        'downpayment_discount',
    ])

# These paramaters pertain to a particular loan structure.
LoanParams = namedtuple(
    'LoanParams',
    [
        'downpayment_percentage',
        'maximum_loan_amount',
        'loan_period_months',
        'interest_rate_percentage_annual',
    ])

# These paramaters pertain to a particular class of homes (condo,
# single-family, etc).
HomeClassParams = namedtuple(
    'HomeClassParams',
    [
        'home_insurance_percentage_annual',
        'home_maintenance_annual',
    ])

# These paramaters pertain to a particular home.
HomeParams = namedtuple(
    'HomeParams',
    [
        'address',
        'home_value',
        'hoa_monthly',
        'rental_monthly',
        'finishing_costs',
    ])

