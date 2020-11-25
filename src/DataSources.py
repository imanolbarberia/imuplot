"""
DataSources.py

Data source classes are defined here. Data sources are objects that somehow "produce" IMU data (either by reading
a serial communication, or from a file, or...) and notify that data via a PyQt5 signal.
"""
from PyQt5 import QtCore
import time
import random
import csv
import serial

# DataSource data notification modes
MODE_LIVE = 1
MODE_ONE_SHOT = 2


class DataSourceSignals(QtCore.QObject):
    """
    Signals for the DataSource class
    """
    data_ready = QtCore.pyqtSignal(list)
    work_started = QtCore.pyqtSignal()
    work_stopped = QtCore.pyqtSignal()


class DataSource(QtCore.QRunnable):
    """
    Base DataSource class, that is a runnable that emits data signals
    """

    signals = DataSourceSignals()

    def __init__(self, m=MODE_LIVE):
        """
        Class constructor, call first QObject constructor and then QRunnable constructor
        """
        super().__init__()

        self.setAutoDelete(False)
        self._running = False
        self._mode = m
        self._name = "datasource"

    def get_name(self):
        """
        Return datasource name
        :return:
        """
        return self._name

    def get_mode(self):
        """
        Return specified mode
        :return: Mode type
        """
        return self._mode

    def _work_started(self):
        """
        Put the object in running mode and emit the start signal
        """
        self._running = True
        self.signals.work_started.emit()

    def _work_stopped(self):
        """
        Put the object in stopped mode and emit the stop signal
        """
        self._running = False
        self.signals.work_stopped.emit()

    def run(self):
        """
        Inherited method from QRunnable. This method is called from a Threadpool to be run in background
        :return: Nothing
        """
        self._work_started()

        while self._running:
            pass

        self._work_stopped()

    def stop(self):
        """
        Mark the object as not running
        :return:
        """
        self._running = False

    def is_running(self):
        """
        Return if the runnable is currently running or not
        :return:
        """
        return self._running


class DummyDataSource(DataSource):
    """
    Dummy data source that produces random data, just made for testing
    """

    def __init__(self, m=MODE_LIVE):
        """
        Class constructor
        """
        super().__init__(m)
        self._name = "dummy"

    def run(self):
        """
        Inherited method from QRunnable. This method is called from a Threadpool to be run in background
        :return: Nothing
        """
        self._work_started()

        old_data_point = [0]*9
        counter = 0
        while self.is_running():
            # Generate new point
            data_point = [el+random.randint(-10, 10) for el in old_data_point]

            # Emit data point signal
            self.signals.data_ready.emit(data_point)

            # Prepare next iteration
            old_data_point = data_point
            time.sleep(0.1)
            counter += 1

        self._work_stopped()


class FileDataSource(DataSource):
    """
    Dummy data source that produces random data, just made for testing
    """

    def __init__(self, fname, dt=0.1, m=MODE_LIVE):
        """
        Class constructor
        """
        super().__init__(m)
        self._name = None
        self._file = open(fname, "r")
        self._dt = dt

        # If opening the file failed, next line won't be executed, leaving the name as None
        self._name = fname

    def run(self):
        """
        Inherited method from QRunnable. This method is called from a Threadpool to be run in background
        :return: Nothing
        """
        self._work_started()

        csv_reader = csv.reader(self._file, delimiter=',')
        # skip line 0, which is column headers
        next(csv_reader)

        if self.get_mode() == MODE_LIVE:
            # read rows
            while self.is_running():
                try:
                    row = next(csv_reader)
                    self.signals.data_ready.emit([int(x) for x in row[1:]])
                    time.sleep(self._dt)
                except StopIteration:
                    self.stop()
        elif self.get_mode() == MODE_ONE_SHOT:
            self.signals.data_ready.emit([list(map(lambda x: int(x), el[1:])) for el in list(csv_reader)])
        else:
            pass

        self._file.close()
        self._work_stopped()


class SerialDataSource(DataSource):
    """
    Serial data source that produces data processing what's coming from the serial
    """

    def __init__(self, ser: serial.Serial):
        """
        Class constructor
        """
        super().__init__(MODE_LIVE)
        self._ser = ser
        self._name = "{}@{}".format(ser.name, ser.baudrate)

    def run(self):
        """
        Inherited method from QRunnable. This method is called from a Threadpool to be run in background
        :return: Nothing
        """
        self._work_started()
        # self._ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)

        while self.is_running():
            # Read data line
            dataline = self._ser.readline().decode()

            try:
                """
                Try and see if there is valid data
                """
                datapoint = [int(el) for el in dataline.split(",")]

                if len(datapoint) == 10:
                    """
                    If the data is valid, emit the ready signal
                    """
                    self.signals.data_ready.emit(datapoint[1:])

            except ValueError:
                """
                If data is not valid, just ignore it
                """
                pass

        self._ser.close()
        self._work_stopped()
