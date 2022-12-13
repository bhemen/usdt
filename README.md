# Python scripts for analyzing USDT on Ethereum

## USDT

USDT is a fiat-backed stablecoin issued by Tether.  You can read about the off-chain reserves backing USDT at Tether's [transparency](https://tether.to/en/transparency/) page.
Tether currently issues USDT on [14 blockchains](https://tether.to/en/transparency/), but this repository focuses on the contracts that control USDT on Ethereum.
On Ethereum, USDT is implemented as an ERC-20 contract, but it has significant additional functionality beyond the minimum specified by the [ERC-20 standard](https://ethereum.org/en/developers/docs/standards/tokens/erc-20/).

This repository is provided to aid in analysis of the on-chain use of USDT.  If you are considering *using* USDT, please read the [terms of service](https://tether.to/en/legal/).

## Contract overview

The USDT contract is deployed at [0xdAC17F958D2ee523a2206206994597C13D831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7).

Following [OpenZeppelin standards](https://docs.openzeppelin.com/contracts/2.x/api/ownership#Ownable), the USDT contract is "ownable", 
and the owner is [0xC6CDE7C39eB2f0F0095F41570af89eFC2C1Ea828](https://etherscan.io/address/0xC6CDE7C39eB2f0F0095F41570af89eFC2C1Ea828).
The owner is [Gnosis Safe](https://gnosis-safe.io/).  This multisig wallet is a 3-out-of-6 multisig, controlled by the following 6 Externally Owned Accounts

* [0xf4B51B14b9EE30dc37EC970B50a486F37686E2a8](https://etherscan.io/address/0xf4B51B14b9EE30dc37EC970B50a486F37686E2a8)
* [0xEe5207d3c88562fc814496Af0845B34CFD4afc8c](https://etherscan.io/address/0xEe5207d3c88562fc814496Af0845B34CFD4afc8c)
* [0x61D5a4d5Bd270e59E9320243e574288e2a199fED](https://etherscan.io/address/0x61D5a4d5Bd270e59E9320243e574288e2a199fED)
* [0x25bB61643e4881147E6aabb65e6DD45CF2904155](https://etherscan.io/address/0x25bB61643e4881147E6aabb65e6DD45CF2904155)
* [0x4096a34E582664F969753b34dA6E72D55b3C85C1](https://etherscan.io/address/0x4096a34E582664F969753b34dA6E72D55b3C85C1)
* [0x4D915Dd2c56814BD3Db51a1dA35b302BCC9c8973](https://etherscan.io/address/0x4D915Dd2c56814BD3Db51a1dA35b302BCC9c8973)

The contract is also "[Pausable](https://docs.openzeppelin.com/contracts/4.x/api/security#Pausable)", meaning that the owner can pause the contract at will.  In the context of 
USDT, pausing the contract prevents all transfers (including mints and burns).

The contract is "[Blacklistable](https://github.com/centrehq/centre-tokens/blob/master/contracts/v1/Blacklistable.sol)", meaning that special accounts ("Blacklisters") can selectively 
freeze the funds of target users.  Basically, the contract will not process transfers from "Blacklisted" addresses ([See Line 340](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#code)).
It appears that Tether allows you to transfer USDT *to* "blacklisted" addresses.  This diverges from Circle's functionality.

Since mints and burns are special types of transfers, you cannot mint funds to or burn funds from a "blacklisted" address.
Unlike the "Ownable" and "Pausable" which were standardized by OpenZeppelin and used by a wide variety of contracts, the Blacklistable property was developed by Centre and the code seems to be specific to the USDT 
contract.  Other fiat-backed stablecoins (e.g. USDC, USDP, BUSD) implement a similar functionality, but with different terminology and code.

The USDT contract charges a fee on every transfer ([See Line 184](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#code#L184)), [currently that fee is set to 0](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#readContract#F17), 
so effectively there is no fee, but the existence of code supporting a transfer fee indicates an interest in assessing a transfer fee.

## Tools

[get_usdt_configs.py](get_usdt_configs.py) Will scrape all "configuration" events from the USDT contract.  Specifically, it scans the Ethereum blockchain for the following events, 
and records them to [data/usdt_configs.csv](data/usdt_configs.csv).

The events emitted by the USDT contract (e.g. AddedBlacklist, Issue etc) do *not* record the caller's address.  So we have to get that separately.
The script [add_sender.py](add_sender.py) adds a new column ("msg.sender") to [data/usdt_configs.csv](data/usdt_configs.csv).

The file [analysis/usdt_analysis.py](analysis/usdt_analysis.py) does some basic analytics, e.g. counting the number of mints and burns by minter address.

The file [analysis/usdt_frozen_funds.py](analysis/usdt_frozen_funds.py) looks at all the frozen addresses, and gets their USDT balance at the time of their freeze.

## Who's in charge?

All the functionality of the USDT is controlled by the contract owner [0xC6CDE7C39eB2f0F0095F41570af89eFC2C1Ea828](https://etherscan.io/address/0xC6CDE7C39eB2f0F0095F41570af89eFC2C1Ea828).
This means that there is no separation of roles, the same (3-out-of-5) multisig account is in control of issuing, redeeming, blacklisting, clawbacks and pausing.

### Minting

USDT calls the process of "minting" new tokens "issuing."
Issuing new USDT is controlled by the contract owner [0xC6CDE7C39eB2f0F0095F41570af89eFC2C1Ea828](https://etherscan.io/address/0xC6CDE7C39eB2f0F0095F41570af89eFC2C1Ea828).

### Freezing

Tether calls the process of freezing an account's USDT "blacklisting."  

To date, [809 accounts have been frozen](https://bloxy.info/txs/events_sc/0xdac17f958d2ee523a2206206994597c13d831ec7?signature_id=37764)

### Clawbacks

USDT implements "clawbacks" through the "DestroyBlackFunds" function ([See Line 291](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#code#L291)).
As the name implies, Tether only has the ability to remove funds from users that were previously "blacklisted."  Thus a clawback is a two-step process, first the address 
must be frozen, and only then can the funds be removed.  This is not much of a barrier to clawbacks since both steps of the process are controlled by the same address (the owner), 
and both steps can be incorporated into a single transaction.
