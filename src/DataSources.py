"""
DataSources.py

Data source classes are defined here. Data sources are objects that somehow "produce" IMU data (either by reading
a serial communication, or from a file, or...) and notify that data via a PyQt5 signal.
"""
from PyQt5 import QtCore
import time
import random
import csv

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

    def __init__(self, m=MODE_LIVE):
        """
        Class constructor
        """
        super().__init__(m)

    def run(self):
        """
        Inherited method from QRunnable. This method is called from a Threadpool to be run in background
        :return: Nothing
        """
        self._work_started()

        # line_count = sum(1 for line in open('test.csv'))
        # print("Line count: {}".format(line_count))

        with open('test.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # skip line 0, which is column headers
            next(csv_reader)

            if self.get_mode() == MODE_LIVE:
                # read rows
                while self.is_running():
                    try:
                        row = next(csv_reader)
                        self.signals.data_ready.emit([int(x) for x in row[1:]])
                        time.sleep(0.005)
                    except StopIteration:
                        self.stop()
            elif self.get_mode() == MODE_ONE_SHOT:
                self.signals.data_ready.emit([list(map(lambda x: int(x), el[1:])) for el in list(csv_reader)])
            else:
                pass

        self._work_stopped()
