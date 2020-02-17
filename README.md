# SmartCrop

There are 2 main ideas:
* SmartCrop is a simple tool to generate better crops to minimise distorsion caused by wide angle lenses
* It is also possible to generate cylindric perspective. Most softwares propose this perspective only for panos

This tool enables to rotate the camera toward the subject you want to crop.
This will generate a **more natural picture** just as if you had shot it directly directed toward your subject.
Besides, if the crop remains large (for the width), the cylindric perspective can improve even more the image.

You can see examples in the wiki

# Requirements

Many distributions like anaconda include these packages:
python3, PyQt5
matplotlib, numpy and PIL

# Installation

Copy the 2 files in the installation directory:
* crop.py
* smart_crop.py

+ need the qimage2ndarray package(https://pypi.org/project/qimage2ndarray)
download zip file: https://github.com/hmeine/qimage2ndarray/archive/release-1.8.2.zip

Simply copy the directory qimage2ndarray from the zip in the installation directory

At the end, you should have these files installed:
crop.py
smart_crop.py
qimage2ndarray/__init__.py
qimage2ndarray/dynqt.py.py
qimage2ndarray/qimageview_python.py
qimage2ndarray/qrgb_polyfill.py
qimage2ndarray/qt_driver.py



# How to launch it

python smart_crop.py

# How to use it

This is based on a basic workflow, you see the status with label of the button used to crop.

The workflow is:
1. Load an image from menu
2. select the perspective you want to generate (rectilinear or cylindric) = see suggestion below
3. create a crop rectangle (optional)
4. Click on SmartCrop and wait a bit, the button label switches to BasicCrop when finished
5. create a crop rectangle (optional)
6. Click on BasicCrop

Suggestions:
* Use rectlinear if the crop width is not too large. It will keep the line straightened
* For large width crops, you can try the cylindric projection

Remarks:
* The back button will go back in the workflow described above
* selecting a crop is optional, which means all the image is selected when you crop. Click on crop to go to the next step even if you do not really crop

IMPORTANT:
* Use an original image untouched by any other cropping/perspective correction
* THE focal used is the 35mm equivalent focal length read from the EXIF. If this is not present, set it explicitely in the text area. This tool will work also with different ratio than 3:2
