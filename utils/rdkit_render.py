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
from rdkit import Geometry

from libcml import Cml
from libreact.Reaction import Reaction, list_without_state
from libreact.Reaction import verify as Reaction_verify
from libreact.Reactor import sublist_in_list
from libreact.Reactor import Reactor
from molecule import Skeletal


def render_all_reactions():
        cml = Cml.Reactions()
        cml.parse("data/reactions.cml")
        reactor = Reactor(cml.reactions)
        for reaction in reactor.reactions:
            reactants = reaction.reactants
            products = list_without_state(reaction.products)
            render_reaction_image(reactants, products, Skeletal.reactionPath(reaction))
            render_reaction_image([], products, Skeletal.reactionUnknownProductPath(reaction))


def render_all_molecules():
    for filename in os.listdir("data/molecule"):
        if filename.endswith(".cml"):
            formula = filename.split(".")[0]
            molecule = Cml.Molecule()
            molecule.parse(f"data/molecule/{formula}.cml")
            smiles = molecule.property.get("Smiles", "")
            if smiles == "":
                print(f"Failed to fetch SMILES for {formula}")
                continue
            img = render_molecule(smiles)
            img.save(f"img/skeletal/molecule/{formula}.png", format='PNG')

def render_molecule(molecule: str, size: tuple = (300, 300)):
    ps = Chem.SmilesParserParams()
    ps.removeHs = False
    ps.sanitize = False
    mol = Chem.MolFromSmiles(molecule, ps)
    if mol is None:
        print(f"Failed to render molecule: {molecule}")
        return None
    #Chem.Kekulize(mol)
    return Draw.MolToImage(mol, size=size)

def fetch_smiles(formula):
    #strip state if present
    formula = formula.split("(")[0]
    molecule = Cml.Molecule()
    molecule.parse(f"data/molecule/{formula}.cml")
    return molecule.property.get("Smiles", "")

def render_individual_molecule(formula, smiles, output):
    if formula:
        molecule = fetch_smiles(formula)
    elif smiles:
        molecule = smiles
    else:
        print("Please provide either --formula or --smiles.")
        return

    img = render_molecule(molecule)
    if img is None:
        return
    if output:
        img.save(output, format='PNG')
    else:
        img.show()

def render_reaction_image(reactants, products, output):
    reactant_smiles = [fetch_smiles(formula) for formula in reactants]
    product_smiles = [fetch_smiles(formula) for formula in products]

    catalyst_smiles = list(set(reactant_smiles) & set(product_smiles))
    reactant_smiles = [smiles for smiles in reactant_smiles if smiles not in catalyst_smiles]
    product_smiles = [smiles for smiles in product_smiles if smiles not in catalyst_smiles]

    if len(reactant_smiles) == 0:
        reactant_smiles = ["*"]
    reaction = AllChem.ReactionFromSmarts(".".join(reactant_smiles) + ">"+ ".".join(catalyst_smiles) +">" + ".".join(product_smiles), useSmiles=True)
    img = Draw.ReactionToImage(reaction)

    if output:
        img.save(output, format='PNG')
    else:
        img.show()

def _render_reaction_image(reaction, output):
    reaction = AllChem.ReactionFromSmarts(reaction, useSmiles=True)
    img = Draw.ReactionToImage(reaction)

    if output:
        img.save(output, format='SVG')
    else:
        #img.DrawString("Reaction", Geometry.Point2D(10, 10))
        img.show()
        # d = Draw.MolDraw2DSVG(600,200)
        # d.SetFontSize(0.6)
        # d.DrawReaction(reaction)
        # d.DrawString("Reaction", Geometry.Point2D(10, 10))
        # d.FinishDrawing()
        # print(d.GetDrawingText())
        #img.show()


def main():
    parser = argparse.ArgumentParser(description='Render and save molecule image or reaction image.')
    parser.add_argument('--formula', metavar='F', type=str, help='molecule formula')
    parser.add_argument('--smiles', metavar='S', type=str, help='molecule smiles')
    parser.add_argument('--reactants', metavar='R', nargs='+', type=str, help='reactants formulas')
    parser.add_argument('--products', metavar='P', nargs='+', type=str, help='products formulas')
    parser.add_argument('-o', '--output', metavar='OUTPUT', type=str, help='output file name')
    parser.add_argument('--render-all', action='store_true', help='render all reactions and molecules')
    parser.add_argument('--reaction', metavar='REACTION', type=str, help='reaction smiles')

    args = parser.parse_args()


    if args.render_all:
        render_all_reactions()
        render_all_molecules()
    elif args.reactants or args.products:
        render_reaction_image(args.reactants, args.products, args.output)
    elif args.reaction:
        _render_reaction_image(args.reaction, args.output)
    else:
        render_individual_molecule(args.formula, args.smiles, args.output)

if __name__ == "__main__":
    main()