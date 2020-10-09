import binascii
import json

from web3 import Web3, HTTPProvider

pk = '0x6f1313062db38875fb01ee52682cbf6a8420e92bfbc578c5d4fdc0a32c50266f'
node_url = 'http://localhost:8545'
deposit_address = '0x0351690173d2985c766fEC173dcd01A575269726'
deposit_data_file = 'deposit_data-1602227114.json'
mainnet = False


def deposit_local(data):
    tx_hash = deposit_contract.functions.deposit(binascii.unhexlify(data['pubkey']),
                                                 binascii.unhexlify(data['withdrawal_credentials']),
                                                 binascii.unhexlify(data['signature']),
                                                 binascii.unhexlify(data['deposit_data_root'])).transact(
        {'from': w3.eth.defaultAccount.address, 'value': Web3.toWei(32, 'ether')})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(tx_receipt)


def deposit_mainnet(data):
    pass


w3 = Web3(HTTPProvider(node_url))
w3.eth.defaultAccount = w3.eth.account.privateKeyToAccount(pk)

with open('deposit_abi.json', 'r') as file:
    abi = file.read()

deposit_contract = w3.eth.contract(abi=abi, address=deposit_address)
x = deposit_contract.functions.get_deposit_count().call({'from': w3.eth.defaultAccount.address})
print(x)

with open(deposit_data_file, 'r') as file:
    deposit_data = json.loads(file.read())

for validator_data in deposit_data:
    print(validator_data)
    if mainnet:
        deposit_mainnet(validator_data)
    else:
        deposit_local(validator_data)

