import sys

from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox


class FractionWindow(QWidget):

    def __init__(self,fraction=1,minPoint=0.0001,neumerator=1,denominator=1):
        super().__init__()

        self.onlyDoubl = QDoubleValidator()
        self.Fraction=fraction
        self.neumerator=neumerator
        self.denominator=denominator
        self.Minpoint=minPoint
        # Create input fields and button

        self.setWindowTitle("Set Fraction")
        self.setFixedSize(250,180)
        self.label1 = QLabel('Numerator      ')
        self.input1 = QLineEdit()

        self.label2 = QLabel('Denominator   ')
        self.input2 = QLineEdit()

        self.label4 = QLabel('Minimum Point')
        self.input4 = QLineEdit()

        self.label3 = QLabel('')

        self.button = QPushButton('Ok')
        # self.button.clicked.connect(self.on_submit)

        # Add input fields and button to layout
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.label1)
        hbox1.addWidget(self.input1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.label2)
        hbox2.addWidget(self.input2)

        hbox5 = QHBoxLayout()
        hbox5.addWidget(self.label4)
        hbox5.addWidget(self.input4)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.label3)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.button)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        # vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)
        vbox.addLayout(hbox3)

        # Set layout
        self.setLayout(vbox)

        self.input1.setText(str(self.neumerator))
        self.input2.setText(str(self.denominator))
        self.input4.setText(str("{:.5f}".format(self.Minpoint)))


    def on_submit(self):

        # Get values from input fields
        val1 = self.input1.text()
        val2 = self.input2.text()
        minPoint=self.input4.text()

        # Check if input2 is 0
        if val1=='':
           QMessageBox.warning(self, 'Warning', 'Numerator cannot be Empty') 
           return False
        elif val2=='':
           QMessageBox.warning(self, 'Warning', 'Denominator cannot be Empty')  
           return False
        elif val2 == '0' or val1=='0':
            QMessageBox.warning(self, 'Warning', 'Cannot be 0')
            return False
        elif minPoint=="" or minPoint=='0':
            QMessageBox.warning(self, 'Warning', 'Minimum point must be at least 0.00001 to max 0.9')
            return False

        try:
            val1=int(val1)
            val2=int(val2)
            self.Fraction=round(val1/val2,10)
            minPoint=float(minPoint)

            if minPoint>0.9 or minPoint<0.00001:
                   QMessageBox.warning(self, 'Warning', 'Minimum point must be at least 0.0001 to max 0.9')
                   return False
            
            self.Minpoint=minPoint
            self.neumerator=val1
            self.denominator=val2
            return True
            # self.label3.setText(round(val1/val2,4))

        except:
            QMessageBox.warning(self, 'Warning', 'Please Enter Numerical Values.')
            return False
        


        # # Print values
        # print('Input 1:', val1)
        # print('Input 2:', val2)

if __name__ == '__main__':
    
    # Create application and window
    app = QApplication(sys.argv)
    window = FractionWindow()
    window.show()
    sys.exit(app.exec_())
