import sys
import os
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QInputDialog, QPushButton
import utils, ui
from PIL import Image, ImageFilter


if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

SUPPORTED_FORMATS = ['jpg', 'png', 'bmp', 'jpeg', 'webp']


def load_image(self, path):
        self.img = Image.open(path)
        self.update_image()


class ImgTools(utils.BaseWindow):
    def __init__(self):
        super().__init__()
        self.img: Image.Image = None
        self.optimized = False
        self.initUI()

    def initUI(self):
        uic.loadUi('./ui/main.ui', self)

        # Connecting buttons
        self.load_btn.clicked.connect(self.load_image)
        self.convert_btn.clicked.connect(self.convert)
        self.resize_btn.clicked.connect(self.resize_)
        self.blur_btn.clicked.connect(self.blur)
        self.crop_btn.clicked.connect(self.crop)
        self.cc_btn.clicked.connect(self.color_correction)
        self.optimize_btn.clicked.connect(self.optimize)
        self.censore_btn.clicked.connect(self.censore)

    def image_check(self) -> bool:
        if self.img is None:
            self.statusBar().showMessage('Please load image first!')
            return False
        return True

    def create_dialogs(self):
        self.resize_dialog = ui.Resize(self.resize_callback, self.img)
        self.crop_dialog = ui.Crop(self.crop_callback, self.img)
        self.cc_dialog = ui.ColorCorrection(self.cc_callback, self.img)
        self.censore_dialog = ui.Censore(self.censore_callback, self.img)

        # Linking events
        self.resize_dialog.hideEvent = self.enable_buttons
        self.crop_dialog.hideEvent = self.enable_buttons
        self.cc_dialog.hideEvent = self.enable_buttons
        self.censore_dialog.hideEvent = self.enable_buttons

        self.resize_dialog.showEvent = self.disable_buttons
        self.crop_dialog.showEvent = self.disable_buttons
        self.cc_dialog.showEvent = self.disable_buttons
        self.censore_dialog.showEvent = self.disable_buttons
    
    def enable_buttons(self, _):
        # When any dialog window hide all buttons will get enabled
        self.load_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        self.resize_btn.setEnabled(True)
        self.optimize_btn.setEnabled(True)
        self.crop_btn.setEnabled(True)
        self.cc_btn.setEnabled(True)
        self.blur_btn.setEnabled(True)
        self.censore_btn.setEnabled(True)

    def disable_buttons(self, _):
        # When any dialog window show all buttons will get disabled
        self.load_btn.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.resize_btn.setEnabled(False)
        self.optimize_btn.setEnabled(False)
        self.crop_btn.setEnabled(False)
        self.cc_btn.setEnabled(False)
        self.blur_btn.setEnabled(False)
        self.censore_btn.setEnabled(False)

    def optimize(self):
        '''Optimize image'''
        if not self.image_check():
            return

        self.optimized = not self.optimized
        if self.optimized:
            self.statusBar().showMessage('Image will be optimized on save')
        else:
            self.statusBar().showMessage('Image will be saved without optimization')


    def load_image(self):
        '''Loading image'''

        self.statusBar().showMessage('Choose file in dialog')
        # Get path to image
        fname = QFileDialog.getOpenFileName(
                self,
                'Choose image', '',
                utils.create_file_formats(SUPPORTED_FORMATS, 'Image')
            )[0]

        # No prompt / File doesn't exists
        if not os.path.isfile(fname):
            self.statusBar().showMessage('Can\'t locate chosen file')
            return
        
        # Loading image thru external function
        self.fp, self.fname = os.path.split(fname)
        self.fname = self.fname[:self.fname.rfind('.')]
        load_image(self, fname)
        self.statusBar().showMessage('Image loaded')

        # Creating all dialogs again
        self.create_dialogs()
    
    # Editing image
    def convert(self):
        '''Converts image to certain file format'''
        if not self.image_check():
            return

        self.statusBar().showMessage('Choose file format and file name in dialog')
        nfn, ok_pressed = QInputDialog.getText(
            self, "Save file", "Choose new file name", text=self.fname
        )
        ff, ok_pressed = QInputDialog.getItem(
            self, "Save file", "Choose file format", 
            SUPPORTED_FORMATS, 1, False
        )
        if ok_pressed:
            fn = '%s.%s' % (nfn, ff)
            self.img.save(
                os.path.join(
                    self.fp,
                    fn
                ),
                quality=90 if self.optimized else 100,
                optimize=self.optimized
            )
            self.statusBar().showMessage('Saved converted file: %s' % (
                utils.format_path(os.path.join(
                    self.fp, fn
                ))
            ))
        else:
            self.statusBar().showMessage('File saving aborted')
    
    def resize_(self):
        '''Resize image'''

        if not self.image_check():
            return

        self.create_dialogs()
        self.resize_dialog.show()
        self.statusBar().showMessage('Enter new width and height in dialog')
    
    def resize_callback(self, _):
        self.resize_dialog.hide()

        w1, h1 = self.img.size
        ratio = self.resize_dialog.ratio_btn.isChecked()
        w2 = int(self.resize_dialog.width_.value())
        h2 = int(self.resize_dialog.height_.value())

        if not ratio:
            self.img = self.img.resize((w2, h2))
        else:
            if w1 == w2:
                self.img = self.img.resize((
                    round(h2 * (w1 / h1)), h2
                ))
            elif h1 == h2:
                self.img = self.img.resize((
                    w2, round(w2 * (h1 / w1))
                ))
            else:
                self.img = self.img.resize((w2, h2))
        
        self.update_image()
        self.statusBar().showMessage('Image resized!')
    
    def blur(self):
        '''Blur image'''
        
        if not self.image_check():
            return

        self.statusBar().showMessage('Enter blur radius in dialog')
        radius, ok_pressed = QInputDialog.getDouble(
            self, "Blur", "Blur radius",
            0.1, 0.0, 100, 3
        )

        if ok_pressed:
            self.img = self.img.filter(
                ImageFilter.GaussianBlur(radius)
            )
            self.statusBar().showMessage('Blurred image with blur radius %s' % radius)
            self.update_image()
            return

        self.statusBar().showMessage('Image blur aborted')
    
    def crop(self):
        '''Crop image'''

        if not self.image_check():
            return

        self.create_dialogs()
        self.crop_dialog.show()
        self.statusBar().showMessage('Set crop box in dialog')
    
    def crop_callback(self, _):
        self.crop_dialog.hide()
        box = self.crop_dialog.get_points()
        box = [*box[1], *box[0]]

        # Correcting box to (left, upper, right, lower) format
        if box[0] > box[2]:
            box[0], box[2] = box[2], box[0]
        if box[1] > box[3]:
            box[1], box[3] = box[3], box[1]

        self.img = self.crop_dialog.old_img.crop(box)
        self.update_image()
        self.statusBar().showMessage('Cropped image')

    def censore(self):
        '''Censore image'''

        if not self.image_check():
            return

        self.create_dialogs()
        self.censore_dialog.show()
        self.statusBar().showMessage('Choose part of image to censor')
    
    def censore_callback(self, _):
        self.censore_dialog.hide()
        
        self.censore_dialog.preview()
        self.img = self.censore_dialog.img.copy()

        self.update_image()
        self.statusBar().showMessage('Censored image')
    
    def color_correction(self):
        '''CC Image'''

        if not self.image_check():
            return
        
        self.create_dialogs()
        self.cc_dialog.show()
        self.statusBar().showMessage('Correct everything you need and press "Apply!"')
    
    def cc_callback(self):
        self.cc_dialog.hide()

        self.img = self.cc_dialog.img.copy()
        self.update_image()
        self.statusBar().showMessage('Color correction applied!')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImgTools()
    ex.show()
    sys.exit(app.exec())