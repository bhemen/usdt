# Schema 

## USDT ([Link to Box](https://upenn.box.com/s/h0gm29etd67y499o5yqdxxphs2b5e46p))

We've parsed events emitted by [USDT contract](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7) using this [Ethereum Log Parser](https://github.com/niuniu-zhang/Ethereum-Log-Parser) and uploaded them into [Box](https://upenn.box.com/s/h0gm29etd67y499o5yqdxxphs2b5e46p). Here are the descriptions of schema for each event:

### AddedBlackList 

The file `usdt_AddedBlackList.csv` contains all the "AddedBlackList" events emitted by the relevant USDT contract. The dataset includes the following fields:

* `event` - The name of the event (in this case, "AddedBlackList").
* `logIndex` - The index of this specific event within the transaction.
* `transactionIndex` - The index position of the transaction within the block.
* `transactionHash` - The hash of the transaction that triggered this event.
* `address` - The address of the contract that generated this event.
* `blockHash` - The hash of the block where this event was recorded.
* `blockNumber` - The number of the block where this event was recorded.
* `_user` - The address of the user who is being added to the blacklist.
* `block_timestamp` - The timestamp of the block where this event was recorded.

### Approval

The file `usdt_Approval.csv` contains all the "Approval" events emitted by the relevant USDT contract. The dataset includes the following fields:

* `event` - The name of the event (in this case, "Approval").
* `logIndex` - The index of this specific event within the transaction.
* `transactionIndex` - The index position of the transaction within the block.
* `transactionHash` - The hash of the transaction that triggered this event.
* `address` - The address of the contract that generated this event.
* `blockHash` - The hash of the block where this event was recorded.
* `blockNumber` - The number of the block where this event was recorded.
* `owner` - The address of the owner in the approval event.
* `spender` - The address of the spender in the approval event.
* `value` - The value involved in the approval event.
* `block_timestamp` - The timestamp of the block where this event was recorded.

### DestroyedBlackFunds

The file `usdt_DestroyedBlackFunds.csv` contains all the "DestroyedBlackFunds" events emitted by the relevant USDT contract. The dataset includes the following fields:

* `event` - The name of the event (in this case, "DestroyedBlackFunds").
* `logIndex` - The index of this specific event within the transaction.
* `transactionIndex` - The index position of the transaction within the block.
* `transactionHash` - The hash of the transaction that triggered this event.
* `address` - The address of the contract that generated this event.
* `blockHash` - The hash of the block where this event was recorded.
* `blockNumber` - The number of the block where this event was recorded.
* `_blackListedUser` - The address of the blacklisted user in the event.
* `_balance` - The balance that was destroyed in the event.
* `block_timestamp` - The timestamp of the block where this event was recorded.

### Issue

The file `usdt_Issue.csv` contains all the "Issue" events emitted by the relevant USDT contract. The dataset includes the following fields:

* `event` - The name of the event (in this case, "Issue").
* `logIndex` - The index of this specific event within the transaction.
* `transactionIndex` - The index position of the transaction within the block.
* `transactionHash` - The hash of the transaction that triggered this event.
* `address` - The address of the contract that generated this event.
* `blockHash` - The hash of the block where this event was recorded.
* `blockNumber` - The number of the block where this event was recorded.
* `amount` - The amount of USDT issued in the event.
* `block_timestamp` - The timestamp of the block where this event was recorded.

### Redeem

The file `usdt_Redeem.csv` contains all the "Redeem" events emitted by the relevant USDT contract. The dataset includes the following fields:

* `event` - The name of the event (in this case, "Redeem").
* `logIndex` - The index of this specific event within the transaction.
* `transactionIndex` - The index position of the transaction within the block.
* `transactionHash` - The hash of the transaction that triggered this event.
* `address` - The address of the contract that generated this event.
* `blockHash` - The hash of the block where this event was recorded.
* `blockNumber` - The number of the block where this event was recorded.
* `amount` - The amount of USDT redeemed in the event.
* `block_timestamp` - The timestamp of the block where this event was recorded.

### RemovedBlackList

The file `usdt_RemovedBlackList.csv` contains all the "RemovedBlackList" events emitted by the relevant USDT contract. The dataset includes the following fields:

* `event` - The name of the event (in this case, "RemovedBlackList").
* `logIndex` - The index of this specific event within the transaction.
* `transactionIndex` - The index position of the transaction within the block.
* `transactionHash` - The hash of the transaction that triggered this event.
* `address` - The address of the contract that generated this event.
* `blockHash` - The hash of the block where this event was recorded.
* `blockNumber` - The number of the block where this event was recorded.
* `_user` - The address of the user who is being removed from the blacklist.
* `block_timestamp` - The timestamp of the block where this event was recorded.

### Transfer

The file `usdt_Transfer.csv` has been split into two parts due to its large size: `Part 1` and `Part 2`. These files contain all the "Transfer" events emitted by the relevant USDT contract. The dataset includes the following fields:

* `event` - The name of the event (in this case, "Transfer").
* `logIndex` - The index of this specific event within the transaction.
* `transactionIndex` - The index position of the transaction within the block.
* `transactionHash` - The hash of the transaction that triggered this event.
* `address` - The address of the contract that generated this event.
* `blockHash` - The hash of the block where this event was recorded.
* `blockNumber` - The number of the block where this event was recorded.
* `from` - The address of the sender in the transfer event.
* `to` - The address of the receiver in the transfer event.
* `value` - The value of the transfer.
* `block_timestamp` - The timestamp of the block where this event was recorded.