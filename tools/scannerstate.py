"""A stateful event scanner for Ethereum-based blockchains using Web3.py.

With the stateful mechanism, you can do one batch scan or incremental scans,
where events are added wherever the scanner left off.
"""

from .eventscanner import EventScanner, EventScannerState

import datetime
import time
import logging
from typing import Tuple, Optional, Callable, List, Iterable

from web3 import Web3
from web3.datastructures import AttributeDict
import json
import pandas as pd

logger = logging.getLogger(__name__)

class TabularState(EventScannerState):
	"""Store the state of scanned blocks and all events.

	All state is an in-memory dict.
	Simple load/store massive csv on start up.
	"""

	def __init__(self,fname="",columns=[]):
		self.state = None
		self.columns = columns
		if fname == "":
			self.fname = "test-state.csv"
		else:
			self.fname = fname
		# How many second ago we saved the JSON file
		self.last_save = 0

	def reset(self):
		"""Create initial state of nothing scanned."""
		base_columns = ['event_name','block_number', 'txhash', 'log_index', 'timestamp' ] 
		self.state = {
			"last_scanned_block": 0,
			"blocks": pd.DataFrame(columns=base_columns + self.columns)
		}

	def restore(self):
		"""Restore the last scan state from a file."""
		try:
			self.state = {}
			self.state['blocks'] = pd.read_csv(self.fname)
		except Exception as e:
			print("State starting from scratch #1")
			self.reset()
			return 

		if self.state['blocks'].shape[0] == 0:
			print("State starting from scratch #2")
			self.reset()
			return

		self.state['last_scanned_block'] = int( self.state['blocks']['block_number'].max() ) #Note pd ints are not JSON serializable

		if pd.isnull( self.state['last_scanned_block'] ):
			print("State starting from scratch #3")
			self.reset()
			return

		print(f"Restored the state, previously {self.state['last_scanned_block']} blocks have been scanned")

	def save(self):
		"""Save everything we have scanned so far in a file."""
		self.state['blocks'].to_csv(self.fname,index=False,header=True)
		self.last_save = time.time()

	#
	# EventScannerState methods implemented below
	#

	def get_last_scanned_block(self):
		"""The number of the last block we have stored."""
		return self.state["last_scanned_block"]

	def delete_data(self, since_block):
		"""Remove potentially reorganised blocks from the scan data."""
		since = max(since_block,0)
		if since < self.get_last_scanned_block():
			#self.state['blocks'] = self.state['blocks'].query(f"{since} < block_number")
			self.state['blocks'] = self.state['blocks'][self.state['blocks']['block_number'] < since]

	def start_chunk(self, block_number, chunk_size):
		pass

	def end_chunk(self, block_number):
		"""Save at the end of each block, so we can resume in the case of a crash or CTRL+C"""
		# Next time the scanner is started we will resume from this block
		self.state["last_scanned_block"] = block_number

		# Save the database file for every minute
		if time.time() - self.last_save > 60:
			self.save()

	def process_event(self, block_when: datetime.datetime, event: AttributeDict) -> str:
		"""Record a ERC-20 transfer in our database."""
		# Events are keyed by their transaction hash and log index
		# One transaction may contain multiple events
		# and each one of those gets their own log index

		args = event["args"]

		#print( event.keys() )

		row = { 
			'event_name': event.event,
			'contract_address': event.address,
			'block_number': event.blockNumber, 
			'txhash': event.transactionHash.hex(), 
			'log_index': event.logIndex,
			'timestamp': block_when.isoformat(),
		}

		extra_cols = list( set( args.keys() ).intersection( self.state['blocks'].columns ).difference( row.keys() ) )
		if len(extra_cols) > 0:	
			row.update( { col: args[col] for col in extra_cols } )
		else:
			print( "Error: This event didn't match any extra columns in the table" )
			print( "Are you sure your table has the correct column names?" )

	
		#print( self.state['blocks'].columns )	
		#print( pd.DataFrame([row]).columns )
		self.state['blocks'] = pd.concat( [self.state['blocks'], pd.DataFrame( [row] )] )
		#self.state['blocks'] = self.state['blocks'].append(row,ignore_index=True)

		# Return a pointer that allows us to look up this event later if needed
		return f"{event.blockNumber}-{event.transactionHash.hex()}-{event.logIndex}"

class JSONifiedState(EventScannerState):
	"""Store the state of scanned blocks and all events.

	All state is an in-memory dict.
	Simple load/store massive JSON on start up.
	"""

	def __init__(self):
		self.state = None
		self.fname = "test-state.json"
		# How many second ago we saved the JSON file
		self.last_save = 0

	def reset(self):
		"""Create initial state of nothing scanned."""
		self.state = {
			"last_scanned_block": 0,
			"blocks": {},
		}

	def restore(self):
		"""Restore the last scan state from a file."""
		try:
			self.state = json.load(open(self.fname, "rt"))
			print(f"Restored the state, previously {self.state['last_scanned_block']} blocks have been scanned")
		except (IOError, json.decoder.JSONDecodeError):
			print("State starting from scratch")
			self.reset()

	def save(self):
		"""Save everything we have scanned so far in a file."""
		with open(self.fname, "wt") as f:
			json.dump(self.state, f)
		self.last_save = time.time()

	#
	# EventScannerState methods implemented below
	#

	def get_last_scanned_block(self):
		"""The number of the last block we have stored."""
		return self.state["last_scanned_block"]

	def delete_data(self, since_block):
		"""Remove potentially reorganised blocks from the scan data."""
		for block_num in range(since_block, self.get_last_scanned_block()):
			if block_num in self.state["blocks"]:
				del self.state["blocks"][block_num]

	def start_chunk(self, block_number, chunk_size):
		pass

	def end_chunk(self, block_number):
		"""Save at the end of each block, so we can resume in the case of a crash or CTRL+C"""
		# Next time the scanner is started we will resume from this block
		self.state["last_scanned_block"] = block_number

		# Save the database file for every minute
		if time.time() - self.last_save > 60:
			self.save()

	def process_event(self, block_when: datetime.datetime, event: AttributeDict) -> str:
		"""Record a ERC-20 transfer in our database."""
		# Events are keyed by their transaction hash and log index
		# One transaction may contain multiple events
		# and each one of those gets their own log index

		# event_name = event.event # "Transfer"
		log_index = event.logIndex  # Log index within the block
		# transaction_index = event.transactionIndex  # Transaction index within the block
		txhash = event.transactionHash.hex()  # Transaction hash
		block_number = event.blockNumber

		# Convert ERC-20 Transfer event to our internal format
		args = event["args"]
		transfer = {
			"from": args["from"],
			"to": args.to,
			"value": args.value,
			"timestamp": block_when.isoformat(),
		}

		# Create empty dict as the block that contains all transactions by txhash
		if block_number not in self.state["blocks"]:
			self.state["blocks"][block_number] = {}

		block = self.state["blocks"][block_number]
		if txhash not in block:
			# We have not yet recorded any transfers in this transaction
			# (One transaction may contain multiple events if executed by a smart contract).
			# Create a tx entry that contains all events by a log index
			self.state["blocks"][block_number][txhash] = {}

		# Record ERC-20 transfer in our database
		self.state["blocks"][block_number][txhash][log_index] = transfer

		# Return a pointer that allows us to look up this event later if needed
		return f"{block_number}-{txhash}-{log_index}"

