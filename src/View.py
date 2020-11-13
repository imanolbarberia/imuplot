from PyQt5 import QtCore, uic, QtWidgets
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from Model import Model
from DataSources import DummyDataSource
import random

matplotlib.use("Qt5Agg")


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(111)

        super().__init__(fig)


class View(QtWidgets.QMainWindow):
    """
    View class
    """
    def __init__(self):
        """
        Class constructor
        """
        super().__init__()

        # Load UI layout
        self.ui = uic.loadUi("ui/wndmain.ui", self)

        # Add plot canvas
        self._canvas = MplCanvas(self)
        self.ui.layPlots.addWidget(self._canvas)
        self._plot_x = None
        self._xdata = list(range(20))
        self._ydata = [0]*20
        self.on_data_received()

        # Set model
        self._model = Model()
        self._model.set_data_src(DummyDataSource())
        self._model.data_received.connect(self.on_data_received)

        # Connect widget signals
        self.ui.btnTest.clicked.connect(self.on_btn_test_clicked)

    def closeEvent(self, event):
        """
        Event for when closing the window, either by menu or by close button
        :return:
        """
        if self._model.get_data_src() is not None:
            """
            We have a data source selected
            """
            if self._model.is_listening():
                """
                Frame listening ongoing, so stop it
                """
                self._model.stop_listening()

                # Wait until it is finished
                while self._model.is_listening():
                    QtWidgets.QApplication.processEvents()

            else:
                """
                No frame listening ongoing, we can leave safely
                """
                pass

        else:
            """
            No frame source selected, no problem
            """
            pass

        event.accept()

    def on_btn_test_clicked(self):
        if self._model.is_listening():
            self._model.stop_listening()
        else:
            self._model.start_listening()

    def on_data_received(self):
        """
        Update and redraw plot with new data
        """
        if self._plot_x is None:
            """
            Initial draw
            """
            plot_refs = self._canvas.axes.plot(self._xdata, self._ydata, 'r')
            self._plot_x = plot_refs[0]
            self._canvas.axes.set_ylim(-200, 200)
            self._canvas.axes.set_xticks(list(range(20)))
            self._canvas.axes.set_xticklabels([0]*20, rotation=45)
            self._canvas.axes.grid()
        else:
            """
            Process new data
            """
            data_set = self._model.get_data()
            datalen = len(data_set)

            if len(data_set) < 20:
                self._ydata = [0]*(20-datalen)+[el[0] for el in data_set]
                self._canvas.axes.set_xticklabels([0]*(20-datalen)+list(range(datalen)))
            else:
                self._ydata = [el[0] for el in data_set[datalen-20:]]
                self._canvas.axes.set_xticklabels(list(range(datalen-20, datalen)))

            self._plot_x.set_ydata(self._ydata)

        self._canvas.draw()




