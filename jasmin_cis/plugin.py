import logging

def get_all_subclasses(cls, module):
    '''
    Recursively find all subclasses of a given class

    @param cls: The class to find subclasses of
    @return: A list of all subclasses
    '''
    __import__(module)
    subclasses = []
    for subclass in cls.__subclasses__():
        subclasses += get_all_subclasses(subclass, module)
    subclasses += cls.__subclasses__()
    return subclasses


def find_plugins(plugin_dir, parent_class_name):
    import logging
    import os, sys

    # if plugin_dir is None, there is no plugin to import, so return an empty list
    if plugin_dir is None:
        return []

    logging.info("Looking for plugins... ")

    plugin_files = []
    for f in os.listdir(plugin_dir):

        if f.lower().endswith(('.pyc', '__init__.py')): continue

        if f.endswith(".py"):
            plugin_files.append(f[:-3])

    logging.info("importing plugin " + str(plugin_files))
    sys.path.insert(0, plugin_dir)

    for plugin in plugin_files:
        module = __import__(plugin)
        classes = [getattr(module, x) for x in dir(module) if isinstance(getattr(module, x), type)]
        product_classes = [ cls for cls in classes if parent_class_name in str(cls.__bases__[0])]

    return product_classes

def find_plugin_classes(parent_class, built_in_module):
    import os
    import cis
    # find plugin classes, if any
    ENV_PATH = "_".join([cis.__name__.upper(),"PLUGIN","HOME"])
    plugin_dir = os.environ.get(ENV_PATH, None)
    plugin_classes = find_plugins(plugin_dir, parent_class)

    # find built-in classes, i.e. subclasses of parent_class
    subclasses = get_all_subclasses(parent_class, built_in_module)
    all_classes = plugin_classes + subclasses

    logging.debug(parent_class.__name__+" subclasses are: " + str(all_classes))
    return all_classes
