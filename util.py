# Utilities for estimating costs of buying vs renting a home. The bottom-line
# function is at the bottom.

from collections import namedtuple
import itertools

MortgagePayment = namedtuple(
    'MortgagePayment',
    [
        'principal',
        'interest',
    ])

def get_loan_amount(loan_params, home_params):
    return (1 - loan_params.downpayment_percentage/100) * home_params.home_value

def get_mortgage_payments(market_params, loan_params, home_params):
    # Generator for mortgage payments. After the mortgage is paid off, returns
    # 0-value payments.

    P = get_loan_amount(loan_params, home_params)
    r = loan_params.interest_rate_percentage_annual/100/12
    n = loan_params.loan_period_months

    fixed_amount = P*r*(1 - 1/(1-(1+r)**n))
    mps = []
    for i in range(n):
        interest = r * (P - sum(mp.principal for mp in mps))
        principal = fixed_amount - interest
        mps.append(MortgagePayment(principal=principal, interest=interest))
        yield mps[-1]
    while True:
        yield MortgagePayment(0, 0)

def appreciation_annual_to_monthly(annual_percentage):
    # Convert an annual appreciation percentage to a monthly percentage.

    annual_multiplier = 1 + annual_percentage/100
    return (annual_multiplier**(1/12) - 1) * 100

def get_initial_payment(market_params, loan_params, home_params):
    # Compute the initial payment for a particular home.

    downpayment_amount = loan_params.downpayment_percentage/100 * home_params.home_value
    buyers_fee = market_params.buyers_fee_percentage/100 * home_params.home_value
    return downpayment_amount + buyers_fee

def tax_adjusted_nonmortgage_monthly_payment(
    market_params, loan_params, home_class_params, home_params):
    # Compute the non-mortage-related monthly payments for a home. These will
    # persist beyond the lifetime of the mortgage. Adjusts for tax-deductable
    # portions of the payment.

    property_tax = (market_params.property_tax_percentage_annual/100/12 *
                    home_params.home_value)
    home_insurance = (home_class_params.home_insurance_percentage_annual/100/12 *
                      home_params.home_value)
    maintenance = home_class_params.home_maintenance_annual/12
    hoa = home_params.hoa_monthly
    return (home_insurance + maintenance + hoa +
            property_tax * (1 - market_params.marginal_tax_rate_percentage/100))

def tax_adjusted_monthly_payments(
    market_params, loan_params, home_class_params, home_params):
    # Generator for the total monthly payment over time (mortgage +
    # non-mortgage payments). Adjusts for tax-deductable portions of the
    # payment.

    mortgage_payments = get_mortgage_payments(market_params, loan_params, home_params)
    for mortgage_payment in mortgage_payments:
        yield (
            mortgage_payment.principal +
            tax_adjusted_nonmortgage_monthly_payment(
                market_params, loan_params, home_class_params, home_params) +
            mortgage_payment.interest *
                (1 - market_params.marginal_tax_rate_percentage/100))

def get_total_home_payment(
    market_params, loan_params, home_class_params, home_params, sell_month):
    # Compute the total payment made for the home before sale, if the home is
    # sold on |sell_month|.

    initial_payment = get_initial_payment(market_params, loan_params, home_params)
    monthly_payments = tax_adjusted_monthly_payments(
        market_params, loan_params, home_class_params, home_params)
    mortgage_payments = get_mortgage_payments(market_params, loan_params, home_params)
    remaining_principal = (
        get_loan_amount(loan_params, home_params) -
        sum(mp.principal for mp in itertools.islice(mortgage_payments, sell_month)))
    return (initial_payment +   
            sum(mp for mp in itertools.islice(monthly_payments, sell_month)) +
            remaining_principal)

def get_home_sale_price(market_params, home_params, sell_month):
    # Compute the sale price of the home if sold on |sell_month|.

    assert sell_month >= 0
    monthly_growth_factor = (
        1 + appreciation_annual_to_monthly(
                market_params.home_appreciation_rate_annual)/100)
    return home_params.home_value * monthly_growth_factor**sell_month

def get_sellers_fee(market_params, home_params, sell_month):
    # Compute the additional price of the sale.

    return (get_home_sale_price(market_params, home_params, sell_month) *
                market_params.sellers_fee_percentage/100 +
            market_params.sellers_fee_base)

def net_profit_home_scenario(market_params, loan_params, home_class_params,
                             home_params, sell_month):
    # Compute the net profit for buying a home, if it is sold on |sell_month|.
    # This is computed by deducting the total home payment and sellers fee from
    # the total home sale price.

    total_home_payment = get_total_home_payment(
        market_params, loan_params, home_class_params, home_params, sell_month)
    sellers_fee = get_sellers_fee(market_params, home_params, sell_month)
    home_sale_price = get_home_sale_price(market_params, home_params, sell_month)
    home_profit = ((home_sale_price - total_home_payment) *
                   (1 - market_params.capital_gains_rate_percentage/100))
    return home_profit - sellers_fee

def get_monthly_rental_payments(market_params, home_params):
    # Return a generator for the monthly rental payment. Assume the rental
    # price appreciates by the home appreciation rate, but only once a year.
    rental_appreciation_factor = (
        1 + market_params.home_appreciation_rate_annual/100)
    rent = home_params.rental_monthly
    for i in itertools.count():
        if i > 0 and i % 12 == 0:
            rent *= rental_appreciation_factor
        yield rent

def net_profit_comparative_rental_scenario(
    market_params, loan_params, home_class_params, home_params, sell_month):
    # Compute the net profit for renting for |sell_month| months.
    #
    # Assume we put the home's initial payment into the stock market. Each
    # month, we put the difference between the monthly rental payment and the
    # monthly home payment into the stock market. The rental payment goes down
    # the drain.
    #
    # At sell_month, we cash out entirely from the stock market, so our net is
    # our stock-profit (taxed at capital gains) minus the amount spent on rent.
    stock_market_deposits = []
    total_rental = 0
    monthly_home_payments = tax_adjusted_monthly_payments(
        market_params, loan_params, home_class_params, home_params)
    monthly_rental_payments = get_monthly_rental_payments(
        market_params, home_params)
    for i in range(sell_month):
        stock_market_deposit = 0
        if i == 0:
            stock_market_deposit += get_initial_payment(
                market_params, loan_params, home_params)
        monthly_home_payment = next(monthly_home_payments)
        monthly_rental_payment = next(monthly_rental_payments)
        total_rental += monthly_rental_payment
        stock_market_deposit += monthly_home_payment - monthly_rental_payment
        stock_market_deposits.append(stock_market_deposit)

    stock_market_growth_factor_monthly = (
        1 + appreciation_annual_to_monthly(
                market_params.stock_market_growth_percentage_annual)/100)
    stock_market_revenue = sum(
        deposit * stock_market_growth_factor_monthly**(sell_month-i)
        for i, deposit in enumerate(stock_market_deposits))
    stock_market_profit = (
        (stock_market_revenue - sum(stock_market_deposits)) *
        (1 - market_params.capital_gains_rate_percentage/100))
    return stock_market_profit - total_rental

def home_vs_rental(
    market_params, loan_params, home_class_params, home_params, sell_month):
    # Returns the difference between the net profit in the home-buying scenario
    # and the net profit in the comparative rental scenario. This should be the
    # expected profit for buying vs renting a particular property.
    return (
        net_profit_home_scenario(
            market_params, loan_params, home_class_params, home_params,
            sell_month) -
        net_profit_comparative_rental_scenario(
            market_params, loan_params, home_class_params, home_params,
            sell_month))
