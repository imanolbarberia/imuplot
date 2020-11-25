from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from Model import Model
from DataSources import DummyDataSource, FileDataSource, SerialDataSource
import DataSources
import pyqtgraph as pg
import math
import serial.tools.list_ports


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


class SessionDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # Load layout
        self.ui = uic.loadUi("ui/wndsession.ui", self)
        self.ui.optFile.toggled.connect(self.on_source_selected)
        self.ui.optSerial.toggled.connect(self.on_source_selected)
        self.ui.btnRefresh.clicked.connect(self.refresh_serial_list)
        self.ui.btnFileSelect.clicked.connect(self.select_file)

        self.refresh_serial_list()

        # Default enable
        self.ui.txtFileSelect.setEnabled(True)
        self.ui.btnFileSelect.setEnabled(True)
        self.ui.lblUpdateMode.setEnabled(True)
        self.ui.optLive.setEnabled(True)
        self.ui.optOneShot.setEnabled(True)
        self.ui.cmbSerial.setEnabled(False)
        self.ui.btnRefresh.setEnabled(False)

    def select_file(self):
        opts = QFileDialog.Options()
        opts |= QFileDialog.DontUseNativeDialog
        fname, _ = QFileDialog.getOpenFileName(self,
                                               "Select log file", "", "CSV files (*.csv);;All files (*)",
                                               options=opts)
        self.ui.txtFileSelect.setText(fname)

    def refresh_serial_list(self):
        self.ui.cmbSerial.clear()

        lst = serial.tools.list_ports.comports()

        if len(lst) == 0:
            self.ui.cmbSerial.addItem("<No available ports>")
        else:
            for port, desc, hwid in sorted(lst):
                self.ui.cmbSerial.addItem(port)

    def get_config(self):
        if self.ui.optFile.isChecked():
            src = 0
            name = self.ui.txtFileSelect.text()
            if self.ui.optLive.isChecked():
                mode = DataSources.MODE_LIVE
            else:
                mode = DataSources.MODE_ONE_SHOT
        else:
            src = 1
            name = self.ui.cmbSerial.currentText()
            mode = DataSources.MODE_LIVE

        return src, name, mode

    def on_source_selected(self):
        opt = self.sender()
        if opt.isChecked():
            if opt == self.ui.optFile:
                self.ui.txtFileSelect.setEnabled(True)
                self.ui.btnFileSelect.setEnabled(True)
                self.ui.lblUpdateMode.setEnabled(True)
                self.ui.optLive.setEnabled(True)
                self.ui.optOneShot.setEnabled(True)
                self.ui.cmbSerial.setEnabled(False)
                self.ui.btnRefresh.setEnabled(False)

            elif opt == self.ui.optSerial:
                self.ui.txtFileSelect.setEnabled(False)
                self.ui.btnFileSelect.setEnabled(False)
                self.ui.lblUpdateMode.setEnabled(False)
                self.ui.optLive.setEnabled(False)
                self.ui.optOneShot.setEnabled(False)
                self.ui.cmbSerial.setEnabled(True)
                self.ui.btnRefresh.setEnabled(True)


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
        self._session_dialog = SessionDialog()
        self._lblStatus = QtWidgets.QLabel("")
        self.statusBar().addWidget(self._lblStatus)

        # Load plot tabs
        self.ui.tabPlots.setEnabled(False)
        self._acc_canvas = SensorCanvas("Acc")
        self.ui.layAccel.addWidget(self._acc_canvas)
        self._gyro_canvas = SensorCanvas("Gyro")
        self.ui.layGyro.addWidget(self._gyro_canvas)
        self._mag_canvas = SensorCanvas("Mag")
        self.ui.layMag.addWidget(self._mag_canvas)

        # Set model
        self._model = Model()
        self._model.data_received.connect(self.on_data_received)

        # Connect widget signals
        self.ui.mnu_session_new.triggered.connect(self.on_mnu_session_new)
        self.ui.mnu_session_close.triggered.connect(self.on_mnu_session_close)
        self.ui.mnu_session_exit.triggered.connect(self.on_mnu_session_exit)
        self.ui.mnu_help_about.triggered.connect(self.on_mnu_help_about)

        self.update_gui_status()

    def on_mnu_session_new(self):
        session_start = self._session_dialog.exec()

        if session_start == 1:
            # If OK button pressed
            ds, nm, md = self._session_dialog.get_config()

            if ds == 0:
                # File data source selected
                if nm == "":
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Name empty")
                    msg.setText("CSV file name not specified")
                    msg.setIcon(QMessageBox.Critical)
                    msg.exec()
                else:
                    self._model.set_data_src(FileDataSource(m=md))
                    self._model.start_listening()

            else:
                # Serial data source selected
                is_available = True
                try:
                    ser = serial.Serial(nm, 115200)
                    ser.close()
                except serial.SerialException:
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Serial port not available")
                    msg.setText("Port '{}' is already in use.".format(nm))
                    msg.setIcon(QMessageBox.Critical)
                    msg.exec()
                    is_available = False

                if is_available:
                    self._model.set_data_src(SerialDataSource())
                    self._model.start_listening()
        else:
            # If Cancel button pressed
            pass

        self.update_gui_status()

    def update_gui_status(self):
        if self._model.get_data_src() is None:
            self.ui.mnu_session_new.setEnabled(True)
            self.ui.mnu_session_close.setEnabled(False)
            self.ui.tabPlots.setEnabled(False)
            self._lblStatus.setText("No session.")
        else:
            self.ui.mnu_session_new.setEnabled(False)
            self.ui.mnu_session_close.setEnabled(True)
            self.ui.tabPlots.setEnabled(True)
            self._lblStatus.setText("ToDo: add session description")

    def on_mnu_session_close(self):
        if self._model.get_data_src() is not None:
            if self._model.is_listening():
                self._model.stop_listening()

                # Wait until it is finished
                while self._model.is_listening():
                    QtWidgets.QApplication.processEvents()

            else:
                pass

            self._model.set_data_src(None)

        else:
            pass

        self.update_gui_status()

    def on_mnu_session_exit(self):
        self.close()

    def on_mnu_help_about(self):
        pass

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
        self._acc_canvas.x.line.setData(accx_data)
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
