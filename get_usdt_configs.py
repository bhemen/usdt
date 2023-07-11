"""
Scan the chain for configuration events for configuration events from the USDT contract
"""

api_url = 'http://127.0.0.1:8545' #Address of your Ethereum node
start_block = 4634748 #The scanner scans the chain from start_block to the end of the chain (start_block is set to the block where the USDT contract was deployed)
contract_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7" #Address of the USDT contract
outfile = "data/usdt_configs.csv" #Where to save the data
scanned_events = ["Pause","Unpause","AddedBlackList","RemovedBlackList","DestroyedBlackFunds","Issue","Deprecate","Params","Redeem"] #Which events to scan

from tools.get_contract_events import getContractEvents

getContractEvents(api_url,start_block,contract_address,outfile,scanned_events)

