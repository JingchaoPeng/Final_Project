import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import requests
from requests.exceptions import HTTPError
import bs4 as bs 
import plotly.graph_objects as go 
import datetime
import matplotlib.pyplot as plt

# 1. Get Basic Financials of One Company and Its Peer Companies
def get_compare_conpany_info(api_key, symbol='AAPL'):
    """
    This is a function to get financials of one company and its peer companies.
    
    Parameters
    ----------
    api_key: str
        You can sign up for a Finnhub account and find your API Key under Dashboard.
    symbol: str
        The ticker of a company that you want to choose.
        
    Returns
    ----------
    df
        A pandas dataframe that contains basic financials of the chosen company and its peer companies. The first row shows data about the chosen company, and the rest rows show data about peer companies.
        
    Examples
    ----------
    >>> get_compare_conpany_info(api_key='token', symbol='AAPL')

    """
    try:
        r2 = requests.get('https://finnhub.io/api/v1/stock/peers?symbol='+symbol+'&token='+api_key)   
        r2.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')   
    else:
        print('Status_code: Success!')
    json_response2 = r2.json()
    r_json_df = pd.DataFrame()  
    for i in json_response2:
        r1 = requests.get('https://finnhub.io/api/v1/stock/metric?symbol='+i+'&metric=all&token='+api_key)
        json_response1 = r1.json()
        r_json_df = r_json_df.append(pd.DataFrame(json_response1).T[['52WeekHigh','52WeekLow','roaRfy','roeRfy', 'peExclExtraAnnual', 'psAnnual','pbAnnual']].rename(index={'metric':i})[:1])
    return r_json_df



# 2. Get Quote Data of S&P500 Member Companies
# 2.1 Get Tickers of S&P500 Member Companies from Wikipedia
def SP500():
    """
    This is a function to get S&P500 member companies' tickers from Wikipedia.
    
    Parameters
    ----------
    none
        
    Returns
    ----------
    list
        A list that contains S&P500 member companies' tickers.
        
    Examples
    ----------
    >>> SP500()

    """
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.replace('\n','')
        tickers.append(ticker)
    return tickers


# 2.2 Get Quote Data
def compare_conpany_quote(api_key):
    """
    This is a function to get quotes of S&P500 member companies.
    
    Parameters
    ----------
    api_key: str
        You can sign up for a Finnhub account and find your API Key under Dashboard.
        
    Returns
    ----------
    df
        A pandas dataframe that contains quotes of S&P500 member companies. Columns are current price, high price, low price, open price, previous close price, and timestamp respectively.
        
    Examples
    ----------
    >>> compare_conpany_quote('api_key')

    """
    try:
        quote_df = pd.DataFrame()  
        for i in SP500():
            r = requests.get('https://finnhub.io/api/v1/quote?symbol='+i+'&token='+api_key)
            json_response = r.json()      
            quote_df = quote_df.append(pd.DataFrame(json_response,index=[0]).rename(index={0:i}))
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')   
    except requests.exceptions.ConnectionError:
        r.status_code = "Connection refused"
    else:
        pass
    return quote_df


# 3. Get News Sentiment of One Company and Its Peer Companies
def get_news_sentiment(api_key, symbol='AAPL'):
    """
    This is a function to get news sentiment information of one company and its peer companies.
    
    Parameters
    ----------
    api_key: str
        You can sign up for a Finnhub account and find your API Key under Dashboard.
    symbol: str
        The ticker of a company that you want to choose.
        
    Returns
    ----------
    df
        A pandas dataframe that contains news sentiment information of the chosen company and its peer companies. The first row shows data about the chosen company, and the rest rows show data about peer companies.
        
    Examples
    ----------
    >>> get_compare_conpany_info('AAPL','api_key')

    """

    r2 = requests.get('https://finnhub.io/api/v1/stock/peers?symbol='+symbol+'&token='+api_key)  
    json_response2 = r2.json()
    sentiment_comp = pd.DataFrame(columns = ['articlesInLastWeek','buzz','weeklyAverage','companyNewsScore', 'sectorAverageBullishPercent',
                                           'sectorAverageNewsScore','sentiment-bearishPercent', 'sentiment-bullishPercent'])

    for i in json_response2:
        try:
            r3 = requests.get('https://finnhub.io/api/v1/news-sentiment?symbol='+i+'&token='+api_key)
            json_response3 = r3.json()
            sentiment_comp.loc[json_response3['symbol']] = json_response3["buzz"]["articlesInLastWeek"],json_response3["buzz"]["buzz"],json_response3["buzz"]["weeklyAverage"],json_response3["companyNewsScore"],json_response3["sectorAverageBullishPercent"],json_response3["sectorAverageNewsScore"],json_response3["sentiment"]["bearishPercent"],json_response3["sentiment"]["bullishPercent"]
        except:
            pass
    return sentiment_comp



# 4. Draw COVID-19 Map
def covid19(api_key, type='case'):
    """
    This is a function to draw COVID-19 map of the United States.
    
    Parameters
    ----------
    type: str
        You can type in 'Death' or 'Case' to see the COVID-19 death map or COVID-19 case map.
    api_key: str
        You can sign up for a Finnhub account and find your API Key under Dashboard.
        
    Returns
    ----------
    map
        A map pictures that shows COVID-19 case number or death number distribution in the United States.
        
    Examples
    ----------
    >>> covid19('Death','api_key')

    """
    r = requests.get('https://finnhub.io/api/v1/covid19/us?token='+api_key)
    json_response = r.json()
    df = pd.DataFrame(json_response)
    
    # web scraping postal codes of each state
    states = pd.read_html('https://www.infoplease.com/us/postal-information/state-abbreviations-and-state-postal-codes')[0].rename(columns = {'Postal Code': 'PostalCode'})
    
    # merge two dataframes
    map_df = pd.merge(states, df, how='left', left_on='State/District', right_on='state').rename(columns = {'death': 'Death','case': 'Case'})
    
    # draw a map
    fig = go.Figure(data=go.Choropleth( 
    locations=map_df['PostalCode'],  
    z = map_df[type].astype(float), 
    locationmode = 'USA-states', 
    colorscale = 'Reds', 
    colorbar_title = type + " Number"))

    fig.update_layout(title_text = 'Covid-19 ' + type + ' Number in the United States', geo_scope='usa')
        
    return fig



# 5. Get company historical quarterly earnings surprise within one year
def earnings(api_key, period='2020-03-31',symbol='AAPL',type='actual'):
    """
    This is a function to draw COVID-19 map of the United States.
    
    Parameters
    ----------
    period: str
        The quarter period. Since we only have data for the latest year, period can only be '2019-12-31', '2020-03-31', '2020-06-30', '2020-09-30'.
    symbol: str
        The ticker of the company you want to have a look at.
    api_key: str
        You can sign up for a Finnhub account and find your API Key under Dashboard.
    type: str
        type = 'actual' returns the actual earnings surprise. type = 'estimate' returns the estimate earnings surprise. type = 'alll' returns both actual and estimate earnings surprise.
        
    Returns
    ----------
    float
        The actual or estimate earnings surprise.
    dict
        Both the actual or estimate earnings surprise.
    
        
    Examples
    ----------
    >>> earnings(period='2020-03-31',symbol='AAPL', api_key='token',type='actual')
    0.64
    >>> earnings(period='2020-06-30',symbol='A', api_key='toekn',type='estimate')
    0.6222
    >>> earnings(period='2019-12-31',symbol='V', api_key='token',type='all')
    {'actual': 1.46, 'estimate': 1.4892}
    """
    date_input = datetime.datetime.strptime(period, '%Y-%m-%d').date()
    if date_input > datetime.date(2020, 9, 30): 
        print ('The period needs to be before 2020-09-30')
    elif date_input < datetime.date(2019, 12, 31): 
        print ('The period needs to be after 2019-12-31')
    else: 
        r5 = requests.get('https://finnhub.io/api/v1/stock/earnings?symbol='+symbol+'&token='+api_key)
        json_response = r5.json()
        if type == 'all':
            dic = next(item for item in json_response if item['period'] == period)
            type_all = ['actual', 'estimate']
            all_dic = {key: dic[key] for key in type_all}
            return all_dic
        elif type == 'actual' or 'estimate':
            v = next(item for item in json_response if item['period'] == period)[type]
            return v
        
        
        

# 6. Draw a plot that shows the trend of different recommendation levels for a company and two other peer companies.
def recomd(api_key,symbol='AAPL', re_level='buy'):
    """
    This is a function to show trends of different recommendation levels for a company and two other peer companies.
    
    Parameters
    ----------
    api_key: str
        You can sign up for a Finnhub account and find your API Key under Dashboard.
    symbol: str
        The ticker of the company you want to have a look at.
    re_level: str
        The recommendation level you want to have a look at. re_level can be 'strongBuy', 'buy', 'hold', 'sell', 'strongSell'.
        
    Returns
    ----------
    plt
        A plot that shows the trend of different recommendation levels for a company and two other peer companies.
        
    Examples
    ----------
    >>> recomd(api_key,symbol='AAPL', re_level='strongBuy')

    """
    color = ['r','b','g']
    
    r2 = requests.get('https://finnhub.io/api/v1/stock/peers?symbol='+symbol+'&metric=all&token='+api_key)
    json_response2 = r2.json()
    fig = plt.figure(figsize = (15,7))
    for i in range(len(json_response2[:3])):
        r4 = requests.get('https://finnhub.io/api/v1/stock/recommendation?symbol='+json_response2[i]+'&token='+api_key)
        json_response4 = r4.json()
        df = pd.DataFrame(json_response4)
        time = [list(df["period"])[-i] for i in range(1,len(df)+1)]
        buy_count = [list(df[re_level])[-i] for i in range(1,len(df)+1)]
        time_odd = [time[i] for i in range(len(time)) if i%2==0]
        plt.plot(buy_count,color=color[i], linestyle="-", linewidth=1,label = json_response2[i] )
        plt.legend()
    plt.xlabel("Time Period")
    plt.ylabel("Count")
    plt.xticks(range(0,len(time),2),time_odd,rotation = 30)


    
# 7. Get maximum and minimum value of selected basic financials among one company and its peer companies.
def get_min_max_valuess(api_key,symbol,*args, **kwargs): #input of info items
    """
    This is a function that shows maximum and minimum value of selected basic financials among one company and its peer companies.
    
    Parameters
    ----------
    api_key: str
        You can sign up for a Finnhub account and find your API Key under Dashboard.
    symbol: str
        The ticker of the company you want to have a look at.
        
    Returns
    ----------
    tuple
        A tuple that shows maximum and minimum value of selected basic financials among one company and its peer companies.
        
    Examples
    ----------
    >>> get_min_max_valuess(api_key,'AAPL','52WeekLow','52WeekHigh')

    """
    r_json_df = get_compare_conpany_info(api_key,symbol)
    max_ = {}
    min_ = {}
    for i in args:
        max_[i] = r_json_df[i].max()
        min_[i] = r_json_df[i].min()
    return max_,min_




