from functools import partial
import json
import sys

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QDialog, QInputDialog, QMessageBox, \
    QApplication, QCheckBox, QDoubleSpinBox, QFrame, QWidget, QLabel, QComboBox, \
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QColorDialog
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from datetime import datetime
from settingsgrid import LabeledSlider
# from plotWindow import LineAngle

FILE_PATH = 'data.json'


def create_labeled_slider(step, current_value, value_changed_slot):
    if step == 0:
        labels = [f'{round(v, 2):.2f}' for v in np.arange(1, 1 * 10 + 1, 1)]
        slider = LabeledSlider(1, len(labels), 1, labels=labels, curent=current_value / 1, orientation=Qt.Horizontal)
    else:
        labels = [f'{round(v, 2):.2f}' for v in np.arange(step, step * 10 + step, step)]
        slider = LabeledSlider(1, len(labels), 1, labels=labels, curent=current_value/step, orientation=Qt.Horizontal)
    slider.sl.valueChanged.connect(value_changed_slot)
    return slider

class AngleWindow(QDialog):
    def __init__(self, anglelist={}, linewidth=2, alpha=1,
                 step=0.25):
        super(AngleWindow, self).__init__()
        self.checkedRows = []
        self.result = QDialog.Rejected
        self.step = step
        self.step_alpha = 0.1
        self.anglelist = anglelist
        self.linewidth = linewidth
        self.line_alpha = alpha
        # set the window title and fixed size
        self.setWindowTitle("Angle Window")
        self.setFixedSize(800, 500)

        # create the main layout and add it to the window
        mainwidget = QWidget()
        main_layout = QVBoxLayout(mainwidget)
        # self.setCentralWidget(mainwidget)
        self.setLayout(main_layout)

        # create the gray box layout and add it to the main layout
        gray_box_layout = QGridLayout()
        slider_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        main_layout.addLayout(gray_box_layout)
        main_layout.addLayout(slider_layout)
        main_layout.addLayout(button_layout)

        # create the angle input and add it to the gray box layout
        angle_label = QLabel("Angle (0-360):")
        # self.angle_input = QLineEdit()
        self.angle_input = QDoubleSpinBox()
        self.angle_input.setDecimals(2)
        self.angle_input.setRange(0, 360)
        self.angle_input.setSingleStep(0.01)
        self.angle_input.setFixedWidth(100)

        angle_couple = QWidget()
        angle_label.setParent(angle_couple)
        self.angle_input.setParent(angle_couple)
        angle_label.move(20, 0)
        self.angle_input.move(120, 0)
        angle_couple.setFixedWidth(230)
        gray_box_layout.addWidget(angle_couple, 0, 0)
        # gray_box_layout.addWidget(self.angle_input, 0, 1)

        # create the color dropdown and add it to the gray box layout
        color_label = QLabel("Color:")
        # self.color_dropdown = QComboBox()
        # self.color_dropdown.addItems(["Red", "Green", "Blue"])
        self.color_dropdown = QColorDialog(self)
        self.label_color = QLabel()
        self.background_color = QColor(255, 0, 0)
        self.label_color.setStyleSheet(f'background-color: {self.background_color.name()}')
        self.label_color.setFixedSize(30, 30)
        self.color_button = QPushButton('...', self)
        self.color_button.clicked.connect(self.show_color_dialog)

        color_couple = QWidget()
        color_label.setParent(color_couple)
        # self.color_dropdown.setParent(color_couple)
        color_label.move(20, 0)
        # self.color_dropdown.move(70, 0)
        self.color_button.setParent(color_couple)
        self.label_color.setParent(color_couple)
        self.label_color.move(70, 0)
        self.color_button.move(100, 0)
        color_couple.setFixedWidth(180)
        gray_box_layout.addWidget(color_couple, 0, 1)

        # create the add button and add it to the gray box layout
        self.add_button = QPushButton("Add")
        self.add_button.setFixedWidth(150)
        self.add_button.clicked.connect(self.add_angle)
        gray_box_layout.addWidget(self.add_button, 0, 2)

        # create the angles table and add it to the gray box layout
        self.angles_table = QTableWidget()
        self.angles_table.setColumnCount(5)
        # self.angles_table.setFixedHeight(200)
        self.angles_table.setHorizontalHeaderLabels(["Angle", "Color", "Delete", "Select", "Hide"])
        gray_box_layout.addWidget(self.angles_table, 1, 0, 1, 3)

        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)

        self.ax.xaxis.set_tick_params(which='major', width=0)
        self.ax.yaxis.set_tick_params(which='major', width=0)

        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])

        self.combo_profile_items = {}
        self.combo_profile = QComboBox(self)
        self.combo_profile.addItems(self.load_items_combo())
        gray_box_layout.addWidget(self.combo_profile)
        # self.combo_profile.move(50, 50)
        self.combo_profile.activated[str].connect(self.onActivated_combo)

        self.combo_profile_bt_save = QPushButton('Save')
        # self.combo_profile_bt_save.move(50, 350)
        self.combo_profile_bt_save.clicked.connect(self.save_combo_angle)
        self.combo_profile_bt_del = QPushButton('Del')
        self.combo_profile_bt_del.move(150, 350)
        self.combo_profile_bt_del.clicked.connect(self.del_combo_angle)
        gray_box_layout.addWidget(self.combo_profile_bt_save)
        gray_box_layout.addWidget(self.combo_profile_bt_del)

        self.small_slider_linewidth = create_labeled_slider(self.step, self.linewidth,
                                                            self.linewidth_changed)
        self.small_slider_line_alpha = create_labeled_slider(self.step_alpha, self.line_alpha,
                                                             self.line_alpha_changed)

        slider_layout.addWidget(self.small_slider_linewidth)
        slider_layout.addWidget(self.small_slider_line_alpha)

        previewLabel=QLabel("Preview")
        previewLabel.setStyleSheet("margin-bottom: 170px;margin-left: 70px")
        gray_box_layout.addWidget(previewLabel, 1, 3)
        gray_box_layout.addWidget(self.canvas, 1, 3)
        self.canvas.setMaximumHeight(150)
        gray_box_layout.addWidget(self.canvas, 1, 3)

        self.ok_button = QPushButton("Ok")
        self.ok_button.setFixedWidth(150)
        # self.ok_button.setFixedHeight(50)
        
        self.ok_button.setStyleSheet("margin-top: 50px;padding:5px")
        self.ok_button.clicked.connect(self.ok_accept)

        # create the remove all button and add it to the main layout
        remove_all_button = QPushButton("Remove All")
        remove_all_button.setFixedWidth(150)
        remove_all_button.setStyleSheet("margin-top: 50px;padding:5px")
        remove_all_button.clicked.connect(self.remove_all_angles)
        button_layout.addWidget(remove_all_button) #, 4, 0
        button_layout.addWidget(self.ok_button)
        for key, val in self.anglelist.items():
            self.plotAngle(angle=key, color=val)
        self.previewPlot()

    def linewidth_changed(self):
        self.linewidth = self.small_slider_linewidth.sl.value()*self.step
        self.previewPlot()

    def line_alpha_changed(self):
        self.line_alpha = self.small_slider_line_alpha.sl.value()*self.step_alpha
        self.previewPlot()

    def ok_accept(self):
        self.linewidth = self.small_slider_linewidth.sl.value()*self.step
        self.line_alpha = self.small_slider_line_alpha.sl.value()*self.step_alpha
        self.save_items_combo()
        self.result = QDialog.Accepted
        self.close()

    def show_color_dialog(self):
        set_color = self.background_color.name()
        set_color = self.color_dropdown.getColor(QColor(set_color))
        if set_color.isValid():
            self.background_color = set_color
            self.label_color.setStyleSheet(f'background-color: {self.background_color.name()}')

    def onActivated_combo(self):
        self.remove_all_angles()
        self.anglelist.clear()
        selected_text = self.combo_profile.currentText()
        values = self.combo_profile_items.get(selected_text, [])
        for item in values:
            try:
                self.plotAngle(item[0], item[1])
                self.anglelist[item[0]] = item[1]
            except:
                pass
        self.previewPlot()

    def del_combo_angle(self):
        reply = QMessageBox()
        reply.setWindowTitle('Delete name angle')
        current_index = self.combo_profile.currentIndex()
        if current_index == 0:
            reply.setText("Select delete name.")
            reply.setIcon(QMessageBox.Information)
            reply.exec_()
            return
        else:
            reply.setText("Do you want to delete name?")
            reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            x = reply.exec()
        if x == QMessageBox.StandardButton.Yes:
            name_angle = self.combo_profile.currentText()
            self.combo_profile.removeItem(current_index)
            self.combo_profile_items.pop(name_angle)

    def save_combo_angle(self):
        text, ok = QInputDialog.getText(self, "Input name angle", "Input name:")
        if ok:
            if not text:
                message_box = QMessageBox()
                message_box.setWindowTitle("Message")
                message_box.setText("The name is empty.")
                message_box.setIcon(QMessageBox.Information)
                message_box.exec_()
                return

            if self.angles_table.rowCount() > 0:
                self.combo_profile.addItem(text)

                angles = []
                for key, row in self.anglelist.items():
                    angles.append((key, row))
                self.combo_profile_items[text] = angles
            else:
                message_box = QMessageBox()
                message_box.setWindowTitle("Message")
                message_box.setText("The list of angles is empty.")
                message_box.setIcon(QMessageBox.Information)
                message_box.exec_()

    def load_items_combo(self):
        loaded_data = ['Select ...']
        try:
            with open(FILE_PATH, 'a+') as json_file:
                json_file.seek(0)
                file_contents = json_file.read()

                if file_contents:
                    try:
                        self.combo_profile_items = json.loads(file_contents)
                        loaded_data.extend(list(self.combo_profile_items.keys()))
                    except Exception as error:
                        print(error)

        except Exception as e:
            print("error:", str(e))
        return loaded_data

    def save_items_combo(self):
        with open(FILE_PATH, 'w') as json_file:
            json.dump(self.combo_profile_items, json_file)

    def add_angle(self, angle=None, color=None):
        # get the angle and color from the inputs
        if angle is None or color is None:
            angle = float(self.angle_input.value())
            # color = self.color_dropdown.currentText()
            color = [self.background_color.name(),0]
            # check that the angle is valid
        try:
            if angle < 0 or angle > 360:
                raise ValueError
        except ValueError:
            return
        if self.add_button.text() == "Add" and angle not in self.anglelist.keys():
            # add the angle and color to the table
            self.plotAngle(angle, color)
            self.anglelist[angle] = color.copy()

        elif self.add_button.text() == "Edit":
            # myWig = QWidget()
            # frame = QFrame()
            # frame.setFixedSize(20,20)
            # frame.setParent(myWig)
            # label_1 = QLabel() #f" {color}"
            # label_1.setParent(myWig)
            # frame.move(0, 0)
            # label_1.move(30, 0)
            # myWig.setFixedHeight(25)
            for row in range(self.angles_table.rowCount()):

                    changeit = self.angles_table.cellWidget(row,3)
                    if changeit.isChecked():
                        myWig = self.angles_table.cellWidget(row, 1)
                        frame = myWig.findChild(QFrame)
                        if frame:
                            frame.setStyleSheet(f"background-color: {color[0]};")
                        angle = float(self.angles_table.item(row, 0).text())
                        hideit = self.angles_table.cellWidget(row,4)
                        if hideit.isChecked():
                            color[1]= 1
                        else:
                            color[1]= 0
                        self.anglelist[angle] = color.copy()            
        self.set_text_button_add()
        self.previewPlot()

    def change_cell(self):
        pass

    def set_text_button_add(self):
        self.add_button.setText('Add')
        for row in range(self.angles_table.rowCount()):
            cw = self.angles_table.cellWidget(row,3)
            if cw.isChecked():
                self.add_button.setText('Edit')
                break
            

    def plotAngle(self, angle, color: list):
        row_count = self.angles_table.rowCount()
        self.angles_table.insertRow(row_count)
        self.angles_table.setItem(row_count, 0, QTableWidgetItem(str(angle)))
        my_wig = QWidget()
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {color[0]}")
        frame.setFixedSize(20, 20)
        frame.setParent(my_wig)
        label_1 = QLabel()
        label_1.setParent(my_wig)
        frame.move(0, 0)
        label_1.move(30, 0)
        my_wig.setFixedHeight(25)

        self.angles_table.setCellWidget(row_count, 1, my_wig)
        delete_button = QPushButton("X")
        delete_button.clicked.connect(lambda r=row_count: self.delete_angle(r))
        delete_button.setFixedHeight(25)
        self.angles_table.setCellWidget(row_count, 2, delete_button)

        self.checkBox = QCheckBox()
        self.checkBox.stateChanged.connect(lambda state, r=row_count: self.checkButton(state, r))
        self.checkBox.setFixedHeight(25)
        self.checkBox.setStyleSheet("margin-left: 50px")
        self.angles_table.setCellWidget(row_count, 3, self.checkBox)

        # self.checkBoxHide = QCheckBox()
        # if color:
        #     if color[1] == 1:
        #         self.checkBoxHide.setChecked(True)
        # self.checkBoxHide.stateChanged.connect(lambda state, r=row_count: self.checkButtonHide(state, r))
        # self.checkBoxHide.setFixedHeight(25)
        # self.checkBoxHide.setStyleSheet("margin-left: 50px")
        # self.angles_table.setCellWidget(row_count, 4, self.checkBoxHide)
        check_box_hide = QCheckBox()
        if color and color[1] == 1:
            check_box_hide.setChecked(True)
        check_box_hide.stateChanged.connect(self.checkButtonHide)
        check_box_hide.setFixedHeight(25)
        check_box_hide.setStyleSheet("margin-left: 50px;")
        self.angles_table.setCellWidget(row_count, 4, check_box_hide)
        
        self.angles_table.setRowHeight(row_count, 20)

    def delete_angle(self, row):
        
        row = self.angles_table.currentRow()

        del self.anglelist[float(self.angles_table.item(row, 0).text())]
        self.angles_table.removeRow(row)
        try:
            self.checkedRows.remove(row)
        except:
            pass    
        
        self.set_text_button_add()
        self.previewPlot()

    def remove_all_angles(self):
        self.checkedRows = []
        self.anglelist = {}
        self.angles_table.setRowCount(0)
        self.previewPlot()
        self.set_text_button_add()

    def checkButtonHide(self, state):
        row = self.angles_table.currentRow()
        selectedAngle = self.angles_table.item(row, 0).text()
        selectedAngle = float(selectedAngle)
        l_color_hide = self.anglelist[selectedAngle]
        if state == 0:
            self.anglelist[selectedAngle] = [l_color_hide[0], 0]
        elif state == 2:
            self.anglelist[selectedAngle] = [l_color_hide[0], 1]
        self.previewPlot()

    def checkButton(self, state, row):
        row = self.angles_table.currentRow()
        if state == 0:  # Сняли галочку
            if row in self.checkedRows:
                self.checkedRows.remove(row)
            # if not self.checkedRows:
                
        elif state == 2:  # Поставили галочку
            self.checkedRows.append(row)
            # self.add_button.setText("Edit")


        # Обновляем элементы управления для первой выбранной строки
        if self.checkedRows:
            selectedRow = row  # Первая выделенная строка
            selectedAngle = float(self.angles_table.item(selectedRow, 0).text())
            self.angle_input.setValue(selectedAngle)
            self.background_color = QColor(self.anglelist[selectedAngle][0])
            self.label_color.setStyleSheet(f'background-color: {self.background_color.name()}')

        self.set_text_button_add()

    def previewPlot(self):
        self.ax.clear()
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)

        self.ax.xaxis.set_tick_params(which='major', width=0)
        self.ax.yaxis.set_tick_params(which='major', width=0)

        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])

        angles = list(self.anglelist.keys())
        angles1 = np.deg2rad(angles)

        x = np.array([1 if (i <= 90 or i >= 270) else -1 for i in angles])
        y = np.tan(angles1) * x

        for val in range(len(x)):
            angle = float(angles[val])
            color = self.anglelist[angle][0]
            hiden_itm = self.anglelist[angle][1]

            if hiden_itm == 0:
                # Обработка случая углов 90 и 270 градусов
                if angle == 90:
                    self.ax.plot([0, 0], [0, 1], color=color, alpha=self.line_alpha, linewidth=self.linewidth)
                elif angle == 270:
                    self.ax.plot([0, 0], [0, -1], color=color, alpha=self.line_alpha, linewidth=self.linewidth)
                else:
                    self.ax.plot([0, x[val]], [0, y[val]], color=color, alpha=self.line_alpha, linewidth=self.linewidth)

        self.canvas.draw()

    def getAngleList(self):
        return self.anglelist


if __name__ == '__main__':
    app = QApplication(sys.argv)
    angle_window = AngleWindow()
    angle_window.show()
    sys.exit(app.exec_())