import logging


def find_plugins(plugin_dir, verbose):
    import logging
    import os
    import sys
    import importlib

    # if plugin_dir is None, there is no plugin to import, so return an empty list
    if plugin_dir is None:
        return []

    if verbose:
        logging.info("Looking for plugins... ")

    plugin_files = []
    try:
        for f in os.listdir(plugin_dir):

            if f.lower().endswith(('.pyc', '__init__.py')):
                continue

            if f.endswith(".py"):
                plugin_files.append(f[:-3])
    except OSError:
        logging.warning("Unable to read plugin path: {}".format(plugin_dir))

    if len(plugin_files) == 0:
        return []

    sys.path.insert(0, plugin_dir)

    plugin_modules = []
    for plugin in plugin_files:
        if verbose:
            logging.info("Importing plugin: " + str(plugin))
        plugin_modules.append(importlib.import_module(plugin))

    return plugin_modules


def find_plugin_classes(verbose=True):
    import os
    import iris.fileformats
    # Import the built-in plugins
    import cis.data_io.products as built_in

    # find plugin classes, if any
    ENV_PATH = "CIS_PLUGIN_HOME"
    plugin_dir = os.environ.get(ENV_PATH, None)

    plugins = find_plugins(plugin_dir, verbose) + [built_in]

    specs = [o for plugin in plugins 
             for o in dir(plugin) if 
             isinstance(o, iris.fileformats.FormatSpecification)]
    
    if verbose:
        logging.debug("Plugins are: " + str(specs))

    return specs
