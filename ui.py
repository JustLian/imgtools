import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
import utils
from PIL import ImageDraw, ImageEnhance


class Resize(QMainWindow):
    def __init__(self, callback, image):
        super().__init__()
        self.callback = callback
        self.img = image
        self.initUI()

    def initUI(self):
        uic.loadUi('./ui/resize.ui', self)

        self.resize_btn.clicked.connect(self.callback)
        self.width_.setValue(self.img.size[0])
        self.height_.setValue(self.img.size[1])


class Crop(QMainWindow):
    def __init__(self, callback, image):
        super().__init__()
        
        # Setting up req variables
        self.callback = callback
        self.old_img = image
        self.img = image.copy()

        # Getting image size ration to convert slider position to image coords
        self.x_ratio = image.size[0] / 100
        self.y_ratio = image.size[1] / 100
        
        self.initUI()

    def initUI(self):
        uic.loadUi('./ui/crop.ui', self)

        self.image.resize(723, 523)
        utils.update_image(self)

        # Linking events
        self.p1_x.sliderChange = self.preview
        self.p1_y.sliderChange = self.preview
        self.p2_x.sliderChange = self.preview
        self.p2_y.sliderChange = self.preview

        self.crop_btn.clicked.connect(self.callback)
    
    def get_points(self):
        '''Get crop box coords'''
        return (
            (
                round(self.p1_x.value() * self.x_ratio),
                round((100 - self.p1_y.value()) * self.y_ratio)
            ),
            (
                round(self.p2_x.value() * self.x_ratio),
                round((100 - self.p2_y.value()) * self.y_ratio)
            )
        )

    def preview(self, _):
        self.img = self.old_img.copy()
        d = ImageDraw.Draw(self.img)
        d.rectangle(self.get_points(), outline=(0, 0, 0), width=4)
        utils.update_image(self)


class ColorCorrection(QMainWindow):
    def __init__(self, callback, image):
        super().__init__()

        # Setting up req variables
        self.callback = callback
        self.old_img = image
        self.img = image.copy()

        self.initUI()

    def initUI(self):
        uic.loadUi('./ui/color_correction.ui', self)
        utils.update_image(self)

        self.apply_btn.clicked.connect(self.apply)
        self.preview_btn.clicked.connect(self.preview)


    def apply_cc(self):
        self.img = ImageEnhance.Color(self.old_img).enhance(
            self.color.value() / 100
        )
        self.img = ImageEnhance.Contrast(self.img).enhance(
            self.contrast.value() / 100
        )
        self.img = ImageEnhance.Brightness(self.img).enhance(
            self.brightness.value() / 100
        )
        self.img = ImageEnhance.Sharpness(self.img).enhance(
            self.sharpness.value() / 100
        )
    
    def apply(self):
        self.apply_cc()
        self.callback()
    
    def preview(self):
        self.apply_cc()
        utils.update_image(self)