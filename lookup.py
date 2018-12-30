import json
import requests

'''def lookup(symbol):
	key = '01O7OYJKAUNK9TQ7'

	url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}".format(symbol, key)
    if symbol.startswith("^"):
        return None

    # reject symbol if it contains comma
    if "," in symbol:
        return None

    print(url)
'''
def lookup(symbol):
	key = '01O7OYJKAUNK9TQ7'
	url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}".format(symbol, key)
	if symbol.startswith('^'):
		return None
	if ',' in symbol:
		return None
	page = requests.get(url)
	json = page.json()
	if len(json['Global Quote']) < 1:
		return "Something went wrong"
	else:
		return {
        	"name": json['Global Quote']['01. symbol'],
        	"price": json['Global Quote']['05. price'],
        	"symbol": json['Global Quote']['01. symbol']
    	}