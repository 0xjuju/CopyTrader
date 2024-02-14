
from blockchain.alchemy import Blockchain
from blockchain.blockscsan import Blockscan


def is_likely_bot(wallet: str, chain: str) -> bool:
    blockchain = Blockchain(chain)
    blockscan = Blockscan(chain)

    address = blockchain.checksum_address(wallet)
    normal_tx_list = blockscan.get_normal_transaction_list(address=address)
    txs = normal_tx_list["result"]

    for tx in txs:
        if "swap" in tx["functionName"]:
            print(tx)





