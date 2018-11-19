import sys

from PySide2.QtWidgets import QApplication

from arrhythmia.interface.ViewManager import ViewManager


def main():
    app = QApplication(sys.argv)
    manager = ViewManager()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
