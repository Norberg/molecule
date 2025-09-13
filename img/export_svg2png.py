import glob
import os
import sys
import subprocess
import argparse

to_skip = ["water-beaker", "hotplate","Bunzen_burner", "mining", "inert-solvent-beaker", "fire", "cold", "uv-light", "furnace"]

custom_sizes = {
    "aq": {"width": 112, "height": 112},
    "fireworks": {"width": 256, "height": 256},
}

def collect_all_svgs():
    """Return dict mapping basename -> full svg path from svg/ folder."""
    mapping = {}
    for path in glob.glob("svg/*.svg"):
        base = os.path.splitext(os.path.basename(path))[0]
        mapping[base] = path
    return mapping


def resolve_requested_svgs(args_list, all_svgs):
    """Resolve user supplied names/paths to actual svg paths.

    Accepted forms per argument:
      - basename (e.g. atom-ca)
      - filename.svg (searched first as literal path then in svg/)
      - relative/absolute path to an svg
    Returns list of svg paths (deduplicated, preserving order) and list of missing names.
    """
    if not args_list:
        # No specific request -> all
        return list(all_svgs.values()), []

    resolved = []
    seen = set()
    missing = []
    for raw in args_list:
        candidate = raw
        # If direct path exists use it
        if os.path.isfile(candidate) and candidate.endswith('.svg'):
            path = candidate
        else:
            name = os.path.splitext(os.path.basename(raw))[0]
            path = all_svgs.get(name)
        if path and path not in seen:
            resolved.append(path)
            seen.add(path)
        elif not path:
            missing.append(raw)
    return resolved, missing


def export_svg(svg_path):
    basename = os.path.splitext(os.path.basename(svg_path))[0]
    if basename in to_skip:
        return False  # skipped
    size = custom_sizes.get(basename, {"width": 96, "height": 96})
    # Maintain existing inkscape CLI (legacy), so we don't break environment expectations.
    cmd = [
        "inkscape",
        "--export-png=" + basename + ".png",
        "--export-width=" + str(size["width"]),
        "--export-height=" + str(size["height"]),
        svg_path,
    ]
    subprocess.call(cmd)
    return True


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Export SVG icons in svg/ to PNG med fördefinierade storlekar. Utan argument exporteras alla.")
    parser.add_argument(
        "svgs",
        nargs="*",
        help="(Valfritt) Specifika svg basnamn, filnamn eller sökvägar. Ex: atom-ca atom-ba.svg svg/atom-sr.svg")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    all_svgs = collect_all_svgs()
    selected, missing = resolve_requested_svgs(args.svgs, all_svgs)
    if missing:
        print("Saknas (hittar ej svg): " + ", ".join(missing), file=sys.stderr)
    if not selected:
        return 1 if missing else 0

    for svg in selected:
        base = os.path.splitext(os.path.basename(svg))[0]
        if base in to_skip:
            continue
        export_svg(svg)

    return 0

if __name__ == "__main__":
    main()
