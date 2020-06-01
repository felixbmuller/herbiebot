import subprocess
import logging 
from pathlib import Path
import os
import time
import argparse

logger = logging.getLogger(__name__)

def convert_image(in_path, out_path):
    if in_path.lower().endswith(".cr2"):
        in_path = "cr2:" + in_path
    logger.info(f"Converting {in_path}")
    ret = subprocess.run(["convert", in_path, "-resize", "30%", "-quality", "80%", out_path], capture_output=True, text=True)
    # TODO: chown -R nobody:nogroup
    if ret.returncode != 0:
        logger.error(f"converting {in_path} failed with returncode {ret.returncode}")
        logger.error(f"STDERR: {ret.stderr}")
        logger.error(f"STDOUT: {ret.stdout}")
        return False
    else:
        ret = subprocess.run(["chown", "nobody:nogroup", out_path], capture_output=True, text=True)
        if ret.returncode != 0:
            logging.error(f"chown on {out_path} failed with returncode {ret.returncode}. Won't retry.")
            logger.error(f"STDERR: {ret.stderr}")
            logger.error(f"STDOUT: {ret.stdout}")
        return True

FILE_ENDINGS_TO_CONVERT = [
    ".cr2",
    ".jpg",
    ".jpeg",
]

def process_directory(path):

    for dirpath, subdirs, files in os.walk(path, onerror=logger.error):
        if dirpath.endswith("/_preview"):
            continue
        logger.info(f"Scanning {dirpath}")

        if files and any(f.lower().endswith(ending) for ending in FILE_ENDINGS_TO_CONVERT for f in files):
            # need preview folder
            if "_preview" not in subdirs:
                logger.debug(f"created preview directory")
                os.mkdir(os.path.join(dirpath, "_preview"))
        # convert all files
        for f in files:
            if not any(f.lower().endswith(ending) for ending in FILE_ENDINGS_TO_CONVERT):
                continue

            logger.debug(f"Checking file {f}")

            out_file = os.path.join(dirpath, "_preview", "".join(f.split(".")[:-1] + ["_preview.jpg"]))
            in_file = os.path.join(dirpath, f)

            if os.path.isfile(out_file):
                out_timestamp = os.path.getmtime(out_file)
                in_timestamp = os.path.getmtime(in_file)
                if out_timestamp > in_timestamp:
                    logger.debug(f"Skip because the preview is newer than the file")
                    continue # preview up to date
            
            # try converting
            for _ in range(3):
                if convert_image(in_file, out_file):
                    break
                time.sleep(10)

def main():

    parser = argparse.ArgumentParser(description='Automatically generate preview images of JPG and CR2 images')
    parser.add_argument('root_dir', help='directrory in which to search for images recursively')
    parser.add_argument("--logfile", default="image_preview.log", help="logfile location (default: image_preview.log)")
    parser.add_argument('--debug', action='store_true', help="log debug messages")
    parser.add_argument("--lockfile", default="image_preview.lock", 
                        help="lockfile, avoids running the program twice at the same time (default: image_preview.lock)")

    args = parser.parse_args()

    try:
        fp = open(args.lockfile, mode="x")
        fp.close()

        level = logging.INFO
        if args.debug:
            level = logging.DEBUG

        logging.basicConfig(filename=args.logfile, 
                            filemode='a', 
                            level=level,
                            format='%(asctime)s [%(levelname)s]: %(message)s')

        root =  os.path.abspath(os.path.expanduser(os.path.expandvars(args.root_dir)))

        logger.info(f"Started processing with root {root}")
        process_directory(root)
        logger.info(f"Finished processing root and all subdirs")

        os.remove(args.lockfile)

    except FileExistsError:
        print("Another running instance exists")
    

if __name__ == "__main__":
    main()