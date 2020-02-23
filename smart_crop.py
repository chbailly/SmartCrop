

import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QLine
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QRubberBand, QPushButton,\
    QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QLayout, QHBoxLayout, QComboBox, QAction, QMainWindow, QFileDialog
from PyQt5.QtGui import QPainter, QPen
from qimage2ndarray import array2qimage
import matplotlib.image as mpimg
import numpy as np
from crop import smart_crop, basic_crop
from os.path import dirname

LINE_SELECT, RECT_SELECT = 0, 1

class ImageArea(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.mainw = parent
        self.setMinimumSize(1, 1)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.startx = None # no selection so far
        self.pixmapimg = None
        self.resize(800, 600)
        self.type_selection = RECT_SELECT
        self.line = QLine()
        self.show()

    def setImage(self, image):
        self.pixmapimg = image       
        self.pixmap_scale = self.pixmapimg.scaled(self.width(),self.height(), Qt.KeepAspectRatio)
        self.setPixmap(self.pixmap_scale)

    def resizeEvent(self, event):
        if self.pixmapimg:
            self.pixmap_scale = self.pixmapimg.scaled(self.width(),self.height(), Qt.KeepAspectRatio)
            self.setPixmap(self.pixmap_scale)

    def paintEvent(self,event):
        QLabel.paintEvent(self, event)
        if not self.line.isNull():
            painter = QPainter(self)
            pen = QPen(Qt.red, 3)
            painter.setPen(pen)
            painter.drawLine(self.line)
   

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()           
            self.origin = QPoint(pos)

        if self.type_selection == RECT_SELECT:
            self.startx = pos.x()
            self.starty = pos.y() - (self.height() - self.pixmap_scale.height())/2
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
    
    def mouseMoveEvent(self, event):
    
        if not self.origin.isNull():
            if self.type_selection == RECT_SELECT:
                self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
            else:
                self.line = QLine(self.origin, event.pos())
                self.update()
    
    def mouseReleaseEvent(self, event):
        pos = event.pos()

        if self.type_selection == RECT_SELECT:
            self.endx = pos.x()
            self.endy = pos.y() - (self.height() - self.pixmap_scale.height())/2

            if self.endx < self.startx:
                temp = self.startx
                self.startx = self.endx
                self.endx = temp
            
            if self.endy < self.starty:
                temp = self.starty
                self.starty = self.endy
                self.endy = temp

        else:
            angle = -np.arctan((pos.y() - self.origin.y()) / (pos.x() - self.origin.x()))
            self.mainw.edit_angle.setText(str(np.rad2deg(angle)))
        #if event.button() == Qt.LeftButton:
         #   self.rubberBand.hide()
        

INITIAL, SMARTCROPPED, ROTATED, CROPPED = 0, 1, 2, 3


class Window(QMainWindow): 
    def __init__(self):
        QMainWindow.__init__(self)

        self.label = ImageArea(self)
        self.status = INITIAL
        self.widget = QWidget();
        
        self.setCentralWidget(self.widget);

       
        openFile = QAction(QIcon('open.png'), 'Open', self)
        openFile.triggered.connect(self.showDialog)

        saveFile = QAction(QIcon('save.png'), 'Save', self)
        saveFile.triggered.connect(self.saveDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile) 
        fileMenu.addAction(saveFile)          
        inputWidget = QWidget();
        hbox = QHBoxLayout(inputWidget)

        self.cropButton = QPushButton("SmartCrop")
        self.cropButton.clicked.connect(self.crop)
        backButton =  QPushButton("Back")
        backButton.clicked.connect(self.back)
        self.vbox = QVBoxLayout()
        self.widget.setLayout(self.vbox)
        
        #hbox.addStretch(1)
        self.vbox.addWidget(self.label)
        #hbox = QHBoxLayout()
        self.vbox.addWidget(inputWidget)
        hbox.addWidget(self.cropButton)
        hbox.addWidget(backButton)
        fbox = QFormLayout()


        comboLayout= QHBoxLayout()
        cb = QComboBox()
        cb.addItem("Rectilinear")
        cb.addItem("Cylindric")
        comboLayout.addWidget(cb)
        hbox.addLayout(comboLayout)
        l1 = QLabel("Focal 35mm:")
        self.edit_fl  = QLineEdit()
        self.edit_fl.setMaximumWidth(self.edit_fl.sizeHint().width())
        fbox.addRow(l1, self.edit_fl)
        hbox.addLayout(fbox)
        fbox_angle = QFormLayout()
        langle = QLabel("Angle:")
        self.edit_angle  = QLineEdit()
        self.edit_angle.setMaximumWidth(self.edit_angle.sizeHint().width())
        fbox_angle.addRow(langle, self.edit_angle)
        hbox.addLayout(fbox_angle)     
        cb.currentIndexChanged.connect(lambda :self.selectionchange(cb))

        self.setWindowTitle('Buttons')
        # self.load_image_file("D:\Dropbox\Quebec2017\DSCF1461.jpg") 
        self.cylindric = False
        self.angle = 0
        hbox.setSizeConstraint(QLayout.SetFixedSize)
        inputWidget.setFixedHeight(50)
        self.resize(800, 600)
        self.show()

    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/')
        self.load_image_file(fname[0])

    def saveDialog(self):
        fname = QFileDialog.getSaveFileName(self, 'Saves file', dirname(self.filename))
        mpimg.imsave(fname[0], self.img)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.label.rubberBand.hide()
            if self.label.type_selection == RECT_SELECT:
                self.label.startx = None
            self.label.line = QLine()
            self.label.update()

        event.accept()

    def display_status(self):
        if self.status == INITIAL:
            self.cropButton.setText("SmartCrop")
            self.set_image(self.img_orig)
            self.edit_angle.setText("0")
            self.set_image(self.img_orig)
        if self.status == SMARTCROPPED:
            self.cropButton.setText("Rotate (or not)")
            self.edit_angle.setText("0")
            self.set_image(self.img_sc)
        elif self.status == ROTATED:
            self.cropButton.setText("BasicCrop")
            self.set_image(self.img_rotated)
        elif self.status == CROPPED:
            self.cropButton.setText("BasicCrop")
            self.set_image(self.img_crop)

        if self.status == SMARTCROPPED:
            self.label.type_selection = LINE_SELECT         
        else:
            self.label.type_selection = RECT_SELECT
        
        if self.status != SMARTCROPPED:
            self.label.startx = None
        self.label.line = QLine()
        self.label.update()

    def back(self):
        before = {
            INITIAL: INITIAL,
            SMARTCROPPED: INITIAL,
            ROTATED: SMARTCROPPED,
            CROPPED: ROTATED
        }
        self.status = before[self.status]
        self.display_status()

    def crop(self):
        
        self.cropButton.setText("Running...")
        app.processEvents()
        self.label.rubberBand.hide()
        if self.status == INITIAL:
            self.img_sc = self.smart_crop()
            self.status = SMARTCROPPED

        elif self.status == SMARTCROPPED:
            if self.edit_angle.text() != "0" and self.edit_angle.text().strip() != "":
                self.img_rotated = self.smart_crop()
            else:
                self.img_rotated = self.img_sc  
            self.status = ROTATED
        elif self.status in [ROTATED, CROPPED]:
            self.img_crop = self.basic_crop()
            self.status = CROPPED
        self.display_status()


    def selectionchange(self, cb):
        if cb.currentText() == "Rectilinear":
            self.cylindric = False
        else:
            self.cylindric = True

    def crop_area(self):
        ratio = self.img.shape[1]/self.label.pixmap_scale.width()
        if self.label.startx is None:
            x1 = 0
            y1 = 0
            x2 = self.img.shape[1]
            y2 = self.img.shape[0]
        else:
            x1 = ratio * self.label.startx
            y1 = ratio * self.label.starty
            x2 = ratio * self.label.endx
            y2 = ratio * self.label.endy
        return [x1, y1], [x2, y2]

    def basic_crop(self):
        start_pos, end_pos = self.crop_area()
        return basic_crop(self.img, start_pos, end_pos)

    def smart_crop(self):
        if self.status == INITIAL: # for rotation, keep the area for sc
            self.start_pos_sc, self.end_pos_sc = self.crop_area()

        angle = np.deg2rad(float(self.edit_angle.text()))
        fl = float(self.edit_fl.text())

        return smart_crop(self.img_orig, 
            self.start_pos_sc,
            self.end_pos_sc,
            fl, self.cylindric, angle)




    def load_image_file(self, imgfile):
        try:
            import PIL.Image
            img_pil = PIL.Image.open(imgfile)

            import PIL.ExifTags
            exif = {
                PIL.ExifTags.TAGS[k]: v
                for k, v in img_pil._getexif().items()
                if k in PIL.ExifTags.TAGS 
            }
            fl = exif["FocalLengthIn35mmFilm"]
        except Exception:
            fl = 35
        self.edit_fl.setText(str(fl))
        self.angle = 0
        self.edit_angle.setText("0")
        img = mpimg.imread(imgfile)
        self.filename = imgfile
        self.img_orig = img
        print ("Load image {}-{}".format(img.shape[1], img.shape[0]))
        self.set_image(img)
        self.status = INITIAL
        self.cropButton.setText("SmartCrop")

    
    def set_image(self, img):
        self.img = img
        self.label.setImage(QtGui.QPixmap.fromImage(array2qimage(self.img)))
        self.show()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    
    window = Window()

    window.show()
    sys.exit(app.exec_())
