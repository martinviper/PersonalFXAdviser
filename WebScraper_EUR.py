import sys
import os
import urllib
import urllib2
# we are using the Beautiful Soup 4 (bs4)
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import csv
# to make ANSI escape character sequences (producing colored terminal text and cursor positioning) work under Windows OS
# https://pypi.python.org/pypi/colorama
from colorama import init, Fore, Back, Style
init(autoreset=True)
# #####################################################################
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL
# #####################################################################

def pnlTrade(currency, amount, tradePrice):
    currentPrice = scrapCinkciarzFXRate('sell' if amount > 0 else 'buy', currency, abs(amount))
    pnlPLN = tradePrice * -amount + currentPrice * amount
    pnlEUR = (-amount * (tradePrice / currentPrice)) + amount
    return (round(pnlPLN, 2), round(pnlEUR, 2), currentPrice)

def pnlTradeBonus(currency, amount, tradePrice):
    currentPrice = scrapCinkciarzFXRate('sell' if amount > 0 else 'buy', currency, abs(amount))
    if amount > 0:
        priceImprovement = 0.004
    else:
        priceImprovement = -0.004
    pnlPLN = tradePrice * -amount + (currentPrice + priceImprovement) * amount	
    pnlEUR = (-amount * (tradePrice / (currentPrice + priceImprovement))) + amount
    return (round(pnlPLN, 2), round(pnlEUR, 2), (currentPrice + priceImprovement))
    
def scrapCinkciarzFXRate(type, currency, amount):
    transaction_type_dict = {'buy': '1', 'sell': '2', 'exchange': '3'}
    currency_dict = {'USD': '1', 'EUR': '2', 'GBP': '3', 'CHF': '4'}
    baseurl = 'https://cinkciarz.pl'
    calculator = '/kantor/kalkulator-walutowy'
    submitVars = dict()
    # submitVars['data[BankRates][transaction_type]'] = transaction_type_dict[type]
    submitVars['transaction_type'] = transaction_type_dict[type]
    amount_to_post = amount
    # below logic behind proper formatting of string with requested amount to be exchanged (for our POST request)
    # for all the cases where requested amount to be exchanged is less than a 1000 units
    if abs(float(amount_to_post)) < 1000:
        small_amount_to_post = abs(float(amount_to_post))
        amount_to_post = str(small_amount_to_post).replace('.', ',') + '0'
        print amount_to_post
    # for all the cases where requested amount to be exchanged is at least 1000 units or more
    else:
        amount_to_post_thousand = abs(float(amount_to_post))/1000
        amount_to_post_reminder = abs(float(amount_to_post)) - (int(amount_to_post_thousand) * 1000)
        if amount_to_post_reminder >= 100:
            amount_to_post = (str(int(amount_to_post_thousand)) + ' ' + str(amount_to_post_reminder).replace('.', ',') + '0')
        elif amount_to_post_reminder >= 10:
            amount_to_post = (str(int(amount_to_post_thousand)) + ' 0' + str(amount_to_post_reminder).replace('.', ',') + '0')
        else:
            amount_to_post = (str(int(amount_to_post_thousand)) + ' 00' + str(amount_to_post_reminder).replace('.', ',') + '0')
    # submitVars['data[BankRates][amount]'] = amount_to_post
    submitVars['amount'] = amount_to_post
    # submitVars['data[BankRates][currency]'] = currency_dict[currency]
    submitVars['currency'] = currency_dict[currency]
    # submitVars['data[BankRates][swap_currency]'] = '2'
    submitVars['swap_currency'] = '5'
    submitVars['_method'] = 'POST'
    # proxy = urllib2.ProxyHandler({'https': 'webavdub803.susq.com:8080'})
    # opener = urllib2.build_opener(proxy)
    # urllib2.install_opener(opener)
    # for our HTML form, the data needs to be encoded in a standard way, and then passed to the POST request
    # if we do not pass the data argument, urllib uses a GET request
    # urllib.urlencode() function takes a mapping or sequence of 2-tuples and returns a string in this format
    submitVarsUrlencoded = urllib.urlencode(submitVars)
    # below we are going to open the URL [baseurl+calculator], which will be a POST request object
    # data argument to be send to the server in this case is submitVarsUrlencoded encoded in a standard way
    # currently HTTP requests are the only ones that use data
    # the HTTP request will be a POST instead of a GET as the data parameter is provided
    # function below returns a file-like object to our response handler
    response = urllib2.urlopen(baseurl+calculator, submitVarsUrlencoded)
    # html-based response-data is being read into html object
    html = response.read()
    # Beautiful Soup parses data from 'html' object using 'lxml' parser, and does the tree traversal stuff
    # lxml is the most feature-rich and easy-to-use library for processing XML and HTML in the Python language
    # it parses the document and creates a corresponding data structure in memory (into 'soup' object)
    soup = BeautifulSoup((html), "lxml")
    try:
        # below we try to traverse the returned 'soup' object in order to find what returned exchange rate is
        # current_exchange_rate = str(soup.find_all(attrs={'class': 'currencies wide bank_rates'})[0].span.string)
        current_exchange_rate = str(soup.find_all(attrs={'class': 'table currencies bank-rates'})[0].span.string)
    except:
        current_exchange_rate = str(soup.find_all(attrs={'class': 'currencies wide bank_rates'})[0].span.string)
        # print ('Exchange rate has been found in the alternative search !!!')
    return float((current_exchange_rate.replace(',', '.')))

str_now_file = datetime.today().strftime("%Y%m%d.%H%M%S")

def read_trades(file):
    trades = []
    with open(file) as csvfile:
        reader = csv.reader(csvfile, delimiter='|')
        for row in reader:
            t = (row[0], float(row[1]), float(row[2]), row[3])
            trades.append(t)
    return trades

def read_trades_format(file):
    print (Fore.WHITE + 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    print (Fore.WHITE + 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    print (Fore.RED + "------------------------------------------------")
    print (Back.BLACK + Fore.WHITE + Style.BRIGHT + "Reading trades from file: \"") + file + "\""
    print (Fore.RED + "------------------------------------------------")
    trades_format = []
    with open(file) as csvfile:
        reader = csv.reader(csvfile, delimiter='|')
        for row in reader:
            t1 = row[0]
            t2 = row[1]
            if float(t2) < 0:
                t2_sign = '-'
            else:
                t2_sign = '+'
            if abs(float(t2)) > 1000:
                t2_thousand = abs(float(t2))/1000
                t2_reminder = abs(float(t2)) - (int(t2_thousand) * 1000)
                if t2_reminder >= 100:
                    t2 = t2_sign+(str(int(t2_thousand)) + ' ' + str(t2_reminder) + '0')
                elif t2_reminder >= 10:
                    t2 = t2_sign+(str(int(t2_thousand)) + ' 0' + str(t2_reminder) + '0')
                else:
                    t2 = t2_sign+(str(int(t2_thousand)) + ' 00' + str(t2_reminder) + '0')
            t3 = row[2]
            t4 = row[3]
            if t2_sign == '-':
                transaction = '%3s' % str(t1) + ' || ' + Fore.RED + '%10s' % t2 + Fore.YELLOW + ' || ' + '%6s' % t3 + ' || ' + '%16s' % t4
            else:
                transaction = '%3s' % str(t1) + ' || ' + Fore.GREEN + '%10s' % t2 + Fore.YELLOW + ' || ' + '%6s' % t3 + ' || ' + '%16s' % t4
            trades_format.append(transaction)
    return trades_format

while True:
    # trades = [('EUR', -20000, 4.3567), ('EUR', -10000, 4.3167)]
    try:
        inFile = sys.argv[1]
    except:
        inFile = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'trades_EUR.csv')
    str_now = datetime.today().strftime("%H:%M:%S || ")
    trades = read_trades(inFile)
    trades_format = read_trades_format(inFile)
    print Fore.YELLOW + Style.DIM + ("\n").join(str(x) for x in trades_format)
    print (Fore.RED + "------------------------------------------------")
    print (Fore.RED + '-------------------------------------------------------------------------------------------------------------------------------------------------')
    print (Back.BLACK + Fore.WHITE + Style.BRIGHT + 'Calculating Real-Time Profit_&_Loss for transactions:')
    print (Fore.RED + '-------------------------------------------------------------------------------------------------------------------------------------------------')
    print (Back.BLUE + Style.BRIGHT + 'Current_Time ||' + ' Trade_Availability || Ccy    Amount  Org_Rate      Transact_Time  || (Profit/Loss) PLN || (Profit/Loss) EUR ||  Current_Rate  ||')
    print (Fore.RED + '-------------------------------------------------------------------------------------------------------------------------------------------------')
    totalPnl = [0, 0]
    totalPnlBonus = [0, 0]
    for t in trades:
        pnl = pnlTrade(t[0], t[1], t[2])
        pnlBonus = pnlTradeBonus(t[0], t[1], t[2])
        totalPnl[0] += pnl[0]
        totalPnlBonus[0] += pnlBonus[0]
        totalPnl[1] += pnl[1]
        totalPnlBonus[1] += pnlBonus[1]
        pnlStr = map(lambda x: str(x), pnl)
        pnlStrBonus = map(lambda x: str(x), pnlBonus)
        if float(t[1]) >= 0:
            sign = '+'
        else:
            sign = ''
        if (pnl[0] > 0):
            print ('%16s' % str_now + 'Trade Now          || ' + '%3s' % t[0] + '%10s' % (sign + str(t[1])) + '%10s' % t[2] + '%19s' % t[3] + '  ||  PLN: ' + Fore.GREEN + '%11s' % pnlStr[0] + Fore.RESET + ' || EUR: ' + Fore.GREEN + '%12s' % pnlStr[1] + Fore.RESET + ' ||  EURPLN ' + Fore.YELLOW + '%6s' % pnlStr[2] + Fore.RESET + ' ||')
        else:
            print ('%16s' % str_now + 'Trade Now          || ' + '%3s' % t[0] + '%10s' % (sign + str(t[1])) + '%10s' % t[2] + '%19s' % t[3] + '  ||  PLN: ' + Fore.RED + '%11s' % pnlStr[0] + Fore.RESET + ' || EUR: ' + Fore.RED + '%12s' % pnlStr[1] + Fore.RESET + ' ||  EURPLN ' + Fore.YELLOW + '%6s' % pnlStr[2] + Fore.RESET + ' ||')
        if (pnlBonus[0] > 0):
            print ('%16s' % str_now + 'Trade Now (Rebate) || ' + '%3s' % t[0] + '%10s' % (sign + str(t[1])) + '%10s' % t[2] + '%19s' % t[3] + '  ||  PLN: ' + Fore.GREEN + '%11s' % pnlStrBonus[0] + Fore.RESET + ' || EUR: ' + Fore.GREEN + '%12s' % pnlStrBonus[1] + Fore.RESET + ' ||  EURPLN ' + Fore.YELLOW + '%6s' % pnlStrBonus[2] + Fore.RESET + ' ||')
        else:
            print ('%16s' % str_now + 'Trade Now (Rebate) || ' + '%3s' % t[0] + '%10s' % (sign + str(t[1])) + '%10s' % t[2] + '%19s' % t[3] + '  ||  PLN: ' + Fore.RED + '%11s' % pnlStrBonus[0] + Fore.RESET + ' || EUR: ' + Fore.RED + '%12s' % pnlStrBonus[1] + Fore.RESET + ' ||  EURPLN ' + Fore.YELLOW + '%6s' % pnlStrBonus[2] + Fore.RESET + ' ||')
        print ('-------------------------------------------------------------------------------------------------------------------------------------------------')
    if (totalPnl[0] > 0):
        print (Fore.YELLOW + Style.BRIGHT + '\t\t\t\t\t\t\t    Current Profit_&_Loss ||  PLN: ' + Fore.GREEN + '%11s' % str(totalPnl[0]) + Fore.YELLOW + ' || EUR: ' + Fore.GREEN + '%12s' % str(totalPnl[1]) + Fore.YELLOW + ' ||')
    else:
        print (Fore.YELLOW + Style.DIM + '\t\t\t\t\t\t\t    Current Profit_&_Loss ||  PLN: ' + Fore.RED + '%11s' % str(totalPnl[0]) + Fore.YELLOW + ' || EUR: ' + Fore.RED + '%12s' % str(totalPnl[1]) + Fore.YELLOW + ' ||')
    if (totalPnlBonus[0] > 0):
        print (Fore.YELLOW + Style.BRIGHT + '\t\t\t\t\t\t   Current Profit_&_Loss (COUPON) ||  PLN: ' + Fore.GREEN + '%11s' % str(totalPnlBonus[0]) + Fore.YELLOW + ' || EUR: ' + Fore.GREEN + '%12s' % str(totalPnlBonus[1]) + Fore.YELLOW + ' ||')
    else:
        print (Fore.YELLOW + Style.DIM + '\t\t\t\t\t\t   Current Profit_&_Loss (REBATE) ||  PLN: ' + Fore.RED + '%11s' % str(totalPnlBonus[0]) + Fore.YELLOW + ' || EUR: ' + Fore.RED + '%12s' % str(totalPnlBonus[1]) + Fore.YELLOW + ' ||')
    print (Fore.RED + '-------------------------------------------------------------------------------------------------------------------------------------------------')
    default_amount_to_buy_sell = 1000
    cinSellPrice = scrapCinkciarzFXRate('buy', 'EUR', default_amount_to_buy_sell)
    cinBuyPrice = scrapCinkciarzFXRate('sell', 'EUR', default_amount_to_buy_sell)
    r = [cinBuyPrice, cinSellPrice, (cinSellPrice-cinBuyPrice), (cinSellPrice + cinBuyPrice)/2.]
    r = map(lambda x: str(x), r)
    print (Fore.RED + '--------------------------------------')
    print (Back.BLUE + Style.BRIGHT + 'CINKCIARZ :: Current Rates (' + datetime.today().strftime("%H:%M:%S") + ')')
    print (Fore.RED + '--------------------------------------')
    print ('BUY:\t\t' + Fore.GREEN + '%6s' % r[0])
    print ('SELL:\t\t' + Fore.RED + '%6s' % r[1])
    print ('SPREAD:\t\t' + Fore.CYAN + '%6s' % r[2])
    print ( 'MIDPOINT:\t' + Fore.YELLOW + '%6s' % str(r[3])[:5])
    print (Fore.RED + '--------------------------------------')
    print (Fore.WHITE + 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    print (Fore.WHITE + 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n')
    # md.write(str_now + ',' + ','.join(r)+'\n')
    # pnl.flush()
    # md.flush()
    sleep(60)
