from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
import glob
import subprocess
from molecule.Levels import Level

from libcml import Cml
import cml2img
from molecule import Skeletal
from libreact.Reaction import list_without_state

def getMolecule(filename):
    molecule = Cml.Molecule()
    molecule.parse(filename)
    formula = filename.split("/")[-1].split(".cml")[0]
    return {
        "formula": formula,
        "property": molecule.property,
        "isAtom": molecule.is_atom
    }

router = APIRouter()
known_molecules = [filename.split("/")[-1].split(".cml")[0] for filename in glob.glob("data/molecule/*")]
moleculeList = [getMolecule(filename) for filename in glob.glob("data/molecule/*")]

@router.get("/state")
async def get_game_state():
    return {"state": "running"}

@router.get("/molecule")
async def getMolecules():
    return [molecule for molecule in moleculeList if not molecule["isAtom"]]

@router.get("/molecule/{formula}/image")
async def getMoleculeImage(formula):
    state_formula = formula+"(aq)"
    subprocess.run(["python", "cml2img.py", "-f", state_formula, "-o", "preview.png"])
    return FileResponse("preview.png")

@router.get("/molecule/{formula}/skeletal")
async def getMoleculeSkeletal(formula):
    validateFormula(formula)
    path = "img/skeletal/molecule/" + formula + ".png"
    return FileResponse(path)

@router.get("/atom")
async def getAtoms():
    return [molecule for molecule in moleculeList if molecule["isAtom"]]

@router.get("/atom/{symbol}/image")
async def getAtomImage(symbol):
    symbol = stripAtomSymbol(symbol.lower())
    path = "img/atom-" + symbol + ".png"
    return FileResponse(path)

@router.get("/level/current")
async def getCurrentLevel(request: Request):
    current_level: Level = request.app.state.server.level
    return {"points": current_level.get_points(),
             "time": current_level.get_time(),
             "victoryCondition": current_level.cml.victory_condition,
             "hint" : current_level.cml.hint,
             "reactionHint": reactionHint(current_level.cml.reactions_hint),
             "reactingElements" : reactingElements(current_level.elements),
             "reactionLog"  : reactionHint(current_level.reaction_log)
            }

@router.get("/reaction/image/{filename}")
async def getReactionImage(filename):
    path = Skeletal.REACTION_DIR + filename
    return FileResponse(path)

def validateFormula(formula):
    if not formula in known_molecules:
        raise HTTPException(status_code=404, detail="Formula not found")

def stripAtomSymbol(symbol):
    return ''.join(filter(str.isalpha, symbol))[:3]

def reactingElements(elements):
    return [element.formula for element in elements]

def reactionHint(reactions):
    response = []
    for reaction in reactions:
        description = reaction.description
        tags = reaction.tags

        if len(reaction.reactants) == 1 and description == None:
            description = "Dissociates in aqueous solution to form ions"
            tags = ["Acid dissociation", "Ionization"]

        response.append({
            "reactants": list_without_state(reaction.reactants), 
            "products": list_without_state(reaction.products),
            "description": description,
            "tags": tags,
            "reactionPath": Skeletal.reactionFileName(reaction),
            "reactionHintPath" : Skeletal.reactionUnknownProductFileName(reaction) })
    return response


