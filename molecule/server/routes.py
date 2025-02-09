from fastapi import APIRouter, HTTPException
from libcml import Cml
import glob


router = APIRouter()

@router.get("/state")
async def get_game_state():
    return {"state": "running"}

@router.get("/molecule")
async def getMolecules():
    return [getMolecule(filename) for filename in glob.glob("data/molecule/*")]

def getMolecule(filename):
    molecule = Cml.Molecule()
    molecule.parse(filename)
    formula = filename.split("/")[-1].split(".cml")[0]
    return {"formula": formula, "property": molecule.property}

    