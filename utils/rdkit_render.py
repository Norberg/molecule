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

import cairo
import numpy as np


def render_all_reactions():
        cml = Cml.Reactions()
        cml.parse("data/reactions.cml")
        reactor = Reactor(cml.reactions)
        for reaction in reactor.reactions:
            reactants = reaction.reactants
            products = list_without_state(reaction.products)
            requirements = reaction.requirements
            render_reaction_image(reactants, products, Skeletal.reactionPath(reaction), requirements)
            render_reaction_image([], products, Skeletal.reactionUnknownProductPath(reaction), requirements)


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

def render_all_ions():
    for filename in os.listdir("data/molecule"):
        if filename.endswith(".cml"):
            formula = filename.split(".")[0]
            molecule = Cml.Molecule()
            molecule.parse(f"data/molecule/{formula}.cml")
            aqueus = molecule.get_state("aq")
            if aqueus is None:
                continue
            ions = aqueus.ions
            if ions is None:
                continue
            ionReaction = Cml.Reaction(reactants=[formula], products=ions)
            render_reaction_image([formula], ions, Skeletal.reactionPath(ionReaction))
            render_reaction_image([], ions, Skeletal.reactionUnknownProductPath(ionReaction))

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

def crop_white_sides_cairo(surface, tolerance=240, margin=20):
    """
    Crop white margins from the left and right sides of a cairo ImageSurface, 
    but preserve a fixed margin (20px by default) on each side.
    """
    width = surface.get_width()
    height = surface.get_height()
    stride = surface.get_stride()

    buf = surface.get_data()
    arr = np.frombuffer(buf, np.uint8).reshape(height, stride // 4, 4)
    arr = arr[:, :width, :]

    # Due to little-endian, ARGB is stored as BGRA in memory.
    b = arr[:, :, 0]
    g = arr[:, :, 1]
    r = arr[:, :, 2]
    # Create mask for pixels that are white (based on the tolerance)
    white_mask = (r >= tolerance) & (g >= tolerance) & (b >= tolerance)

    # Determine which columns are completely white
    col_white = white_mask.all(axis=0)
    non_white = np.where(~col_white)[0]
    if non_white.size == 0:
        return surface
    # Find the exact non-white boundaries
    left = int(non_white[0])
    right = int(non_white[-1] + 1)  # Include the last non-white column

    # Expand the crop boundaries keeping a fixed margin, ensuring they don't exceed image dimensions
    new_left = max(0, left - margin)
    new_right = min(width, right + margin)
    new_width = new_right - new_left

    # Create a new surface with the adjusted dimensions
    new_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, new_width, height)
    ctx = cairo.Context(new_surface)
    # Offset drawing by new_left to maintain the white margin at the left side
    ctx.set_source_surface(surface, -new_left, 0)
    ctx.paint()
    return new_surface

def process_png_with_cairo(png_path, tolerance=240):
    """
    Load the saved PNG as a cairo ImageSurface, crop its white sides, and overwrite the file.
    """
    surface = cairo.ImageSurface.create_from_png(png_path)
    cropped = crop_white_sides_cairo(surface, tolerance)
    cropped.write_to_png(png_path)

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
        process_png_with_cairo(output)  # Post-processing: crop white margins using Cairo
    else:
        img.show()

def render_reaction_image(reactants, products, output,  requirements = []):
    reactant_smiles = [fetch_smiles(formula) for formula in reactants]
    product_smiles = [fetch_smiles(formula) for formula in products]

    catalyst_smiles = list(set(reactant_smiles) & set(product_smiles))


    if any(req.type == Cml.Requirement.EnergyType.UV_LIGHT for req in requirements):
        catalyst_smiles = ["[U].[V]"]
    elif len(requirements) > 0:
        print(f"Unhandled requirements: {requirements}")
        catalyst_smiles = ["[U].[V]"]

    reactant_smiles = ['(' + smiles + ')' for smiles in reactant_smiles if smiles not in catalyst_smiles]
    product_smiles = ['(' + smiles + ')' for smiles in product_smiles if smiles not in catalyst_smiles]

    if len(reactant_smiles) == 0:
        reactant_smiles = ["*"]
    reaction = AllChem.ReactionFromSmarts(".".join(reactant_smiles) + ">"+ ".".join(catalyst_smiles) +">" + ".".join(product_smiles), useSmiles=True)
    img = Draw.ReactionToImage(reaction)

    if output:
        img.save(output, format='PNG')
        process_png_with_cairo(output)  # Crop white margins from the reaction image
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
        render_all_ions()
    elif args.reactants or args.products:
        render_reaction_image(args.reactants, args.products, args.output)
    elif args.reaction:
        _render_reaction_image(args.reaction, args.output)
    else:
        render_individual_molecule(args.formula, args.smiles, args.output)

if __name__ == "__main__":
    main()