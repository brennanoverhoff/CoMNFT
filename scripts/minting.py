from brownie import CoMNFT, APIConsumer, accounts, config, network
from scripts.helpful_scripts import get_account, fund_with_link
import os
from rdkit import Chem
import rdkit.Chem.Draw
import rdkit.Chem.Descriptors
from pinatapy import PinataPy
from dotenv import load_dotenv
import json
load_dotenv()

def main():
   generate_tsv(["Aspirin","Osimertinib","Repsox"],["CC(=O)OC1=CC=CC=C1C(=O)O","CN1C=C(C2=CC=CC=C21)C3=NC(=NC=C3)NC4=C(C=C(C(=C4)NC(=O)C=C)N(C)CCN(C)C)OC","CC1=NC(=CC=C1)C2=C(C=NN2)C3=NC4=C(C=C3)N=CC=C4"],"scripts/mint.tsv")
   mint("scripts/mint.tsv")

def mint(path):
   pinata_api_key = str(os.environ.get('PinataAPIKey'))
   pinata_secret_api_key = str(os.environ.get('PinataAPISecret'))
   pinata = PinataPy(pinata_api_key, pinata_secret_api_key)
   with open(path,'r') as file:
      lines = file.readlines()
      names = [l.split('\t')[0] for l in lines]
      smis = [l.split('\t')[1] for l in lines]
   for s in smis:
      name = names[smis.index(s)]
      print(f"Beginning mint for {name}...")
      mol = Chem.MolFromSmiles(s)
      s = Chem.MolToSmiles(mol) #canonicalize
      mw = Chem.Descriptors.ExactMolWt(mol)
      Chem.Draw.MolToFile(mol,f"scripts/metadata/{name}.png")
      image_cid = pinata.pin_file_to_ipfs(f"scripts/metadata/{name}.png")["IpfsHash"]
      image_url = f"https://ipfs.io/ipfs/{image_cid}/metadata/{name}.png"
      print(image_url)
      meta = {
         "name": "CoM NFTs",
         "description": f"SMILES: {s}",
         "image": image_url,
         "data": {
            "cmpdName": name,
            "cmpdProperties": {
               "MW": mw #sample chemical property than could be tracked with CoMNFTs
            }
         },
         "smiles": s
      }
      with open(f"{name}.json",'w') as file:
         metas = json.dumps(meta)
         file.write(metas)
      meta_cid = pinata.pin_file_to_ipfs(f"{name}.json")["IpfsHash"]
      print(f"https://ipfs.io/ipfs/{meta_cid}")
      os.remove(f"{name}.json")
      account = get_account()
      nft = CoMNFT[-1]
      print("Transfering LINK to smart contract...")
      tx = fund_with_link(
         nft.address, amount=config["networks"][network.show_active()]["fee"]
      )
      tx.wait(1)
      print(f"Deployed CoMNFT contract: {nft}")
      supply = nft.totalSupply()
      print(f"Supply prior to minting: {supply}")
      smiles = s
      tokenURI = meta_cid
      print("Requesting mint...")
      tx = nft.mintCoM(account, smiles, tokenURI, {"from": account})
      print(f"Minting transaction: {tx}")
      supply = nft.totalSupply()
      print(f"Supply after sending mint request: {supply}")

def generate_tsv(names,smiles,path):
   lines = [f"{n}\t{s}\n" for n,s in zip(names,smiles)]
   with open(path,'w') as file:
      file.writelines(lines)