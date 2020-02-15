# SmartCrop

There are 2 main ideas:
* SmartCrop is a simple tool to generate better crops to minimise distorsion caused by wide angle lenses
* It is also possible to generate cylindric perspective. Most softwares propose this perspective only for panos

This tool enables to rotate the camera toward the subject you want to crop.
This will generate a more natural picture just as if you had shot it directly directed toward your subject.
Besides, if the crop remains large (for the width), the cylindric perspective can improve even more the image.

# Beware:
* do not use the loop tool
* if you change FL, press enter otherwise the change is ignored. The tool reads the Focal length in the EXIF so you may not need to change it

# Requirements

python3
matplotlib, numpy and PIL
Many distributions like anaconda include all.

# How to launch it

python smart_crop.py <image_file>

# How to use it

This is based on a basic workflow, you see the status with label of the button used to crop.

The workflow is:
1. create a crop rectangle (optional)
2. Click on SmartCrop and wait a bit
3. create a crop rectangle (optional)
4. Click on BasicCrop
5. click on Save =>the image is saved in your directory with "_perspective" extension

Remarks:
* The back button will go back in the workflow described above
* selecting a crop is optional, which means all the image is selected when you crop. Click on crop to go to the next step even if you do not really crop

IMPORTANT:
* Use an original image untouched by any other cropping/perspective correction
* THE FL used is the 35mm equivalent focal length. This tool will work also with different ratio than 3:2
