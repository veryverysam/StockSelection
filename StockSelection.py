#!/usr/bin/env python
# coding: utf-8

# Date: 2019-06-20
# Title: Fundamental Factors Affecting Active Stock Selection
# Desc: Use US SEC 13F Report to analysis Fund's Manager's Stock Selection Criteria
# Usage: By links of US SEC 13F XML Documents, the program read the XML files, filter only stocks holdings change, retrieved stocks statistics from Yahoo Finance and analysis on Fund's Managers Selection Behaviour
# Reference: A recommender system for active stock selection

# Read XML files download from US SEC 13F Report and save it into Pandas

# In[5]:


import requests
import xml.etree.ElementTree as ET
import pandas as pd
import datetime

# do this if running in jupyter
pd.set_option('display.max_columns', None)

# Download txt file from 
def downloadXML(html,headers):
    content = requests.get(html, headers=headers).text
    return content
  
def txt2XML(content):
    xmlCheck1 = False
    xmlCheck2 = False
    xmlLine = ""
    for line in content.splitlines():
        if "</XML>" in line:
            xmlCheck2 = False
        if xmlCheck2:
            xmlLine += line + "\n"
        if "<XML>" in line and xmlCheck1:
            xmlCheck2 = True
        if "<XML>" in line:
            xmlCheck1 = True
    root = ET.fromstring(xmlLine)
    return root

def XML2Array(root,reportPeriod,ns):
    all_records = []
    keepRecord = True
    for infoTable in root.findall('infoHolding:infoTable',ns):    
        for shrsOrPrnAmt in infoTable.findall("infoHolding:shrsOrPrnAmt",ns):
            if(shrsOrPrnAmt.find('infoHolding:sshPrnamtType', ns).text != 'SH'):
                keepRecord = False
        if keepRecord:
            record = {}
            record['cusip'] = infoTable.find('infoHolding:cusip', ns).text
            for shrsOrPrnAmt in infoTable.findall("infoHolding:shrsOrPrnAmt",ns):
                record['sshPrnamt'] = float(shrsOrPrnAmt.find('infoHolding:sshPrnamt', ns).text)
            if (infoTable.find('infoHolding:otherManager', ns) == None):
                record['Manager'] = 2
            elif (infoTable.find('infoHolding:otherManager', ns) == "1,5"):
                record['Manager'] = 5
            else:
                record['Manager'] = pd.to_numeric(infoTable.find('infoHolding:otherManager', ns).text.replace("1,",""))
            record['reportPeriod'] = reportPeriod
            all_records.append(record)
        keepRecord = True
    return all_records
    

def getReportPeriod(content):
    reportPeriod = datetime.datetime.today()
    for line in content.splitlines():
        if "CONFORMED PERIOD OF REPORT:" in line:
            reportPeriod = datetime.datetime.strptime(line[-8:],'%Y%m%d')
            break
    return reportPeriod


# Extract 13F for reporting period 2019-03-31 and 2018-12-31
website = {'https://www.sec.gov/Archives/edgar/data/315066/000031506619001533/0000315066-19-001533.txt',
        'https://www.sec.gov/Archives/edgar/data/315066/000031506619000784/0000315066-19-000784.txt'
       }
headers = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}

# Store Holiding Change data for 5 quarters
all_records = []

# Download the 13F From from the Internet
for html in website:
    quarterRecord = []
    content = downloadXML(html,headers)
    reportPeriod = getReportPeriod(content)
    root = txt2XML(content)
    ns = {'infoHolding': 'http://www.sec.gov/edgar/document/thirteenf/informationtable',
      'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
    quarterRecord = XML2Array(root,reportPeriod,ns)
    all_records = all_records + quarterRecord

# Convert Array to DataFrame
df_13F = pd.DataFrame(all_records)


# In[8]:


# Check Point
df_13F[df_13F["cusip"]=='03062T105']


# Retrieve Ticker from CUSIP from Fidelity Investment website

# In[ ]:


from bs4 import BeautifulSoup
import time
secRecords = []
i = 1
totalCnt = len(df_13F['cusip'].unique())
for cusip in df_13F['cusip'].unique():
    if i % 500 == 0:
        print("Retriving Ticker: Progress: ", i , "/" , totalCnt)
    i = i + 1
    html = 'https://quotes.fidelity.com/mmnet/SymLookup.phtml?reqforlookup=REQUESTFORLOOKUP&productid=mmnet&isLoggedIn=mmnet&rows=50&for=stock&by=cusip&criteria='+cusip+'&submit=Search'
    content = requests.get(html, headers=headers).text
    record = {}
    record['cusip'] = cusip
    for line in content.splitlines():
        if "<font class=\"smallfont\">" in line:
            soap = BeautifulSoup(line)
            record['SecName'] = soap.text
        if "/webxpress/get_quote?QUOTE_TYPE" in line:
            soap = BeautifulSoup(line)
            record['Ticker'] = soap.text
    secRecords.append(record)
df_secRecords = pd.DataFrame(secRecords)


# In[ ]:


# Remove non-stock from the list
final_secRecords=df_secRecords[pd.notnull(df_secRecords['Ticker'])]
final_secRecords = final_secRecords[-final_secRecords['SecName'].str.contains('ETF', regex=False)]
final_secRecords = final_secRecords[-final_secRecords['SecName'].str.contains('FUND', regex=False)]
final_secRecords = final_secRecords[-final_secRecords['SecName'].str.contains('BOND', regex=False)]
final_secRecords = final_secRecords[-final_secRecords['SecName'].str.contains('TRUST', regex=False)]
final_secRecords = final_secRecords[-final_secRecords['SecName'].str.contains('VANGUARD', regex=False)]
final_secRecords = final_secRecords[-final_secRecords['SecName'].str.contains('DIREXION', regex=False)]
final_secRecords = final_secRecords[-final_secRecords['SecName'].str.contains('INDEX', regex=False)]
final_secRecords = final_secRecords[-final_secRecords['SecName'].str.contains('ISHARES', regex=False)]
final_secRecords = final_secRecords[-final_secRecords['SecName'].str.contains('SPDR', regex=False)]
final_secRecords = final_secRecords[-final_secRecords['SecName'].str.contains('PROSHARES', regex=False)]
final_secRecords = final_secRecords[-final_secRecords['SecName'].str.contains('INVESCO', regex=False)]
final_secRecords = final_secRecords[-final_secRecords['Ticker'].str.contains('/', regex=False)]


# In[ ]:


# Check point
final_secRecords.head(5)


# Construct Stocks' Key Statistics from Yahoo Finance

# In[ ]:


all_secStatics = []
i = 1
totalCnt = len(final_secRecords['Ticker'].unique())
for ticker in final_secRecords['Ticker']:
    secStatics = {}
    secStatics['Ticker'] = ticker
    name = ""
    
    # Display Progress
    if i % 500 == 0:
        print("Progress: ", i, "/", totalCnt)
    i = i + 1

    # Retireve the latent variables from Key Statistics Page
    html = 'https://finance.yahoo.com/quote/' + ticker + '/key-statistics?p=' + ticker 
    content = requests.get(html, headers=headers).text
    soap = BeautifulSoup(content)
    tables = soap.findAll('div')
    for tab in tables:
        for tr in tab.findAll('tr'):
            for td in tr.findAll('td'):
                if name != "":
                    secStatics[name] = td.getText()
                    name = ""
                if 'Shares Outstanding 5' in td.getText():
                    name = 'Shares Outstanding'
                if 'Book Value Per Share' in td.getText():
                    name = 'Book Value Per Share'
    
    # Retrieve the latent variables from Income Statement
    html = 'https://finance.yahoo.com/quote/' + ticker + '/financials?p=' + ticker 
    content = requests.get(html, headers=headers).text
    soap = BeautifulSoup(content)
    tables = soap.findAll('table')
    for tab in tables:
        for tr in tab.findAll('tr'):
            for td in tr.findAll('td'):
                if name != "":
                    secStatics[name] = td.getText()
                    name = ""
                if 'Total Revenue' in td.getText():
                    name = 'Total Revenue'          
                if 'Net Income' in td.getText():
                    name = 'Net Income'    
                    
    # Retrieve the latent variables from Balance Sheet
    html = 'https://finance.yahoo.com/quote/' + ticker + '/balance-sheet?p=' + ticker
    content = requests.get(html, headers=headers).text
    soap = BeautifulSoup(content)
    tables = soap.findAll('table')
    for tab in tables:
        for tr in tab.findAll('tr'):
            for td in tr.findAll('td'):
                if name != "":
                    secStatics[name] = td.getText()
                    name = ""
                if 'Cash And Cash Equivalents' in td.getText():
                    name = 'Cash And Cash Equivalents'
                if 'Total Current Assets' in td.getText():
                    name = 'Total Current Assets'
                if 'Total Assets' in td.getText():
                    name = 'Total Assets'             
                if 'Total Current Liabilities' in td.getText():
                    name = 'Total Current Liabilities'   
                if 'Total Liabilities' in td.getText():
                    name = 'Total Liabilities'  
                if 'Total Stockholder Equity' in td.getText():
                    name = 'Total Stockholder Equity'
                    
    # Retrieve the latent variables from Cash Flow
    html = 'https://finance.yahoo.com/quote/' + ticker + '/cash-flow?p=' + ticker
    content = requests.get(html, headers=headers).text
    soap = BeautifulSoup(content)
    tables = soap.findAll('table')
    for tab in tables:
        for tr in tab.findAll('tr'):
            for td in tr.findAll('td'):
                if name != "":
                    secStatics[name] = td.getText()
                    name = ""
                if 'Dividends Paid' in td.getText():
                    name = 'Dividends Paid'
    all_secStatics.append(secStatics)    
df_secStatics = pd.DataFrame(all_secStatics)


# In[ ]:


# Remove instrument that has missing latent variables
df_secStatics = df_secStatics[-pd.isna(df_secStatics['Net Income'])]
df_secStatics = df_secStatics[df_secStatics['Cash And Cash Equivalents']!='Short Term Investments']
df_secStatics = df_secStatics[df_secStatics['Total Revenue']!='-']
df_secStatics = df_secStatics[df_secStatics['Book Value Per Share']!='N/A']
df_secStatics = df_secStatics[df_secStatics['Total Current Liabilities']!='-']

# remove thousands delimiter
df_secStatics = df_secStatics.replace(',','',regex=True)

# Convert numbers represented as characters
d = {'K': 1000, 'M': 1000000, 'B': 1000000000}
df_secStatics['Shares Outstanding'] = pd.to_numeric(df_secStatics['Shares Outstanding'].str[:-1]) * df_secStatics['Shares Outstanding'].str[-1].replace(d)

# replace - to 0
df_secStatics = df_secStatics.replace('-','0',regex=True)


# In[ ]:


# Check Point
df_secStatics.head(5)


# Retrieve Stock Price from Yahoo Finance using Pandas DataReader

# In[ ]:


import pandas_datareader.data as web
all_secPrice = []
getPrice = False
for ticker in df_secStatics['Ticker']:
    secPrice = {}
    secPrice['Ticker'] = ticker
    try:
        quotes = web.DataReader(ticker, 'yahoo', pd.to_datetime('2018-09-01').date(), pd.to_datetime('2018-12-31').date()).sort_values(by='Date',ascending=False)
        getPrice = True
    except:
        print("Issue Ticker: ", ticker)
    if getPrice:
        try:
            secPrice['2018-12-31'] = quotes.query('Date <= "2018-12-31"').iloc[:1,5].to_list()[0]
        except:
            secPrice['2018-12-31'] = 'na'
            print("Issue Ticker: 2018-12-31: ", ticker)
        try:
            secPrice['2018-09-30'] = quotes.query('Date <= "2018-09-30"').iloc[:1,5].to_list()[0]
        except:
            secPrice['2018-09-30'] = 'na'
            print("Issue Ticker: 2018-09-30: ", ticker)
        all_secPrice.append(secPrice)
df_secPrice = pd.DataFrame(all_secPrice)


# In[ ]:


# Remove Stocks that does not have full set of Prices
final_secPrice = df_secPrice[df_secPrice['2018-09-30']!='na']
final_secPrice = final_secPrice[final_secPrice['2018-12-31']!='na']


# In[ ]:


# Check Point
final_secPrice.head(5)


# Construct Key Statistics Table for Stocks

# In[ ]:


final_secStatics = df_secStatics[df_secStatics['Ticker'].isin(final_secPrice['Ticker'])]
final_secRecord = final_secRecords[final_secRecords['Ticker'].isin(final_secPrice['Ticker'])]
final_perference = df_perference[df_perference['cusip'].isin(final_secRecord['cusip'])]


# In[ ]:


# Join all Tables
final_sec = final_secRecord.set_index('Ticker').join(final_secPrice.set_index('Ticker')).join(final_secStatics.set_index('Ticker'))


# In[ ]:


# Check Point
final_sec.head(5)


# Construct Managers' Ratings Table

# In[ ]:


# Filter Out non-stock holldings change
df_13F_Final = df_13F[df_13F['cusip'].isin(final_secRecords['cusip'])]

# Merge the two Table
df_perference = pd.merge(df_13F_Final[df_13F_Final['reportPeriod']=='2018-12-31'],df_13F_Final[df_13F_Final['reportPeriod']=='2019-03-31'],how='outer',on=['Manager','cusip']).sort_values(by=['Manager','cusip'])

# Fill Empty Value
df_perference = df_perference.fillna(0)

# Assign Rating to each Stock for each Manager
df_perference.loc[pd.to_numeric(df_perference['sshPrnamt_x'])==0,'Rating'] = 2
df_perference.loc[pd.to_numeric(df_perference['sshPrnamt_x'])<pd.to_numeric(df_perference['sshPrnamt_y']),'Rating'] = 1
df_perference.loc[pd.to_numeric(df_perference['sshPrnamt_x'])==pd.to_numeric(df_perference['sshPrnamt_y']),'Rating'] = 0
df_perference.loc[pd.to_numeric(df_perference['sshPrnamt_x'])>pd.to_numeric(df_perference['sshPrnamt_y']),'Rating'] = -1
df_perference.loc[pd.to_numeric(df_perference['sshPrnamt_y'])==0,'Rating'] = -2

# Contruct a Manager x Stocks Table
final_perference = pd.pivot_table(df_perference, values='Rating', index=['Manager'], columns=['cusip'])
final_perference = pd.pivot_table(df_perference, values='Rating', index=['Manager'], columns=['cusip'])


# In[ ]:


# Check Point
#final_perference.to_csv(r'C:\temp\perference.csv')
final_perference


# Construct Stocks x Latent Variables Table

# In[ ]:


secFeatures = {}
secFeatures['cusip'] = final_sec['cusip']
secFeatures['Market Cap'] = pd.to_numeric(final_sec['2018-12-31']) * pd.to_numeric(final_sec['Shares Outstanding'] / 1000000)
secFeatures['EPS'] = pd.to_numeric(final_sec['Net Income'])/ pd.to_numeric(final_sec['Shares Outstanding']) * 1000
secFeatures['PE'] = pd.to_numeric(final_sec['2018-12-31'])/ pd.to_numeric(final_sec['Net Income']) * pd.to_numeric(final_sec['Shares Outstanding']) / 1000
secFeatures['PS'] = pd.to_numeric(final_sec['2018-12-31'])/ pd.to_numeric(final_sec['Total Revenue']) * pd.to_numeric(final_sec['Shares Outstanding']) / 1000
secFeatures['PB'] = pd.to_numeric(final_sec['2018-12-31'])/ pd.to_numeric(final_sec['Book Value Per Share'])
secFeatures['ROA'] = pd.to_numeric(final_sec['Net Income'])/ pd.to_numeric(final_sec['Total Assets'])
secFeatures['ROE'] = pd.to_numeric(final_sec['Net Income'])/ pd.to_numeric(final_sec['Total Stockholder Equity'])
secFeatures['Current Ratio'] = pd.to_numeric(final_sec['Total Current Assets'])/ pd.to_numeric(final_sec['Total Current Liabilities'])
secFeatures['Debt to Equity'] = pd.to_numeric(final_sec['Total Liabilities'])/ pd.to_numeric(final_sec['Total Stockholder Equity'])
secFeatures['MOM'] = (pd.to_numeric(final_sec['2018-12-31']) - pd.to_numeric(final_sec['2018-09-30'])) / pd.to_numeric(final_sec['2018-09-30'])
secFeatures['DY'] = pd.to_numeric(final_sec['Dividends Paid']) * 1000 / pd.to_numeric(final_sec['Shares Outstanding'])  / pd.to_numeric(final_sec['2018-12-31'])
pd_secFeatures = pd.DataFrame(secFeatures)


# In[ ]:


# Form latent variables tables with index as CUSIP
final_secFeatures = pd_secFeatures.set_index('cusip')


# In[ ]:


# Check Point
final_secFeatures.head(5)


# Export the Matrix and analysis on R

# In[ ]:


final_perference.to_csv(r'C:\temp\perference.csv')
final_secFeatures.to_csv(r'C:\temp\sec.csv')


# Use Principle Component Analysis to decompose the Manager's Rating Table into 2 differnt Matrix
# Mananger x q and q x Stocks

# In[ ]:


from sklearn import decomposition as dc
pca = dc.PCA(n_components = 4, svd_solver = 'full')
principalComponents = pca.fit_transform(final_perference)
principalDf = pd.DataFrame(data = principalComponents, columns = ['Comp 1', 'Comp 2', 'Comp 3', 'Comp 4'])
principalDf
print(pca.explained_variance_ratio_)  
print(pca.singular_values_)


# In[ ]:


from sklearn.decomposition import FactorAnalysis
fact_4c=FactorAnalysis(n_components=4)
X_factor=fact_4c.fit_transform(final_secFeatures.T)

