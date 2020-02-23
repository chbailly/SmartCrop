from matplotlib.widgets import RectangleSelector
from matplotlib.widgets import TextBox, CheckButtons, Button
from os.path import splitext
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import threading
import sys


img2 = None
first = True

x1,y1, x2, y2 = None, None, None ,  None


def rotatez(p, angle):
    matz = np.array([
        [np.cos(angle), np.sin(angle), 0],
        [-np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]])
    return p @ matz

def rotatey(p, angle):
    maty = np.array([
        [np.cos(angle), 0, -np.sin(angle)],
        [0, 1, 0],
        [np.sin(angle), 0, np.cos(angle)]])

    return p @ maty

def rotate_axe(axe, target_point, angles):
        only1 = False
        if not isinstance(angles,list) and not isinstance(angles,np.ndarray):
            angles = [angles]
            only1 = True
        ux = axe[0]
        uy = axe[1]
        uz = axe[2]
        res = target_point @ np.array([[
                [ ux * ux * (1 - c) + c, ux * uy * (1 -c) + uz * s, ux * uz * (1 -c) - uy * s],
                [ ux * uy * (1 - c) - uz * s, uy * uy * (1 - c) + c, uy * uz *(1-c) + ux * s],
                [  ux * uz * (1 - c) + uy * s, uy * uz * (1 -c) - ux *s, uz * uz * (1-c) + c]
            ] for c, s in [(np.cos(angle), np.sin(angle)) for angle in angles]])

        return (res[0] if only1 else res)

def norm(v):
    return np.sqrt(v[0]*v[0] + v[1] * v[1] + v[2] * v[2])


def change_text_button(label):
    axbox2.clear()
    button_box.__init__(axbox2, label)
    button_box.on_clicked(make_crop)



def do_back(event_back):
    global x1, x2, y1, y2

    if button_box.label.get_text() == "BasicCrop":
        img_ax.imshow(img)

    elif button_box.label.get_text() == "Save":
        img_ax.imshow(img2)

    previous = {
        "Save": 'BasicCrop',
        'BasicCrop': 'SmartCrop',
        'SmartCrop': 'SmartCrop'
    }

    change_text_button(previous[button_box.label.get_text()])
    x1, x2, y1, y2 = None, None, None, None
    plt.draw()

def basic_crop(img, start_pos, end_pos):
    x1, y1 = start_pos
    x2, y2 = end_pos

    return img[int(y1):int(y2),int(x1):int(x2),:]


def smart_crop(img, start_pos, end_pos, fl, cylindric, angle_rot):
    x1, y1 = start_pos
    x2, y2 = end_pos


    print("Start smart crop")


    sensor_nb_height = img.shape[0]
    sensor_nb_width = img.shape[1]

    mid_sensor = [sensor_nb_height/2, sensor_nb_width/2]

    # calculation to support different ration (m43..)
    sensor_height = 24
    sensor_width = 36
    sensor_diag = np.sqrt(24*24 + 36*36)
    ratio = sensor_nb_width/sensor_nb_height

    sensor_height = sensor_diag/np.sqrt(1 + ratio * ratio)
    sensor_width = ratio * sensor_height


    posx = (y1 + y2)/2
    posy = (x1 + x2)/2
    width = int((x2 - x1))
    height = int((y2 - y1))

    if cylindric:
        cylindric = 2
    

    pixel_size = sensor_height/sensor_nb_height

    mid_sensor_pos = (mid_sensor - np.array([posx, posy])) * pixel_size
    mid_sensor_pos = np.array([fl, mid_sensor_pos[0], mid_sensor_pos[1]])

    mid_sensor_pos = mid_sensor_pos * fl / norm(mid_sensor_pos)

    angle0 = np.arcsin(mid_sensor_pos[1]/fl) 
    angle1 = np.arcsin(mid_sensor_pos[2]/(fl* np.cos(angle0)))


    target_point = rotatey(rotatez([[fl, 0, 0]], angle0), angle1)
    p2 = np.array([
        [fl, (mid_sensor[0]-posx) * pixel_size, (posy - mid_sensor[1]) * pixel_size],
        [fl, (mid_sensor[0]-y1) * pixel_size, (x1 - mid_sensor[1]) * pixel_size],
        [fl, (mid_sensor[0]-posx) * pixel_size, (x1 - mid_sensor[1]) * pixel_size],
        [fl, (mid_sensor[0]-y1) * pixel_size, (posy - mid_sensor[1]) * pixel_size],
        [fl, (mid_sensor[0]-y2) * pixel_size, (x2 - mid_sensor[1]) * pixel_size],
        [fl, (mid_sensor[0]-posx) * pixel_size, (x2 - mid_sensor[1]) * pixel_size],
        [fl, (mid_sensor[0]-y2) * pixel_size, (posy - mid_sensor[1]) * pixel_size]])

    p3 = rotatez(rotatey(p2, -angle1), -angle0)

    if cylindric:
        p3 = p3 * fl/np.sqrt(p3[:,0:1] * p3[:,0:1] + p3[:,1:2] * p3[:,1:2] + p3[:,2:3] * p3[:,2:3])

        sensor2_mid = p3[0]

        height_length = 2 * np.max(
            [np.abs(np.max(p3[:,1]) - sensor2_mid[1]),
             np.abs(np.min(p3[:,1]) - sensor2_mid[1])])
    
        angle = 2 * np.max([
            np.abs(np.max(np.arctan(p3[:,2:3]/p3[:,0:1])) - np.arctan(sensor2_mid[2]/sensor2_mid[0])),
            np.abs(np.min(np.arctan(p3[:,2:3]/p3[:,0:1])) - np.arctan(sensor2_mid[2]/sensor2_mid[0]))])

        pixel_angle = angle/width

        pixel_size2 = np.min([
           height_length/height,
           pixel_angle * fl]
        )

        width2 = int(angle * fl/pixel_size2)
        height2 = int(height_length/pixel_size2)
        pixel_angle = angle/width2
    else:    
        p3 = p3 * fl/p3[:,0:1]
    
        sensor2_mid = p3[0]
        height_length = 2 * np.max(
            [np.abs(np.max(p3[:,1]) - sensor2_mid[1]),
             np.abs(np.min(p3[:,1]) - sensor2_mid[1])])

        width_length = 2 * np.max(
            [np.abs(np.max(p3[:,2]) - sensor2_mid[2]),
             np.abs(np.min(p3[:,2]) - sensor2_mid[2])]) 
        

        pixel_size2 = np.min([
            height_length/height,
            width_length/width])
        pixel_size2 *= 0.8
        height2 = int(height_length/pixel_size2)
        width2 = int(width_length/pixel_size2)


    if cylindric == 1:
        unit_height = np.array(
            [[0,
            1,
            0]])
    else:       
        unit_height = rotatey(rotatez([[0, 1, 0]], angle0), angle1)[0]

    unit_width = rotatey(rotatez([[0, 0, 1]], angle0), angle1)[0]
    axe = np.cross(unit_width, unit_height)
    unit_width = rotate_axe(axe, unit_width, [angle_rot])
    unit_height = rotate_axe(axe, unit_height, [angle_rot])

    enlarge = np.abs(1/np.cos(angle_rot))
    width2 = int(width2 * enlarge)
    height2 = int(height2 * enlarge)
    img2 = np.zeros((height2,width2, 3),dtype=np.uint8)
    size_rectangle = np.array([height2, width2])
    mid_rectangle = size_rectangle/2

    vec_height = pixel_size2 * unit_height

    if cylindric == 1:
        pos1 = rotate_axe(unit_height, target_point[0], 
            [pixel_angle*h for h in [mid_rectangle[1]-x for x in range(width2)]])
        #pos1 = np.array([
        #    target_point @ (np.array([
        #        [np.cos(pixel_angle*h), 0, np.sin(pixel_angle*h)],
        #        [0,1,0],
        #        [-np.sin(pixel_angle*h), 0, np.cos(pixel_angle*h)]
        #        ]).transpose())  for h in [mid_rectangle[1]-x for x in range(width2)]])
    elif cylindric == 2:
        pos1 = rotate_axe(unit_height[0], target_point[0], 
            [pixel_angle*h for h in [mid_rectangle[1]-x for x in range(width2)]])
    else:
        vec_width = pixel_size2  * unit_width
        pos1 = target_point + vec_width * (np.arange(width2).reshape(width2, 1) - mid_rectangle[1])
        
        

    pos2 = vec_height * (mid_rectangle[0] - np.arange(height2).reshape(height2, 1))
    for y in range(width2):
        x = pos1[y:y+1,:] + pos2
        z =  x[:, 1:3] * fl/x[:,0:1]
        orig = (np.array([mid_sensor]) + z * np.array([[-1/pixel_size, 1/pixel_size]])).astype(int)

        line = (
            (orig[:, 0:1] < sensor_nb_height) &
            (orig[:, 0:1] > 0) &
            (orig[:, 1:2] < sensor_nb_width) &
            (orig[:, 1:2] >0)
            )[:, 0]

        img2[line, y, :] =  img[orig[line,0], orig[line,1]]

    plt.draw()
    print("End smart crop")
    return(img2)

def toggle_selector(event):
    print(' Key pressed.')
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print(' RectangleSelector deactivated.')
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print(' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)

def submit_fl(fl_text):
    global fl
    print("FL changed")
    fl = float(fl_text)



class ImageCropView(object):
    def __init__(self, canvas, fig, axe):
        self.axe = axe
        self.fig = fig
        self.cylindric = False
        self.canvas = canvas



        self.canvas.draw()


    def on_click(self, event):
        print("On click")
        if event.button == 1 or event.button == 3 and not self.rs.active:
            self.rs.set_active(True)
        else:
            self.rs.set_active(False)


    def line_select_callback(self, eclick, erelease):
        global x1, x2, y1, y2
        
        'eclick and erelease are the press and release events'
        
        self.x1, self.y1 = int(eclick.xdata), int(eclick.ydata)
        self.x2, self.y2 = int(erelease.xdata), int(erelease.ydata)
        print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))

    def load_image(self, img_file):
        self.img=mpimg.imread(img_file)

        self.cylindric = False
        try:
            import PIL.Image
            img_pil = PIL.Image.open(img_file)

            import PIL.ExifTags
            exif = {
                PIL.ExifTags.TAGS[k]: v
                for k, v in img_pil._getexif().items()
                if k in PIL.ExifTags.TAGS 
            }
            self.fl = exif["FocalLengthIn35mmFilm"]
        except Exception:
            self.fl = 35

        self.sensor_nb_height = self.img.shape[0]
        self.sensor_nb_width = self.img.shape[1]

        self.mid_sensor = [self.sensor_nb_height/2, self.sensor_nb_width/2]

        # calculation to support different ration (m43..)
        self.sensor_height = 24
        self.sensor_width = 36
        self.sensor_diag = np.sqrt(24*24 + 36*36)
        self.ratio = self.sensor_nb_width/self.sensor_nb_height

        self.sensor_height = self.sensor_diag/np.sqrt(1 + self.ratio * self.ratio)
        self.sensor_width = self.ratio * self.sensor_height

        self.im_axe = self.axe.imshow(self.img)

        self.rs = RectangleSelector(self.axe, self.line_select_callback,
            drawtype='box', useblit=True,
            button=[1, 3],  # don't use middle button
            minspanx=5, minspany=5,
            spancoords='pixels',
            interactive=True)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('key_press_event', self.on_click)


        #self.canvas.draw()



