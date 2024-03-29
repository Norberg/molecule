import glob
import subprocess

to_skip = ["water-beaker", "hotplate"]

custom_sizes = {
    "aq": {"width": 112, "height": 112},
}

def main():
    svgs = glob.glob("svg/*.svg")
    for svg in svgs:
        basename = svg.strip("svg/").split(".")[0]
        if basename in to_skip:
            continue

        size = custom_sizes.get(basename, {"width": 96, "height": 96})
        subprocess.call(["inkscape", "--export-png="+basename+".png",
                         "--export-width=" + str(size["width"]),
                         "--export-height=" + str(size["height"]), svg])

if __name__ == "__main__":
    main()
