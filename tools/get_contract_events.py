"""
Scan the chain for all events from a specific contract
"""

from .eventscanner import EventScanner, EventScannerState
from .scannerstate import JSONifiedState, TabularState

import datetime
import time
import logging
from typing import Tuple, Optional, Callable, List, Iterable
import json

from web3 import Web3
from web3.contract import Contract
from web3.datastructures import AttributeDict
from web3.exceptions import BlockNotFound
from eth_abi.codec import ABICodec

# Currently this method is not exposed over official web3 API,
# but we need it to construct eth_getLogs parameters
from web3._utils.filters import construct_event_filter_params
from web3._utils.events import get_event_data

import sys
from web3.providers.rpc import HTTPProvider
from tqdm import tqdm

from utils import get_cached_abi, get_event_args, get_proxy_address

logger = logging.getLogger(__name__)

import pandas as pd

#def getContractEvents(api_url,min_start_block,contract_address,outfile,db_columns,scanned_events,abikw=""):
def getContractEvents(api_url,min_start_block,contract_address,outfile,scanned_events,abikw="",follow_proxy=True):
	# Enable logs to the stdout.
	# DEBUG is very verbose level
	logging.basicConfig(level=logging.INFO)

	provider = HTTPProvider(api_url)

	# Remove the default JSON-RPC retry middleware
	# as it correctly cannot handle eth_getLogs block range
	# throttle down.
	provider.middlewares.clear()

	web3 = Web3(provider)

	checksum_address = Web3.toChecksumAddress(contract_address)
	abi_address = checksum_address
	if follow_proxy:
		proxy_address = get_proxy_address(web3,checksum_address) #Check if the address is a proxy contract, and if so get the address of the proxy contract
		proxy_address = Web3.toChecksumAddress(proxy_address)
		if proxy_address != checksum_address:
			print( f"Proxy found: {checksum_address} -> {proxy_address}" )
			abi_address = proxy_address
	abi = get_cached_abi(abi_address,abikw)
	if abi is None:
		print( f"Failed to get abi for {abi_address}" )
		return
	event_names, event_args = get_event_args( checksum_address,scanned_events,abikw)
	db_columns = event_args

	contract = web3.eth.contract(abi=abi)

	state = TabularState(fname=outfile,columns=db_columns)

	# Restore/create our persistent state
	state.restore()

	target_events = [getattr(contract.events,evt) for evt in scanned_events]

	# chain_id: int, web3: Web3, abi: dict, state: EventScannerState, events: List, filters: {}, max_chunk_scan_size: int=10000
	scanner = EventScanner(
		web3=web3,
		contract=contract,
		state=state,
		events=target_events,
		filters={"address": checksum_address}, #Get all events that are from the pool
		# How many maximum blocks at the time we request from JSON-RPC
		# and we are unlikely to exceed the response size limit of the JSON-RPC server
		max_chunk_scan_size=100
	)

	# Assume we might have scanned the blocks all the way to the last Ethereum block
	# that mined a few seconds before the previous scan run ended.
	# Because there might have been a minor Etherueum chain reorganisations
	# since the last scan ended, we need to discard
	# the last few blocks from the previous scan results.
	chain_reorg_safety_blocks = 10
	scanner.delete_potentially_forked_block_data(state.get_last_scanned_block() - chain_reorg_safety_blocks)

	# Scan from [last block scanned] - [latest ethereum block]
	# Note that our chain reorg safety blocks cannot go negative
	start_block = max(state.get_last_scanned_block() - chain_reorg_safety_blocks, min_start_block)
	end_block = scanner.get_suggested_scan_end_block()
	blocks_to_scan = end_block - start_block

	print(f"Scanning events from blocks {start_block} - {end_block}")

	# Render a progress bar in the console
	start = time.time()
	with tqdm(total=blocks_to_scan) as progress_bar:
		def _update_progress(start, end, current, current_block_timestamp, chunk_size, events_count):
			if current_block_timestamp:
				formatted_time = current_block_timestamp.strftime("%d-%m-%Y")
			else:
				formatted_time = "no block time available"
			progress_bar.set_description(f"Current block: {current} ({formatted_time}), blocks in a scan batch: {chunk_size}, events processed in a batch {events_count}")
			progress_bar.update(chunk_size)

		# Run the scan
		result, total_chunks_scanned = scanner.scan(start_block, end_block, progress_callback=_update_progress)

	state.save()
	duration = time.time() - start
	print(f"Scanned total {len(result)} Transfer events, in {duration} seconds, total {total_chunks_scanned} chunk scans performed")

