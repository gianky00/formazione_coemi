import sys
import shutil
import os

def copy_license_files(source_dir, dest_dir):
    """
    Copies license files from a source to a destination directory.
    This script is intended to be run with elevated privileges.
    """
    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        for filename in ["pyarmor.rkey", "config.dat"]:
            source_file = os.path.join(source_dir, filename)
            dest_file = os.path.join(dest_dir, filename)
            if os.path.exists(source_file):
                shutil.copy2(source_file, dest_file)

        # We can't easily signal success back, but exiting with 0 is a good sign.
        sys.exit(0)

    except Exception as e:
        # Write error to a log file so the main process can see it
        with open(os.path.join(source_dir, "copy_error.log"), "w") as f:
            f.write(str(e))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python copy_license.py <source_directory> <destination_directory>")
        sys.exit(1)

    source = sys.argv[1]
    destination = sys.argv[2]
    copy_license_files(source, destination)
