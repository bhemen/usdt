"""
Utilities for getting contract ABIs from Etherscan and caching them locally
"""

import requests
import json
import time
#from web3 import Web3
import os

ABI_ENDPOINT = 'https://api.etherscan.io/api?module=contract&action=getabi&address='

if not os.path.exists('abis'):
    os.makedirs('abis')

_cache_file = "abis/cached_abis.json"

_cache = dict() #Dictionary of address: abi pairs

def fetch_abi(contract_address,retry=0):
	"""
	get abi for contract address from etherscan
	This does *not* follow proxies
	"""

	max_retries = 1
	try:
		response = requests.get( f"{ABI_ENDPOINT}{contract_address}", timeout = 20 )	
	except requests.exceptions.ReadTimeout as e:
		if retry < max_retries:
			print( f"Timeout, trying again" )
			return fetch_abi(contract_address,retry+1)
		else:
			print( f"Retried {retry} times" )
			print( f"Failed to get abi" )
			return None
	except Exception as e:
		print( f"Failed to get {address} from {ABI_ENDPOINT}" )
		print( e )
		return None

	try:
		response_json = response.json()
		abi_json = json.loads(response_json['result'])
	except Exception as e:
		print( f"Error in fetch_abi ({contract_address})" )
		print( f"Failed to load json" )
		print( e )
		if retry < max_retries:
			print( f"JSON error, trying again" )
			return fetch_abi(contract_address,retry+1)
		else:
			print( f"Retried {retry} times" )
			print( f"Failed to get abi for {contract_address}" )
			return None
	#print( type( abi_json ) ) #list
	#print( type( abi_json[0] ) ) #dict
	return abi_json

def set_abi(contract_address,abi,overwrite=True):
	"""
	Explicitly add a contract's abi to the cache
	"""
	try:
		with open(_cache_file) as f:
			_cache = json.load(f)
	except Exception as e:
		_cache = dict()
	
	if contract_address not in _cache.keys() or overwrite:
		_cache[contract_address] = abi	
		with open(_cache_file, 'w') as outfile:
			json.dump(_cache, outfile,indent=2)
	else:
		print( f"abi already exists" )
		


def get_cached_abi(contract_address,abikw=""):
	"""
	Check if the abi is in the cache.
	If so, return it
	If not, fetch it from Etherscan
	"""

	try:
		with open(_cache_file) as f:
			_cache = json.load(f)
	except Exception as e:
		_cache = dict()
	
	if abikw:
		search_for = abikw
	else:
		search_for = contract_address
	
	abi = _cache.get(search_for)

	if not abi:
		abi = fetch_abi(search_for)
		if abi is not None:
			_cache[search_for] = abi
			with open(_cache_file, 'w') as outfile:
				json.dump(_cache, outfile,indent=2)
		
	return abi

def create_contract(web3,address):
	"""
	Take an address and return a contract object referring to the contract at that address
	"""
	abi = get_cached_abi(address)
	contract = web3.eth.contract(address, abi=abi)
	return contract

def get_event_args(contract_address,target_events='all',abikw=''):
	"""
	Get a list of events and their arguments from the ABI	
	"""
	abi = get_cached_abi(contract_address,abikw)

#	full_event_signatures = {}
#	for evt in [obj for obj in abi if obj['type'] == 'event']:
#		name = evt['name']
#		types = [input['type'] for input in evt['inputs']]
#		full = '{}({})'.format(name,','.join(types))
#		#full_event_signatures[full] = Web3.keccak(text=full).hex()
#		full_event_signatures[Web3.keccak(text=full).hex()] = full
#
#	event_signatures = {}
#	for evt in [obj for obj in abi if obj['type'] == 'event']:
#		name = evt['name']
#		types = [input['type'] for input in evt['inputs']]
#		full = '{}({})'.format(name,','.join(types))
#		#event_signatures[full] = Web3.keccak(text=full).hex()
#		event_signatures[Web3.keccak(text=full).hex()] = name

	events = [obj for obj in abi if obj['type'] == 'event' ]
	if target_events != 'all':
		events = [e for e in events if e['name'] in target_events]

	event_names = list(set([e['name'] for e in events]))
	event_args = list(set([inp['name'] for e in events for inp in e['inputs']]))

	return event_names, event_args

def get_proxy_address(web3,address):
	"""
		Check if a contract is a proxy, and if so, return the address of the underlying implementation
	"""
	storage_locations = [
		"0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc", 	#hex(int( Web3.keccak(text='eip1967.proxy.implementation').hex(), 16 ) - 1)   https://eips.ethereum.org/EIPS/eip-1967
		"0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50",	#hex(int( Web3.keccak(text='eip1967.proxy.beacon').hex(), 16 ) - 1)   https://eips.ethereum.org/EIPS/eip-1967
		"0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2c036e5a723fd8ee048ed3f8c3",	#Web3.keccak(text='org.zeppelinos.proxy.implementation').hex()    https://github.com/OpenZeppelin/openzeppelin-labs/blob/master/initializer_with_sol_editing/contracts/UpgradeabilityProxy.sol
		"0xc5f16f0fcc639fa48a6947836d9850f504798523bf8c9a3a87d5876cf622bcf7",	#Web3.keccak(text='PROXIABLE').hex() https://eips.ethereum.org/EIPS/eip-1822
		"0x5f3b5dfeb7b28cdbd7faba78963ee202a494e2a2cc8c9978d5e30d2aebb8c197" ] #Recommended by TrueBlocks https://github.com/TrueBlocks/trueblocks-core/blob/develop/src/libs/etherlib/ethcall.cpp#L540
	addr = None
	for p in storage_locations:
		try:
			addr = web3.eth.get_storage_at(address,p) #Returns 32 bytes
			addr = addr.hex() 
			addr = "0x" + addr[-40:] #Last 20 bytes (40 hex chars) is the address
			addr = web3.toChecksumAddress(addr)
		except Exception as e:
			addr = None
			print(f"Error in get_proxy_address: Failed to read address at location {p}" )
			print( e )
		if addr is not None and int(addr,16) != 0:
			if p == "0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50": #Beacon proxy https://eips.ethereum.org/EIPS/eip-1967
				try:
					beacon_abi = '[{"inputs":[],"name":"implementation","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'
					contract = web3.eth.contract(address=addr,abi=beacon_abi)
					impl = contract.functions.implementation().call()
					if impl is not None and int(impl,16) != 0:
						addr = web3.toChecksumAddress(impl)
				except Exception as e:
					print( f"Error getting beacon implementation" )
					print( f"{addr}" )
					print( f"{beacon_abi}" )
					print( e )
			break

	if addr is None or int(addr,16) == 0:
		addr = address #Contract was not a proxy, so we return the original address
	else:
		#Cache the abi
		abi = get_cached_abi(addr)
		set_abi(address,abi) #Record this as the abi for the *original* address so future calls to get_cached_abi will get it

	return addr

#if __name__ == '__main__':
#	print( get_rarible_721() )
