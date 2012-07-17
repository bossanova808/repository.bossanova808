## repo addons.xml and addons.xml.md5 generator

from xml.dom.minidom import parseString
import hashlib
import os
import sys


class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
    """

    def __init__( self ):
        # generate addons.xml file
        if ( not self._generate_addons_xml_file() ):
            sys.exit( 0 )
        # generate addons.xml.md5 file
        if ( not self._generate_addons_xml_md5_file() ):
            sys.exit( 0 )
        # notify user of successfully updating files
        print "Finished updating addons.xml and addons.xml.md5 files!"

    def _generate_addons_xml_file( self ):
        # addons.xml heading block
        addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n"
        # list of only folders, skip special .svn folder
        folders = [ f for f in os.listdir( os.curdir )
                   if ( os.path.isdir( f ) and f != ".svn" ) ]
        # loop thru and add each addons addon.xml to the final addons.xml file
        for folder in folders:
            try:
                # new addon.xml text holder
                addon_xml = u""
                # create full path to an addon.xml file
                _path = os.path.join( folder, "addon.xml" )
                # split lines for stripping
                with open( _path, "r" ) as addon_file:
                    # loop thru cleaning each line
                    for line in addon_file:
                        # skip heading block as we already have one
                        if ( line.find( "<?xml" ) >= 0 ): continue
                        # add line
                        addon_xml += unicode( line.rstrip() + "\n", "UTF-8" )
                # check for a properly formatted xml file
                parseString( addon_xml.encode( "UTF-8" ) )
            except Exception as e:
                # missing or malformed formatted addon.xml
                print "* Excluding {path} for {error}".format( path=_path, error=e )
            else:
                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + "\n\n"
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u"\n</addons>\n"
        # save file and return result
        return self._save_file( data=addons_xml.encode( "UTF-8" ), file="addons.xml" )

    def _generate_addons_xml_md5_file( self ):
        try:
            # create a new md5 hash
            md5 = hashlib.md5( open( "addons.xml" ).read() ).hexdigest()
        except IOError as e:
            # oops
            print "An error occurred creating md5 hash from addons.xml file!\n{error}".format( error=e )
            # return failed
            return False
        else:
            # save file
            return self._save_file( data=md5 + " addons.xml\n", file="addons.xml.md5" )

    def _save_file( self, data, file ):
        try:
            # write data to the file
            open( file, "w" ).write( data )
        except IOError as e:
            # oops
            print "An error occurred saving {file} file!\n{error}".format( file=file, error=e )
            # return failed
            return False
        else:
            # return success
            return True


# start
if ( __name__ == "__main__" ):
    Generator()
