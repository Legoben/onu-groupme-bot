import locale
from datetime import *
import quandl
import matplotlib
import matplotlib.pyplot as plt
import tempfile
import os
import requests

locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8')) # Set locale to en_US
quandl.ApiConfig.api_key = "V5uEXA4L1zfc9Q6Dp9Lz" # Set API key

# Returns price info in a pandas DataFrame
def get_stock_info(ticker, dataset, suffix='', start_date='', end_date=''):
    return quandl.get(dataset + '/' + ticker.upper() + suffix, start_date=start_date, end_date=end_date)

# Returns end-of-day stock price from the previous day
def get_stock_price(ticker):
    # Wiki prices
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        data = get_stock_info(ticker, dataset='EOD', suffix='', start_date=yesterday)
    except quandl.errors.quandl_error.ForbiddenError:
        data = get_stock_info(ticker, dataset='WIKI', suffix='', start_date=yesterday)
    return data.tail(1)['Close'].tolist()[0]

def get_stock_earnings_plot(ticker):
    # Core US Fundamentals Data
    # Earnings per Basic Share (Most Recent - Quarterly)
    five_years = 365*5
    five_years = (datetime.now() - timedelta(days=five_years)).strftime('%Y-%m-%d')
    data = get_stock_info(ticker, dataset='SF1', suffix='_EPS_MRQ', start_date=five_years)
    # Plot graph
    plot = plt.plot(data)

    # Save to a temporary file and upload to GroupMe
    f = tempfile.NamedTemporaryFile(suffix='.png', delete=False) # open temporary file
    plt.xlabel('Time')
    plt.ylabel('Price')
    title = 'Earnings for %s' % ticker
    plt.title(title)
    plt.savefig(f.name, frameon=False, facecolor='#f7f7f7g')
    #ax = fig.gca()
    #ax.legend_.remove()
    upload_image(f.name, "Quarterly earnings for " + ticker.upper())
    return f.name # image picture filepath

def get_stock_earnings(ticker):
    # Core US Fundamentals Data
    # Earnings per Basic Share (Most Recent - Quarterly)
    data = get_stock_info(ticker, dataset='SF1', suffix='_EPS_MRQ')
    last = data['Value'].iloc[-1]
    first = data['Value'].iloc[1]
    CAGR = ((last/first)**(0.2))-1
    return (last, CAGR)

def get_stock_revenues(ticker):
    five_years = 365*5
    five_years = (datetime.now() - timedelta(days=five_years)).strftime('%Y-%m-%d')
    data = get_stock_info(ticker, dataset='SF1', suffix='_REVENUE_MRQ', start_date=five_years)
    #print(data)
    last = (data['Value'].iloc[-1])/1e9
    first = (data['Value'].iloc[0])/1e9
    CAGR =((last/first)**(0.2))-1
    if last <= 1:
        size = 'small'
        grade = CAGR/0.15
    elif last >= 1 and last<=10:
        size = 'medium'
        grade = CAGR/0.12
    elif last > 10:
        size = 'large'
        grade = CAGR/0.07

    return (last, CAGR, size, grade)

def stock_grade(ticker):
    [earnings, earnings_growth] = get_stock_earnings(ticker)
    [sales, sales_growth, size, sales_grade] = get_stock_revenues(ticker)

    if size == 'small':
        earnings_grade = earnings_growth/0.15
    elif size == 'medium':
        earnings_grade = earnings_growth/0.12
    elif size == 'large':
        earnings_grade = earnings_growth/0.07
    grade = (0.5*earnings_grade + 0.5*sales_grade)*100
    grade_str = '%d%% out of 100%%' %grade
    return grade_str

# Returns stock price in a user-friendly way
# https://stackoverflow.com/questions/320929/currency-formatting-in-python
def get_stock_price_friendly(ticker):
    try:
        price = get_stock_price(ticker)
        price_pretty = locale.currency(price)
        return "Yesterday's end-of-day price for %s is %s." % (ticker.upper(), price_pretty)
    except quandl.errors.quandl_error.NotFoundError as e:
        # print(e) # debug
        return "Sorry, %s is not a valid ticker symbol name." % ticker

def upload_image(file_path, text=''):
    # Upload image
    headers = { 'Content-Type': 'image/jpeg',
                'X-Access-Token': 'd98e567023a601356f8c53d177af4f91' # GM_TOKEN
                }

    url = ''
    with open(file_path, 'rb') as f:
        response = requests.post('https://image.groupme.com/pictures', headers=headers, data=f)
        url = response.json()['payload']['picture_url']

    # Post message
    msg = {
            "bot_id": "638f64d07ce7f83bdee814c31d",
            "text": text,
            "attachments": [
                {
                    "type": "image",
                    "url": url
                    }
                ]
            }


    print(requests.post('https://api.groupme.com/v3/bots/post', json=msg))


def test():
    # print(get_stock_price_friendly('AAPL'))
    # print(get_stock_price_friendly('GOOG'))
    # print(get_stock_price_friendly('FB'))
    # print(get_stock_price_friendly('COF'))
    # print(get_stock_price_friendly('QWERTY')) # invalid
    print(get_stock_earnings_plot('AAPL'))

if __name__ == "__main__":
    test()
