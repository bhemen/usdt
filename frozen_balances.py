import pandas as pd

usdc_configs = pd.read_csv("data/usdc_configs.csv")

blacklists = usdc_configs.loc[usdc_configs.event_name=='Blacklisted']

transfers = pd.read_csv("data/usdc_transfers.csv")

transfers_to = transfers[transfers['to'].isin(blacklists._account)][['block_number','txhash','timestamp','value','to']].copy()
transfers_to = transfers[['block_number','txhash','timestamp','value','to']].copy()
transfers_to.rename({'to':'user'},axis='columns',inplace=True)
transfers_from = transfers[transfers['from'].isin(blacklists._account)][['block_number','txhash','timestamp','value','from']].copy()
transfers_from = transfers[['block_number','txhash','timestamp','value','to']].copy()
transfers_from.rename({'from':'user'},axis='columns',inplace=True)
transfers_from['value'] *= -1

transfers = pd.concat( [transfers_to,transfers_from] )
transfers.sort_values(by=['user','block_number','timestamp'],inplace=True)

user_balances = transfers.groupby(by=['user','block_number'])[['value']].sum().groupby(level=0).cumsum()

print( user_balances.head() )
