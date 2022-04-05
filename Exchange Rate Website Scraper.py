# Scrape CNBC's Exchange website for exchange rates

from bs4 import BeautifulSoup
import requests, re

inputvalue = input("Input the currency's 3 letter code (e.g. Euro = EUR) ")

link = 'https://www.cnbc.com/quotes/MXN='.replace('MXN',inputvalue)
website = requests.get(link).text
soup = BeautifulSoup(website, 'lxml')

# FIND CURRENCY NAME
# Searches within the tag 'span' and the class 'QuoteStrip-name'
rateName = soup.find('span', class_='QuoteStrip-name').text.replace(' FX Spot Rate','')
rateNameSearch  = rateName.replace(' FX Spot Rate','').replace(' ', '/')
# Search using the regex [a-zA-Z]+, which searches for any word
currencyRegex = re.compile(r'([a-zA-Z]+)')
# The regex uses findall instead of re.compile(r'([a-zA-Z]+)\([a-zA-Z]+)\([a-zA-Z]+)\([a-zA-Z]+)') since
# it would allow the correct value to be selected depending on the size of the list.
mo = currencyRegex.findall(rateNameSearch)

# Sometimes the currency name includes the country name (e.g. US Dollar/Korean Won) while other times
# it doesn't (e.g. JPY/USD). Since the number of values in the list depends on the number of words, the
# correct value can be selected depending on size of the string. Why is the text structured like this?
if len(mo) == 4:
    fromCurrency = mo[1]
    toCurrency = mo[3]
    # If the two currencies have the same name (e.g. Australian Dollar and US Dollar), include the country
    # name.
    if toCurrency == fromCurrency:
        fromCurrency = f"""{mo[0]} {fromCurrency}"""
        toCurrency = f"""{mo[2]} {toCurrency}"""
elif len(mo) == 2:
    fromCurrency = mo[0]
    toCurrency = mo[1]

# OBTAINS LAST UPDATED TIME
time = soup.find('div', class_='QuoteStrip-lastTradeTime').text.replace('Last | ', '')

# OBTAINS CURRENT RATE
valuedescript = ['']*4 # Creates empty 4 value empty listring to store found values

# The original code used .find('span', class_='QuoteStrip-changeDown'). However, this would only work
# when 'QuoteStrip-changeDown' (which is when the change is negative), not if the change is positive.

# Narrows search radius to values in 'QuoteStrip-lastPriceStripContainer' with tag 'div'
valuebox = soup.find('div', class_='QuoteStrip-lastPriceStripContainer')
# Within valuebox, look for values with the tag 'span'
valuestring = valuebox.find_all('span')
count = 0 # count is used an index to specify where in the list to assign the variable.

# Loop search with each found result, saving it to the valuedescript list
for i in valuestring:
    text = i.text.replace(' ', '').replace('(', '').replace(')', '')
    valuedescript[count] = text

    count = count + 1

rate = valuedescript[0].replace(',','')
reversedrate = str(1/float(rate))
abschange = valuedescript[2]
percentchange = valuedescript[3]

# PRINT RESULTS
print('')
# You don't need \n when using f strings, just make a new line in the code.
print(f"""{rateName}
Rate: 1 {fromCurrency} = {rate} {toCurrency} (or 1 {toCurrency} = {reversedrate} {fromCurrency})
Change: {abschange} {toCurrency} ({percentchange})
Last Updated: {time}""")
