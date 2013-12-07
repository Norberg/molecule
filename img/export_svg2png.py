import glob
import subprocess

to_skip = ["water-beaker"]

def main():
    svgs = glob.glob("svg/*.svg")
    for svg in svgs:
        basename = svg.strip("svg/").split(".")[0]
        if basename in to_skip:
            continue
        subprocess.call(["inkscape", "--export-png="+basename+".png", 
                         "--export-width=96", "--export-height=96", svg])

if __name__ == "__main__":
    main()
