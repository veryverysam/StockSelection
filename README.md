# StockSelection
Base on the position changes of different fund managers, predict which fundamental factors affect the stocks selection of fund managers using latent variables model.
Objective:
Base on the position changes of different fund managers, predict which fundamental factors affect the stocks selection of fund managers using latent variables model.
Target Client: Fidelity Investments
Data Source: 
1.	EDGAR Database 13F Form 
2.	Fidelity CUSIP look up for Stocks and Bonds
3.	Yahoo Finance
Details Data Retrieved from different public sources:
1.	Position change between each quarter (13F Form)
2.	Mapping for CUSIP and Ticker (Fidelity CUSIP look up)
3.	Fundamental Factors and Prices of each Ticker (Yahoo Finance)
Data Preprocessing:
1.	Period for 2 quarter: 2019-03-31 and 2018-12-31
2.	Only Stocks is included, i.e. removes all ETF, fund, Trust, Rights, Futures / Options
3.	Adjusted last price is retrieved from 2018-12-31 from Yahoo Finance
4.	All the key statistics are always > 0.
Final Data Set:
1.	10 Fund Managers
2.	33XX Stocks
3.	10 Fundamental Factors (Price used is the adjusted close price of 2018-12-31)
a.	Market Capital
b.	EPS
c.	PE
d.	PS
e.	PB
f.	ROA
g.	ROE
h.	Current Ratio
i.	Debt to Equity Ratio
j.	90 days momentum
k.	Dividend Yield
Methodology:
1.	Build a matrix of Managers Preference (V) on Manager M x Stocks I with Manager Rating on each stock. It is the output of our analysis
a.	If the stock is newly brought, rating is 2
b.	The position is increased, rating is 1.
c.	The position remains unchanged or remains no position, rating is 0.
d.	The position is reduced, rating is -1.
e.	The position is liquidated, rating is -2.
2.	Decompose the matrix V to M x q and q x I matrix using PCA, where q is the latent variables 
a.	Identify the important latent variables that affect Managers’ Rating
3.	Build a matrix of Stock Features (W) on Stocks I x Fundamental Factors F
4.	Analyze the matrix using Factor Analysis with nFactors = 6
a.	Identify the latent variables that can explain the Stock Features
