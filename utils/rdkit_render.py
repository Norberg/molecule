import argparse
import subprocess

from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem

def render_molecule(molecule: str, size: tuple = (300, 300)):
    ps = Chem.SmilesParserParams()
    ps.removeHs = False
    mol = Chem.MolFromSmiles(molecule, ps)
    if mol is None:
        print(f"Failed to render molecule: {molecule}")
        return None
    #Chem.Kekulize(mol)
    return Draw.MolToImage(mol, size=size)

def fetch_smiles(formula):
    ret = subprocess.Popen(["obabel", "-icml", f"data/molecule/{formula}.cml", "-osmi"], stdout=subprocess.PIPE)
    return ret.stdout.read().decode().strip()

def render_individual_molecule(formula, smiles, output):
    if formula:
        molecule = fetch_smiles(formula)
    elif smiles:
        molecule = smiles
    else:
        print("Please provide either --formula or --smiles.")
        return
    
    img = render_molecule(molecule)
    if output:
        img.save(output, format='PNG')
    else:
        img.show()

def render_reaction_image(reactants, products, output):
    reactant_smiles = [fetch_smiles(formula) for formula in reactants]
    product_smiles = [fetch_smiles(formula) for formula in products]

    reaction = AllChem.ReactionFromSmarts(".".join(reactant_smiles) + ">>" + ".".join(product_smiles), useSmiles=True)
    img = Draw.ReactionToImage(reaction)

    if output:
        img.save(output, format='PNG')
    else:
        img.show()

def main():
    parser = argparse.ArgumentParser(description='Render and save molecule image or reaction image.')
    parser.add_argument('--formula', metavar='F', type=str, help='molecule formula')
    parser.add_argument('--smiles', metavar='S', type=str, help='molecule smiles')
    parser.add_argument('--reactants', metavar='R', nargs='+', type=str, help='reactants formulas')
    parser.add_argument('--products', metavar='P', nargs='+', type=str, help='products formulas')
    parser.add_argument('-o', '--output', metavar='OUTPUT', type=str, help='output file name')

    args = parser.parse_args()

    if args.reactants or args.products:
        render_reaction_image(args.reactants, args.products, args.output)
    else:
        render_individual_molecule(args.formula, args.smiles, args.output)

if __name__ == "__main__":
    main()