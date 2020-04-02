import json
import sharesies
import yfinance
import numpy as np
from time import sleep
from datetime import datetime, timedelta


def load_config():
    with open('config.json', 'r') as handle:
        return json.loads(handle.read())


def get_nz_time():
    return datetime.utcnow() + timedelta(hours=12)


def is_trading_time():
    now = get_nz_time()

    if now.weekday() < 5:
        if now.hour >= 11 and now.hour <= 15:
            return True
    
    return False


def log(message, error=False):
    # format the message
    now = get_nz_time()
    timestamp = f'[{now.hour+1}:{now.minute}] [{now.day}/{now.month}/{now.year}]'
    line = f'{timestamp} {message}'

    # console and log
    print(line)
    with open('logs.txt', 'a') as handle:
        handle.write(line + '\n')
    
    # stop the program?
    if error:
        exit(-1)


def vwap(df):
    q = df.Volume.values
    p = (df.Close.values + df.High.values + df.Low.values) / 3

    if not q.any():
        return df.assign(vwap=p)

    return df.assign(vwap=(p * q).cumsum() / q.cumsum())


def should_buy(market_price, history, margin_percent):
    try:
        # calculate vwap
        history = history.groupby(history.index.date, group_keys=False)
        history = history.apply(vwap)

        # calculate direction
        moves = np.gradient(history['vwap'])
        median = np.median(moves)
        average = np.average(moves)

        # calculate margin price
        margin_price = history['vwap'][-1]
        margin_price -= (margin_price * margin_percent)

        # agree if going up and below margin
        if median > 0 and average > 0 and market_price <= margin_price:
            return True
    except:
        pass

    return False


def should_sell(original_price, market_price, margin_percent):
    percent_change = (market_price - original_price) / original_price
    return percent_change >= margin_percent


def scan_market(client, buy_amount):
    profile = client.get_profile()
    balance = float(profile['user']['wallet_balance'])

    # todo: look to sell stocks
    portfolio = profile['portfolio']
    for company in portfolio:
        pass

    # find new stocks to buy
    companies = client.get_companies()
    for company in companies:
        if balance < buy_amount:
            break

        # todo: don't double invest

        symbol = company['code'] + '.NZ'
        price = float(company['market_price'])

        stock = yfinance.Ticker(symbol)
        history = stock.history(period='5d', interval='15m')

        if should_buy(price, history, 0.004):
            log(f'Buying ${buy_amount} of {symbol}')
            client.buy(company, buy_amount)
            balance -= buy_amount


if __name__ == '__main__':
    # config
    config = load_config()
    log('Loaded config')

    # init client
    client = sharesies.Client()
    if client.login(config['Username'], config['Password']):
        log('Connected to Sharesies')
    else:
        log('Failed to login', error=True)
    
    # trade loop
    while True:
        if is_trading_time():
            log('Scanning market')
            scan_market(client, config["BuyAmount"])

        sleep(30 * 60)
