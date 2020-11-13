"""
DataSources.py

Data source classes are defined here. Data sources are objects that somehow "produce" IMU data (either by reading
a serial communication, or from a file, or...) and notify that data via a PyQt5 signal.
"""
from PyQt5 import QtCore
import time
import random


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

    def __init__(self):
        """
        Class constructor, call first QObject constructor and then QRunnable constructor
        """
        super().__init__()

        self.running = False
        self.setAutoDelete(False)

    def run(self):
        """
        Inherited method from QRunnable. This method is called from a Threadpool to be run in background
        :return: Nothing
        """
        self.running = True

        """ Emit the 'work_started' signal """
        self.signals.work_started.emit()

        while self.running:
            pass

        """ Emit the 'work_stopped signal' """
        self.signals.work_stopped.emit()

    def stop(self):
        """
        Mark the object as not running
        :return:
        """
        self.running = False

    def is_running(self):
        """
        Return if the runnable is currently running or not
        :return:
        """
        return self.running


class DummyDataSource(DataSource):
    """
    Dummy data source that produces random data, just made for testing
    """

    def __init__(self):
        """
        Class constructor
        """
        super().__init__()

    def run(self):
        """
        Inherited method from QRunnable. This method is called from a Threadpool to be run in background
        :return: Nothing
        """
        self.running = True
        self.signals.work_started.emit()

        old_data_point = [0]*9
        counter = 0
        while self.running:
            # Generate new point
            data_point = [el+random.randint(-10, 10) for el in old_data_point]

            # Emit data point signal
            self.signals.data_ready.emit(data_point)

            # Prepare next iteration
            old_data_point = data_point
            time.sleep(0.1)
            counter += 1

        self.signals.work_stopped.emit()
