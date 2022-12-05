from rdkit import Chem
from flask import *
import urllib.request, json

app = Flask(__name__)
app.secret_key = "SECRET"

@app.route("/validate/<cid>",methods=["GET"])
def submit(cid):
   if request.method == "GET":
      with urllib.request.urlopen("https://ipfs.io/ipfs/" + cid) as url:
         data = json.load(url)
         smiles = data["smiles"]
         try:
            mol = Chem.MolFromSmiles(smiles)
            smiles = Chem.MolToSmiles(mol)
            return jsonify({"smiles":smiles}), 200
         except:
            return jsonify({"smiles": "`"}), 400

