#!/usr/bin/env python3

import sys
from PyQt5 import QtWidgets
from View import View


def main():
    app = QtWidgets.QApplication(sys.argv)
    v = View()

    v.show()

    app.exec_()


if __name__ == "__main__":
    main()
