import logging


def get_all_subclasses(parent_class, mod):
    """
        This will recursively find subclasses of parent_class in mod.
        The use of importlib allows mod to be of the form package.module
        Take extreme care when changing the function as it has been known to break!

    :param parent_class: The class to find subclasses of
    :param mod: The module to find subclasses in
    :return: A list of subclasses
    """
    import importlib
    importlib.import_module(mod)
    subclasses = []
    for subclass in parent_class.__subclasses__():
        subclasses += get_all_subclasses(subclass, mod)
    subclasses += parent_class.__subclasses__()
    return subclasses


def find_plugins(plugin_dir, parent_class_name, verbose):
    import logging
    import os, sys

    # if plugin_dir is None, there is no plugin to import, so return an empty list
    if plugin_dir is None:
        return []

    if verbose:
        logging.info("Looking for plugins... ")

    plugin_files = []
    for f in os.listdir(plugin_dir):

        if f.lower().endswith(('.pyc', '__init__.py')): continue

        if f.endswith(".py"):
            plugin_files.append(f[:-3])

    if len(plugin_files) == 0:
        return []

    if verbose:
        logging.info("importing plugin " + str(plugin_files))

    sys.path.insert(0, plugin_dir)

    product_classes = []
    for plugin in plugin_files:
        module = __import__(plugin)
        classes = [getattr(module, x) for x in dir(module) if isinstance(getattr(module, x), type)]
        product_classes = [ cls for cls in classes if parent_class_name in str(cls.__bases__[0])]

    return product_classes


def find_plugin_classes(parent_class, built_in_module, verbose=True):
    import os
    # find plugin classes, if any
    ENV_PATH = "CIS_PLUGIN_HOME"
    plugin_dir = os.environ.get(ENV_PATH, None)
    plugin_classes = find_plugins(plugin_dir, parent_class.__name__, verbose)

    # find built-in classes, i.e. subclasses of parent_class
    subclasses = get_all_subclasses(parent_class, built_in_module)
    all_classes = plugin_classes + subclasses

    for subclass in all_classes:
        if subclass.__name__.startswith('abstract') or subclass.__name__.startswith('Abstract'):
            all_classes.remove(subclass)

    all_classes = sorted(all_classes, key=lambda subclass: subclass.__name__)

    if verbose:
        logging.debug(parent_class.__name__+" subclasses are: " + str(all_classes))

    return all_classes
