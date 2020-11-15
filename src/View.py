from PyQt5 import uic, QtWidgets
from Model import Model
from DataSources import DummyDataSource
import pyqtgraph as pg


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
        self._canvas = pg.PlotWidget()
        self.ui.layPlots.addWidget(self._canvas)
        self._plot_ref = self._canvas.plot([0]*20, pen=(255, 0, 0), name="AccX")

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

        y_data = [el[0] for el in data_set]

        # plot the current data
        self._plot_ref.setData(y_data)
