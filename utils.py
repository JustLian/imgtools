from PIL import Image
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow
import typing as t


class BaseWindow(QMainWindow):
    '''QMainWindow class w/ method for updating self.img PIL Image'''
    def update_image(self):
        size = resize_img(self.img, self.image.size().width(), self.image.size().height())
        self.pixmap = pil2pixmap(self.img.resize(size))
        self.image.setPixmap(self.pixmap)


def pil2pixmap(im: Image.Image) -> QPixmap:
    '''Converts PIL.Image to QtGui.QPixmap'''

    if im.mode == "RGB":
        r, g, b = im.split()
        im = Image.merge("RGB", (b, g, r))
    elif  im.mode == "RGBA":
        r, g, b, a = im.split()
        im = Image.merge("RGBA", (b, g, r, a))
    elif im.mode == "L":
        im = im.convert("RGBA")

    im2 = im.convert("RGBA")
    data = im2.tobytes("raw", "RGBA")
    qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
    pixmap = QPixmap.fromImage(qim)
    return pixmap


def resize_img(im: Image.Image, w1: int, h1: int) -> t.Tuple[int, int]:
    '''Resizes image to fit in the window'''
    w2, h2 = im.size

    ratio = min(w1 / w2, h1 / h2)
    return (round(w2 * ratio), round(h2 * ratio))


def create_file_formats(file_formats: t.Sequence[str], text: str) -> str:
    '''Converts sequence of file formats to string'''
    return ';;'.join([
        '%s (*.%s)' % (text, ff)
        for ff in file_formats
    ])


def format_path(path: str) -> str:
    '''Makes path string pretty'''
    return path.replace(
        '\\', '/'
    ).replace(
        '//', '/'
    )