import sharesies
import yfinance
from time import sleep
from tqdm import tqdm
from stockwatch import Market, util
import config


def perform_selling(client, portfolio, companies, dividends):
    ''' Look to sell stocks from the portfolio '''

    for company in portfolio:
        fund_id = company['fund_id']

        contribution = float(company['contribution'])
        current_value = float(company['value'])

        # does company give dividends?
        if fund_id in dividends:
            util.log(f'Not selling {fund_id}:{code} due to dividends')
            continue

        # sell if we're making a profit
        if Market.should_sell(contribution, current_value):
            code = util.get_code_from_id(fund_id, companies)
            util.log(f'Selling ${current_value} of {code}')
            client.sell(company, float(company['shares']))


def perform_buying(client, investments, companies, balance):
    ''' Find new stocks to buy from the companies '''

    for company in companies:

        # don't double invest
        if company['id'] in investments:
            continue

        # ignore penny stocks
        price = float(company['market_price'])
        if price < config.minimum_stock_price:
            continue

        symbol = company['code'] + '.NZ'
        stock = yfinance.Ticker(symbol)
        history = stock.history(period='1mo', interval='15m')

        # buy if it is a bargain
        if Market.should_buy(price, history, 0.4):

            buy_amount = config.buy_amount

            # value shares more as dividends are upcoming
            dividends_soon = util.dividends_soon(company['dividends'])
            if dividends_soon and config.dividends_bonus > 1:
                buy_amount *= config.dividends_bonus

            # check we have balance
            if balance < buy_amount:
                util.log(f'Want to buy {symbol} but not enough $$$')
                break

            # submit the buy order
            util.log(f'Buying ${buy_amount} of {symbol}')
            client.buy(company, buy_amount)
            balance -= buy_amount


def scan_market(client):
    ''' Scan market to make informed buy/sell decisions '''

    profile = client.get_profile()

    # gather the information
    balance = float(profile['user']['wallet_balance'])
    portfolio = profile['portfolio']
    dividends = profile['upcoming_dividends']

    investments = util.get_fund_ids(portfolio)
    companies = client.get_companies()

    # it's show time
    perform_selling(client, portfolio, companies, dividends)
    perform_buying(client, investments, companies, balance)


if __name__ == '__main__':

    # config
    util.log('Loaded config')

    # init client
    client = sharesies.Client()
    if client.login(config.username, config.password):
        util.log('Connected to Sharesies')
    else:
        util.log('Failed to login', error=True)

    # trade loop
    while True:
        minutes_till_open = Market.minutes_till_trading()

        if minutes_till_open == 0:
            util.log('Market is currently open!')
            scan_market(client)

            util.log(f'Scanned market - next scan in {config.scan_interval}m')
            sleep(config.scan_interval * 60)

        else:
            util.log(f'Waiting {round(minutes_till_open/60, 2)}h till reopen')
            sleep(minutes_till_open * 60)
