#!/usr/bin/python3
from brownie import CoMNFT, config, network
from web3 import Web3
from scripts.helpful_scripts import (
    BLOCK_CONFIRMATIONS_FOR_VERIFICATION,
    get_account,
    get_contract,
    is_verifiable_contract,
)


def deploy_nft():
    jobId = config["networks"][network.show_active()]["jobId"]
    jobId = "7d80a6386ef543a3abb52817f6707e3b" #goerli compatible GET string data
    fee = config["networks"][network.show_active()]["fee"]
    account = get_account()
    oracle = get_contract("oracle").address
    link_token = get_contract("link_token").address
    nft = CoMNFT.deploy(
        oracle,
        Web3.toHex(text=jobId),
        fee,
        link_token,
        {"from": account},
    )

    if is_verifiable_contract():
        nft.tx.wait(BLOCK_CONFIRMATIONS_FOR_VERIFICATION)
        CoMNFT.publish_source(nft)

    print(f"CoMNFT deployed to {nft.address}")
    return nft


def main():
    deploy_nft()
