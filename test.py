import requests
from config import keys, EXCHANGE_TOKEN


currencies = '%2C'.join(keys.values())
print(currencies)
url = f"https://api.apilayer.com/fixer/latest?symbols={currencies}&base=RUB"


payload = {}
headers = {
    "apikey": EXCHANGE_TOKEN
    }

response = requests.request("GET", url, headers=headers, data=payload)
result = response.text
print(result)