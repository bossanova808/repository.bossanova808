#!/bin/python3

import glob
import os
import re
import sys
import shutil
import hashlib
from dirhash import dirhash

from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "rule strong": "bold green",
    "exec": "bold green",
})

console = Console(record=True, theme=custom_theme)

# Get the list of addons
with os.scandir(os.getcwd()) as cwd:
    addons = [i.name for i in cwd if i.is_dir() and not i.name.startswith('.')]
    # console.log(f"Addons found:")
    # console.log(addons)

# Will be set to true if we detect the need to make any new releases
changes_detected = False
# Build up the (potential) new addons.xml file
addons_xml = []

for addon in addons:

    addon_xml_lines = open(f"{addon}/addon.xml", 'r', encoding="utf-8").readlines()[1:]
    # console.log(addon_xml_lines)
    addons_xml += addon_xml_lines
    addons_xml.append("\n")

    # find the version - this is always the first version tag, just use it verbatim
    version = None
    for addon_xml_line in addon_xml_lines:
        version_tag = re.search(r'version="(.*?)"', addon_xml_line)
        if version_tag:
            version = version_tag.group(1)
            console.log(f"Releasing addon id '{addon}', at version: {version}")
            break

    if not version:
        console.log(f"Could not find version for addon id '{addon}'", style="danger")
        sys.exit(1)

    # If there have been changes, then zip up the new version and move to the download folder with the correct name
    make_new_zip = True
    new_dirhash = dirhash(addon, "md5", jobs=8)
    addon_dir_hash_existing = None
    dirhash_file = f"../repository-downloads/{addon}/dirhash"

    if os.path.exists(dirhash_file):
        with open(dirhash_file, 'r') as dirhash_old_file:
            addon_dir_hash_existing = dirhash_old_file.readline()
            # console.log(f"Existing dirhash: {addon_dir_hash_existing}")

    if addon_dir_hash_existing and addon_dir_hash_existing == new_dirhash:
        console.log(f"Valid release zip already exists, skipping.", style="info")
        # console.log("(dirhash: {addon_dir_hash_existing} matches new dirhash: {new_dirhash})")
        make_new_zip = False

    if make_new_zip:
        changes_detected = True
        repo_download_folder = f"../repository-downloads/{addon}"
        zip_filename = f"{addon}-{version}"
        console.log(f"Making new release zip: '{repo_download_folder}/{zip_filename}.zip'")
        shutil.make_archive(f"{repo_download_folder}/{zip_filename}", 'zip', base_dir=addon)
        console.log(f"& writing dirhash file: '{dirhash_file}'")
        with open(dirhash_file, 'w', encoding="utf-8") as dirhash_new_file:
            dirhash_new_file.write(new_dirhash)

        list_of_zips = glob.glob(f"{repo_download_folder}/**/*.zip", recursive=True)
        if len(list_of_zips) > 2:
            zips_to_delete = list_of_zips[0:-2]
            console.log(f"Deleting release zips prior to previous version:")
            console.log(zips_to_delete)
            for zips_to_delete in zips_to_delete:
                os.remove(f"{zips_to_delete}")

if changes_detected:
    # write out the addons.xml and addons.xml.md5 files
    with open("addons.xml", 'w', encoding="utf-8") as addons_xml_file:
        addons_xml_file.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        addons_xml_file.write('<addons>\n\n')
        for line in addons_xml:
            addons_xml_file.write("    " + line)
        addons_xml_file.write("</addons>\n")
    console.log("Updated addons.xml")

    # calculate & write the md5 file
    md5 = hashlib.md5(open("addons.xml", "r", encoding="utf-8").read().encode("utf-8")).hexdigest()
    with open("addons.xml.md5", 'w', encoding="utf-8") as addons_xml_md5_file:
        addons_xml_md5_file.write(md5 + "\n")
    console.log("Updated addons.xml.md5")
else:
    # Do nothing!
    console.log("No changes detected, thus no update needed for addons.xml and addons.xml.md5", style="info")
