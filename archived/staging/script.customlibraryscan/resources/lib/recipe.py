import yaml
from .store import Store
from .common import *


class Recipe:
    """
    Class to encapsulate functionality for custom scanning recipes
    """

    @staticmethod
    def loadRecipe(recipe_name):
        """
        Load a custom scanning recipe from its yaml file - if no filename provided try and load 'default.yaml'
        @return:
        """

        if ADDON.getSetting("RecipesFolder"):
            settings_folder = ADDON.getSetting("RecipesFolder")
        else:
            settings_folder = PROFILE

        log("Settings folder: " + settings_folder)
        recipe_to_load = settings_folder + "/" + recipe_name + '.yaml'

        # If there is no default, it's not actually a failure
        if not xbmcvfs.exists(recipe_to_load) and recipe_name == "default":
            return

        # load a recipe into our Store object
        # https://stackoverflow.com/questions/1773805/how-can-i-parse-a-yaml-file-in-python
        try:
            with xbmcvfs.File(recipe_to_load) as file:
                try:
                    Store.recipe = yaml.safe_load(file.read())
                except yaml.YAMLError as inst:
                    notify(f'Error loading {recipe_to_load} - check logs!')
                    log(inst)
        except IOError as error:
            log(error)
            notify(str(error))

        log('Loaded custom scanning recipe:')
        log(Store.recipe)
