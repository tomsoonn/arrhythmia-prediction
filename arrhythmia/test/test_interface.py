from time import sleep

import pytest

from arrhythmia.interface.MenuWindow import MenuWindow
from arrhythmia.interface.ViewManager import ViewManager

@pytest.fixture
def manager(qtbot):
    """
    Starts the visual interface.
    :return: ViewManager
    """
    manager = ViewManager()
    assert manager.isVisible()
    return manager


def test_menu(qtbot, manager):
    """
    Tests that after launch current widget is menu.
    """
    current_widget = manager.currentWidget()
    menu_widget = manager.menu.window
    assert current_widget == menu_widget
