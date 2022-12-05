from brownie import CoMNFT, APIConsumer, accounts, config, network
from scripts.helpful_scripts import (
    BLOCK_CONFIRMATIONS_FOR_VERIFICATION,
    get_account,
    get_contract,
    is_verifiable_contract,
)

def main():
   account = get_account()
   nft = CoMNFT[-1]
   supply = nft.totalSupply()
   print(f"Current CoMNFTs: {supply}")