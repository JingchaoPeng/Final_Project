from finnhub import __version__
from finnhub import finnhub

def test_version():
    assert __version__ == '0.1.0'
    
def test_earnings_1():
    symbol = 'AAPL'
    api_key = 'bv541mn48v6ucj69cnfg'
    period='2020-03-31'
    type='actual'
    expected = 0.64
    actual = earnings(period,symbol, api_key,type)
    assert actual == expected
    
    
def test_earnings_2():
    symbol = 'A'
    api_key = 'bv541mn48v6ucj69cnfg'
    period='2020-06-30'
    type='estimate'
    expected = 0.6222
    actual = earnings(period,symbol, api_key,type)
    assert actual == expected


def test_earnings_3():
    symbol = 'V'
    api_key = 'bv541mn48v6ucj69cnfg'
    period = '2019-12-31'
    type = 'all'
    expected = {'actual': 1.46, 'estimate': 1.4892}
    actual = earnings(period,symbol, api_key,type)
    assert actual == expected
