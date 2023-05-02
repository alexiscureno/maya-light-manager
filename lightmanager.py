import json
import time

from PyQt5 import QtWidgets, QtCore, QtGui, uic, Qt
from PyQt5.QtWidgets import QDialog, QPushButton, QComboBox, QCheckBox, QScrollArea, QWidget, QGridLayout, QSlider, \
    QVBoxLayout, QMainWindow, QFileDialog
from PyQt5 import Qt
import pymel.core as pm
from functools import partial
import os
import logging

logging.basicConfig()
logger = logging.getLogger('lightingManager')
logger.setLevel(logging.DEBUG)


class LightManager(QDialog):
    light_types = {
        "Point Light": pm.pointLight,
        "Spot Light": pm.spotLight,
        "Ambient Light": pm.ambientLight,
        "Directional Light": pm.directionalLight,
        "Area Light": partial(pm.shadingNode, 'areaLight', asLight=True),
        "Volume Light": partial(pm.shadingNode, 'volumeLight', asLight=True)

    }

    def __init__(self):

        super(LightManager, self).__init__()
        uic.loadUi(r'C:\Users\user\Documents\maya\2023\scripts\light.ui', self)

        self.create_btn = self.findChild(QPushButton, 'create_button')
        self.create_btn.clicked.connect(self.create_light)

        self.refresh_btn = self.findChild(QPushButton, 'refresh_button')
        self.refresh_btn.clicked.connect(self.populate)

        self.save_btn = self.findChild(QPushButton, 'save_button')
        self.save_btn.clicked.connect(self.save_lights)

        self.import_btn = self.findChild(QPushButton, 'import_button')
        self.import_btn.clicked.connect(self.import_lights)

        self.scroll_widget = self.findChild(QWidget, "scrollAreaWidgetContents")
        self.scroll_layout = self.findChild(QVBoxLayout, 'verticalLayout_3')
        self.scroll_widget.setLayout(self.scroll_layout)

        self.scroll_area = self.findChild(QScrollArea, "scrollArea")
        self.scroll_area.setWidget(self.scroll_widget)

        self.combo_box = self.findChild(QComboBox, 'comboBox')
        for light_type in sorted(self.light_types):
            self.combo_box.addItem(light_type)

        self.populate()

    def populate(self):
        while self.scroll_layout.count():
            widget = self.scroll_layout.takeAt(0).widget()
            if widget:
                widget.setVisible(False)
                widget.deleteLater()

        for light in pm.ls(
                type=['ambientLight', 'areaLight', 'spotLight', 'pointLight', 'directionalLight', 'volumeLight']):
            self.add_light(light)

    def save_lights(self):
        properties = {}

        for light_widget in self.findChildren(LightWidget):
            light = light_widget.light
            transform = light.getTransform()

            properties[str(transform)] = {
                'translate': list(transform.translate.get()),
                'rotation': list(transform.rotate.get()),
                'lightType': pm.objectType(light),
                'intensity': light.intensity.get(),
                'color': light.color.get()
            }

        directory = self.get_directory()

        lightFile = os.path.join(directory, 'lightFile_%s.json' % time.strftime('%m%d'))
        with open(lightFile, 'w') as f:
            json.dump(properties, f, indent=4)

        logger.info('Saving file to %s' % lightFile)

    def get_directory(self):
        directory = os.path.join(pm.internalVar(userAppDir=True), 'lightManager')
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory

    def import_lights(self):
        directory = self.get_directory()
        file_name = QFileDialog.getOpenFileName(self, "Light Browser", directory)

        with open(file_name[0], 'r') as f:
            properties = json.load(f)

        for light, info in properties.items():
            lightType = info.get('lightType')
            for lt in self.light_types:
                if ('%sLight' % lt.split()[0].lower()) == lightType:
                    break
            else:
                logger.info('Cannot find a corresponding light type for %s (%s)' % (light, lightType))
                continue

            light = self.create_light(light_type=lt)
            light.intensity.set(info.get('intensity'))

            light.color.set(info.get('color'))

            transform = light.getTransform()
            transform.translate.set(info.get('translate'))
            transform.rotate.set(info.get('translate'))

        self.populate()

    def create_light(self, light_type=None):
        if not light_type:
            light_type = self.combo_box.currentText()

        func = self.light_types[light_type]
        light = func()

        widget = LightWidget(light)
        self.scroll_layout.addWidget(widget)

        #self.add_light(light)
        widget.onSolo.connect(self.on_solo)

        return light

    def add_light(self, light):
        widget = LightWidget(light)
        self.scroll_layout.addWidget(widget)
        self.scroll_widget.setLayout(self.scroll_layout)
        widget.onSolo.connect(self.on_solo)

    def on_solo(self, value):
        light_widgets = self.findChildren(LightWidget)
        for widget in light_widgets:
            if widget != self.sender():
                widget.disable_lights(value)


class LightWidget(QWidget):
    onSolo = QtCore.pyqtSignal(bool)

    def __init__(self, light):
        super(LightWidget, self).__init__()
        if isinstance(light, str):
            light = pm.PyNode(light)
        if isinstance(light, pm.nodetypes.Transform):
            light = light.getShape()

        self.light = light
        self.create_widgets()

    def create_widgets(self):
        layout = QGridLayout(self)

        self.checkbox = QCheckBox(str(self.light.getTransform()))
        self.checkbox.setChecked(self.light.visibility.get())
        self.checkbox.toggled.connect(lambda val: self.light.getTransform().visibility.set(val))
        layout.addWidget(self.checkbox, 0, 0)

        self.solo_btn = QPushButton('Solo')
        self.solo_btn.setCheckable(True)
        self.solo_btn.toggled.connect(lambda val: self.onSolo.emit(val))
        layout.addWidget(self.solo_btn, 0, 1)

        self.delete_btn = QPushButton('x')
        self.delete_btn.clicked.connect(self.delete_lights)
        self.delete_btn.setMaximumWidth(10)
        layout.addWidget(self.delete_btn, 0, 2)

        self.slider_intensity = QSlider(QtCore.Qt.Horizontal)
        self.slider_intensity.setMinimum(1)
        self.slider_intensity.setMaximum(1000)
        self.slider_intensity.setValue(self.light.intensity.get())
        self.slider_intensity.valueChanged.connect(lambda val: self.light.intensity.set(val))
        layout.addWidget(self.slider_intensity, 1, 0, 1, 2)

        self.color_btn = QPushButton()
        self.color_btn.setMaximumWidth(20)
        self.color_btn.setMaximumHeight(20)
        self.set_btn_color()
        self.color_btn.clicked.connect(self.set_color)
        layout.addWidget(self.color_btn, 1, 2)

    def disable_lights(self, value):
        self.checkbox.setChecked(not value)

    def delete_lights(self):
        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()
        pm.delete(self.light.getTransform())

    def set_btn_color(self, color=None):
        if not color:
            color = self.light.color.get()
        assert len(color) == 3, "Please, provide a list of 3 colors"
        r, g, b = [c * 255 for c in color]

        self.color_btn.setStyleSheet('background-color: rgba(%s, %s, %s, 1.0)' % (r, g, b))

    def set_color(self):
        light_color = self.light.color.get()
        color = pm.colorEditor(rgbValue=light_color)

        r, g, b, a = [float(c) for c in color.split()]
        color = (r, g, b)

        self.light.color.set(color)
        self.set_btn_color(color)


window = LightManager()
window.show()
