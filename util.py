# Utilities for estimating costs of buying vs renting a home. The bottom-line
# function is at the bottom.

import itertools
import params

from collections import namedtuple

MortgagePayment = namedtuple(
    'MortgagePayment',
    [
        'principal',
        'interest',
    ])

def get_loan_amount(loan_params, home_params):
    return min(
        loan_params.maximum_loan_amount,
        (1 - loan_params.downpayment_percentage/100) * (home_params.home_value + home_params.finishing_costs))

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

    downpayment_amount = max(
        0,
        (home_params.home_value + home_params.finishing_costs) - get_loan_amount(loan_params, home_params) - market_params.downpayment_discount)
    buyers_fee = market_params.buyers_fee_percentage/100 * home_params.home_value
    return downpayment_amount + buyers_fee

def tax_adjusted_nonmortgage_monthly_payment(
    market_params, loan_params, home_class_params, home_params):
    # Compute the non-mortage-related monthly payments for a home. These will
    # persist beyond the lifetime of the mortgage. Adjusts for tax-deductable
    # portions of the payment.

    property_tax = (market_params.property_tax_percentage_annual/100/12 *
                    home_params.home_value)
    tax_deductable_property_tax = min(property_tax, 10000/12)
    remaining_property_tax = property_tax - tax_deductable_property_tax
    home_insurance = (home_class_params.home_insurance_percentage_annual/100/12 *
                      home_params.home_value)
    maintenance = home_class_params.home_maintenance_annual/12
    hoa = home_params.hoa_monthly
    return (home_insurance + maintenance + hoa + remaining_property_tax +
            tax_deductable_property_tax *
                (1 - market_params.marginal_tax_rate_percentage/100))

def unadjusted_nonmortgage_monthly_payment(
    market_params, loan_params, home_class_params, home_params):
    property_tax = (market_params.property_tax_percentage_annual/100/12 *
                    home_params.home_value)
    home_insurance = (home_class_params.home_insurance_percentage_annual/100/12 *
                      home_params.home_value)
    maintenance = home_class_params.home_maintenance_annual/12
    hoa = home_params.hoa_monthly
    return property_tax + home_insurance + maintenance + hoa

def tax_adjusted_mortgage_monthly_payments(
    market_params, loan_params, home_class_params, home_params):
    # Generator for the total monthly mortgage payment over time. Adjusts for
    # tax-deductable portions of the payment.

    mortgage_payments = get_mortgage_payments(market_params, loan_params, home_params)
    indebtedness = get_loan_amount(loan_params, home_params)
    for mortgage_payment in mortgage_payments:
        # Your interest payment is tax deductable up to 750000 of total
        # indebtedness. So we compute the fraction of current indebtedness that
        # 750000 comprises, and split your interest along that fraction.
        if indebtedness > 0:
            interest_deductible_fraction = min(750000/indebtedness, 1.0)
        else:
            interest_deductible_fraction = 1.0
        tax_deductable_interest = \
            mortgage_payment.interest * interest_deductible_fraction
        remaining_interest = mortgage_payment.interest - tax_deductable_interest
        yield (
            mortgage_payment.principal +
            tax_deductable_interest *
                (1 - market_params.marginal_tax_rate_percentage/100) +
            remaining_interest)
        indebtedness = max(0, indebtedness - mortgage_payment.principal)

def tax_adjusted_monthly_payments(
    market_params, loan_params, home_class_params, home_params):

    mortgage_monthly_payments = tax_adjusted_monthly_payments(
        market_params, loan_params, home_class_params, home_params)
    nonmortgage_amount = tax_adjusted_nonmortgage_monthly_payment(
        market_params, loan_params, home_class_params, home_params)
    for mortgage_amount in mortgage_monthly_payments:
        yield mortgage_amount + nonmortgage_amount

def unadjusted_monthly_payments(
    market_params, loan_params, home_class_params, home_params):
    mortgage_payments = get_mortgage_payments(market_params, loan_params, home_params)
    for mortgage_payment in mortgage_payments:
        yield (
            mortgage_payment.principal + mortgage_payment.interest +
            unadjusted_nonmortgage_monthly_payment(
                market_params, loan_params, home_class_params, home_params))

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
    # This is computed by computing the profit on the home investment (home
    # sale price - total home payment) and then subtracting the sellers fee.

    total_home_payment = get_total_home_payment(
        market_params, loan_params, home_class_params, home_params, sell_month)
    sellers_fee = get_sellers_fee(market_params, home_params, sell_month)
    home_sale_price = get_home_sale_price(market_params, home_params, sell_month)
    home_profit = (home_sale_price - total_home_payment)

    # We can keep up to |home_profit_tax_exclusion_amount| of the profit
    # without taxation. The rest gets taxed at capital gains.
    untaxed_home_profit = min(
        home_profit, market_params.home_profit_tax_exclusion_amount)
    taxed_home_profit = home_profit - untaxed_home_profit
    adjusted_home_profit = (
        untaxed_home_profit +
        taxed_home_profit * (1 - market_params.capital_gains_rate_percentage/100))
    return adjusted_home_profit - sellers_fee

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

def find_max_hoa(
    market_params, loan_params, home_class_params, sell_month,
    home_value, rental_monthly, min_hoa=0, max_hoa=3000):
    # Finds the maximum HOA payment that would result in a net profit against
    # renting at |rental_monthly|, for a fixed home value |home_value|. Returns
    # None if no profitable HOA is possible.
    assert min_hoa <= max_hoa

    hp = params.HomeParams(
        address='',
        home_value=home_value,
        hoa_monthly=0,
        rental_monthly=rental_monthly)

    if home_vs_rental(market_params, loan_params, home_class_params,
                      hp._replace(hoa_monthly=min_hoa), sell_month) < 0:
      return None

    start = min_hoa
    length = max_hoa - min_hoa + 1

    while length > 1:
        step = int(length/2)
        cur = start + step
        if home_vs_rental(market_params, loan_params, home_class_params,
                          hp._replace(hoa_monthly=cur), sell_month) >= 0:
            # cur is profitable. Pick the right side.
            start = cur
            length -= step
        else:
            # cur is not profitable. Pick the left side.
            length = step
    return start
