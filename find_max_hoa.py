from saved_params import (
    market_params, loan_params_30, condo_params)
from util import find_max_hoa


if __name__ == '__main__':
    for sell_month in [60, 120]:
        print('Sell month = %s' % sell_month)
        for rental_monthly in [2000, 2500, 3000]:
            print('\tRental monthly = %s' % rental_monthly)
            for home_value in range(800000, 1100000 + 1, 100000):
                max_hoa = find_max_hoa(market_params, loan_params_30, condo_params, sell_month, home_value, rental_monthly)
                print('\t\tHome value = %s, Max HOA = %s' % (home_value, max_hoa))
