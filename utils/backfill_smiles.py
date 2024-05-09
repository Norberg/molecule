import argparse
import subprocess

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem

from libcml import Cml
from libreact.Reaction import Reaction
from libreact.Reaction import verify as Reaction_verify
from libreact.Reactor import sublist_in_list
from libreact.Reactor import Reactor

def fetch_smiles(formula):
    ret = subprocess.Popen(["obabel", "-icml", f"data/molecule/{formula}.cml", "-osmi"], stdout=subprocess.PIPE)
    return ret.stdout.read().decode().strip()


def main():
    # for all files in data/molecule
    for filename in os.listdir("data/molecule"):
        if filename.endswith(".cml"):
            formula = filename.split(".")[0]
            smiles = fetch_smiles(formula)
            if smiles == "":
                print(f"Failed to fetch SMILES for {formula}")
                continue
            molecule = Cml.Molecule()
            molecule.parse(f"data/molecule/{formula}.cml")
            molecule.property["Smiles"] = smiles
            molecule.write(f"data/molecule/{formula}.cml")

if __name__ == "__main__":
    main()