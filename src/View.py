from PyQt5 import uic, QtWidgets
from Model import Model
from DataSources import DummyDataSource
import pyqtgraph as pg
import math


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

        # Load plot
        self._canvas = pg.GraphicsLayoutWidget()
        self.ui.layPlots.addWidget(self._canvas)
        self._plot_accx = self._canvas.addPlot(title="AccX")
        self._plot_accx_line = self._plot_accx.plot([0]*20, pen=(255, 0, 0), name="AccX")
        self._plot_accy = self._canvas.addPlot(title="AccY")
        self._plot_accy_line = self._plot_accy.plot([0]*20, pen=(0, 255, 0), name="AccY")
        self._canvas.nextRow()
        self._plot_accz = self._canvas.addPlot(title="AccZ")
        self._plot_accz_line = self._plot_accz.plot([0]*20, pen=(0, 0, 255), name="AccZ")
        self._plot_acc = self._canvas.addPlot(title="|Acc|")
        self._plot_acc_line = self._plot_acc.plot([0]*20, pen=(255, 255, 0), name="|Acc|")

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
        data_set = self._model.get_data()

        accx_data = [el[0] for el in data_set]
        accy_data = [el[1] for el in data_set]
        accz_data = [el[2] for el in data_set]
        acc_data = [math.sqrt(el[0]**2+el[1]**2+el[2]**2) for el in data_set]

        # plot the current data
        self._plot_accx_line.setData(accx_data)
        self._plot_accy_line.setData(accy_data)
        self._plot_accz_line.setData(accz_data)
        self._plot_acc_line.setData(acc_data)
