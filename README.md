# CoM-NFT
## Motivation
Claiming and transacting composition of matter (CoM) intellectual property (IP) is a common operation of companies in the materials and life science sectors.
Composition of matter patents are used to protect assets involving the formulation of chemicals/compounds
to serve a purpose. CoM patents are commonly sought by biotech and pharma companies to protect
novel small molecule therapies. Prior to patent protection, companies will often exchange extensive
libraries of investigational chemicals to be further studied, developed, and commercialized by other
entities. The goal of this project is to validate and define ownership of CoM IP on chain to facilitate
these transactions at scale. 

## Implementation
This project implements an ERC721 NFT smart contract to define CoM on chain in the form of SMILES strings. While anyone is able to mint
new CoM-NFTs, several security checks and handshakes occur prior to ensure:
1. The minter provides a valid SMILES string, i.e. one which corresponds to a physically viable molecule
2. The provided SMILES string is canonical so alternative valid representations cannot be minted
3. The provided canonical SMILES string matches that which is defined in its metadata (file on IPFS)
4. The provided canonical SMILES string has not been minted before

These security checks are accomplished through a combination of off-chain validations (via oracles)
in addition to on-chain SMILES hashing to define a non-repeatable NFT ID.  

A barebones REST API is currently deployed off-chain [here](https://smiles-validator.onrender.com/validate/QmRrmHZffDGtLBvR6YbpTs2AXDqJCZWqTherk5FPxmNF9Z) using [Render](https://render.com/). 
Prior to minting a given SMILES string, a Chainlink oracle queries this API to ensure that said SMILES string is valid, canonical, and represented in the NFT's metadata file on IPFS.

This project made use of the Chainlink brownie mix to inform contract creation and deployment. 

## Prerequisites
Please ensure the following are installed:
* Python
* Brownie

Python packages necessary for scripts:
* rdkit

Python packages necessary to redeploy REST API:
* flask
* gunicorn
* rdkit

Create a Pinata account and obtain API keys to run minting scripts.

Then create a wallet with Goerli (only tested here) test ETH and LINK (available from faucets). Test LINK is needed to enable Chainlink verification.
After cloning this repo, create a .env file in the root directory formatted as follows (fill in environment vars):
```buildoutcfg
export PRIVATE_KEY=
export WEB3_INFURA_PROJECT_ID=
export PinataAPIKey=
export PinataAPISecret=
```

## Running
To deploy the CoMNFT smart contract run the following in the root directory:
```buildoutcfg
brownie run scripts/deploy.py --network goerli
```
To mint new tokens corresponding to compounds denoted in scripts/mint.tsv:
```buildoutcfg
brownie run scripts/minting.py --network goerli
```
This will pin metadata to IPFS that includes the SMILES string, compound name, a URL pointing to 
an image of the molecular structure (logged in the terminal), and a sample chemical property (molecular weight) computed at runtime
which could potentially be used by relevant parties to communicate/mine useful information. Edit scripts/mint.tsv to 
try different compounds. 

To check number of tokens (supply) successfully minted (validated with oracle and not previosly minted):
```buildoutcfg
brownie run scripts/supply.py --network goerli
```
Note that because an oracle must validate the provided SMILES prior to minting, changes in supply may take a few
moments to take effect. If no change is observed over an extended period of time, the SMILES string
provided likely already was minted, was not canonically represented, or chemically invalid.