
# How to Update

(Feb 2019 - Currently set up only at home)

The basic  appraoch is to:

- (https://help.github.com/articles/syncing-a-fork/)
- merge upstream/master (or upstream/leia) (right click and choose merge)
- commit to bossnavova80 Confluence repo
- Copy all EXCEPT addon.xml to repository.bossnova808/staging area (delete everything but addon.xml then copy over)
- Update addon.xml to add version digits(2) to end of upstream version 
  e.g. 4.5.1501
- Run addons_xml_generator.py & copy over zip as usual
- Commit & test









