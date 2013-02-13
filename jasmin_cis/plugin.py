import logging

def __find_plugins(plugin_dir, parent_class_name):

    import os, sys

    # if plugin_dir is None, there is no plugin to import, so return an empty list
    if plugin_dir is None:
        logging.debug
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
