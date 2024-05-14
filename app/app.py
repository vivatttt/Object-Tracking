import cv2
import os
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog, QWidget, QLabel, QVBoxLayout, QSlider, QPushButton, QHBoxLayout, QStackedWidget, QComboBox, QCheckBox
from utils.filter_countours import filter_contours

path_to_file = None

class MainPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()

        self.stacked_widget = stacked_widget
        self.initUI()
    
    def initUI(self):
        self.win_h = 800
        self.win_w = 1200
    
        self.setFixedSize(self.win_w, self.win_h)
        self.setWindowTitle("Main window") 
        self.layout = QVBoxLayout(self)
      
        self.label = QLabel('Object Tracker 3000', self) 
        self.label.setStyleSheet("font-size: 42pt; font-weight: bold;")     
        self.button_mode_1 = QPushButton('Mode 1')
        self.button_mode_2 = QPushButton('Mode 2')
        self.button_settings = QPushButton('Settings')
        self.button_file = QPushButton('Choose file', self)
        self.button_file.clicked.connect(self.showFileDialog)

        self.button_mode_1.setFixedSize(100, 40)
        self.button_mode_2.setFixedSize(100, 40)
        self.button_settings.setFixedSize(100, 40)
        self.button_file.setFixedSize(100, 40)

        self.updateLayout()

    def updateLayout(self):

        for i in reversed(range(self.layout.count())): 
            widget = self.layout.itemAt(i).widget()
            if widget is not None: 
                widget.setParent(None)
        
        self.layout.addStretch(1)
        global path_to_file
        if path_to_file:
            self.layout.addWidget(self.label, 0, Qt.AlignHCenter)
            self.layout.addSpacing(100)
            self.layout.addWidget(self.button_mode_1, 0, Qt.AlignHCenter)
            self.layout.addSpacing(20)
            self.layout.addWidget(self.button_mode_2, 0, Qt.AlignHCenter)
            self.layout.addSpacing(20)
            self.layout.addWidget(self.button_settings, 0, Qt.AlignHCenter)
            self.layout.addSpacing(20)
            self.layout.addWidget(self.button_file, 0, Qt.AlignHCenter)
        else:
            self.layout.addWidget(self.label, 0, Qt.AlignHCenter)
            self.layout.addSpacing(60)
            self.layout.addWidget(self.button_file, 0, Qt.AlignHCenter)
        self.layout.addStretch(1)
        self.connectButtons() 
    
    def connectButtons(self):
        self.button_mode_1.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(mode1_page))
        self.button_mode_2.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(mode2_page))
        self.button_settings.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(settings_page))
    
    def showFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        global path_to_file
        
        # если путь до файла не был задан (а раз зашли в эту функцию, то будет задан), то меняем виджеты на главной странице 
        flag = 1 if not path_to_file else 0 
        path_to_file, _ = QFileDialog.getOpenFileName(self, 
                                                      "Open File", 
                                                      "", 
                                                      "MP4 Files (*.mp4);;All Files (*)", 
                                                      options=options)
    
        if path_to_file:
            self.updateAllPages()
            if flag:
                self.updateLayout()
                self.connectButtons()

    def updateAllPages(self):   
        global mode1_page, mode2_page, settings_page

        mode1_page.update_file()
        mode2_page.update_file()
        settings_page.update_file()

class Mode1Page(QWidget):
    def __init__(self, stacked_widget, input_widget):
        super().__init__()

        self.percent = 90
        self.win_h = 800
        self.win_w = 1200

        self.setFixedSize(1200, 800)
        self.setWindowTitle("Settings") 
        
        self.timer = QTimer(self)
        
        
        self.input_widget = input_widget # получаем класс Settings, из которого достаем измененные параметры для настройки
        self.init_ui(stacked_widget)

    def update_file(self):
        global path_to_file
        
        self.video = path_to_file
        self.video_capture = cv2.VideoCapture(self.video)  
        self.object_detector = cv2.createBackgroundSubtractorMOG2()
        self.timer.timeout.connect(self.update_frame)
        self.update_frame() # показываем первый кадр

    def init_ui(self, stacked_widget):

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)

        self.play_button = QPushButton('Старт', self)
        self.play_button.setFixedSize(100, 40)
        self.play_button.clicked.connect(self.play_video)

        self.pause_button = QPushButton('Стоп', self)
        self.pause_button.setFixedSize(100, 40)
        self.pause_button.clicked.connect(self.pause_video)

        self.home_button = QPushButton('Main Page', clicked=lambda: (stacked_widget.setCurrentWidget(main_page), self.pause_video()))
        self.home_button.setFixedSize(100, 40)

        layout_control = QVBoxLayout()  

        layout_control.addStretch(1)
        layout_control.addWidget(self.play_button, 0, Qt.AlignHCenter)
        layout_control.addWidget(self.pause_button, 0, Qt.AlignHCenter)
        layout_control.addStretch(1)
        layout_control.addWidget(self.home_button, 0, Qt.AlignHCenter)
        layout_control.addSpacing(50)
      
        layout = QHBoxLayout(self)
        layout.addWidget(self.video_label)
        

        layout.addLayout(layout_control)
        
        self.roi = [0, 0, int(self.win_w * self.percent // 100), int(self.win_h * self.percent // 100)]
        

    def update_parametres(self):
        self.received_percent, self.slider_min_area, self.slider_eps, self.checkbox_noise, self.checkbox_shadows, self.roi = self.input_widget.get_data()
        self.roi = list(map(lambda el: int(el * self.percent // self.received_percent), self.roi))

    def play_video(self):
        self.timer.start(33)  

    def pause_video(self):
        self.timer.stop()

    def update_frame(self):

        ret, frame = self.video_capture.read()

        if ret:
            frame = self.r_resize(frame)

            self.update_parametres() # получаем значения из Settings и обновляем их

            self.cur_shot = frame
            
            cropped = frame[int(self.roi[1]) : int(self.roi[1]) + int(self.roi[3]) , int(self.roi[0]) : int(self.roi[0]) + int(self.roi[2])]

            mask = self.object_detector.apply(cropped)

            if self.checkbox_shadows:
                _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)

            if self.checkbox_noise:
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            eps = int(self.slider_eps)
                               
            try:
                rects = filter_contours(contours, self.slider_min_area, eps)
            except Exception as e:
                rects = []
                for con in contours:
                    con = cv2.approxPolyDP(con, eps, closed=True)
                    area = cv2.contourArea(con)
                    if area > self.slider_min_area:
                        rects.append(cv2.boundingRect(con))

            for rect in rects:
                x, y, w, h = rect
                cv2.rectangle(cropped, (x, y), (x + w, y + h), (255, 0, 255), 2)
            
            # преобразование картинки в формат для PyQt5
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.video_label.setPixmap(pixmap)

        else:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0) # если видео закончилось, воспроизводим его заново
       
    def r_resize(self, shot):

        height = int(self.win_h / 100 * self.percent)
        width = int(self.win_w / 100 * self.percent)
        return cv2.resize(shot, (width, height))
    

class Mode2Page(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()

        self.percent = 90
        self.win_h = 800
        self.win_w = 1200

        self.setFixedSize(1200, 800)
        self.setWindowTitle("Settings") 

        
        self.timer = QTimer(self)
            
        self.init_ui(stacked_widget)
        
    def update_file(self):
        global path_to_file

        self.video = path_to_file

        self.video_capture = cv2.VideoCapture(self.video)
        self.object_detector = cv2.createBackgroundSubtractorMOG2()  
        self.timer.timeout.connect(self.update_frame)

    def init_ui(self, stacked_widget):

        self.play_button = QPushButton('Старт', self)
        self.play_button.setFixedSize(100, 40)
        self.play_button.clicked.connect(self.play_video)

        self.pause_button = QPushButton('Стоп', self)
        self.pause_button.setFixedSize(100, 40)
        self.pause_button.clicked.connect(self.pause_video)

        self.roi_button = QPushButton('Выбрать ROI', self)
        self.roi_button.setFixedSize(100, 40)
        self.roi_button.clicked.connect(self.object_selection)

        self.home_button = QPushButton('Main Page', clicked=lambda: (stacked_widget.setCurrentWidget(main_page), self.pause_video(), cv2.destroyAllWindows()))
        self.home_button.setFixedSize(100, 40)

        layout_control = QVBoxLayout()  

        layout_control.addStretch(1)
        layout_control.addWidget(self.play_button, 0, Qt.AlignHCenter)
        layout_control.addWidget(self.pause_button, 0, Qt.AlignHCenter)
        layout_control.addSpacing(50)
        layout_control.addWidget(self.roi_button, 0, Qt.AlignHCenter)
        layout_control.addStretch(1)
        layout_control.addWidget(self.home_button, 0, Qt.AlignHCenter)
        layout_control.addSpacing(50)
      
        layout = QHBoxLayout(self)
    
        layout.addLayout(layout_control)

        self.trackers = [] # массив трекеров

    def play_video(self):
        self.timer.start(33)  

    def pause_video(self):
        self.timer.stop()

    def update_frame(self):

        ret, frame = self.video_capture.read()

        if ret:
            frame = self.r_resize(frame)
            self.cur_shot = frame

            i = 0
            while i != len(self.trackers):
                _, box = self.trackers[i].update(frame)
                if sum(box) == 0:
                    del self.trackers[i]
                else:
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2, 1)
                    i += 1

            cv2.imshow('tracking', frame)

        else:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0) # если видео закончилось, воспроизводим его заново

    def object_selection(self):
        self.pause_video()

        roi = cv2.selectROI('tracking', self.cur_shot)
        tracker = cv2.legacy.TrackerKCF_create()
        tracker.init(self.cur_shot, roi)
        
        self.trackers.append(tracker)

        self.play_video()

    def r_resize(self, shot):

        height = int(self.win_h / 100 * self.percent)
        width = int(self.win_w / 100 * self.percent)
        return cv2.resize(shot, (width, height))

class SettingsPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()

        self.percent = 60
        self.win_h = 800
        self.win_w = 1200

        self.setFixedSize(1200, 800)
        self.setWindowTitle("Settings") 
  
        self.timer = QTimer(self)
        
        
        self.init_ui(stacked_widget)

    def update_file(self):
        global path_to_file

        self.video = path_to_file

        self.video_capture = cv2.VideoCapture(self.video)
        self.timer.timeout.connect(self.update_frame)
        self.object_detector = cv2.createBackgroundSubtractorMOG2()

        self.update_frame() # показываем первый кадр
    def init_ui(self, stacked_widget):

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)

        
        video_label = QLabel('Выберите режим отображения видео', self) 
        slider_label = QLabel('Выберите минимальную площадь контура от 500 до 5000', self) 
        eps_label = QLabel('Выберите коэффициент аппроксимации контура от 0 до 20', self) 

        self.play_button = QPushButton('Старт', self)
        self.play_button.setFixedSize(100, 40)
        self.play_button.clicked.connect(self.play_video)

        self.pause_button = QPushButton('Стоп', self)
        self.pause_button.setFixedSize(100, 40)
        self.pause_button.clicked.connect(self.pause_video)

        self.roi_button = QPushButton('Выбрать ROI', self)
        self.roi_button.setFixedSize(100, 40)
        self.roi_button.clicked.connect(self.select_roi)

        self.slider_min_area = QSlider(Qt.Horizontal)

        self.slider_min_area.setMinimum(500)
        self.slider_min_area.setMaximum(5000)

        self.slider_eps = QSlider(Qt.Horizontal)

        self.slider_eps.setMinimum(0)
        self.slider_eps.setMaximum(20)
   

        self.comboBox = QComboBox(self)
        self.comboBox.addItems(['Стандартная', 'Обработанная', 'Контуры', 'Отслеживание'])

        self.checkbox_shadows = QCheckBox('Убрать тени', self)
        self.checkbox_noise = QCheckBox('Убрать шум ', self)

        self.home_button = QPushButton('Main Page', clicked=lambda: (stacked_widget.setCurrentWidget(main_page), self.pause_video()))
        self.home_button.setFixedSize(100, 40)

        layout_control = QVBoxLayout()
        layout_control.addStretch(1)
        
        layout_control.addWidget(video_label, 0, Qt.AlignHCenter)
        layout_control.addSpacing(10)
        layout_control.addWidget(self.comboBox, 0, Qt.AlignHCenter)
        layout_control.addSpacing(60)

        layout_control.addWidget(slider_label, 0, Qt.AlignHCenter)
        layout_control.addSpacing(10)
        layout_control.addWidget(self.slider_min_area)
        layout_control.addSpacing(30)

        layout_control.addWidget(eps_label, 0, Qt.AlignHCenter)
        layout_control.addSpacing(10)
        layout_control.addWidget(self.slider_eps)
        layout_control.addSpacing(30)
    
        layout_control.addWidget(self.checkbox_shadows, 0, Qt.AlignHCenter)
        layout_control.addWidget(self.checkbox_noise, 0, Qt.AlignHCenter)

        layout_control.addWidget(self.play_button, 0, Qt.AlignHCenter)
        layout_control.addWidget(self.pause_button, 0, Qt.AlignHCenter)
        layout_control.addSpacing(30)

        layout_control.addWidget(self.roi_button, 0, Qt.AlignHCenter)
        
        layout_control.addStretch(1)
        layout_control.addWidget(self.home_button, 0, Qt.AlignHCenter)
        layout_control.addSpacing(50)
      
        layout = QHBoxLayout(self)
        layout.addWidget(self.video_label)
        

        layout.addLayout(layout_control)
        
        self.roi = [0, 0, int(self.win_w * self.percent // 100), int(self.win_h * self.percent // 100)]
        
        
    def play_video(self):
        self.timer.start(33)  

    def pause_video(self):
        self.timer.stop()
    
    def get_data(self):
        return [self.percent, self.slider_min_area.value(), self.slider_eps.value(), self.checkbox_noise.isChecked(), self.checkbox_shadows.isChecked(), self.roi]

    def update_frame(self):

        ret, frame = self.video_capture.read()
        

        if ret:
            
            frame = self.r_resize(frame)
            frame_copy = frame.copy()

            self.cur_shot = frame
            
            cropped = frame[int(self.roi[1]) : int(self.roi[1]) + int(self.roi[3]) , int(self.roi[0]) : int(self.roi[0]) + int(self.roi[2])]

            if self.comboBox.currentText() == "Обработанная":
                mask = self.object_detector.apply(frame)

                if self.checkbox_shadows.isChecked():
                    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)

                if self.checkbox_noise.isChecked():
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

                frame = mask

            elif self.comboBox.currentText() in ('Контуры', 'Отслеживание'):

                mask = self.object_detector.apply(cropped)

                if self.checkbox_shadows.isChecked():
                    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)

                if self.checkbox_noise.isChecked():
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                eps = int(self.slider_eps.value())
                
                if self.comboBox.currentText() == 'Контуры':
                    for con in contours:
                        con = cv2.approxPolyDP(con, eps, closed=True)
                        cv2.drawContours(cropped, [con], -1, (0, 255, 0), 1)
            
                else:
                
                    try:
                        rects = filter_contours(contours, self.slider_min_area.value(), eps)
                    except Exception as e:
                        rects = []
                        for con in contours:
                            con = cv2.approxPolyDP(con, eps, closed=True)
                            area = cv2.contourArea(con)
                            if area > self.slider_min_area.value():
                                rects.append(cv2.boundingRect(con))

                    for rect in rects:
                        x, y, w, h = rect
                        cv2.rectangle(cropped, (x, y), (x + w, y + h), (255, 0, 255), 2)
                    
                    
                

            # преобразование картинки в формат для PyQt5
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.video_label.setPixmap(pixmap)

        else:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0) # если видео закончилось, воспроизводим его заново

    def select_roi(self):
        self.pause_video()
        
        roi = cv2.selectROI("select the ROI", self.cur_shot)
        cv2.destroyWindow("select the ROI")  
        self.roi = list(roi)

        self.play_video()

        
    def r_resize(self, shot):

        height = int(self.win_h / 100 * self.percent)
        width = int(self.win_w / 100 * self.percent)

        return cv2.resize(shot, (width, height))
    
    


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.stacked_widget = QStackedWidget(self)

        # Создаем виджеты для каждой страницы
        global main_page, mode1_page, mode2_page, settings_page
        main_page = MainPage(self.stacked_widget)
        
        settings_page = SettingsPage(self.stacked_widget)
        mode1_page = Mode1Page(self.stacked_widget, settings_page)
        mode2_page = Mode2Page(self.stacked_widget)

        # Добавляем страницы в QStackedWidget
        self.stacked_widget.addWidget(main_page)
        self.stacked_widget.addWidget(mode1_page)
        self.stacked_widget.addWidget(mode2_page)
        self.stacked_widget.addWidget(settings_page)

        # Устанавливаем главную страницу в качестве текущей
        self.stacked_widget.setCurrentWidget(main_page)

        # Размещаем QStackedWidget в основном макете
        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)

