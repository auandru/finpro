import ast
import json
import os
import sys

from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QColor, QPainter, QFont
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QDoubleSpinBox, \
    QTabWidget, QWidget, QColorDialog, QStyle, QStyleOptionSlider, QSlider, QHBoxLayout, QLayout
import math
from matplotlib.widgets import Cursor
import numpy as np
from matplotlib.pyplot import Annotation, Text

FILE_PATH='params.ini'

class LabeledSlider(QWidget):
    def __init__(self, minimum, maximum, interval=1, curent=1, orientation=Qt.Horizontal,
                 labels=None, parent=None):
        super(LabeledSlider, self).__init__(parent=parent)
        levels = range(minimum, maximum + interval, interval)
        if labels is not None:
            if not isinstance(labels, (tuple, list)):
                print('Exception("<labels> is a list or tuple.")')
                raise Exception("<labels> is a list or tuple.")
            if len(labels) != len(levels):
                print('Exception("Size of <labels> doesnt match levels.")')
                raise Exception("Size of <labels> doesn't match levels.")
            self.levels = list(zip(levels, labels))
        else:
            self.levels = list(zip(levels, map(str, levels)))
        if orientation == Qt.Horizontal:
            self.layout = QVBoxLayout(self)
        elif orientation == Qt.Vertical:
            self.layout = QHBoxLayout(self)
        else:
            print('Exception("<orientation> wrong.")')
            raise Exception("<orientation> wrong.")
        # gives some space to print labels
        self.left_margin = 10
        self.top_margin = 10
        self.right_margin = 10
        self.bottom_margin = 10
        self.layout.setContentsMargins(self.left_margin, self.top_margin,
                                       self.right_margin, self.bottom_margin)
        self.sl = QSlider(orientation, self)
        self.sl.setMinimum(minimum)
        self.sl.setMaximum(maximum)
        try:
            self.sl.setValue(int(curent))
        except Exception as ex:
            print(ex)
        if orientation == Qt.Horizontal:
            self.sl.setTickPosition(QSlider.TicksBelow)
            self.sl.setMinimumWidth(300)  # just to make it easier to read
        else:
            self.sl.setTickPosition(QSlider.TicksLeft)
            self.sl.setMinimumHeight(300)  # just to make it easier to read
        self.sl.setTickInterval(interval)
        self.sl.setSingleStep(1)
        self.layout.addWidget(self.sl)

    def paintEvent(self, e):

        super(LabeledSlider, self).paintEvent(e)

        style = self.sl.style()
        painter = QPainter(self)
        st_slider = QStyleOptionSlider()
        st_slider.initFrom(self.sl)
        st_slider.orientation = self.sl.orientation()

        length = style.pixelMetric(QStyle.PM_SliderLength, st_slider, self.sl)
        available = style.pixelMetric(QStyle.PM_SliderSpaceAvailable, st_slider, self.sl)

        for v, v_str in self.levels:
            # get the size of the label
            rect = painter.drawText(QRect(), Qt.TextDontPrint, v_str)
            if self.sl.orientation() == Qt.Horizontal:
                # I assume the offset is half the length of slider, therefore
                # + length//2
                x_loc = QStyle.sliderPositionFromValue(self.sl.minimum(),
                                                       self.sl.maximum(), v, available) + length // 2

                # left bound of the text = center - half of text width + L_margin
                left = x_loc - rect.width() // 2 + self.left_margin
                bottom = self.rect().bottom()

                # enlarge margins if clipping
                if v == self.sl.minimum():
                    if left <= 0:
                        self.left_margin = rect.width() // 2 - x_loc
                    if self.bottom_margin <= rect.height():
                        self.bottom_margin = rect.height()

                    self.layout.setContentsMargins(self.left_margin,
                                                   self.top_margin, self.right_margin,
                                                   self.bottom_margin)

                if v == self.sl.maximum() and rect.width() // 2 >= self.right_margin:
                    self.right_margin = rect.width() // 2
                    self.layout.setContentsMargins(self.left_margin,
                                                   self.top_margin, self.right_margin,
                                                   self.bottom_margin)

            else:
                y_loc = QStyle.sliderPositionFromValue(self.sl.minimum(),
                                                       self.sl.maximum(), v, available, upsideDown=True)

                bottom = y_loc + length // 2 + rect.height() // 2 + self.top_margin - 3
                # there is a 3 px offset that I can't attribute to any metric

                left = self.left_margin - rect.width()
                if left <= 0:
                    self.left_margin = rect.width() + 2
                    self.layout.setContentsMargins(self.left_margin,
                                                   self.top_margin, self.right_margin,
                                                   self.bottom_margin)

            pos = QPoint(left, bottom)
            painter.drawText(pos, v_str)

        return


class InputDialogSettings(QDialog):
    def __init__(self, grid_parametrs):
        super().__init__()
        # self.param = param
        self.param = grid_parametrs
        self.setWindowTitle("Settings grid")
        self.setGeometry(100, 100, 300, 200)

        central_widget = QWidget(self)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        tab_widget = QTabWidget(self)

        tab_basic = QWidget()
        layout_b = QVBoxLayout()
        self.list_proc = (0.0, 0.25, 0.5, 0.75, 1)
        self.list_small_line = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1)

        list_str = list(map(str, self.list_small_line))
        self.small_slider_linewidth = LabeledSlider(1, 10, 1, labels=list_str, curent=int(self.param[5]*10),
                                                    orientation=Qt.Horizontal)
        cur_pos = self.list_proc.index(self.param[6])
        self.small_slider_alpha = LabeledSlider(1, 5, 1, labels=('0%', '25%', '50%', '75%', '100%',), curent=cur_pos+1,
                           orientation=Qt.Horizontal)
        self.slider_linewidth = LabeledSlider(1, 10, 1, curent=self.param[3], orientation=Qt.Horizontal)
        cur_pos = self.list_proc.index(self.param[4])
        self.slider_alpha = LabeledSlider(1, 5, 1, labels=('0%', '25%', '50%', '75%', '100%',), curent=cur_pos + 1,
                                          orientation=Qt.Horizontal)
        self.label_grid = QLabel("Grid size:")
        self.label_grid_size = QLabel("Size ?:")
        self.label_grid_size.setFont(QFont('Times', 10))
        self.label_grid.setFont(QFont('Times', 10))
        self.small_label_line = QLabel("Small grid line:")
        self.small_label_line.setFont(QFont('Times', 10))
        self.label_line = QLabel("Big grid line:")
        self.label_line.setFont(QFont('Times', 10))
        self.grid_edit = QDoubleSpinBox()
        self.grid_edit.setDecimals(0)
        self.grid_edit.setRange(1, 360)
        self.grid_edit.setSingleStep(1.00)
        self.grid_edit.setFixedWidth(100)
        self.grid_edit_size = QDoubleSpinBox()
        self.grid_edit_size.setDecimals(0)
        self.grid_edit_size.setRange(1, 1000)
        self.grid_edit_size.setSingleStep(50)
        self.grid_edit_size.setFixedWidth(100)
        layout_b.addWidget(self.label_grid)
        layout_b.addWidget(self.grid_edit)
        layout_b.addWidget(self.label_grid_size)
        layout_b.addWidget(self.grid_edit_size)
        layout_b.addWidget(self.small_label_line)
        layout_b.addWidget(self.small_slider_linewidth)
        layout_b.addWidget(self.small_slider_alpha)
        layout_b.addWidget(self.label_line)

        layout_b.addWidget(self.slider_linewidth)
        layout_b.addWidget(self.slider_alpha)

        tab_basic.setLayout(layout_b)

        tab_color = QWidget()
        layout_c = QVBoxLayout()
        self.color_dialog = QColorDialog(self)
        self.color_dialog.setOption(QColorDialog.NoButtons)
        # self.color_dialog.currentColorChanged.connect(self.changed_color)
        layout_c.addWidget(self.color_dialog)
        tab_color.setLayout(layout_c)

        tab_color_bg = QWidget()
        layout_bg = QVBoxLayout()
        self.color_dialog_bg = QColorDialog(self)
        self.color_dialog_bg.setOption(QColorDialog.NoButtons)
        # self.color_dialog.currentColorChanged.connect(self.changed_color)
        layout_bg.addWidget(self.color_dialog_bg)
        tab_color_bg.setLayout(layout_bg)

#---------------------------------------------------
        tab_color_dot = QWidget()
        layout_dot = QVBoxLayout()
        self.color_dialog_dot = QColorDialog(self)
        self.color_dialog_dot.setOption(QColorDialog.NoButtons)
        # self.color_dialog.currentColorChanged.connect(self.changed_color)
        layout_dot.addWidget(self.color_dialog_dot)
        tab_color_dot.setLayout(layout_dot)

#---------------------------------------------------
        tab_color_up = QWidget()
        layout_up = QVBoxLayout()
        self.color_dialog_up = QColorDialog(self)
        self.color_dialog_up.setOption(QColorDialog.NoButtons)
        # self.color_dialog.currentColorChanged.connect(self.changed_color)
        layout_up.addWidget(self.color_dialog_up)
        tab_color_up.setLayout(layout_up)
#---------------------------------------------------
        tab_color_down = QWidget()
        layout_down = QVBoxLayout()
        self.color_dialog_down = QColorDialog(self)
        self.color_dialog_down.setOption(QColorDialog.NoButtons)
        # self.color_dialog.currentColorChanged.connect(self.changed_color)
        layout_down.addWidget(self.color_dialog_down)
        tab_color_down.setLayout(layout_down)

#---------------------------------------------------
        tab_color_cand = QWidget()
        layout_cand = QVBoxLayout()
        self.color_dialog_cand = QColorDialog(self)
        self.color_dialog_cand.setOption(QColorDialog.NoButtons)
        # self.color_dialog.currentColorChanged.connect(self.changed_color)
        layout_cand.addWidget(self.color_dialog_cand)
        
        tab_color_cand.setLayout(layout_cand)



        button = QPushButton("OK")
        button.clicked.connect(self.get_values)
        button_load = QPushButton("LOAD")
        button_load.clicked.connect(self.load_parametrs)
        button_save = QPushButton("SAVE")
        button_save.clicked.connect(self.save_params)

        tab_widget.addTab(tab_basic, "Basic")
        tab_widget.addTab(tab_color, "Line")
        tab_widget.addTab(tab_color_dot, "Dot line")
        tab_widget.addTab(tab_color_up, "UP")
        tab_widget.addTab(tab_color_down, "Down")
        tab_widget.addTab(tab_color_cand, "Candle")
        
        tab_widget.addTab(tab_color_bg, "Color BG")

        layout.addWidget(tab_widget)
        # layout.addChildLayout()
        # layout.addWidget(button)
        # layout.addWidget(button_save)

        button_layout = QHBoxLayout()

        # Добавляем кнопки в горизонтальный компоновщик
        button_layout.addWidget(button)
        button_layout.addWidget(button_load)
        button_layout.addWidget(button_save)

        # Добавляем горизонтальный компоновщик с кнопками в основной вертикальный компоновщик
        layout.addLayout(button_layout)



        self.setLayout(layout)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        if len(self.param) > 0:
            self.set_values()
            self.set_color()

    def set_values(self):
        self.grid_edit.setValue(self.param[0])
        self.grid_edit_size.setValue(self.param[8])
        
    def load_parametrs(self):
        if os.path.exists(FILE_PATH):
            with open(file=FILE_PATH,) as file:
                line = file.readline()
                self.param = ast.literal_eval(line)
                self.set_color()



    def set_color(self):
        try:
            self.color_dialog.setCurrentColor(QColor(self.param[1]))
            self.color_dialog_bg.setCurrentColor(QColor(self.param[7]))
            self.color_dialog_dot.setCurrentColor(QColor(self.param[2]))
            self.color_dialog_up.setCurrentColor(QColor(self.param[9]))
            self.color_dialog_down.setCurrentColor(QColor(self.param[10]))
            self.color_dialog_cand.setCurrentColor(QColor(self.param[11]))
        except Exception as e:
            print(f'Exctption {e}')
            pass

    def save_params(self):
        self.param = [
                    self.grid_edit.value(),
                    self.color_dialog.currentColor().name(),
                    self.color_dialog_dot.currentColor().name(), 
                    self.slider_linewidth.sl.value(),
                    self.list_proc[self.slider_alpha.sl.value()-1],
                    self.small_slider_linewidth.sl.value()/10,
                    self.list_proc[self.small_slider_alpha.sl.value() - 1],
                    self.color_dialog_bg.currentColor().name(),
                    self.grid_edit_size.value(),
                    self.color_dialog_up.currentColor().name(),
                    self.color_dialog_down.currentColor().name(),
                    self.color_dialog_cand.currentColor().name()
                    ]
        self.save_params_to_file()

    def save_params_to_file(self):
        with open(FILE_PATH, 'w') as json_file:
            json.dump(self.param, json_file)

    def get_values(self):
        self.param[0] = self.grid_edit.value()
        selected_color = self.color_dialog.currentColor()
        selected_color_bg = self.color_dialog_bg.currentColor()
        self.param[1] = selected_color.name()
        self.param[2] = self.color_dialog_dot.currentColor().name()
        self.param[3] = self.slider_linewidth.sl.value()
        self.param[4] = self.list_proc[self.slider_alpha.sl.value()-1]
        self.param[5] = self.small_slider_linewidth.sl.value()/10
        self.param[6] = self.list_proc[self.small_slider_alpha.sl.value() - 1]
        self.param[7] = selected_color_bg.name()
        self.param[8] = self.grid_edit_size.value()
        self.param[9] = self.color_dialog_up.currentColor().name()
        self.param[10] = self.color_dialog_down.currentColor().name()
        self.param[11] = self.color_dialog_cand.currentColor().name()
        # print(self.param)
        self.accept()

class MyCursor(Cursor):
    def __init__(self, bm, offset=(5, 5), **kwargs):
        self.ax = kwargs.get('ax')

        self.bm = bm
        self.offset = offset
        self.text_annot = Annotation(
                "", xy=(0, 0), xytext=self.offset, textcoords="offset points", zorder=15, annotation_clip=False)
        self.dict_label_x_with_data = {}
        super().__init__(**kwargs)
        self.visible = False

    def add_dict_x_labels(self, x_labels: dict, dec_round: float):
        self.dec_round = dec_round
        self.dict_label_x_with_data = x_labels

    def onmove(self, event):
        # PlotWindow.isLeftToRight()
        if event.inaxes != self.ax:
            if self.text_annot is not None:
                self.text_annot.set_text(None)
            super().onmove(event)
            return
        super().onmove(event)
        if not self.get_active() or not self.visible:
            return
        # Draw the widget, if event coordinates are valid.
        if self.text_annot is not None:
            if self.dec_round < 1:
                # Для чисел менее чем 1, округляем до ближайшей десятой (0.1, 0.2, 0.3, ...)
                round_num = 0.1 * math.floor(event.xdata / 0.1)
                round_num = np.round(round_num, 2)
            else:
                power_of_10 = 10 ** (len(str(int(self.dec_round))) - 1)
                round_num = power_of_10 * math.floor(event.xdata / power_of_10)

            self.text_annot.set_text(f"{self.dict_label_x_with_data.get(round_num, '')}\n{event.ydata:.5f}")
            self.text_annot.xy = (event.xdata, event.ydata)
        # self.text.set_visible(self.visible)

            if self.useblit:
                # self.ax.draw_artist(self.text)
                # if PlotWindow.collection_itms:
                #     for itm in PlotWindow.collection_itms:
                #         self.ax.draw_artist(itm)
                # self.canvas.blit(self.ax.bbox)
                self.bm.update()
            else:
                self.canvas.draw_idle()
                self.canvas.flush_events()

    def clear(self, event):
        if self.text_annot is not None:
            self.text_annot.set_text(None)
        super().clear(event)


class BlittedCursor:
    """
    A cross-hair cursor using blitting for faster redraw.
    """
    def __init__(self, ax, bm):
        self.ax = ax
        self.background = None
        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--', zorder=15, figure=self.ax.figure)
        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--', zorder=15, figure=self.ax.figure)
        # text location in axes coordinates
        self.textx = Text(0, 0, '', transform=ax.transData)
        self.textx.set_figure(self.ax.figure)
        self.textx.set_backgroundcolor('#79ffaf')
        self.texty = Text(0, 0, '', transform=ax.transData)
        self.texty.set_figure(self.ax.figure)
        self.texty.set_backgroundcolor('#79ffaf')

        self._creating_background = False
        self.bm = bm
        self.visible = False
        self.line = False
        # self.ax.figure.canvas.mpl_connect('draw_event', self.on_draw)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def set_line_paint(self):
        self.line = True

    def del_line_paint(self):    
        self.line = False

    def add_dict_x_labels(self, x_labels: dict, dec_round: float):
        self.dec_round = dec_round
        self.dict_label_x_with_data = x_labels

    def on_draw(self):
        # self.create_new_background()
        if not self.line:
            self.bm.add_artist(self.horizontal_line)
            self.bm.add_artist(self.vertical_line)
        self.bm.add_artist(self.textx)
        self.bm.add_artist(self.texty)


    def set_cross_hair_visible(self, visible):
        # need_redraw = self.horizontal_line.get_visible() != visible
        if not self.line:
            self.horizontal_line.set_visible(visible)
            self.vertical_line.set_visible(visible)
        self.textx.set_visible(visible)
        self.texty.set_visible(visible)
        # return need_redraw

    def create_new_background(self):
        if self._creating_background:
            # discard calls triggered from within this function
            return
        self._creating_background = True
        self.set_cross_hair_visible(False)
        self.ax.figure.canvas.draw()
        self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.bbox)
        self.set_cross_hair_visible(True)
        self._creating_background = False

    def on_mouse_move(self, event):
        # if self.background is None:
        #     self.create_new_background()
        if self.visible:
            if not event.inaxes:
                self.textx.set_text('')
                self.set_cross_hair_visible(False)
                # if need_redraw:
                self.bm.update()
                # self.ax.figure.canvas.restore_region(self.background)
                #     self.ax.figure.canvas.blit(self.ax.bbox)
            else:
                self.set_cross_hair_visible(self.visible)
                # update the line positions
                x, y = event.xdata, event.ydata
                if not self.line:
                    self.horizontal_line.set_ydata([y])
                    self.vertical_line.set_xdata([x])
                # self.text.set_text(f'x={x:1.2f}, y={y:1.2f}')
                if self.dec_round < 1:
                    # Для чисел менее чем 1, округляем до ближайшей десятой (0.1, 0.2, 0.3, ...)
                    round_num = 0.1 * math.floor(event.xdata / 0.1)
                    round_num = np.round(round_num, 2)
                else:
                    power_of_10 = 10 ** (len(str(int(self.dec_round))) - 1)
                    round_num = power_of_10 * math.floor(event.xdata / power_of_10)
                self.texty.set_text(f"{event.ydata:.5f}")
                if self.line:
                    self.texty.set_position((x+0.5, y))
                else:
                    self.texty.set_position((self.ax.get_xlim()[0], y))

                if self.line:
                    self.textx.set_text("")
                
                    self.textx.set_position((x+5, y))
                else:
                    self.textx.set_text(f"{self.dict_label_x_with_data.get(round_num, '')}")
                
                    self.textx.set_position((x, self.ax.get_ylim()[0]))

                self.bm.update()

    def del_artists(self):
        if not self.line:
            self.bm.remove_artist(self.horizontal_line)
            self.bm.remove_artist(self.vertical_line)
        self.bm.remove_artist(self.textx)
        self.bm.remove_artist(self.texty)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = InputDialogSettings([5, 'red', 'black', 2, 1, 0.5, 0.5, 'white', 1,'red'])
    main_window.show()
    sys.exit(app.exec_())
