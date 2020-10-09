from solcx import compile_files, set_solc_version, install_solc
from web3 import Web3, HTTPProvider

oracle_file = '../../depool-dao/zinken/OracleMinimalMock.sol'
oracle_contract_name = 'OracleMinimalMock'
spr_file = '../../depool-dao/zinken/SPRMinimalMock.sol'
spr_contract_name = 'SPRMinimalMock'

node_url = 'http://localhost:8545'
pk = '0x6f1313062db38875fb01ee52682cbf6a8420e92bfbc578c5d4fdc0a32c50266f'


def deploy_to_local(contract_interface):
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    tx_hash = contract.constructor().transact({'from': w3.eth.defaultAccount.address})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print('Contract deployed at address:', tx_receipt.contractAddress)


def deploy_to_external(contract_interface):
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    transaction = contract.constructor().buildTransaction({'from': w3.eth.defaultAccount.address})
    transaction['nonce'] = w3.eth.getTransactionCount(
        w3.eth.defaultAccount.address)  # Get correct transaction nonce for sender from the node
    signed = w3.eth.account.signTransaction(transaction, w3.eth.defaultAccount.privateKey)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    print('Transaction hash:', tx_hash)
    print('Deploy in progress...')
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print('Contract deployed at address:', tx_receipt.contractAddress)


w3 = Web3(HTTPProvider(node_url))
w3.eth.defaultAccount = w3.eth.account.privateKeyToAccount(pk)

install_solc('v0.4.24')
set_solc_version('v0.4.24')
compiled_sol = compile_files([oracle_file])
oracle_interface = compiled_sol[oracle_file + ':' + oracle_contract_name]
deploy_to_local(oracle_interface)

compiled_sol = compile_files([spr_file])
spr_interface = compiled_sol[spr_file + ':' + spr_contract_name]
deploy_to_local(spr_interface)
