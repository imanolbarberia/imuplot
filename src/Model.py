from PyQt5 import QtCore
from DataSources import DataSource


class Model(QtCore.QObject):
    """
    Model class
    """
    data_src_changed = QtCore.pyqtSignal()
    data_received = QtCore.pyqtSignal(list)

    def __init__(self):
        """
        Class constructor
        """
        super().__init__()
        self._data_list = []
        self._listening = False
        self._data_src = None
        self._thpool = QtCore.QThreadPool()

    def add_data_point(self, d):
        """
        Add data point to the data list
        :param d: List with 9 values (3 params with 3 axis each)
        :return: True if the value was correctly added
        """
        if len(d) != 9:
            ret = False
        else:
            self._data_list += [d]
            self.data_received.emit(d)
            ret = True

        return ret

    def get_data(self):
        """
        Return data set
        :return: List of data points
        """
        return self._data_list

    def set_data_src(self, src: DataSource):
        """
        Set the DataSource object to get data from
        :param src: DataSource object
        """
        self._data_src = src
        self.data_src_changed.emit()

    def get_data_src(self):
        """
        Return selected data source
        :return: None if no data source is selected, a DataSource object otherwise
        """
        return self._data_src

    def start_listening(self):
        """
        Starts to run the data source as a separate thread and connects signals

        :return: True if the thread started correctly, False otherwise
        """
        if self._data_src is None:
            """ 
            No data source defined
            """
            ret = False

        elif self._data_src.is_running():
            """
            If the data source is already running, just don't start again
            """
            ret = False

        else:
            """
            Data source selected
            """
            # Connect signals and start running
            self._data_src.signals.work_started.connect(self.data_src_started)
            self._data_src.signals.work_stopped.connect(self.data_src_stopped)
            self._data_src.signals.data_ready.connect(self.add_data_point)
            self._thpool.start(self._data_src)

            ret = True

        return ret

    def stop_listening(self):
        """
        Stops listening to new data

        :return: True if the thread was running, False otherwise
        """
        if self._data_src is None:
            """
            If no data source defined, none to stop
            """
            ret = False

        elif not self._listening:
            """
            If the current source is not emitting data, just don't stop anything...
            """
            ret = False

        else:
            """
            Otherwise
            """
            # Disconnect signals
            self._data_src.signals.work_started.disconnect(self.data_src_started)
            self._data_src.signals.data_ready.disconnect(self.add_data_point)
            self._data_src.stop()

    @QtCore.pyqtSlot()
    def data_src_started(self):
        """
        Slot when data source starts working
        """
        self._listening = True
        self.data_src_changed.emit()

    @QtCore.pyqtSlot()
    def data_src_stopped(self):
        """
        Slot when data source stops working
        """
        self._listening = False
        self.data_src_changed.emit()

    def is_listening(self):
        """
        Return if already listening to incoming data
        :return: True if listening, False otherwise
        """
        return self._listening
