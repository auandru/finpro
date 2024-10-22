# import sys
# from PyQt5.QtWidgets import QApplication, QSizePolicy, QDateEdit, QWidget, QDoubleSpinBox, QMainWindow, QLabel, \
#     QPushButton, QHBoxLayout, QFileDialog, QComboBox, QVBoxLayout
# import pandas as pd
# import mplfinance as mpf
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# import pandas as pd
# from matplotlib.ticker import MultipleLocator
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QDateEdit, QDoubleSpinBox, QFileDialog
from plotWindow import PlotWindow
import sys
import pandas as pd

# from PySide2 import QtWidgets


class CandlestickGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.setWindowTitle("Candlestick Chart")
        self.windowWidth = 800
        self.startRange = 20
        self.baseHeight = 30

        self.setFixedSize(self.windowWidth, 300)
        # Create file selection button
        self.file_label = QLabel(self)
        self.file_label.setText("Select CSV file:")
        self.file_label.move(self.startRange, self.baseHeight)

        self.startRange += 85
        self.file_button = QPushButton(self)
        self.file_button.setText("Select File")
        self.file_button.move(self.startRange, self.baseHeight)
        self.file_button.clicked.connect(self.select_file)

        # Create date range selection fields
        self.startRange += 150
        self.start_date_label = QLabel(self)
        self.start_date_label.setText("Start Date (Y-M-D):")
        self.start_date_label.move(self.startRange, self.baseHeight)
        # self.start_date_entry = QLineEdit(self)
        self.startRange += 120

        self.date_edit = QDateEdit(QDate.currentDate(), self)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.move(self.startRange, self.baseHeight)

        self.startRange += 150
        self.end_date_label = QLabel(self)
        self.end_date_label.setText("End Date (YY-M-D):")
        self.end_date_label.move(self.startRange, self.baseHeight)

        self.startRange += 120
        self.end_date_entry = QDateEdit(QDate.currentDate(), self)
        self.end_date_entry.setDisplayFormat('yyyy-MM-dd')
        self.end_date_entry.move(self.startRange, self.baseHeight)

        # Create candle width selection field
        self.baseHeight += 40
        self.startRange = 20

        self.candle_width_label = QLabel(self)
        self.candle_width_label.setText("Candle Width(x% of width):")

        self.candle_width_label.move(self.startRange, self.baseHeight)
        self.candle_width_label.setMinimumWidth(350)
        # self.candle_width_entry = QLineEdit(self)
        self.startRange += 180

        self.doubleSpinBox = QDoubleSpinBox(self)
        self.doubleSpinBox.setDecimals(2)
        self.doubleSpinBox.setRange(0, 100)
        self.doubleSpinBox.setSingleStep(0.01)
        self.doubleSpinBox.move(self.startRange, self.baseHeight)

        self.baseHeight += 60

        # Create plot button
        self.plot_button = QPushButton(self)
        self.plot_button.setText("Plot")
        self.plot_button.move(int(self.windowWidth / 2) - 50, self.baseHeight)
        self.plot_button.clicked.connect(self.plot_candles)

        self.baseHeight += 60

        self.errorLabel = QLabel(self)
        self.errorLabel.setStyleSheet("color: red;")

        self.errorLabel.setMinimumWidth(350)
        self.errorLabel.move(20, self.baseHeight)

        # self.showMaximized()
        self.plot_windows = []

    def select_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV file")
        self.errorDisplay(' ')
        # self.file_button.setText(self.file_path)

    def errorDisplay(self, error):
        self.errorLabel.setText(f'{self.file_path} {error}')

    def getDataFrame(self):
        startDate = self.date_edit.date().toPyDate()
        endDate = self.end_date_entry.date().toPyDate()

        timestamp = pd.Timestamp(startDate)
        timestamp2 = pd.Timestamp(endDate)
        # Load data from CSV file
        if self.file_path is None:
            self.errorDisplay("Please Select a File path")
            return None

        df = pd.read_csv(self.file_path, names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y.%m.%d %H:%M')
        df['Date'] = pd.to_datetime(df['Date'], format='%Y.%m.%d')

        df = df[df['Date'] >= timestamp]
        df = df[df['Date'] <= timestamp2]

        if df.shape[0] <= 0:
            self.errorDisplay("Empty!!!.No Data To Display")
            return None
        return df


    def plot_candles(self, empty=False):
        self.errorDisplay(" ")
        df = self.getDataFrame()
        if df is None:
            return
        persentageVal = float(self.doubleSpinBox.value())
        plot_window = PlotWindow(df=df, persentageVal=persentageVal)
        self.plot_windows.append(plot_window)
        plot_window.show()


    def setDate(self, date):
        self.startDate = date


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = CandlestickGUI()
    gui.show()
    sys.exit(app.exec())
