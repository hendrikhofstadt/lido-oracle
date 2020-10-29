import json
import logging
import os
import time

from web3 import Web3, WebsocketProvider, HTTPProvider

from beacon import get_beacon
from contracts import get_validators_keys

logging.basicConfig(level=logging.INFO, format='%(levelname)8s %(asctime)s <daemon> %(message)s',
                    datefmt='%m-%d %H:%M:%S')

MAINNET_SECONDS_PER_SLOT = 12
MAINNET_SLOTS_PER_EPOCH = 32
MAINNET_REPORT_INTERVAL_DURATION = 60 * 60 * 24

SECONDS_PER_SLOT = int(os.getenv('SECONDS_PER_SLOT', MAINNET_SECONDS_PER_SLOT))
SLOTS_PER_EPOCH = int(os.getenv('SLOTS_PER_EPOCH', MAINNET_SLOTS_PER_EPOCH))
REPORT_INTERVAL_DURATION = int(os.getenv('REPORT_INTERVAL_DURATION', MAINNET_REPORT_INTERVAL_DURATION))
EPOCH_DURATION = SECONDS_PER_SLOT * SLOTS_PER_EPOCH
# ONE_DAY = 60 * 60 * 24
GENESIS_TIME = None

ts = lambda epoch: int((GENESIS_TIME + (SECONDS_PER_SLOT * SLOTS_PER_EPOCH * epoch)) / REPORT_INTERVAL_DURATION)

logging.info('Starting oracle daemon')

envs = ['ETH1_NODE', 'ETH2_NODE', 'SPR_CONTRACT', 'SPR_ABI_FILE', 'ORACLE_CONTRACT', 'MANAGER_PRIV_KEY',
        'ORACLE_ABI_FILE', 'REPORT_INTVL_SLOTS']
missing = []
for env in envs:
    if env not in os.environ:
        missing.append(env)
        logging.error('Variable %s is missing', env)

if missing:
    exit(1)

spr_abi_path = os.environ['SPR_ABI_FILE']
dp_oracle_abi_path = os.environ['ORACLE_ABI_FILE']
eth1_provider = os.environ['ETH1_NODE']
eth2_provider = os.environ['ETH2_NODE']
oracle_address = os.environ['ORACLE_CONTRACT']
if not Web3.isChecksumAddress(oracle_address):
    oracle_address = Web3.toChecksumAddress(oracle_address)
spr_address = os.environ['SPR_CONTRACT']
if not Web3.isChecksumAddress(spr_address):
    spr_address = Web3.toChecksumAddress(spr_address)
manager_privkey = os.environ['MANAGER_PRIV_KEY']
report_interval_slots = int(os.environ['REPORT_INTVL_SLOTS'])

beacon = get_beacon(eth2_provider, SLOTS_PER_EPOCH)
logging.info('Connecting to %s', beacon)

provider = None

if eth1_provider.startswith('http'):
    provider = HTTPProvider(eth1_provider)
elif eth1_provider.startswith('ws'):
    provider = WebsocketProvider(eth1_provider)
else:
    logging.error('Unsupported ETH provider!')
    exit(1)

w3 = Web3(provider)

if not w3.isConnected():
    logging.error('ETH node connection error!')
    exit(1)

with open(spr_abi_path, 'r') as file:
    a = file.read()
abi = json.loads(a)
spr = w3.eth.contract(abi=abi['abi'], address=spr_address)

with open(dp_oracle_abi_path, 'r') as file:
    a = file.read()
abi = json.loads(a)
oracle = w3.eth.contract(abi=abi['abi'], address=oracle_address)

w3.eth.defaultAccount = w3.eth.account.privateKeyToAccount(manager_privkey)

logging.info('============ CONFIGURATION ============')
logging.info(f'ETH1 Node: {eth1_provider}')
logging.info(f'ETH2 Node: {eth2_provider}')
logging.info(f'Oracle contract address: {oracle_address}')
logging.info(f'Registry contract address: {spr_address}')
logging.info(f'Manager account: {w3.eth.defaultAccount.address}')
logging.info(f'Report interval: {report_interval_slots} slots')
if SECONDS_PER_SLOT != MAINNET_SECONDS_PER_SLOT:
    logging.warning(f'Seconds per slot changed to {SECONDS_PER_SLOT}')
if SLOTS_PER_EPOCH != MAINNET_SLOTS_PER_EPOCH:
    logging.warning(f'Slots per epoch changed to {SLOTS_PER_EPOCH}')
logging.info('=======================================')

# Get genesis time of network
GENESIS_TIME = beacon.get_genesis()

# Get actual slot and last finalized slot from beacon head data
last_slots = beacon.get_actual_slot()
last_finalized_slot = last_slots['finalized_slot']
last_finalized_epoch = int(last_finalized_slot / SLOTS_PER_EPOCH)
actual_slot = last_slots['actual_slot']
# Get current epoch
current_epoch = int(actual_slot / SLOTS_PER_EPOCH)
logging.info('Last finalized epoch %s (slot %s)', last_finalized_epoch, last_finalized_slot)
logging.info('Current epoch %s (slot %s)', current_epoch, actual_slot)

# Get first slot of current epoch
start_slot_current_epoch = current_epoch * SLOTS_PER_EPOCH

# Wait till the next epoch start

# Get first slot of next epoch
start_slot_next_epoch = start_slot_current_epoch + SLOTS_PER_EPOCH
next_epoch = int(start_slot_next_epoch / SLOTS_PER_EPOCH)
logging.info('Next epoch %s (first slot %s)', next_epoch, start_slot_next_epoch)

await_time = (start_slot_next_epoch - actual_slot) * SECONDS_PER_SLOT
logging.info('Wait next epoch seconds %s', await_time)
time.sleep(await_time)

# Get actual slot and last finalized slot from beacon head data
last_slots = beacon.get_actual_slot()
logging.info('The oracle daemon is started!')

# Get last epoch on 7200x slot
before_report_epoch = int(
    (last_slots['finalized_slot'] / report_interval_slots) * (report_interval_slots / SLOTS_PER_EPOCH))
logging.info('Previous 7200x slots epoch %s', before_report_epoch)

# Check if current finalized slot multiple of report_interval_slots
if last_slots['finalized_slot'] % report_interval_slots == 0:
    logging.info('Current finalized slot is multiple of %s', report_interval_slots)
    next_report_epoch = before_report_epoch
else:
    logging.info('Wait next epoch on 7200x slot')
    next_report_epoch = int(before_report_epoch + (report_interval_slots / SLOTS_PER_EPOCH))
last_finalized_epoch = int(last_slots['finalized_slot'] / SLOTS_PER_EPOCH)
# Sleep while last finalized slot reach expected epoch
logging.info('Next epoch %s first slot %s', next_report_epoch, int(next_report_epoch * SLOTS_PER_EPOCH))
while True:
    print(next_report_epoch, last_finalized_epoch)
    if next_report_epoch <= last_finalized_epoch:
        validators_keys = get_validators_keys(spr, w3)
        if len(validators_keys) == 0:
            logging.warning('No keys on Staking Providers Registry contract')
        # Get sum of balances
        sum_balance = beacon.get_balances(next_report_epoch, validators_keys)

        print(ts(next_report_epoch))
        tx_hash = oracle.functions.pushData(ts(next_report_epoch), sum_balance).buildTransaction(
            {'from': w3.eth.defaultAccount.address})
        tx_hash['nonce'] = w3.eth.getTransactionCount(
            w3.eth.defaultAccount.address)  # Get correct transaction nonce for sender from the node
        signed = w3.eth.account.signTransaction(tx_hash, w3.eth.defaultAccount.privateKey)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        logging.info('Transaction in progress...')
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        if tx_receipt.status == 1:
            logging.info('Transaction successful')
            logging.info('Balances pushed!')
        else:
            logging.warning('Transaction reverted')
            # TODO logic when transaction reverted

        next_report_epoch = int(next_report_epoch + (report_interval_slots / SLOTS_PER_EPOCH))
        logging.info('Next report epoch after report %s', next_report_epoch)
    # Get actual slot and last finalized slot from beacon head data
    last_slots = beacon.get_actual_slot()
    last_finalized_epoch = int(last_slots['finalized_slot'] / SLOTS_PER_EPOCH)
    logging.info('Wait finalized epoch %s', int(next_report_epoch))
    logging.info('Current finalized epoch %s', last_finalized_epoch)
    time.sleep(EPOCH_DURATION)
