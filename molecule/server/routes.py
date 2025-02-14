from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import glob
import subprocess

from libcml import Cml
import cml2img
#import utils.rdkit_render as rdkit_render


router = APIRouter()

@router.get("/state")
async def get_game_state():
    return {"state": "running"}

@router.get("/molecule")
async def getMolecules():
    return [getMolecule(filename) for filename in glob.glob("data/molecule/*")]


@router.get("/molecule/{formula}/image")
async def getMoleculeImage(formula):
    state_formula = formula+"(aq)"
    #cml2img.convert_cml2ipng(state_formula, "preview.png")
    ## run cmd like python cml2img.py -f "H2O(aq)" -o preview.png
    subprocess.run(["python", "cml2img.py", "-f", state_formula, "-o", "preview.png"])
    return FileResponse("preview.png")

@router.get("/molecule/{formula}/skeletal")
async def getMoleculeSkeletal(formula):
    rdkit_render.render_individual_molecule(formula, None, "preview-skeletal.png")
    return FileResponse("preview-skeletal.png")


def getMolecule(filename):
    molecule = Cml.Molecule()
    molecule.parse(filename)
    formula = filename.split("/")[-1].split(".cml")[0]
    return {"formula": formula, "property": molecule.property}

    