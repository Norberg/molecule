from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
import glob
import subprocess
import json
from molecule.Levels import Level

from libcml import Cml
import cml2img
from molecule import Skeletal
from molecule.Universe import universe
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
with open("data/reactions/tag_descriptions.json", "r") as f:
    tag_descriptions = json.load(f)

@router.get("/state")
async def get_game_state():
    return {"state": "running"}

@router.get("/reactions/tags")
async def getTags():
    return tag_descriptions

@router.get("/molecule")
async def getMolecules(request: Request):
    levels = request.app.state.server.levels
    if levels is None or levels.player_id is None:
        return []
    seen_formulas = levels.persistence.get_seen_molecules(levels.player_id)
    created_counts = levels.persistence.get_created_molecules(levels.player_id)
    
    response = []
    for molecule in moleculeList:
        if not molecule["isAtom"] and molecule["formula"] in seen_formulas:
            mol_data = molecule.copy()
            mol_data["createdCount"] = created_counts.get(molecule["formula"], 0)
            response.append(mol_data)
    return response

@router.get("/reaction")
async def getReactions(request: Request):
    levels = request.app.state.server.levels
    if levels.player_id is None:
        return []
    performed_reactions = levels.persistence.get_performed_reactions(levels.player_id)
    
    # Map reaction_title back to reaction details if possible
    # We'll use a dictionary to lookup reactions by their key
    reaction_lookup = {r.reaction_key: r for r in universe.reactor.reactions}
    
    response = []
    for perf in performed_reactions:
        title = perf["reaction_title"]
        count = perf["total_count"]
        
        reaction_cml = reaction_lookup.get(title)
        if reaction_cml:
            reaction_data = {
                "reactants": list_without_state(reaction_cml.reactants),
                "products": list_without_state(reaction_cml.products),
                "description": reaction_cml.description,
                "tags": reaction_cml.tags,
                "reactionCount": count,
                "reactionPath": Skeletal.reactionFileName(reaction_cml),
                "reactionHintPath": Skeletal.reactionUnknownProductFileName(reaction_cml)
            }
            response.append(reaction_data)
        else:
            print("Reaction not found found in universe: " + title)
                
    return response

@router.get("/statistics")
async def getStatistics(request: Request):
    levels = request.app.state.server.levels
    if levels.player_id is None:
        return {}
    
    seen_formulas = levels.persistence.get_seen_molecules(levels.player_id)
    performed_reactions = levels.persistence.get_performed_reactions(levels.player_id)
    
    seenMolecules = len([m for m in moleculeList if not m["isAtom"] and m["formula"] in seen_formulas])
    totalMolecules = len([m for m in moleculeList if not m["isAtom"]])
    
    seenAtoms = len([m for m in moleculeList if m["isAtom"] and m["formula"] in seen_formulas])
    totalAtoms = len([m for m in moleculeList if m["isAtom"]])
    
    uniqueReactionsPerformed = len(performed_reactions)
    totalUniqueReactions = len(universe.reactor.reactions)
    totalReactionsMade = sum(r["total_count"] for r in performed_reactions)
    
    return {
        "seenMolecules": seenMolecules,
        "totalMolecules": totalMolecules,
        "seenAtoms": seenAtoms,
        "totalAtoms": totalAtoms,
        "uniqueReactionsPerformed": uniqueReactionsPerformed,
        "totalUniqueReactions": totalUniqueReactions,
        "totalReactionsMade": totalReactionsMade
    }

@router.get("/molecule/all")
async def getAllMolecules():
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
    levels = request.app.state.server.levels
    if levels is None or levels.window.level is None:
        raise HTTPException(status_code=404, detail="No level loaded")
    current_level = levels.window.level
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
            description, tags = handleIons(reaction)

        response.append({
            "reactants": list_without_state(reaction.reactants), 
            "products": list_without_state(reaction.products),
            "description": description,
            "tags": tags,
            "reactionPath": Skeletal.reactionFileName(reaction),
            "reactionHintPath" : Skeletal.reactionUnknownProductFileName(reaction) })
    return response

def handleIons(reaction):
    reactant = reaction.reactants[0]
    ionStrings = " and ".join(list_without_state(reaction.products))
    description = f"{reactant} dissociates in an aqueous solution to form the ions {ionStrings}."
    tags = []
    if "H+(aq)" in reaction.products:
        tags = ["Acid dissociation"]
        description += "This reaction releases a proton (H⁺) in an aqueous solution, forming a conjugate base"
    tags.append("Ionization")
    return description,tags


