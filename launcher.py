from PySide2 import QtWidgets
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import importlib, sys

from .ui.main_ui import VenAutoRig

def get_maya_window():
    """ Return Maya main window as QMainWindow."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)

def show_ui():
    global win
    try:
        win.close()
    except:
        pass

    win = VenAutoRig(get_maya_window())
    win.show()

def reload_and_launch():
    """Reload the whole package and relaunch the UI."""
    import ven_autorig  # your package name here
    recursive_reload(ven_autorig)
    return show_ui()


def recursive_reload(package):
    name = package.__name__
    for modname in list(sys.modules.keys()):
        if modname.startswith(name):
            importlib.reload(sys.modules[modname])
