#!/bin/python3

# Standard imports...
import glob
import os
import re
import sys
import shutil
import hashlib

# These usually need to be installed, e.g. on Ubuntu:
# pip3 install rich dirhash
from dirhash import dirhash
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "red",
    "danger": "bold red",
    "rule strong": "bold green",
    "exec": "bold green",
})

console = Console(record=True, theme=custom_theme)

STAGING_DIR = os.path.join(os.getcwd(), "staging")
REPOSITORY_DOWNLOADS_DIR = os.path.join(os.getcwd(), "repository-downloads")

# Get the list of addons
with os.scandir(STAGING_DIR) as staging_dir:
    addons = [i.name for i in staging_dir if i.is_dir() and not i.name.startswith('.') and not i.name.startswith('dirhash')]
    # console.log(f"Addons found:")
    # console.log(addons)

# Will be set to true if we detect the need to make any new releases
changes_detected = False
# Build up the (potential) new addons.xml file
addons_xml = []

# Loop through all found addons
for addon in addons:

    ADDON_FOLDER_STAGING = os.path.join(STAGING_DIR, addon)
    ADDON_FOLDER_REPOSITORY_DOWNLOADS = os.path.join(REPOSITORY_DOWNLOADS_DIR, addon)

    # Read the file, but kkip the <?xml ...etc line
    addon_xml_lines = open(f"{ADDON_FOLDER_STAGING}/addon.xml", 'r', encoding="utf-8").readlines()[1:]
    # console.log(addon_xml_lines)
    addons_xml += addon_xml_lines
    addons_xml.append("\n")

    # find the version - this is always the first version tag, just use it verbatim
    version = None
    for addon_xml_line in addon_xml_lines:
        version_tag = re.search(r'version="(.*?)"', addon_xml_line)
        if version_tag:
            version = version_tag.group(1)
            console.rule(f"Releasing '{addon}' version: {version}", style="exec")
            break

    if not version:
        console.log(f"Could not find version for addon id '{addon}', bailing out...", style="danger")
        sys.exit(1)

    # Don't add .zip here as shutil.make_archive does that and we don't want .zip.zip
    ZIP_FILE = f"{addon}-{version}"
    # If we detect changes, then zip up the new version and move to the download folder with the correct name
    make_new_zip = True
    # Dirhash version
    DIRHASH_CALCULATED = dirhash(f"staging/{addon}", "md5", jobs=8)
    DIRHASH_RECORDED = None
    # Use a relative path here as ?dirhash across environments changing?
    DIRHASH_FILE = f"./staging/dirhash/{addon}.dirhash"

    # Is there an existing recorded dirhash?  And does it match the newly calculated dirhash?
    if os.path.exists(DIRHASH_FILE):
        with open(DIRHASH_FILE, 'r') as f:
            DIRHASH_RECORDED = f.readline()
            # console.log(f"Existing dirhash: {DIRHASH_RECORDED}")
            if DIRHASH_RECORDED == DIRHASH_CALCULATED:
                console.log(f"Valid release zip already exists (dirhash=dirhash), skipping.", style="info")
                # console.log("(dirhash: {DIRHASH_RECORDED} matches new dirhash: {DIRHASH_CALCULATED})")
                make_new_zip = False
            else:
                console.log(f"Dirhash does not match.", style="info")
                console.log(f"Recorded: '{DIRHASH_RECORDED}' Calculated: '{DIRHASH_CALCULATED}'", style="info")

    # If the addon zip is not actually present, we need to make it no matter what the dirhash situation...
    if not os.path.exists(f"{ADDON_FOLDER_REPOSITORY_DOWNLOADS}/{ZIP_FILE}.zip"):
        console.log(f"{ZIP_FILE} not found in {ADDON_FOLDER_REPOSITORY_DOWNLOADS}, thus creating new release zip")
        make_new_zip = True

    if make_new_zip:
        # Making a new release, so we'll later need to update the addons.xml file etc.
        changes_detected = True
        console.log(f"Making new release zip: '{ADDON_FOLDER_REPOSITORY_DOWNLOADS}/{ZIP_FILE}.zip'")
        shutil.make_archive(f"{ADDON_FOLDER_REPOSITORY_DOWNLOADS}/{ZIP_FILE}", 'zip', root_dir=STAGING_DIR, base_dir=addon)
        console.log(f"Writing new dirhash '{DIRHASH_CALCULATED}' to file: '{DIRHASH_FILE}'")
        with open(DIRHASH_FILE, 'w', encoding="utf-8") as f:
            f.write(DIRHASH_CALCULATED)

        list_of_zips = glob.glob(f"{ADDON_FOLDER_REPOSITORY_DOWNLOADS}/**/*.zip", recursive=True)
        if len(list_of_zips) > 2:
            zips_to_delete = list_of_zips[0:-2]
            console.log(f"Deleting release zips prior to previous version:")
            console.log(zips_to_delete)
            for zips_to_delete in zips_to_delete:
                os.remove(f"{zips_to_delete}")

console.rule(f"Repository Actions", style="exec")

if changes_detected:
    # write out the addons.xml and addons.xml.md5 files
    with open(f"{STAGING_DIR}/addons.xml", 'w', encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write('<addons>\n\n')
        for line in addons_xml:
            f.write("    " + line)
        f.write("</addons>\n")
    console.log(f"Updated {STAGING_DIR}/addons.xml")

    # calculate & write the md5 file
    md5 = hashlib.md5(open(f"{STAGING_DIR}/addons.xml", "r", encoding="utf-8").read().encode("utf-8")).hexdigest()
    with open(f"{STAGING_DIR}/addons.xml.md5", 'w', encoding="utf-8") as f:
        f.write(md5 + "\n")
    console.log(f"Updated {STAGING_DIR}/addons.xml.md5")
else:
    # Do nothing!
    console.log("No changes detected, not updating addons.xml & addons.xml.md5", style="info")

