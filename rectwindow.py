import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QDoubleSpinBox, QSpinBox

class InputDialog(QDialog):
    def __init__(self, param=[]):
        super().__init__()
        self.param = param
        self.setWindowTitle("Rectangle window")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.label_angle = QLabel("Angle:")
        self.line_edit_angle = QDoubleSpinBox()
        self.line_edit_angle.setDecimals(0)
        self.line_edit_angle.setRange(0, 360)
        self.line_edit_angle.setSingleStep(1.00)
        self.line_edit_angle.setFixedWidth(100)
        layout.addWidget(self.label_angle)
        layout.addWidget(self.line_edit_angle)

        self.label_number = QLabel("Quantity:")
        self.line_edit_number = QSpinBox()
        self.line_edit_number.setRange(1, 10000)
        layout.addWidget(self.label_number)
        layout.addWidget(self.line_edit_number)

        self.label_slash = QLabel("Fraction(*/*):")
        self.line_edit_slash = QLineEdit()
        layout.addWidget(self.label_slash)
        layout.addWidget(self.line_edit_slash)

        self.label_length = QLabel("Length:")
        self.line_edit_length = QSpinBox()
        self.line_edit_length.setRange(1,10000)
        self.line_edit_length.setValue(1)
        layout.addWidget(self.label_length)
        layout.addWidget(self.line_edit_length)

        button = QPushButton("OK")
        button.clicked.connect(self.get_values)
        layout.addWidget(button)

        self.setLayout(layout)
        if len(self.param) > 0:
            self.set_values()

    def set_values(self):

        self.line_edit_angle.setValue(self.param[0])
        self.line_edit_number.setValue(int(self.param[1]))
        self.line_edit_slash.setText(self.param[2])
        self.line_edit_length.setValue(int(self.param[3]))


    def get_values(self):
        self.param.clear()
        self.param.extend((self.line_edit_angle.value(),
                           self.line_edit_number.text(),
                           self.line_edit_slash.text(),
                           self.line_edit_length.text()))
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = InputDialog()
    main_window.show()
    # main_window.get_values()
    sys.exit(app.exec_())
