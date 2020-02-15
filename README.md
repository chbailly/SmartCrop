# SmartCrop

SmartCrop is a simple tool to generate better crops to minimise distorsion caused by wide angle lenses

Beware:
* do not use the loop tool
* if you change FL, press enter otherwise the change is ignored

# Requirements

python3
matplotlib, numpy and PIL
Many distributions like anaconda include all.

# How to launch it

python smart_crop.py <image_file>

# How to use it

This is based on a basic workflow, you see the status with label of the button used to crop.

The workflow is:
## create a crop rectangle (optional)
## Click on SmartCrop and wait a bit
## create a crop rectangle (optional)
## Click on BasicCrop
## click on Save =>the image is saved in your directory with "_perspective" extension

Remarks:
* The back button will go back in the workflow described above
* selecting a crop is optional, which means all the image is selected when you crop.

IMPORTANT:
* Use an original image untouched by any other cropping/perspective correction
* THE FL used is the 35mm equivalent focal length
