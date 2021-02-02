# Pro tip: create you own config.py
# by using this as a template

# Don't put credentials in config files!
# Set them as environment variables in your shell

import os

''' ========= LOGIN =========== '''
username = os.environ["email_shell_variable"]
password = os.environ["password_shell_variable"]

''' ======== BUY/SELL ========= '''
buy_amount          = 10    # Dollar amount to buy when a good stock is found.
minimum_stock_price = 1     # The lowest stock price you're willing to buy.
sell_profit_margin  = 2     # Profit percentage to reach before selling a stock.
dividends_bonus     = 2     # Multiplier for stocks with an upcoming dividend (ignored when <=1).

''' ========= TRADING ========= '''
scan_interval   = 30        # In minutes
open_time       = '10:00am'
close_time      = '5:00pm'
days_closed     = ['saturday', 'sunday']
