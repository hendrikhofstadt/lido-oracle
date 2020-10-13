# Oracle Daemon Algorithm specification

This document contains the specification of improved DePool oracle algorithm.

Motivation: the algorithm should provide deterministic results in real-world scenarios.

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

## 2. Get finalized states

## 3. Calculate last checkpoint

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
