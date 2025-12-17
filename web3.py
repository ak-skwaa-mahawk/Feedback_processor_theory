import json
from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware

# Connect to chain (e.g., Polygon testnet)
w3 = Web3(Web3.HTTPProvider('https://rpc-mumbai.maticvigil.com'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Your private key (securely stored, e.g., env var)
private_key = 'YOUR_PRIVATE_KEY_HERE'  # Replace with actual
acct = Account.from_key(private_key)

# Sample smart contract ABI (for a simple SSI contract)
abi = [
    {
        "inputs": [{"name": "hash", "type": "string"}],
        "name": "storeSealHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "hash", "type": "string"}],
        "name": "verifySeal",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Contract address (deploy your own first)
contract_address = '0xYourContractAddressHere'
contract = w3.eth.contract(address=contract_address, abi=abi)

def store_seal_on_chain(seal_hash):
    """Store a seal hash on-chain for sovereignty verification."""
    nonce = w3.eth.get_transaction_count(acct.address)
    txn = contract.functions.storeSealHash(seal_hash).build_transaction({
        'from': acct.address,
        'nonce': nonce,
        'gas': 2000000,
        'gasPrice': w3.to_wei('5', 'gwei')
    })
    signed_txn = acct.sign_transaction(txn)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def verify_seal_on_chain(seal_hash):
    """Verify seal integrity via blockchain."""
    return contract.functions.verifySeal(seal_hash).call()

# Example: Integrate with your seals (e.g., DefenseSeal.svg hash)
defense_hash = '9d153113bd93bd14736c190be7fcff350617eff8542be9b86963ce2fbde3f505'
tx = store_seal_on_chain(defense_hash)
print(f"Seal stored on-chain: {tx}")

# For FPT resonance: Call from feedback_processor.py
# e.g., after resonance check, store result hash on-chain