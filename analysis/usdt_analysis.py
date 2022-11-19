import pandas as pd

#CSV columns:
#event_name,block_number,txhash,log_index,timestamp,newAddress,amount,feeBasisPoints,maxFee,_user,_balance,_blackListedUser,contract_address
usdt_configs = pd.read_csv("../data/usdt_configs.csv")

print( usdt_configs.groupby(['event_name']).size() )

blacklists = usdt_configs.loc[usdt_configs.event_name=='AddedBlacklist']
unblacklists = usdt_configs.loc[usdt_configs.event_name=='RemovedBlacklist']

if 'msg.sender' in blacklists.columns:
	print( blacklists.groupby(['msg.sender']).size() )	
else:
	print( "The USDT events do *not* record the address that made the transaction." )
	print( "Run the script ../addSender.py and try again" )
