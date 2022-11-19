import pandas as pd
from web3 import Web3

url="http://127.0.0.1:8545" #This should really only be run against a local node
w3 = Web3(Web3.HTTPProvider(url))

def getSender(txhash):
	try:
		tx = w3.eth.get_transaction(txhash)
		sender = tx['from']
	except Exception as e:
		sender = None
	return sender

def addSender(datafile):
	df = pd.read_csv(datafile)

	if 'txhash' not in df.columns:
		return

	new_col = 'msg.sender'
	while new_col in df.columns:
		new_col += 'a'
		
	df[new_col] = df.txhash.apply(getSender)
	
	df.to_csv(datafile,index=False)


if __name__ == '__main__':
	addSender('data/usdt_configs.csv')
