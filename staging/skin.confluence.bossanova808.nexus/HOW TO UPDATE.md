
# How to Update

The basic  approach is to:

- Sync with upstream repo (https://help.github.com/articles/syncing-a-fork/)
- `git pull upstream/master` (or upstream/whatever)
- Fix merge conflicts
- Commit to bossanova808 Confluence repo
- Copy all files EXCEPT addon.xml to Kodi test area - test & fix isses
- Copy and commit any changes back to JD confluence repo
- Copy all files EXCEPT addon.xml to repository.bossnova808/staging area (delete everything but addon.xml then copy over)
- Update addon.xml to add version digits(2) to end of upstream version 
  e.g. 4.5.1501
- Run addons_xml_generator.py & copy over zip as usual
- Commit & test again!









