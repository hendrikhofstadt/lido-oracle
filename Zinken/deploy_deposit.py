from solcx import compile_files, set_solc_version, install_solc
from web3 import Web3, HTTPProvider

deposit_file = 'deposit.sol'
deposit_contract_name = 'DepositContract'

node_url = 'http://localhost:8545'
pk = '0x6f1313062db38875fb01ee52682cbf6a8420e92bfbc578c5d4fdc0a32c50266f'


def deploy_contract(contract_interface):
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    tx_hash = contract.constructor().transact({'from': w3.eth.defaultAccount.address})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print('Contract deployed at address:', tx_receipt.contractAddress)


w3 = Web3(HTTPProvider(node_url))
w3.eth.defaultAccount = w3.eth.account.privateKeyToAccount(pk)

install_solc('v0.6.11')
set_solc_version('v0.6.11')
compiled_sol = compile_files([deposit_file])
deposit_interface = compiled_sol[deposit_file + ':' + deposit_contract_name]

deploy_contract(deposit_interface)
