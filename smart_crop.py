

import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QRubberBand, QPushButton,\
    QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QComboBox, QAction, QMainWindow, QFileDialog
from qimage2ndarray import array2qimage
import matplotlib.image as mpimg
from crop import smart_crop
from os.path import dirname

class ImageArea(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.setMinimumSize(1, 1)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.startx = None # no selection so far
        self.resize(800, 600)
        self.show()

    def setImage(self, image):
        self.pixmap = image
        self.pixmap_scale = self.pixmap.scaled(self.width(),self.height(), Qt.KeepAspectRatio)
        self.setPixmap(self.pixmap_scale)

    def resizeEvent(self, event):
        self.pixmap_scale = self.pixmap.scaled(self.width(),self.height(), Qt.KeepAspectRatio)
        self.setPixmap(self.pixmap_scale)
        self.resize(self.width(), self.height())

    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            self.startx, self.starty = (pos.x(), pos.y())
            self.origin = QPoint(pos)
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
    
    def mouseMoveEvent(self, event):
    
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
    
    def mouseReleaseEvent(self, event):
        pos = event.pos()
        self.endx, self.endy = (pos.x(), pos.y())
        print (self.startx, self.starty)
        print (self.endx, self.endy)
        if event.button() == Qt.LeftButton:
            self.rubberBand.hide()
        

INITIAL, SMARTCROPPED, CROPPED = 0, 1, 2

class Window(QMainWindow): 
    def __init__(self):
        QMainWindow.__init__(self)
        self.label = ImageArea(self)
        self.status = INITIAL
        widget = QWidget();
        self.setCentralWidget(widget);

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
        vbox = QVBoxLayout()
        widget.setLayout(vbox)
        #hbox.addStretch(1)
        vbox.addWidget(self.label)
        #hbox = QHBoxLayout()
        vbox.addWidget(inputWidget)
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
        cb.currentIndexChanged.connect(lambda :self.selectionchange(cb))

        self.resize(800, 600)
        self.setWindowTitle('Buttons')
        self.load_image_file("D:\Dropbox\Quebec2017\DSCF1461.jpg") 
        self.cylindric = False 
        inputWidget.setFixedHeight(50)
        self.show()

    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/')
        self.load_image_file(fname[0])

    def saveDialog(self):
        fname = QFileDialog.getSaveFileName(self, 'Saves file', dirname(self.filename))
        mpimg.imsave(fname[0], self.img)



    def back(self):
        if self.status == SMARTCROPPED:
            self.cropButton.setText("SmartCrop")
            self.label.startx = None
            self.status = INITIAL
            self.set_image(self.img_orig)
        elif self.status in [SMARTCROPPED, CROPPED]:
            self.cropButton.setText("SmartCrop")
            self.label.startx = None
            self.status = SMARTCROPPED
            self.set_image(self.img_sc)

    def crop(self):
        if self.status == INITIAL:
            self.img_sc = self.smart_crop()
            self.status = SMARTCROPPED
            self.cropButton.setText("BasicCrop")
            self.label.startx = None
            self.set_image(self.img_sc)
        elif self.status in [SMARTCROPPED, CROPPED]:
            self.img_crop = self.smart_crop()
            self.status = CROPPED
            self.cropButton.setText("BasicCrop")
            self.label.startx = None
            self.set_image(self.img_crop)

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
        start_pos, end_pos = self.crop_area()

        return smart_crop(self.img, 
            start_pos,
            end_pos,
            self.fl, self.cylindric)




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
            self.fl = exif["FocalLengthIn35mmFilm"]
        except Exception:
            self.fl = 35
        self.edit_fl.setText(str(self.fl))
        img = mpimg.imread(imgfile)
        self.filename = imgfile
        self.img_orig = img
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
