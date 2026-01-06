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
from libreact.Reactor import sublist_in_list, Reactor
from molecule import Skeletal
from PIL import Image, ImageDraw, ImageFont, ImageChops

import cairo
import numpy as np

class ReactionCondition:
    def __init__(self, upper, lower):
        self.upper = upper
        self.lower = lower

def get_font(size=24):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except IOError as e:
        print(f"Failed to load font due to {e} using default font. Please install DejaVuSans.ttf")
        return ImageFont.load_default(size)

def render_all_reactions():
    cml = Cml.Reactions()
    cml.parse("data/reactions")
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
    # strip state if present
    formula = formula.split("(")[0]
    molecule = Cml.Molecule()
    molecule.parse(f"data/molecule/{formula}.cml")
    return molecule.property.get("Smiles", "").strip()

def crop_white_sides_cairo(surface, tolerance=240, margin=20):
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

def render_reaction_image(reactants, products, output, requirements=[]):
    reactant_smiles = [fetch_smiles(formula) for formula in reactants]
    product_smiles = [fetch_smiles(formula) for formula in products]

    catalyst_smiles = list(set(reactant_smiles) & set(product_smiles))
    requirement_text = None
    if any(req.type == Cml.Requirement.EnergyType.UV_LIGHT for req in requirements):
        requirement_text = "UV light"
    elif len(requirements) > 0:
        print(f"Unhandled requirements: {requirements}")

    reactionCondition = ReactionCondition(requirement_text, None)

    reactant_smiles = ['(' + smiles + ')' for smiles in reactant_smiles if smiles not in catalyst_smiles]
    product_smiles = ['(' + smiles + ')' for smiles in product_smiles if smiles not in catalyst_smiles]

    if len(reactant_smiles) == 0:
        reactant_smiles = ["*"]
    reaction = AllChem.ReactionFromSmarts(".".join(reactant_smiles) + ">" + ".".join(catalyst_smiles) + ">" + ".".join(product_smiles), useSmiles=True)
    img = _reaction_to_image(reaction, reactionCondition)

    if output:
        img.save(output, format='PNG')
        process_png_with_cairo(output)  # Crop white margins from the reaction image
    else:
        img.show()

def _render_reaction_image(reaction, reactionCondition, output):
    reaction = AllChem.ReactionFromSmarts(reaction, useSmiles=True)    
    img = _reaction_to_image(reaction, reactionCondition)

    if output:
        img.save(output, format='SVG')
    else:
        img.show()

def _groupTemplates(num_templates, get_template, subImgSize):
    groups = {}
    for i in range(num_templates):
        tmpl = get_template(i)
        tmpl.UpdatePropertyCache(False)
        key = Chem.MolToSmiles(tmpl)
        if key in groups:
            groups[key]['count'] += 1
        else:
            groups[key] = {'tmpl': tmpl, 'count': 1}
    images = []
    for idx, group in enumerate(groups.values()):
        if group['count'] > 1:
            img = _createLabeledImage(group['tmpl'], group['count'], subImgSize)
        else:
            img = Draw.MolToImage(group['tmpl'], size=subImgSize)
            img = _crop_white_borders(img, margin=25)
        images.append(img)
        # Insert plus image between groups
        if idx < len(groups) - 1:
            images.append(_createPlusImage(subImgSize))
    if not images:
        images.append(_createPlaceholder(subImgSize, "*"))
    return images

def _reaction_to_image(reaction, reactionCondition):
    subImgSize = (200, 200)
    # Process reactants by grouping duplicate templates.
    reactant_count = reaction.GetNumReactantTemplates()
    if reactant_count > 0:
        reactant_images = _groupTemplates(reactant_count, reaction.GetReactantTemplate, subImgSize)
    else:
        reactant_images = [_createPlaceholder(subImgSize, "*")]
    
    # Process products by grouping duplicate templates.
    product_count = reaction.GetNumProductTemplates()
    if product_count > 0:
        product_images = _groupTemplates(product_count, reaction.GetProductTemplate, subImgSize)
    else:
        product_images = [_createPlaceholder(subImgSize, "*")]

    # Process agents by grouping duplicate templates.
    agent_count = reaction.GetNumAgentTemplates()
    if agent_count > 0:
        scale_factor = 2
        image_size = (subImgSize[0] // scale_factor, subImgSize[1] // scale_factor)
        agent_images = _groupTemplates(agent_count, reaction.GetAgentTemplate, image_size)
    else:
        agent_images = []
    
    # Create reaction arrow.
    arrow_img = _drawReactionArrow(subImgSize, agent_images, reactionCondition)
    
    # Combine reactants, reaction arrow, and products.
    cell_images = reactant_images + [arrow_img] + product_images
    total_width = sum(img.width for img in cell_images)
    res = Image.new("RGBA", (total_width, subImgSize[1]), (255, 255, 255, 255))
    
    offset_x = 0
    for img in cell_images:
        res.paste(img, (offset_x, 0))
        offset_x += img.width
    return res

def _crop_white_borders(image, margin=0):
    # Create a white background image of the same size.
    bg = Image.new(image.mode, image.size, (255, 255, 255, 255) if "A" in image.getbands() else (255, 255, 255))
    # Compute the difference between the image and a pure white background.
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        left, _, right, _ = bbox  # ignore upper and lower boundaries
        left = max(0, left - margin)
        right = min(image.width, right + margin)
        # Crop only left and right, preserve full height
        return image.crop((left, 0, right, image.height))
    return image

def _createLabeledImage(mol, count, size):
    label_width = 30
    mol_img = Draw.MolToImage(mol, size=size)
    mol_img = _crop_white_borders(mol_img, margin=5)
    
    new_width = mol_img.width + label_width
    new_img = Image.new("RGBA", (new_width, mol_img.height), (255, 255, 255, 255))
    new_img.paste(mol_img, (label_width, 0))
    draw = ImageDraw.Draw(new_img)
    font = get_font(38)
    text = str(count)
    text_position = (5, (mol_img.height // 2) - 21)
    draw.text(text_position, text, fill=(0, 0, 0), font=font)
    return new_img

def _createPlaceholder(size, text):
    image = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    text_position = (size[0] // 2 - 10, size[1] // 2 - 10)
    draw.text(text_position, text, fill=(0, 0, 0), font=get_font(24))
    return image

def _createPlusImage(size):
    new_size = (20, size[1])
    image = Image.new("RGBA", new_size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    center_x, center_y = new_size[0] // 2, new_size[1] // 2
    line_length = 14
    line_width = 2

    half_length = line_length // 2
    horizontal_start = (center_x - half_length, center_y)
    horizontal_end = (center_x + half_length + 1, center_y)
    vertical_start = (center_x, center_y - half_length)
    vertical_end = (center_x, center_y + half_length + 1)

    draw.line([horizontal_start, horizontal_end], fill=(0, 0, 0), width=line_width)
    draw.line([vertical_start, vertical_end], fill=(0, 0, 0), width=line_width)
    return image

def _drawReactionArrow(subImgSize, agent_images, reactionCondition):
    # Define arrow margin and default arrow length.
    arrow_margin = 20  # margin from left/right edges
    default_arrow_length = subImgSize[0] - 2 * arrow_margin
    arrow_length = default_arrow_length

    # Compute new canvas width if needed.
    new_width = subImgSize[0]
    if agent_images:
        if reactionCondition.upper:
            raise ValueError("Cannot specify both agent images and an upper text in reactionCondition.")

        total_width = sum(img.width for img in agent_images)
        max_height = max(img.height for img in agent_images)
        combined_agent = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))
        offset = 0
        for img in agent_images:
            mask = img.split()[3] if img.mode == "RGBA" else None
            combined_agent.paste(img, (offset, (max_height - img.height) // 2), mask)
            offset += img.width

        # Increase arrow length if the agent image is wider than default.
        arrow_length = max(default_arrow_length, combined_agent.width)
        # New canvas width: margin on left and right plus the new arrow length.
        new_width = arrow_margin + arrow_length + arrow_margin

    canvas_size = (new_width, subImgSize[1])
    arrow_img, draw = _createCanvas(canvas_size)
    
    # Set arrow start and end points.
    arrow_start_point = (arrow_margin, subImgSize[1] // 2)
    arrow_end_point = (arrow_start_point[0] + arrow_length, subImgSize[1] // 2)
    
    # If agent images are provided, render them above the arrow.
    if agent_images:
        # Center the combined agent image above the arrow.
        agent_x = arrow_start_point[0] + (arrow_length - combined_agent.width) // 2
        agent_y = arrow_start_point[1] - combined_agent.height - 5
        arrow_img.paste(combined_agent, (agent_x, agent_y), combined_agent.split()[3])
    
    # Draw the arrow lines.
    draw.line([arrow_start_point, arrow_end_point], fill=(0, 0, 0), width=2)
    arrow_upper_head_point = (arrow_end_point[0] - 10, arrow_end_point[1] - 10)
    arrow_lower_head_point = (arrow_end_point[0] - 10, arrow_end_point[1] + 10)
    draw.line([arrow_upper_head_point, arrow_end_point], fill=(0, 0, 0), width=2)
    draw.line([arrow_lower_head_point, arrow_end_point], fill=(0, 0, 0), width=2)
    
    text_x_offset = 30
    text_x = arrow_start_point[0] + text_x_offset
    arrow_y = subImgSize[1] // 2
    
    if reactionCondition.upper:
        upper_text = str(reactionCondition.upper)
        text_offset = 30
        upper_text_position = (text_x, arrow_y - text_offset - 10)
        font = get_font(24)
        draw.text(upper_text_position, upper_text, fill=(0, 0, 0), font=font)
    
    if reactionCondition.lower:
        lower_text = str(reactionCondition.lower)
        text_offset = 5
        lower_text_position = (text_x, arrow_y + text_offset)
        font = get_font(24)
        draw.text(lower_text_position, lower_text, fill=(0, 0, 0), font=font)
    
    return arrow_img

def _createCanvas(size):
    image = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    return image, draw

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
        _render_reaction_image(args.reaction, ReactionCondition(None, None), args.output)
    else:
        render_individual_molecule(args.formula, args.smiles, args.output)

if __name__ == "__main__":
    main()