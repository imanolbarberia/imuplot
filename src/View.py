from PyQt5 import uic, QtWidgets
from Model import Model
from DataSources import DummyDataSource, FileDataSource
import DataSources
import pyqtgraph as pg
import math


class SensorAxisPlot:
    def __init__(self, cnv: pg.GraphicsLayoutWidget, name, pen):
        self.plot = cnv.addPlot(title=name)
        self.line = self.plot.plot([0]*20, pen=pen, name=name)


class SensorCanvas(pg.GraphicsLayoutWidget):
    def __init__(self, basename):
        super().__init__()
        self.x = SensorAxisPlot(self, basename+"X", (255, 0, 0))
        self.y = SensorAxisPlot(self, basename+"Y", (0, 255, 0))
        self.nextRow()
        self.z = SensorAxisPlot(self, basename+"Z", (0, 0, 255))
        self.a = SensorAxisPlot(self, "|"+basename+"|", (255, 255, 0))


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
        self._acc_canvas = SensorCanvas("Acc")
        self.ui.layAccel.addWidget(self._acc_canvas)
        self._gyro_canvas = SensorCanvas("Gyro")
        self.ui.layGyro.addWidget(self._gyro_canvas)
        self._mag_canvas = SensorCanvas("Mag")
        self.ui.layMag.addWidget(self._mag_canvas)

        # Set model
        self._model = Model()
        self._model.set_data_src(FileDataSource(m=DataSources.MODE_ONE_SHOT))
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

        gyrox_data = [el[3] for el in data_set]
        gyroy_data = [el[4] for el in data_set]
        gyroz_data = [el[5] for el in data_set]
        gyro_data = [math.sqrt(el[3]**2+el[4]**2+el[5]**2) for el in data_set]

        magx_data = [el[6] for el in data_set]
        magy_data = [el[7] for el in data_set]
        magz_data = [el[8] for el in data_set]
        mag_data = [math.sqrt(el[6]**2+el[7]**2+el[8]**2) for el in data_set]

        # plot current ACC data
        self._acc_canvas.x.line.setData(gyrox_data)
        self._acc_canvas.y.line.setData(accy_data)
        self._acc_canvas.z.line.setData(accz_data)
        self._acc_canvas.a.line.setData(acc_data)

        # plot current GYRO data
        self._gyro_canvas.x.line.setData(gyrox_data)
        self._gyro_canvas.y.line.setData(gyroy_data)
        self._gyro_canvas.z.line.setData(gyroz_data)
        self._gyro_canvas.a.line.setData(gyro_data)

        # plot current MAG data
        self._mag_canvas.x.line.setData(magx_data)
        self._mag_canvas.y.line.setData(magy_data)
        self._mag_canvas.z.line.setData(magz_data)
        self._mag_canvas.a.line.setData(mag_data)
