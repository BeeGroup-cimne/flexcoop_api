import os
import importlib

def add_resource_hooks(app):
    for module in os.listdir(os.path.dirname(__file__)):
        if module == '__init__.py' or module[0] == '_':
            continue
        print("importing hooks {}".format(module))
        rmodule = importlib.import_module("modules.{}.{}".format(module,module))
        print(rmodule)
        rmodule.set_hooks(app)
        del module
