import pytest

from arrhythmia.experimental.mitdb import download_mitdb
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


def test_loading_and_plotting_explore(qtbot, manager):
    """
    Simple test for loading and plotting in explore window
    """
    explore = manager.explore
    explore.load_plot_from_file("100.dat")
    explore.set_plot()

    assert explore.start == 0
    assert explore.start_line.text() == "0"
    assert explore.sig_len > 0
    assert explore.figure is not None


def test_loading_and_plotting_predict(qtbot, manager):
    """
    Simple test for loading and plotting in predict window
    """
    predict = manager.predict
    predict.load_plot_from_file("100.dat")
    predict.set_plot()

    assert predict.start == 0
    assert predict.start_line.text() == "0"
    assert predict.sig_len > 0
    assert predict.figure is not None
