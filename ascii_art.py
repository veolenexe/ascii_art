from graphic_user_interface import UserInterface
import sys
import os
from PyQt5.QtWidgets import QApplication


def main():
    QApplication.addLibraryPath(os.getcwd())
    app = QApplication(sys.argv)
    gui = UserInterface()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
