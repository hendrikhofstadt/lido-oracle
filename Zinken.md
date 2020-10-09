**Zinken testnet HOWTO**

Faucet  
First of all you need at least 32eth on you account
https://faucet.goerli.mudit.blog/

1. Official launchpad  
Go to https://zinken.launchpad.ethereum.org  
Press Get started  
Overview stage accept everything  
Client Selection choose and set up eth1 client  
[Geth example](Zinken/docker-compose.geth.yml)

Generate Keys  
Here wil bw link to script for key generation  
https://github.com/ethereum/eth2.0-deposit-cli  
Script require python 3.7 and ubuntu 18.04 support only 3.6.9  
So we can run it in docker  
```bash
docker run -it -v ${HOME}/keys:/keys python:3-slim bash
```
Inside container run  
```bash
apt update
apt install git gcc
git clone https://github.com/ethereum/eth2.0-deposit-cli.git
cd eth2.0-deposit-cli
./deposit.sh install
./deposit.sh --num_validators=1 --mnemonic_language=english --chain=zinken --folder=/keys
```
Fallow instruction and validator keys will be generated in volume (${HOME}/keys in this example)

Upload Validator  
Here you need to drag **deposit-data-[timestamp].json** file from generated keys directory to browser window.Page require metamask or any other wallet were connected. Transaction to deposit contract will be generated.
 
After this you'll see instructions how to set up validator
https://docs.prylabs.network/docs/testnet/zinken/  
[Beacon setup](Zinken/docker-compose.beacon.prysm.yml)  
To set up validator 
First you have to import validator keys
```bash
docker run -it -v ${HOME}/keys/validator_keys:/keys \
  -v ${HOME}/Eth2Validators/prysm-wallet-v2:/wallet \
  -v ${HOME}/Eth2:/validatorDB \
  --name validator \
  gcr.io/prysmaticlabs/prysm/validator:latest \
  accounts-v2 import --keys-dir=/keys --wallet-dir=/wallet --datadir=/validatorDB --zinken
```
To run validator using imported keys run
```bash
docker run -it -v $HOME/Eth2Validators/prysm-wallet-v2:/wallet \
  -v $HOME/Eth2:/validatorDB \
  --network="host" --name validator \
  gcr.io/prysmaticlabs/prysm/validator:latest \
  --beacon-rpc-provider=127.0.0.1:4000 \
  --wallet-dir=/wallet --datadir=/validatorDB --zinken
```
Alternative validator setup
```bash
mkdir prysm && cd prysm
curl https://raw.githubusercontent.com/prysmaticlabs/prysm/master/prysm.sh --output prysm.sh && chmod +x prysm.sh
./prysm.sh validator --wallet-dir=/opt/prysm-wallet-v2 --beacon-rpc-provider=95.217.143.215:4000 --zinken
```

https://zinken.launchpad.ethereum.org/lighthouse/  
[Beacon setup](Zinken/docker-compose.beacon.lh.yml)

First you have to import validator keys
```bash
docker run -it \
    -v /opt/data/.lighthouse:/root/.lighthouse \
    -v ${HOME}/keys/validator_keys:/validator_keys \
    sigp/lighthouse:v0.3.0 \
    lighthouse --testnet zinken account validator import --directory /validator_keys
```

Manual deposit
First you need:
* deposit-data-[timestamp].json
* eth account private key
* eth1 node url
Write all this data to [deposite.py](Zinken/deposit.py) variables
Set mainnet variable to True for mainnet, or to False for ganache
Run script
