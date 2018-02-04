"""
Magic Reload Library
Luke Campagnola   2010

Python reload function that actually works (the way you expect it to)
 - No re-importing necessary
 - Modules can be reloaded in any order
 - Replaces functions and methods with their updated code
 - Changes instances to use updated classes
 - Automatically decides which modules to update by comparing file modification times
 
Does NOT:
 - re-initialize exting instances, even if __init__ changes
 - update references to any module-level objects
   ie, this does not reload correctly:
       from module import someObject
       print someObject
   ..but you can use this instead: (this works even for the builtin reload)
       import module
       print module.someObject
"""

import inspect
import os
import sys
import builtins
import importlib
import gc
import traceback


def reload_all(whitelist=None, debug=False):
    """
    Automatically reload everything that's in the whitelist.
    - Skips reload if the file has not been updated (if .pyc is newer than .py)
    """
    for module_name in whitelist:
        if module_name not in sys.modules:
            continue

        module = sys.modules[module_name]

        if not inspect.ismodule(module):
            continue
        if module_name == '__main__':
            continue

        if not hasattr(module, '__file__') or os.path.splitext(module.__file__)[1] not in ['.py', '.pyc']:
            # Ignore if the module does not have a .py file
            continue

        # Ignore if the .pyc is newer than the .py (or if there is no pyc or py)
        py = os.path.splitext(module.__file__)[0] + '.py'

        # Get .pyc file name
        pyc = py.split(os.sep)
        file_name = list(os.path.splitext(pyc[-1]))
        file_name[1] = file_name[1] + "c"
        file_name = file_name[0] + ".cpython-36" + file_name[1]
        pyc = pyc[:-1] + ['__pycache__'] + [file_name]
        pyc = os.sep.join(pyc)

        if os.path.isfile(pyc) and os.path.isfile(py) and os.stat(pyc).st_mtime >= os.stat(py).st_mtime:
            if debug:
                print("Ignoring module %s; unchanged" % str(module))
            continue

        try:
            reload_module(module, debug=debug, lists=True, dicts=True)
        except Exception as e:
            print(e)
            print("Error while reloading module %s, skipping\n" % module)


def reload_module(module, debug=False, lists=False, dicts=False):
    """
    Replacement for the builtin reload function:
    - Reloads the module as usual
    - Updates all old functions and class methods to use the new code
    - Updates all instances of each modified class to use the new class
    - Can update lists and dicts, but this is disabled by default
    - Requires that class and function names have not changed
    """
    print("Reloading", module)

    # make a copy of the old module dictionary, reload, then grab the new module dictionary for comparison
    oldDict = module.__dict__.copy()
    importlib.reload(module)
    newDict = module.__dict__

    # Allow modules access to the old dictionary after they reload
    if hasattr(module, '__reload__'):
        module.__reload__(oldDict)

    # compare old and new elements from each dict; update where appropriate
    for k in oldDict:
        old = oldDict[k]
        new = newDict.get(k, None)
        if old is new or new is None:
            continue

        if inspect.isclass(old):
            if debug:
                print("  Updating class %s.%s (0x%x -> 0x%x)" %
                      (module.__name__, k, id(old), id(new)))
            update_class(old, new, debug)

        elif inspect.isfunction(old):
            depth = update_function(old, new, debug)
            if debug:
                extra = ""
                if depth > 0:
                    extra = " (and %d previous versions)" % depth
                print("  Updating function %s.%s%s" %
                      (module.__name__, k, extra))

        elif lists and isinstance(old, list):
            l = len(old)
            old.extend(new)
            for i in range(l):
                old.pop(0)

        elif dicts and isinstance(old, dict):
            old.update(new)
            for k in old:
                if k not in new:
                    del old[k]


def update_function(old, new, debug):
    old.__code__ = new.__code__
    old.__defaults__ = new.__defaults__


def old_update_function(old, new, debug, depth=0, visited=None):
    # For functions:
    # 1) update the code and defaults to new versions.
    # 2) keep a reference to the previous version so ALL versions get updated for every reload
    if debug and depth > 0:
        print("    -> also updating previous version", old, " -> ", new)

    old.__code__ = new.__code__
    old.__defaults__ = new.__defaults__

    if visited is None:
        visited = []
    if old in visited:
        return
    visited.append(old)

    # finally, update any previous versions still hanging around..
    if hasattr(old, '__previous_reload_version__'):
        max_depth = old_update_function(
            old.__previous_reload_version__, new, debug, depth=depth + 1, visited=visited)
    else:
        max_depth = depth

    # We need to keep a pointer to the previous version so we remember to update BOTH
    # when the next reload comes around.
    if depth == 0:
        new.__previous_reload_version__ = old
    return max_depth


def update_class(old, new, debug):
    # For classes:
    # 1) find all instances of the old class and set instance.__class__ to the new class
    # 2) update all old class methods to use code from the new class methods

    # Track down all instances and subclasses of old
    refs = gc.get_referrers(old)
    for ref in refs:
        try:
            if isinstance(ref, old) and ref.__class__ is old:
                ref.__class__ = new
                if debug:
                    print("    Changed class for", safe_str(ref))
            elif inspect.isclass(ref) and issubclass(ref, old) and old in ref.__bases__:
                ind = ref.__bases__.index(old)

                # Does not work:
                #ref.__bases__ = ref.__bases__[:ind] + (new,) + ref.__bases__[ind+1:]
                # reason: Even though we change the code on methods, they remain bound
                # to their old classes (changing im_class is not allowed). Instead,
                # we have to update the __bases__ such that this class will be allowed
                # as an argument to older methods.

                # This seems to work. Is there any reason not to?
                # Note that every time we reload, the class hierarchy becomes more complex.
                # (and I presume this may slow things down?)
                ref.__bases__ = ref.__bases__[
                    :ind] + (new, old) + ref.__bases__[ind + 1:]
                if debug:
                    print("    Changed superclass for", safe_str(ref))
            # else:
                # if debug:
                    # print "    Ignoring reference", type(ref)
        except:
            print("Error updating reference (%s) for class change (%s -> %s)" %
                  (safe_str(ref), safe_str(old), safe_str(new)))
            raise

    # update all class methods to use new code.
    # Generally this is not needed since instances already know about the new class,
    # but it fixes a few specific cases (pyqt signals, for one)
    for attr in dir(old):
        oa = getattr(old, attr)
        if inspect.ismethod(oa):
            try:
                na = getattr(new, attr)
            except AttributeError:
                if debug:
                    print(
                        "    Skipping method update for %s; new class does not have this attribute" % attr)
                continue

            if hasattr(oa, 'im_func') and hasattr(na, 'im_func') and oa.im_func is not na.im_func:
                depth = update_function(oa.im_func, na.im_func, debug)
                # oa.im_class = new  ## bind old method to new class  ## not allowed
                if debug:
                    extra = ""
                    if depth > 0:
                        extra = " (and %d previous versions)" % depth
                    print("    Updating method %s%s" % (attr, extra))

    # And copy in new functions that didn't exist previously
    for attr in dir(new):
        if not hasattr(old, attr):
            if debug:
                print("    Adding missing attribute", attr)
            setattr(old, attr, getattr(new, attr))

    # finally, update any previous versions still hanging around..
    if hasattr(old, '__previous_reload_version__'):
        update_class(old.__previous_reload_version__, new, debug)


# It is possible to build classes for which str(obj) just causes an exception.
# Avoid thusly:
def safe_str(obj):
    try:
        s = str(obj)
    except:
        try:
            s = repr(obj)
        except:
            s = "<instance of %s at 0x%x>" % (safe_str(type(obj)), id(obj))
    return s
