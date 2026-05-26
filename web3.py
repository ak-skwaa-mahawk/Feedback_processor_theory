import os
import json
from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware

# === CONFIGURATION & CONNECTIVITY ===
# Connect to Polygon Amoy Testnet (or change to Polygon Mainnet RPC for live deployment)
RPC_URL = 'https://rpc-amoy.polygon.technology'
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Inject POA middleware for compatibility with proof-of-authority consensus layers
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Verify connection integrity
if not w3.is_connected():
    raise ConnectionError("Failed to connect to the decentralized network node.")

# === ACCOUNT SECURITY ===
# Securely fetch private key from environmental variables to prevent hardcoding leaks
PRIVATE_KEY = os.getenv('SOVEREIGN_PRIVATE_KEY', '0xYOUR_HEX_PRIVATE_KEY_HERE_IF_TESTING')
if PRIVATE_KEY.startswith('0x'):
    PRIVATE_KEY = PRIVATE_KEY[2:]

acct = Account.from_key(bytes.fromhex(PRIVATE_KEY))
print(f"Sovereign Entity Initialized. Address: {acct.address}")

# === SMART CONTRACT INTEGRATION ===
# Application Binary Interface (ABI) for interacting with the deployed seal registry
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

# The active deployment address of your smart contract
CONTRACT_ADDRESS = w3.to_checksum_address('0x0000000000000000000000000000000000000000') # Replace with actual contract address
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# === OPERATIONS ===
def store_seal_on_chain(seal_hash: str) -> str:
    """
    Signs and broadcasts a transaction anchoring the FPT state hash to the blockchain ledger.
    """
    # Fetch current transaction count for account sequencing
    nonce = w3.eth.get_transaction_count(acct.address)
    
    # Dynamically estimate modern EIP-1559 gas fees to ensure optimal network execution
    base_fee = w3.eth.get_block('latest')['baseFeePerGas']
    max_priority_fee = w3.to_wei('2.5', 'gwei') # Tip for validator prioritization
    max_fee = (base_fee * 2) + max_priority_fee

    # Build the transaction payload targeting the smart contract function
    txn = contract.functions.storeSealHash(seal_hash).build_transaction({
        'from': acct.address,
        'nonce': nonce,
        'gas': 150000,  # Standard limit for storing a string hash
        'maxFeePerGas': max_fee,
        'maxPriorityFeePerGas': max_priority_fee,
        'chainId': 80002  # Polygon Amoy Testnet Chain ID (Change to 137 for Polygon Mainnet)
    })
    
    # Locally sign the transaction using the sovereign private key
    signed_txn = acct.sign_transaction(txn)
    
    # Broadcast raw transaction to the distributed network
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction broadcasted. Hash: {tx_hash.hex()}")
    
    # Wait for the transaction to be mined and sealed into a block
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Block confirmation achieved. Status: {receipt['status']} | Block: {receipt['blockNumber']}")
    
    return tx_hash.hex()

def verify_seal_on_chain(seal_hash: str) -> bool:
    """
    Queries the ledger to check if a specific FPT hash has been officially recorded.
    """
    try:
        return contract.functions.verifySeal(seal_hash).call()
    except Exception as e:
        print(f"Verification call failed: {e}")
        return False

# === EXECUTION INTEGRATION ===
if __name__ == "__main__":
    # Example: Processing a hash generated from your localized files or defense SVGs
    defense_hash_example = '9d153113bd93bd14736c190be7fcff350617eff8542be9b86963ce2fbde3f505'
    
    print("\n--- Initializing Ledger Anchor Loop ---")
    # Uncomment the line below to execute live broadcasts when your contract is ready
    # tx_record = store_seal_on_chain(defense_hash_example)
    
    # Verify presence on the distributed architecture
    is_valid = verify_seal_on_chain(defense_hash_example)
    print(f"Ledger Integrity Status for Hash [{defense_hash_example[:10]}...]: {is_valid}")
