# -*- coding: utf-8 -*-

# ************** The Interface is designed by Bahadır ÇÖKMEZ for the GAZİ-TEK Lift-Up team **************

# Form implementation generated from reading ui file 'gazi_tek.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas #**************
import matplotlib.pyplot as plt #**************
from PyQt5.QtCore import QTimer #**************

import datetime       #**************
#import ui_arduino_com #**************
import time     #**************
import gazi_tek_media   #**************

class Ui_MainWindow(object):

    x_values = [] #**************
    y_values = [] #**************
    widgets = [] #**************
    iteration = 1

    x_value_from_user = 1.0
    y_value_from_user = 1.0

    def __init__(self):     #**************
        super().__init__()
        # Other initialization code
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_expired)
 
    def start_execute_methods(self):    #**************
        self.x_value_from_user = float(self.lineEdit_x_input.text())
        self.y_value_from_user = float(self.lineEdit_y_input.text())
        self.update_progress_bar(0)
        QtWidgets.QApplication.processEvents()
        if self.check_inputs():
            if self.send_inputs_to_ui_arduino_com():
                self.label_area_and_scan_mode_output.setText("Inputs taken successfully!")
                self.label_area_and_scan_mode_output.setStyleSheet("background-color: lightgreen")
                self.label_start_output.setText("Scanning...")
                self.label_start_output.setStyleSheet("background-color: lightgreen")
                self.pushButton_start.setEnabled(False)
                QtWidgets.QApplication.processEvents()
                self.timer.start(1000)  # Start the timer with an interval of 1000 milliseconds (1 second)
            else:
                self.label_area_and_scan_mode_output.setText("Transmitting Failed! Please Restart!")
                self.label_area_and_scan_mode_output.setStyleSheet("background-color: rgb(255, 75, 75);")
                self.label_start_output.setText("Scanning Failed!")
                self.label_start_output.setStyleSheet("background-color: rgb(255, 75, 75);")
                self.pushButton_start.setEnabled(True)
                QtWidgets.QApplication.processEvents()
        self.timer_expired()

    def timer_expired(self):    #**************
        start_time = time.time()
        try:
            if ui_arduino_com.arduino.readable():
                data_read = ui_arduino_com.arduino.readline().decode('utf-8').rstrip()
                if data_read == "COMPLETED":
                    print(data_read)
                    elapsed_time = time.time() - start_time
                    print("Time elapsed: {:.6f} seconds".format(elapsed_time))
                    self.label_start_output.setText("Scanning Done Successfully!")
                    self.label_start_output.setStyleSheet("background-color: lightgreen")
                    self.pushButton_start.setEnabled(False)
                    self.update_progress_bar(100)
                    QtWidgets.QApplication.processEvents()
                    self.timer.stop()  # Stop the timer when scanning is done
                elif data_read == "OBJECT_DETECTED":
                    ui_arduino_com.arduino.write(("OBJECT_DETECTED_ACK").encode('utf-8'))
                    if ui_arduino_com.arduino.readable():
                        data_read = ui_arduino_com.arduino.readline().decode('utf-8').rstrip()
                        if data_read:
                            print(data_read)
                            self.graph_producer(float(data_read.split(",")[0]), float(data_read.split(",")[1]))
                            current_date_and_time = datetime.datetime.now()
                            self.message_producer("Object {}".format(self.iteration))
                            self.message_producer("Time: " + str(current_date_and_time.time()).split(".")[0])
                            self.message_producer("Date: " + str(current_date_and_time.date()))
                            self.message_producer("Lat: " + data_read.split(",")[2])
                            self.message_producer("Long: " + data_read.split(",")[3])
                            self.message_producer("******************************")
                            self.iteration += 1
                            elapsed_time = time.time() - start_time
                            print("Time elapsed: {:.6f} seconds".format(elapsed_time))
                            QtWidgets.QApplication.processEvents()
                        else:
                            print(data_read)
                            elapsed_time = time.time() - start_time
                            print("Time elapsed: {:.6f} seconds".format(elapsed_time))
        except Exception as err:
            print(err)
            elapsed_time = time.time() - start_time
            print("Time elapsed: {:.6f} seconds".format(elapsed_time))

    def message_producer(self, new_message): #**************
        self.textEdit_coordinates.append(new_message)

    def graph_producer(self, relative_x, relative_y): #**************

        # create a matplotlib figure and axis
        fig, ax = plt.subplots(facecolor=(235/255, 235/255, 235/255))
        
        # plot dashed lines from x and y axis to the points
        self.x_values.append(relative_x)
        self.y_values.append(relative_y) 
        for x, y in zip(self.x_values, self.y_values):
            ax.plot([x, x], [0, y], 'k--', lw=1) # dashed line from x-axis to point
            ax.plot([0, x], [y, y], 'k--', lw=1) # dashed line from y-axis to point

        # add text labels to each point with its ID number and coordinates above it
        for x, y, id_num in zip(self.x_values, self.y_values, range(1, len(self.x_values) + 1)):
            ax.text(x, y+(0.1), f"({x}, {y})\nID: {id_num}", ha='center', va='bottom', weight='bold', fontsize=14, fontfamily='Calibri')

        # plot the points
        ax.plot(self.x_values, self.y_values, 'bo')

        # Set the font weight and font family of the tick labels
        ax.tick_params(axis='x', which='both', labelsize=12)
        ax.tick_params(axis='y', which='both', labelsize=12)

        # set x and y axis labels and graph title with Calibri font family
        ax.set_xlabel('X(cm)', weight='bold', fontfamily='Calibri', fontsize=18)
        ax.set_ylabel('Y(cm)', weight='bold', fontfamily='Calibri', fontsize=18)
        ax.set_title('RUNWAY\n', weight='bold', fontfamily='Calibri', fontsize=18)

        # set the x and y axis limits to touch the dashed lines
        ax.set_xlim([ 0, self.x_value_from_user*100])
        ax.set_ylim([ 0, self.y_value_from_user*100])

        self.widgets.append(FigureCanvas(fig))

        if(len(self.widgets) == 1):
            self.verticalLayout_2_d_mapping.addWidget(self.widgets[0])
        else:
            self.verticalLayout_2_d_mapping.replaceWidget(self.widgets[-2],self.widgets[-1])
    
    def update_progress_bar(self, percentage_value): #**************
        self.progressBar_start.setValue(percentage_value)

    def send_inputs_to_ui_arduino_com(self): #**************
        if(self.radioButton_fast.isChecked()):
            if(ui_arduino_com.send_inputs_to_arduino(self.lineEdit_x_input.text(),self.lineEdit_y_input.text(),"Fast")):
                return 1
            else:
                return 0
        elif(self.radioButton_normal.isChecked()):
            if(ui_arduino_com.send_inputs_to_arduino(self.lineEdit_x_input.text(),self.lineEdit_y_input.text(),"Normal")):
                return 1
            else:
                return 0
        elif(self.radioButton_detailed.isChecked()):
            if(ui_arduino_com.send_inputs_to_arduino(self.lineEdit_x_input.text(),self.lineEdit_y_input.text(),"Detailed")):
                return 1
            else:
                return 0

    def check_inputs(self): #**************
        if(self.lineEdit_x_input.text()):
            if(self.lineEdit_x_input.text().isdigit()):    
                if(self.lineEdit_y_input.text()):
                    if(self.lineEdit_y_input.text().isdigit()): 
                        if(self.radioButton_fast.isChecked() | self.radioButton_normal.isChecked() | self.radioButton_detailed.isChecked()):
                            return 1
                        else:
                            self.label_area_and_scan_mode_output.setText("Please select a scan mode!")
                            self.label_area_and_scan_mode_output.setStyleSheet("background-color: rgb(255, 75, 75);")
                            QtWidgets.QApplication.processEvents() #labelları tüm aksiyonun bitmesini beklemeden göstermek için
                            return 0
                    else:
                        self.label_area_and_scan_mode_output.setText("Please enter an integer y value!")
                        self.label_area_and_scan_mode_output.setStyleSheet("background-color: rgb(255, 75, 75);")
                        QtWidgets.QApplication.processEvents()
                        return 0
                else:
                    self.label_area_and_scan_mode_output.setText("Please enter y value!")
                    self.label_area_and_scan_mode_output.setStyleSheet("background-color: rgb(255, 75, 75);")
                    QtWidgets.QApplication.processEvents()
                    return 0
            else:
                self.label_area_and_scan_mode_output.setText("Please enter an integer x value!")
                self.label_area_and_scan_mode_output.setStyleSheet("background-color: rgb(255, 75, 75);")
                QtWidgets.QApplication.processEvents()
                return 0
        else:
            self.label_area_and_scan_mode_output.setText("Please enter x value!")
            self.label_area_and_scan_mode_output.setStyleSheet("background-color: rgb(255, 75, 75);")
            QtWidgets.QApplication.processEvents()
            return 0

    def check_com_to_ui_arduino_com(self):
        if(ui_arduino_com.check_communication_with_arduino()):
            self.label_connect_to_rover_output.setText("Connection Successful!")
            self.label_connect_to_rover_output.setStyleSheet("background-color: lightgreen")
            QtWidgets.QApplication.processEvents()
        else:
            self.label_connect_to_rover_output.setText("Connection Failed! Please try again!")
            self.label_connect_to_rover_output.setStyleSheet("background-color: rgb(255, 75, 75);")
            QtWidgets.QApplication.processEvents()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1715, 906)
        MainWindow.setWindowIcon(QtGui.QIcon("ROVER.jpg")) #**************
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_gazi_logo = QtWidgets.QLabel(self.centralwidget)
        self.label_gazi_logo.setGeometry(QtCore.QRect(165, 20, 150, 150))
        self.label_gazi_logo.setText("")
        self.label_gazi_logo.setPixmap(QtGui.QPixmap(":/new/Gazi_Üniversitesi_logo.png"))
        self.label_gazi_logo.setScaledContents(True)
        self.label_gazi_logo.setObjectName("label_gazi_logo")
        self.label_tusas_logo = QtWidgets.QLabel(self.centralwidget)
        self.label_tusas_logo.setGeometry(QtCore.QRect(1365, 45, 250, 100))
        self.label_tusas_logo.setText("")
        self.label_tusas_logo.setPixmap(QtGui.QPixmap(":/tai/logo-3.png"))
        self.label_tusas_logo.setScaledContents(True)
        self.label_tusas_logo.setObjectName("label_tusas_logo")
        self.label_gazi_tek_ui = QtWidgets.QLabel(self.centralwidget)
        self.label_gazi_tek_ui.setGeometry(QtCore.QRect(610, 20, 500, 100))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(72)
        font.setBold(True)
        font.setWeight(75)
        self.label_gazi_tek_ui.setFont(font)
        self.label_gazi_tek_ui.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_gazi_tek_ui.setObjectName("label_gazi_tek_ui")
        self.frame_coordinates = QtWidgets.QFrame(self.centralwidget)
        self.frame_coordinates.setGeometry(QtCore.QRect(1280, 190, 400, 670))
        self.frame_coordinates.setStyleSheet("background-color: rgb(185, 185, 185);")
        self.frame_coordinates.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_coordinates.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_coordinates.setObjectName("frame_coordinates")
        self.label_coordinates = QtWidgets.QLabel(self.frame_coordinates)
        self.label_coordinates.setGeometry(QtCore.QRect(10, 20, 380, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(22)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_coordinates.setFont(font)
        self.label_coordinates.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_coordinates.setStyleSheet("")
        self.label_coordinates.setAlignment(QtCore.Qt.AlignCenter)
        self.label_coordinates.setObjectName("label_coordinates")
        self.line_coordinates = QtWidgets.QFrame(self.frame_coordinates)
        self.line_coordinates.setGeometry(QtCore.QRect(10, 50, 380, 20))
        self.line_coordinates.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_coordinates.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_coordinates.setObjectName("line_coordinates")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.frame_coordinates)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 70, 381, 591))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_coordinates = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_coordinates.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_coordinates.setObjectName("verticalLayout_coordinates")
        self.textEdit_coordinates = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        self.textEdit_coordinates.setFont(font)
        self.textEdit_coordinates.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.textEdit_coordinates.setReadOnly(True)
        self.textEdit_coordinates.setObjectName("textEdit_coordinates")
        self.verticalLayout_coordinates.addWidget(self.textEdit_coordinates)
        self.label_bakcground = QtWidgets.QLabel(self.centralwidget)
        self.label_bakcground.setGeometry(QtCore.QRect(0, 0, 1720, 900))
        self.label_bakcground.setStyleSheet("")
        self.label_bakcground.setText("")
        self.label_bakcground.setPixmap(QtGui.QPixmap(":/newPrefix/RGB_deneme.png"))
        self.label_bakcground.setScaledContents(True)
        self.label_bakcground.setObjectName("label_bakcground")
        self.frame_area_and_scan_mode = QtWidgets.QFrame(self.centralwidget)
        self.frame_area_and_scan_mode.setGeometry(QtCore.QRect(40, 340, 400, 310))
        self.frame_area_and_scan_mode.setStyleSheet("background-color: rgb(185, 185, 185);")
        self.frame_area_and_scan_mode.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_area_and_scan_mode.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_area_and_scan_mode.setObjectName("frame_area_and_scan_mode")
        self.lineEdit_x = QtWidgets.QLineEdit(self.frame_area_and_scan_mode)
        self.lineEdit_x.setGeometry(QtCore.QRect(10, 70, 60, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_x.setFont(font)
        self.lineEdit_x.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.lineEdit_x.setReadOnly(True)
        self.lineEdit_x.setPlaceholderText("")
        self.lineEdit_x.setObjectName("lineEdit_x")
        self.lineEdit_y = QtWidgets.QLineEdit(self.frame_area_and_scan_mode)
        self.lineEdit_y.setGeometry(QtCore.QRect(10, 130, 60, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_y.setFont(font)
        self.lineEdit_y.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.lineEdit_y.setReadOnly(True)
        self.lineEdit_y.setObjectName("lineEdit_y")
        self.lineEdit_x_input = QtWidgets.QLineEdit(self.frame_area_and_scan_mode)
        self.lineEdit_x_input.setGeometry(QtCore.QRect(80, 70, 110, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_x_input.setFont(font)
        self.lineEdit_x_input.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.lineEdit_x_input.setText("")
        self.lineEdit_x_input.setReadOnly(False)
        self.lineEdit_x_input.setPlaceholderText("")
        self.lineEdit_x_input.setObjectName("lineEdit_x_input")
        self.lineEdit_y_input = QtWidgets.QLineEdit(self.frame_area_and_scan_mode)
        self.lineEdit_y_input.setGeometry(QtCore.QRect(80, 130, 110, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_y_input.setFont(font)
        self.lineEdit_y_input.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.lineEdit_y_input.setText("")
        self.lineEdit_y_input.setReadOnly(False)
        self.lineEdit_y_input.setPlaceholderText("")
        self.lineEdit_y_input.setObjectName("lineEdit_y_input")
        self.label_area = QtWidgets.QLabel(self.frame_area_and_scan_mode)
        self.label_area.setGeometry(QtCore.QRect(10, 20, 180, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(22)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_area.setFont(font)
        self.label_area.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_area.setStyleSheet("")
        self.label_area.setAlignment(QtCore.Qt.AlignCenter)
        self.label_area.setObjectName("label_area")
        self.label_area_and_scan_mode_output = QtWidgets.QLabel(self.frame_area_and_scan_mode)
        self.label_area_and_scan_mode_output.setGeometry(QtCore.QRect(10, 250, 380, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.label_area_and_scan_mode_output.setFont(font)
        self.label_area_and_scan_mode_output.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_area_and_scan_mode_output.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.label_area_and_scan_mode_output.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_area_and_scan_mode_output.setObjectName("label_area_and_scan_mode_output")
        self.line_area = QtWidgets.QFrame(self.frame_area_and_scan_mode)
        self.line_area.setGeometry(QtCore.QRect(10, 50, 180, 20))
        self.line_area.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_area.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_area.setObjectName("line_area")
        self.radioButton_detailed = QtWidgets.QRadioButton(self.frame_area_and_scan_mode)
        self.radioButton_detailed.setGeometry(QtCore.QRect(210, 190, 180, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.radioButton_detailed.setFont(font)
        self.radioButton_detailed.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.radioButton_detailed.setObjectName("radioButton_detailed")
        self.line_scan_mode = QtWidgets.QFrame(self.frame_area_and_scan_mode)
        self.line_scan_mode.setGeometry(QtCore.QRect(210, 50, 180, 20))
        self.line_scan_mode.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_scan_mode.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_scan_mode.setObjectName("line_scan_mode")
        self.radioButton_fast = QtWidgets.QRadioButton(self.frame_area_and_scan_mode)
        self.radioButton_fast.setGeometry(QtCore.QRect(210, 70, 180, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.radioButton_fast.setFont(font)
        self.radioButton_fast.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.radioButton_fast.setObjectName("radioButton_fast")
        self.label_scan_mode = QtWidgets.QLabel(self.frame_area_and_scan_mode)
        self.label_scan_mode.setGeometry(QtCore.QRect(210, 20, 180, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(22)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_scan_mode.setFont(font)
        self.label_scan_mode.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_scan_mode.setStyleSheet("")
        self.label_scan_mode.setAlignment(QtCore.Qt.AlignCenter)
        self.label_scan_mode.setObjectName("label_scan_mode")
        self.radioButton_normal = QtWidgets.QRadioButton(self.frame_area_and_scan_mode)
        self.radioButton_normal.setGeometry(QtCore.QRect(210, 130, 180, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.radioButton_normal.setFont(font)
        self.radioButton_normal.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.radioButton_normal.setObjectName("radioButton_normal")
        self.line_area_and_scan_mode = QtWidgets.QFrame(self.frame_area_and_scan_mode)
        self.line_area_and_scan_mode.setGeometry(QtCore.QRect(190, 10, 20, 230))
        self.line_area_and_scan_mode.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_area_and_scan_mode.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_area_and_scan_mode.setObjectName("line_area_and_scan_mode")
        self.radioButton_detailed.raise_()
        self.radioButton_normal.raise_()
        self.radioButton_fast.raise_()
        self.line_scan_mode.raise_()
        self.lineEdit_x.raise_()
        self.lineEdit_y.raise_()
        self.lineEdit_x_input.raise_()
        self.lineEdit_y_input.raise_()
        self.label_area.raise_()
        self.label_area_and_scan_mode_output.raise_()
        self.line_area.raise_()
        self.label_scan_mode.raise_()
        self.line_area_and_scan_mode.raise_()
        self.frame_start = QtWidgets.QFrame(self.centralwidget)
        self.frame_start.setGeometry(QtCore.QRect(40, 670, 400, 190))
        self.frame_start.setStyleSheet("background-color: rgb(185, 185, 185);")
        self.frame_start.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_start.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_start.setObjectName("frame_start")
        self.pushButton_start = QtWidgets.QPushButton(self.frame_start)
        self.pushButton_start.setGeometry(QtCore.QRect(10, 10, 380, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.pushButton_start.setFont(font)
        self.pushButton_start.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.pushButton_start.setObjectName("pushButton_start")
        self.pushButton_start.clicked.connect(self.start_execute_methods) #**************
        self.label_start_output = QtWidgets.QLabel(self.frame_start)
        self.label_start_output.setGeometry(QtCore.QRect(10, 70, 380, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.label_start_output.setFont(font)
        self.label_start_output.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_start_output.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.label_start_output.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_start_output.setObjectName("label_start_output")
        self.progressBar_start = QtWidgets.QProgressBar(self.frame_start)
        self.progressBar_start.setGeometry(QtCore.QRect(10, 130, 380, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.progressBar_start.setFont(font)
        self.progressBar_start.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.progressBar_start.setProperty("value", 0) #**************
        self.progressBar_start.setObjectName("progressBar_start")
        self.frame_connect_to_rover = QtWidgets.QFrame(self.centralwidget)
        self.frame_connect_to_rover.setGeometry(QtCore.QRect(40, 190, 400, 130))
        self.frame_connect_to_rover.setStyleSheet("background-color: rgb(185, 185, 185);")
        self.frame_connect_to_rover.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_connect_to_rover.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_connect_to_rover.setObjectName("frame_connect_to_rover")
        self.pushButton_connect_to_rover = QtWidgets.QPushButton(self.frame_connect_to_rover)
        self.pushButton_connect_to_rover.setGeometry(QtCore.QRect(10, 10, 380, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_connect_to_rover.setFont(font)
        self.pushButton_connect_to_rover.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.pushButton_connect_to_rover.setObjectName("pushButton_connect_to_rover")
        self.pushButton_connect_to_rover.clicked.connect(self.check_com_to_ui_arduino_com) #**************
        self.label_connect_to_rover_output = QtWidgets.QLabel(self.frame_connect_to_rover)
        self.label_connect_to_rover_output.setGeometry(QtCore.QRect(10, 70, 380, 50))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.label_connect_to_rover_output.setFont(font)
        self.label_connect_to_rover_output.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_connect_to_rover_output.setStyleSheet("background-color: rgb(235, 235, 235);")
        self.label_connect_to_rover_output.setObjectName("label_connect_to_rover_output")
        self.frame_2_d_mapping = QtWidgets.QFrame(self.centralwidget)
        self.frame_2_d_mapping.setGeometry(QtCore.QRect(460, 190, 800, 670))
        self.frame_2_d_mapping.setStyleSheet("background-color: rgb(185, 185, 185);")
        self.frame_2_d_mapping.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2_d_mapping.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2_d_mapping.setObjectName("frame_2_d_mapping")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.frame_2_d_mapping)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 70, 781, 591))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2_d_mapping = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2_d_mapping.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2_d_mapping.setObjectName("verticalLayout_2_d_mapping")
        self.line_2_d_mapping = QtWidgets.QFrame(self.frame_2_d_mapping)
        self.line_2_d_mapping.setGeometry(QtCore.QRect(10, 50, 780, 20))
        self.line_2_d_mapping.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2_d_mapping.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2_d_mapping.setObjectName("line_2_d_mapping")
        self.label_2_d_mapping = QtWidgets.QLabel(self.frame_2_d_mapping)
        self.label_2_d_mapping.setGeometry(QtCore.QRect(10, 20, 780, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(22)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_2_d_mapping.setFont(font)
        self.label_2_d_mapping.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_2_d_mapping.setStyleSheet("")
        self.label_2_d_mapping.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2_d_mapping.setObjectName("label_2_d_mapping")
        self.label_bakcground.raise_()
        self.label_gazi_logo.raise_()
        self.label_tusas_logo.raise_()
        self.label_gazi_tek_ui.raise_()
        self.frame_coordinates.raise_()
        self.frame_area_and_scan_mode.raise_()
        self.frame_start.raise_()
        self.frame_connect_to_rover.raise_()
        self.frame_2_d_mapping.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1715, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Foreign Object Detection System")) #**************
        self.label_gazi_tek_ui.setText(_translate("MainWindow", "GAZİ-TEK UI"))
        self.label_coordinates.setText(_translate("MainWindow", "COORDINATES"))
        self.lineEdit_x.setText(_translate("MainWindow", "X(m):"))
        self.lineEdit_y.setText(_translate("MainWindow", "Y(m):"))
        self.label_area.setText(_translate("MainWindow", "AREA"))
        self.label_area_and_scan_mode_output.setText(_translate("MainWindow", "Please enter the inputs!"))
        self.radioButton_detailed.setText(_translate("MainWindow", "Detailed"))
        self.radioButton_fast.setText(_translate("MainWindow", "Fast"))
        self.label_scan_mode.setText(_translate("MainWindow", "SCAN MODE"))
        self.radioButton_normal.setText(_translate("MainWindow", "Normal"))
        self.pushButton_start.setText(_translate("MainWindow", "Start"))
        self.label_start_output.setText(_translate("MainWindow", "Please start scanning!"))
        self.pushButton_connect_to_rover.setText(_translate("MainWindow", "Connect to Rover"))
        self.label_connect_to_rover_output.setText(_translate("MainWindow", "Please connect to rover!"))
        self.label_2_d_mapping.setText(_translate("MainWindow", "2-D MAPPING"))

if __name__ == "__main__":                                              #**************
    import sys                                                          #**************
    app = QtWidgets.QApplication(sys.argv)                              #**************
    MainWindow = QtWidgets.QMainWindow()                                #**************
    ui = Ui_MainWindow()                                                #**************
    ui.setupUi(MainWindow)                                              #**************
    MainWindow.show()                                                   #**************
    sys.exit(app.exec_())                                               #**************