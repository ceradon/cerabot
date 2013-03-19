import os
import sys
import imp

class _Manager(object):
    """Manages all commands and tasks that
    Cerabot has to run."""
    def __init__(self, name, base):
        self.name = name
        self.base = base
        
        #Initaite resources dictionary
        self._resources = {}

    def _load_directory(self, directory):
        """Load all modules in a given directory."""
        print "Loading directory {0}".format(directory)
        for name in os.listdir(directory):
            if name.endswith(".py"):
                if name.startswith(".") or name.startswith("_"):
                    continue
                modname = name.replace(".py", "")
                file, path, desc = imp.find_module(modname, [directory])
                try:
                    module = imp.load_module(modname, file, path, desc)
                except Exception:
                    e = "Couldn't load module {0} from {1}"
                    print e.format(modname, directory)
                    continue
                finally:
                    if file:
                        file.close()

                for obj in vars(module).values():
                    if type(obj) is type:
                        is_resource = issubclass(obj, self.base)
                        if is_resource and not obj is self.base:
                            try:
                                resource = obj()
                            except Exception:
                                e = "Couldn't load {0} {1} from {2}"
                                print e.format(self.name[:-1], modname, path)
                            else:
                                self._resources[resource.name] = resource
                                print "Loaded {0} {1}".format(self.name[:-1],
                                        resource.name)
                        else:
                            continue
            else:
                continue

    @property
    def name(self):
        """Name of the resource; either 'commands' or 'tasks'."""
        return self.name

    @property
    def resources(self):
        """Returns a list of resources."""
        return self._resources
