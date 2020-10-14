# Oracle Daemon Algorithm specification

This document contains the specification of improved DePool oracle algorithm.

Motivation: 
* more deterministic results
* avoid unnecessary entities and conversions make troubleshooting easier (e.g. oracle now uses epochs through entire the app)
* simpler configuration (some parameters come dynamically from nodes)

# Flow diagram

```
        NETWORK/INFRASTRUCTURE                          ORACLE DAEMON
                                                   +----------------------------+
                                                1. | Start,read config (ENVs)   |
                                                   +------------+---------------+
                                                                |
                                                2. +------------v---------------+
         +----------------------------------------->                            |
         |                  +---------------------->    Get finalized states    <-----+
         |                  |                      +------------+---------------+     |
         |                  |                                   |                     |
         |           +------+------+                            |                     |
         |           |             |               +------------v---------------+     |
         |           |  Beacon     |            3. | Calculate last             |     |
         |           |  Node       |               | frame checkpoint (slot)    |     |
         |           |             |               +------------+---------------+     |
         |           |             |                            |                     |
         |           +-----------+-+               +------------v---------------+     |
         |                       |              4. | Get validators' keys at    |     |
         |     +-----------------------------------> given checkpoint (ETH1 blk)|     |
         |     |                 |                 +------------+---------------+     |
         |     |                 |                              |                     |
         |     |                 |              5. +------------v---------------+     |
         |     |                 +-----------------> Get validator balances     |     |
         |     |                                   | Summarize all balances     |     |
  +------+-------------------------------+         +------------+---------------+     |
  |            |                         |                      |                     |
  |   +--------+----+    +------------+  |      6. +------------v---------------+ Yes |
  |   |             |    |            +------------> Already reported this CP?  +----->
  |   | SP Registry |    | Oracle     |  |         +----------------------------+     |
  |   | Contract    |    | Contract   |  |                    No|                     |
  |   |             |    |      +------------------+------------v-----------+         |
  |   |             |    |      |     |  |      7. | Prepare Transaction    |         |
  |   +-------------+    +------------+  |      8. | Set GasPrice           |         |
  |                             |        |      9. | Expedite TX (+gasPrice)|         |
  |   +-------------------------v-----+  |     10. | Mined                  |         |
  |   |       DePool Contract         |  |     11. | Wait N confirmations   |         |
  |   |                               |  |         +------------+-----------+         |
  |   +-------------------------------+  |                      |                     |
  |                                      |                      |                     |
  |                                      |                      +---------------------^
  |       Ethereum 1.0 node and          |
  |       ETH1.0 contracts               |
  |                                      |
  +--------------------------------------+
```
# Oracle configuration

# Oracle algorithm

## 1. Daemon start

Upon the start, stateless oracle daemon reads its configuration from ENVironment variables or uses default values

### 1.1 Configuration

`ETH1_NODE="http://localhost:8545"` - Web3 indpoint of Ethereum 1.0 PoW mainnet node (tested with go-ethereum). Infura will be supported later.

`BEACON_NODE="http://localhost:5052"` - JSON API of Ethereum 2.0 BeaconChain node (tested with Prysm and Lighthouse).

`DEPOOL_CONTRACT=<addr in 0x hex format>` - DePool Oracle contract in Ethereum mainnet. Other contracts (SP registry, oracle) get discovered via getters.

`EPOCHS_PER_REPORT="225"` - The number of beacon epochs between reports. Oracle uses this variable to deterministically calculate Report CheckPoints - the exact slots by which it collects validators' balances. See paragraph 3 for details.

`MEMBER_PRIV_KEY=<key in 0x hex format>` - Private key that is used to initiate, sign and send periodic report transaction to the Oracle. Must have sufficient Eth balance on it.

`ETH1_CONFIRMATIONS="10"` - The number of subsequent ETH1.0 blocks after which the state considered final. Used for calculating the exact checkpoint block for ETH1.0 (p.3) and dispatching oracle-initiated transactions (p.9).


### 1.2 Main loop

Oracle algorithm runs in a endless loop and each iteration starts from a clean state. This makes oracle to be more sustainable and autonomous, gives more flexibility, allows oracles to survive and recover after the faults of Eth1.0 and Beacon nodes. This approach allows to discover and apply the new settings dynamically (say, change `EPOCHS_PER_REPORT` value) without the need to touch the oracle processes.

* Check all the nodes are up and running. Exit with informative message if not.
* Calculate the balance on `MEMBER_PRIV_KEY`. Must be positive. Exit with informative message if not.
* Check if both ORACLE_CONTRACT are deployed (code length > 0). Exit with informative message if not.

### 1.3 Get Beacon genesis time

```
from dateutil import parser
beacon_genesis_dt = parser.isoparse(prysm.get('/node/genesis')['genesisTime'])
beacon_genesis_time = beacon_genesis_dt.timestamp()
beacon_genesis_time
```

## 2. Get finalized states

```
SECONDS_PER_SLOT=12
```

Oracle uses SECONDS_PER_SLOT constant from [ETH2.0 spec](https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/beacon-chain.md#constants) to calculate the datetime of last finalized checkpoint slot


The daemon constantly polls ETH1.0 and Beacon nodes and retrieves the head states.

```
beacon_finalized_slot = prysm.get('/beacon/chainhead')['finalizedSlot']
last_eth1_block = w3.eth.blockNumber()
finalized_eth1_block = web3.eth.getBlock(last_eth1_block - ETH1_CONFIRMATIONS)
finalized_eth1_block_time = finalized_eth1_block.timestamp

```

## 3. Calculate last report checkpoint

## 4. Get validators pubkeys

## 5. Get validators balances

## 6. Check if daemon should report

## 7. Build transaction

## 8. Set gasPrice

## 9. Expedite transaction

### 9.1. Wait for TX inclusion

### 9.2. Calculate gasPrice increment

### 9.3. Build Tx with increased gasPrice

### 9.4. MAX_GASPRICE achieved

## 10. Tx included into the block

## 11. Waiting for confirmations

# Key components
