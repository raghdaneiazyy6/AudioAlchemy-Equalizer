import time
import sys
import os
import warnings

import librosa
from os import path
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtMultimedia
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer  # Updated line
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUiType
import soundfile as sf
from PyQt5.QtGui import QIcon,QFont
from IPython.display import Audio
import pyqtgraph as pg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "design.ui"))

class MainApp(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("AudioAlchemy Equalizer")
        self.originalSpectrogramWidget.setVisible(1)
        self.outputSpectrogramWidget.setVisible(1)
        self.spectrogramRadioButton.setChecked(False)
        self.stopButton.setEnabled(0)
        self.constructAudioButton.setEnabled(0)
        self.deleteButton.setEnabled(0)

        # Set default tab to Equalizer
        self.tabWidget.setCurrentIndex(0)
        self.modeComboBox.setCurrentIndex(0)

        # Set up icons for buttons & sliders
        self.playIcon = QtGui.QIcon("icons/playIcon.png")
        self.pauseIcon = QtGui.QIcon("icons/pauseIcon.png")
        self.stopIcon = QtGui.QIcon("icons/stopIcon.png")
        self.replayIcon = QtGui.QIcon("icons/replayIcon.png")
        self.confirmIcon = QtGui.QIcon("icons/confirmIcon.png")
        self.zoomInIcon = QtGui.QIcon("icons/zoomInIcon.png")
        self.zoomOutIcon = QtGui.QIcon("icons/zoomOutIcon.png")
        self.soundIcon = QtGui.QIcon("icons/soundIcon.png")
        self.muteIcon = QtGui.QIcon("icons/muteIcon.png")
        self.deleteIcon = QtGui.QIcon("icons/deleteIcon.png")
        equalizerTab = QtGui.QIcon("icons/equalizerIcon.png")
        smootherTab = QtGui.QIcon("icons/smootherIcon.png")
        windowIcon = QtGui.QIcon("icons/windowIcon.png")
        self.elephantIcon = QtGui.QIcon("icons/whale.png")
        self.sheepIcon = QtGui.QIcon("icons/cricket.png")
        self.wolfIcon = QtGui.QIcon("icons/bird.png")
        self.tigerIcon = QtGui.QIcon("icons/dog.png")
        self.seaLionIcon = QtGui.QIcon("icons/dog.png")
        self.guitarIcon = QtGui.QIcon("icons/drums.png")
        self.drumsIcon = QtGui.QIcon("icons/trumpet.png")
        self.trumpetIcon = QtGui.QIcon("icons/xylo.png")
        self.pianoIcon = QtGui.QIcon("icons/triangle.png")

        # Set icons for tabs
        self.tabWidget.setTabIcon(0, equalizerTab)  # 0 is the index of the composerTab
        self.tabWidget.setTabIcon(1, smootherTab)   # 1 is the index of the viewerTab
        self.setWindowIcon(windowIcon)

        # Set icons for buttons
        self.playPauseButton.setIcon(self.playIcon)
        self.stopButton.setIcon(self.stopIcon)
        self.replayButton.setIcon(self.replayIcon)
        self.confirmButton.setIcon(self.confirmIcon)
        self.muteOriginalButton.setIcon(self.soundIcon)
        self.deleteButton.setIcon(self.deleteIcon)

        # Apply style sheet for sliders
        self.slidersStyleHorizontal1 = "QSlider::groove:horizontal { border: 1px solid #999999; background: white; width: 8px; border-radius: 4px; }"
        self.slidersStyleHorizontal2 = "QSlider::handle:horizontal { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #d3d3d3, stop:1 #c0c0c0); border: 1px solid #5c5c5c; width: 8px; height: 14px; margin: -2px 0; border-radius: 4px; }"
        self.slidersStyleVertical1 = "QSlider::groove:vertical { border: 1px solid #999999; background: white; width: 8px; border-radius: 4px; }"
        self.slidersStyleVertical2 = "QSlider::handle:vertical { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #d3d3d3, stop:1 #c0c0c0); border: 1px solid #5c5c5c; width: 8px; height: 14px; margin: -2px 0; border-radius: 4px; }"

        # Initialize and configure plotting widgets
        self.originalSignalWidget = pg.PlotWidget()
        self.outputSignalWidget = pg.PlotWidget()
        self.originalSpectrogramWidget = pg.PlotWidget()
        self.outputSpectrogramWidget = pg.PlotWidget()
        self.frequencyWidget = pg.PlotWidget()
        self.smoothedSignalWidget = pg.PlotWidget()

        self.originalSignalLayout.addWidget(self.originalSignalWidget)
        self.outputSignalLayout.addWidget(self.outputSignalWidget)
        self.frequencyLayout.addWidget(self.frequencyWidget)
        self.smoothingLayout.addWidget(self.smoothedSignalWidget)

        ##################### Sliders ##################
        self.speedSlider = self.findChild(QSlider, "speedSlider")
        self.speedLCD = self.findChild(QLCDNumber, "speedLCD")
        self.speedSlider.valueChanged.connect(lambda: self.speedLCD.display(self.speedSlider.value()))
        self.speedSlider.setMinimum(1)
        self.speedSlider.setMaximum(100)
        self.speedSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speedSlider.setTickInterval(1)
        self.speedSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.speedSlider.setStyleSheet(self.slidersStyleHorizontal2)

        self.meanSlider.valueChanged.connect(lambda: self.meanLCD.display(self.meanSlider.value()))
        self.meanSlider.valueChanged.connect(self.updateGaussianWindow)
        self.meanSlider.setTickInterval(1)
        self.meanSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.meanSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.meanSlider.setStyleSheet(self.slidersStyleHorizontal2)

        self.standardDeviationSlider.setMinimum(1)
        self.standardDeviationSlider.setMaximum(30)
        self.standardDeviationSlider.setTickInterval(1)
        self.standardDeviationSlider.setValue(10)
        self.standardDeviationSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.standardDeviationSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.standardDeviationSlider.setStyleSheet(self.slidersStyleHorizontal2)
        self.standardDeviationSlider.valueChanged.connect(self.updateGaussianWindow)
        self.standardDeviationSlider.valueChanged.connect(lambda: self.standardDeviationLCD.display(self.standardDeviationSlider.value() / 10.0))

        self.originalTimer=QTimer(self)
        self.originalTimer.start(1000)
        self.originalTimer.timeout.connect(self.originalMediaProgress)
        self.originalProgressSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.originalProgressSlider.setStyleSheet(self.slidersStyleHorizontal2)

        self.setupSliders()
        ##################### Sliders ##################
        ####window##
        self.smoothing_list = []
        self.smoothing_list.append(1)

        #################### Variables and data structures ####################
        self.playing = False
        self.originalSoundOn = True
        self.outputSoundOn = True
        self.fft_result = None
        self.playheadPosition = 0
        self.elapsedTime = 0
        self.originalSignalDuration = 0
        self.uniformSignals = []
        self.animalSounds = []
        self.musicTracks = []
        self.ecgSignals = []
        self.currentVolume = 50

        self.Normal =3341
        self.instrumentsFrequencyRanges = [
            [0, 1000], # Guitar
            [1000, 2000], # Drums
            [2000, 3000], # Trumpet
            [4000, 5000] # Piano
            ]

        # self.animalsFrequencyRanges  = [
        #     [80, 800], # Bengal Tiger
        #     [15, 100], # Elephant
        #     [100, 1000], # Lamb
        #     [2000, 3000] # Sea Lion
        #     ]

        self.animalsFrequencyRanges  = [
            [600, 800], # Bengal Tiger
            [3800, 7000], # Elephant
            [1000, 6000], # Lamb
            [0, 3000] # Sea Lion
            ]

        self.ecgFrequencyRanges  = [
            [0, 12],
            [0, 0],
            [38, 96],
            ]
        self.mediaDuration = 0
        self.mediaPausePosition = 0
        self.playheadLineOriginal=0
        self.playheadLineOutput=0
        self.file_index_music = 1
        self.file_index_animal = 1
        self.ecgSignal = r"C:\Users\hazem\Downloads\AudioAlchemy-Equalizer-main"

        self.playheadUpdateTimer = QTimer(self)  # bta3 elplayhead fluniform
        self.playheadUpdateInterval = 100

        self.originalTimer = QTimer(self)  # bta3 elprogress bar flaudio
        self.originalTimer.start(100)

        self.menu_actions = {
            self.actionOpenUniformSignal: self.open_signal,
            self.actionOpenAnimalSounds: self.open_animal_sounds,
            self.actionOpenInstrumentsSounds: self.open_instruments_sounds,
            self.actionOpenECGSignal: self.open_medical_signal,
        }  # refactor

        # Create a dictionary to map modes to their parameters
        self.mode_parameters = {
            "Uniform Range Mode": {
                "sliders": 10,
                "lcds": 10,
                "labels": 10,
                "frequency_ranges": None,  # You can update this with actual frequency ranges
            },
            "ECG Abnormalities Mode": {
                "sliders": 3,
                "lcds": 3,
                "labels": 3,
                "frequency_ranges": self.ecgFrequencyRanges,
            },
            "Animal Sounds Mode": {
                "sliders": 4,
                "lcds": 4,
                "labels": 4,
                "frequency_ranges": self.animalsFrequencyRanges,
            },
            "Musical Instruments Mode": {
                "sliders": 4,
                "lcds": 4,
                "labels": 4,
                "frequency_ranges": self.instrumentsFrequencyRanges,
            },
        }  # refactor

        # Define mode mappings
        self.mode_functions = {
            "Uniform Range Mode": self.uniformRangeMode,
            "Animal Sounds Mode": self.animalSoundsMode,
            "Musical Instruments Mode": self.musicalInstrumentsMode,
            "ECG Abnormalities Mode": self.ECGAbnormalitiesMode,
        }

        self.mode_items = {
            "Uniform Range Mode": None,
            "Animal Sounds Mode": [
                [self.elephantIcon, self.sheepIcon, self.wolfIcon, self.seaLionIcon],
                self.animalSounds,
                [4, 5, 6, 7, 8, 9],
            ],
            "Musical Instruments Mode": [
                [self.guitarIcon, self.drumsIcon, self.trumpetIcon, self.pianoIcon],
                self.musicTracks,
                [4, 5, 6, 7, 8, 9],
            ],
            "ECG Abnormalities Mode": [
                None,
                self.ecgSignals,
                [3, 4, 5, 6, 7, 8, 9],
            ],
        }
        #################### Variables and data structures ####################

        ############## Buttons and checkboxes connections ##############
        self.smootherComboBox.setCurrentIndex(0)
        # Connect menu actions to the combined function
        for action, function in self.menu_actions.items():
            action.triggered.connect(function)  # refactor

        self.smootherComboBox.setCurrentIndex(0)
        self.playPauseButton.clicked.connect(self.updatePlayheadForMode)
        self.muteOriginalButton.clicked.connect(self.toggleMuteOriginal)
        self.spectrogramRadioButton.toggled.connect(self.toggleSpectrogramVisibility)
        self.modeComboBox.currentIndexChanged.connect(self.modeChanged)
        self.smootherComboBox.currentIndexChanged.connect(lambda index: self.initiate_wave(index))
        self.changeWindowButton.clicked.connect(lambda _: self.tabWidget.setCurrentIndex(1))
        self.confirmButton.pressed.connect(self.converted)
        self.speedSlider.valueChanged.connect(lambda: self.updatePlayheadSpeed(self.speedSlider.value()))
        self.replayButton.clicked.connect(self.replayToggle)
        self.mediaPlayer = QtMultimedia.QMediaPlayer()
        self.mediaPlayer.setVolume(self.currentVolume)
        self.mediaPlayer.pause()
        self.mediaPlayer.positionChanged.connect(self.updatePlayheadPosition)
        self.originalProgressSlider.sliderMoved[int].connect(lambda: self.mediaPlayer.setPosition(self.originalProgressSlider.value()))
        self.originalVolumeSpinBox.valueChanged[int].connect(lambda: self.originalVolumeChange())
        self.originalProgressSlider.valueChanged[int].connect(self.updatePlayheadPosition)
        self.stopButton.clicked.connect(self.stopMedia)
        self.audioListWidget.itemSelectionChanged.connect(self.plotSelectedSignal)
        self.deleteButton.clicked.connect(self.deleteSelectedItem)
        self.playheadUpdateTimer.timeout.connect(self.updatePlayheadPosition)
        self.originalTimer.timeout.connect(self.originalMediaProgress)
        self.constructAudioButton.clicked.connect(lambda: self.new_song_save(self.fs, self.reconstructed_signal))
        ############## Buttons and checkboxes connections ##############

    # Get the current working directory
        self.current_directory = os.getcwd()

    # Join the current directory path with the filename to get the full path
        self.Normal_csv_path = os.path.join(self.current_directory, 'Normal.csv')

# ------------------------------------------------------------------------------------------
    def open_signal(self):  # refactor tmam
        self.open_file_dialog("Open Uniform Signal File", "Signal Files (*.csv);;All Files (*)", self.uniformSignals,
                              "Uniform Signals Mode")

    def open_animal_sounds(self):  # refactor tmam
        self.open_file_dialog("Add Animal Sounds", "Supported Files (*.mp3;*.m4a;*.wma;*.mpeg;*.ogg;*.MP3;*.wav)",
                              self.animalSounds, "Animal Sounds Mode")

    def open_instruments_sounds(self):  # refactor tmam
        self.open_file_dialog("Add Music Tracks", "Supported Files (*.mp3;*.m4a;*.wma;*.mpeg;*.ogg;*.MP3;*.wav)",
                              self.musicTracks, "Musical Instruments Mode")

    def open_medical_signal(self):  # refactor tmam
        self.open_file_dialog("Add Medical Signals", "Supported Files (*.csv);;All Files (*)", self.ecgSignals,
                              "ECG Abnormalities Mode")

    def open_file_dialog(self, dialog_title, file_filter, target_list, mode_text):  # refactor tmam
        files, _ = QFileDialog.getOpenFileNames(self, caption=dialog_title, directory='://', filter=file_filter)
        self.audioListWidget.clear()
        if files:
            for file in files:
                target_list.append(file)
                self.audioListWidget.addItem(file)
            self.modeComboBox.setCurrentText(mode_text)

    def playMedia(self):
        try:
            self.currentSelection = self.audioListWidget.currentRow()
            self.mode = self.modeComboBox.currentText()

            if self.mode == "Animal Sounds Mode":
                self.currentSound = self.animalSounds[self.currentSelection]
            elif self.mode == "Musical Instruments Mode":
                self.currentSound = self.musicTracks[self.currentSelection]

            if self.originalProgressSlider.value() == 0:
                self.setMediaContent()
                self.originalMediaProgress()

            if self.stopButton.isEnabled():
                self.pauseMedia()
            else:
                self.startMedia()

        except Exception as e:
            print(f"Play media error: {e}")

    def setMediaContent(self):
        mediaURL = QMediaContent(QUrl.fromLocalFile(self.currentSound))
        self.mediaPlayer.setMedia(mediaURL)

    def startMedia(self):
        self.mediaPlayer.setPosition(self.originalProgressSlider.value())
        self.mediaPlayer.play()
        self.toggleMediaControls(True)

    def pauseMedia(self):
        self.mediaPlayer.pause()
        self.toggleMediaControls(False)

    def toggleMediaControls(self, playing):
        self.stopButton.setEnabled(playing)
        self.playPauseButton.setIcon(self.pauseIcon if playing else self.playIcon)
        self.playheadUpdateTimer.start(self.playheadUpdateInterval)
        self.originalTimer.start(self.playheadUpdateInterval)

    def setupSliders(self, num_sliders=10):
        self.sliders = []
        self.lcds = []
        self.labels=[]

        for i in range(num_sliders):
            slider = self.findChild(QSlider, f"slider_{i+1}")
            lcd = self.findChild(QLCDNumber, f"lcd_{i+1}")
            label = self.findChild(QLabel, f"label_{i+1}")

            slider.setOrientation(Qt.Orientation.Vertical)
            slider.setValue(1)
            lcd.display(1)

            slider.setMinimum(0)
            slider.setMaximum(5)
            slider.setStyleSheet(self.slidersStyleVertical1)
            slider.setStyleSheet(self.slidersStyleVertical2)

            slider.setTickPosition(QSlider.TickPosition.TicksRight)
            slider.setTickInterval(1)
            self.sliders.append(slider)
            self.lcds.append(lcd)
            self.labels.append(label)

    def slider_mode(self):
        self.mode = self.modeComboBox.currentText()
        mode_params = self.mode_parameters.get(self.mode, {})  # Get mode-specific parameters
        selected_item = self.audioListWidget.currentItem()
        # print(selected_item)
        # for i in range(self.ecgSignals) :
        #     if self.ecgSignals[i] == self.Normal_csv_path:
        #         print("hazem")
        #         self.ecgFrequencyRanges[0] = [0, 0]
        #         break
        #     else:
        #         self.ecgFrequencyRanges[0] = [0, 12]

        num_sliders = mode_params.get("sliders", 0)
        for index, (slider, lcd, label) in enumerate(
                zip(self.sliders[:num_sliders], self.lcds[:num_sliders], self.labels[:num_sliders])):
            slider.valueChanged.connect(lambda value, idx=index: self.sliderValueChanged(idx, value))
            slider.valueChanged.connect(lambda value, lcd=lcd: lcd.display(value))

    def sliderValueChanged(self, slider_idx, value):  # refactor tmam
        mode_params = self.mode_parameters.get(self.modeComboBox.currentText(), {})
        frequency_ranges = mode_params.get("frequency_ranges", None)

        if frequency_ranges:
            min_frequency, max_frequency = frequency_ranges[slider_idx]
            min_idx = np.argmin(np.abs(self.frequencies - min_frequency))
            max_idx = np.argmin(np.abs(self.frequencies - max_frequency))
        else:
            frequency_step = (len(self.frequencies) / 2) // 10
            min_frequency = slider_idx * frequency_step
            max_frequency = ((slider_idx + 1) * frequency_step) + 2 if slider_idx == 9 else (
                                                                                                    slider_idx + 1) * frequency_step
            min_idx = int(min_frequency)
            max_idx = int(max_frequency)

        self.freqRangeSmoothing = self.frequencies[min_idx:max_idx]
        self.initiate_wave(self.smootherComboBox.currentIndex())
        self.slider_changes[min_idx:max_idx] = value * self.smoothing_window
        self.new_magnitudes = self.fft_magnitudes * self.slider_changes
        self.plotFrequencyDomain(self.frequencies, self.new_magnitudes)
        if self.smootherComboBox.currentIndex() != 0:  # gded
            self.frequencyWidget.plot(self.freqRangeSmoothing, self.smoothing_window * max(self.new_magnitudes),
                                      pen='r')  # gded
            if self.smoothing_list[-1] != self.smoothing_list[len(self.smoothing_list) - 2]:
                self.smootherComboBox.setCurrentIndex(0)


    def playPauseToggling(self):
        mode=self.modeComboBox.currentText()
        if mode=="Uniform Range Mode" or mode=="ECG Abnormalities Mode":
            self.playSignal()
        else:
            self.playMedia()

    def playSignal(self):
        self.playing = not self.playing

        if self.playing or (self.mediaPlayer.state() == QMediaPlayer.PlayingState):
            self.playPauseButton.setIcon(self.pauseIcon)
            self.stopButton.setEnabled(1)
            self.playheadUpdateTimer.start(self.playheadUpdateInterval)
            self.originalTimer.start(self.playheadUpdateInterval)

        else:
            self.stopButton.setEnabled(0)
            self.playPauseButton.setIcon(self.playIcon)

    def stopMedia(self):
        if self.stopButton.isEnabled():
            mode = self.modeComboBox.currentText()
            if mode=="Uniform Range Mode" or mode=="ECG Abnormalities Mode":
                self.playing = False
            elif mode == "Animal Sounds Mode" or mode == "Musical Instruments Mode":
                self.mediaPlayer.stop()

            self.playPauseButton.setIcon(self.playIcon)
            self.stopButton.setEnabled(0)
            self.originalProgressSlider.setValue(0)
            self.playheadLineOriginal.setValue(0)
            self.playheadLineOutput.setValue(0)
            self.originalStartLabel.setText(f"0:00 /")
            self.originalEndLabel.setText(f"0:00")

    def replayToggle(self):
        self.elapsedTime = 0
        mode = self.modeComboBox.currentText()
        if mode=="Uniform Range Mode" or mode=="ECG Abnormalities Mode":
            # Reset the playhead position to the beginning
            self.playheadLineOriginal.setPos(self.elapsedTime)
            self.playheadLineOutput.setPos(self.elapsedTime)
        elif mode == "Animal Sounds Mode" or mode == "Musical Instruments Mode":
            self.mediaPlayer.stop()
            self.stopButton.setEnabled(1)
            self.originalStartLabel.setText(f"0:00 /")
            self.originalEndLabel.setText(f"{self.mediaDuration}")
            self.originalProgressSlider.setValue(0)
            self.mediaPlayer.play()

    def updatePlayheadSpeed(self, speed):
        self.playheadUpdateInterval = speed
        # Update the playhead update interval for the QTimer
        self.playheadUpdateTimer.setInterval(self.playheadUpdateInterval)
        self.originalTimer.setInterval(self.playheadUpdateInterval)

    def updatePlayheadPosition(self):
        if self.playing or (self.mediaPlayer.state() == QMediaPlayer.PlayingState):
            # Update the elapsed time based on the playhead update interval
            mode = self.modeComboBox.currentText()
            if mode == "Uniform Range Mode" or mode=="ECG Abnormalities Mode":
                self.elapsedTime += self.playheadUpdateInterval / 1000.0  # Convert milliseconds to seconds
            else:
                self.elapsedTime = self.originalProgressSlider.value() / 1000.0

            if self.elapsedTime > self.originalSignalDuration:
                self.elapsedTime = self.originalSignalDuration
                self.playing = False  # Stop playing when the end is reached
                self.playPauseButton.setIcon(self.playIcon)

            # Update the position of the playhead line directly
            self.playheadLineOriginal.setPos(self.elapsedTime)
            self.playheadLineOutput.setPos(self.elapsedTime)

    def originalMediaProgress(self):
        if self.mediaPlayer.state()==QMediaPlayer.PlayingState:
            self.originalProgressSlider.setMinimum(0)
            self.originalProgressSlider.setMaximum(self.mediaPlayer.duration())
            sliderValue=self.mediaPlayer.position()
            self.originalProgressSlider.setValue(sliderValue)
            self.currentTime=time.strftime('%M:%S',time.localtime(self.mediaPlayer.position()/1000))
            self.mediaDuration=time.strftime('%M:%S',time.localtime(self.mediaPlayer.duration()/1000))
            self.originalStartLabel.setText(f"{self.currentTime}")
            self.originalEndLabel.setText(f"{self.mediaDuration}")

    def originalVolumeChange(self):
        try:
            self.originalVolume=self.originalVolumeSpinBox.value()
            self.mediaPlayer.setVolume(self.originalVolume)
        except Exception as e:
            print(f"Changing volume error: {e}")

    def toggleMuteOriginal(self):
        self.originalSoundOn = not self.originalSoundOn

        if self.originalSoundOn:
            self.muteOriginalButton.setIcon(self.soundIcon)
            self.mediaPlayer.setMuted(False)
        else:
            self.muteOriginalButton.setIcon(self.muteIcon)
            self.mediaPlayer.setMuted(True)

    def deleteSelectedItem(self):
        selectedIndex = self.audioListWidget.currentRow()
        self.mode = self.modeComboBox.currentText()
        data_dict = {
            "Uniform Range Mode": (self.uniformSignals, self.deleteButton),
            "Animal Sounds Mode": (self.animalSounds, self.deleteButton, self.constructAudioButton),
            "Musical Instruments Mode": (self.musicTracks, self.deleteButton, self.constructAudioButton),
            "default": (self.ecgSignals, self.deleteButton)
        }
        data_list, *buttons = data_dict.get(self.mode, data_dict['default'])

        if selectedIndex >= 0:
            del data_list[selectedIndex]
            if not data_list:
                for button in buttons:
                    button.setEnabled(0)

            # Remove the item from the list widget
            self.audioListWidget.takeItem(selectedIndex)

    def toggleSpectrogramVisibility(self, checked):
        if checked:
            for i in range(self.originalSpectrogramLayout.count()):
                widget = self.originalSpectrogramLayout.itemAt(i).widget()
                widget.setVisible(True)
            for i in range(self.outputSpectrogramLayout.count()):
                widget = self.outputSpectrogramLayout.itemAt(i).widget()
                widget.setVisible(True)

        else:
            for i in range(self.originalSpectrogramLayout.count()):
                widget = self.originalSpectrogramLayout.itemAt(i).widget()
                widget.hide()
            for i in range(self.outputSpectrogramLayout.count()):
                widget = self.outputSpectrogramLayout.itemAt(i).widget()
                widget.hide()

    def plotOriginalSignal(self, t, signal, fs):
        self.mode=self.modeComboBox.currentText()
        self.originalSignalWidget.clear()
        self.originalSignalDuration = t[-1] - t[0]
        min_magnitude = np.min(signal)
        self.originalSignalWidget.plotItem.getViewBox().setLimits(yMin=min_magnitude, yMax=-(min_magnitude))
        if self.mode == "ECG Abnormalities Mode":
            max_magnitude = np.max(t)
            max_magnitude_signal = np.max(signal)
            self.originalSignalWidget.plotItem.getViewBox().setLimits(xMin=0, xMax=(max_magnitude))
            self.originalSignalWidget.plotItem.getViewBox().setLimits(yMin=min_magnitude, yMax=(max_magnitude_signal))
        self.originalSignalWidget.plot(t, signal, pen='g')
        self.originalSignalWidget.setLabel('left', 'Amplitude')
        self.originalSignalWidget.setLabel('bottom', 'Time (s)')
        self.originalSignalWidget.showGrid(True, True)
        self.computeFFT(signal, fs)
        self.playheadLineOriginal = pg.InfiniteLine(pos=self.playheadPosition, angle=90, movable=True, pen=pg.mkPen('r'))
        self.originalSignalWidget.addItem(self.playheadLineOriginal)

    def new_song_save(self,fs,reconstructed_signal):
        reconstructed_signal = np.real(reconstructed_signal)
        sample_rate = fs
        self.mode=self.modeComboBox.currentText()
        if self.mode == "Musical Instruments Mode":
            output_file = f'reconstructed_audio{self.file_index_music}.wav'
            self.musicTracks.append(output_file)
            self.audioListWidget.addItem(output_file)
            self.file_index_music += 1
        elif self.mode == "Animal Sounds Mode":
            output_file = f'reconstructed_audio{self.file_index_animal}.wav'
            self.animalSounds.append(output_file)
            self.audioListWidget.addItem(output_file)
            self.file_index_animal += 1

        ifft_file = np.float64(reconstructed_signal)
        sf.write(output_file, ifft_file, sample_rate)

    def updatePlayheadForMode(self):
        # Check the current mode and update the playhead for the corresponding widget
        currentMode = self.modeComboBox.currentText()

        if currentMode == "Uniform Range Mode" or currentMode=="ECG Abnormalities Mode":
            self.playSignal()

        else:
            self.playMedia()

    def plotSelectedSignal(self):
            self.slider_mode()
            selected_item = self.audioListWidget.currentItem()
            if selected_item:
                selectedFilePath = selected_item.text()

                if selectedFilePath==self.ecgSignal:
                    self.ecgFrequencyRanges[0]=[0,0]
                else :
                    self.ecgFrequencyRanges[0] = [0,12]

            self.clearWidgets()

        # Check if the selected file path is a .wav file
            if selectedFilePath.lower().endswith('.wav'):
                # Load and plot the signal from the selected .wav file
                signal, self.fs = librosa.load(selectedFilePath, sr=None)

                timeVector = np.arange(len(signal)) / self.fs
                self.plotOriginalSignal(timeVector, signal, self.fs)
            # Check if the selected file path is a .csv file
            elif selectedFilePath.lower().endswith('.csv'):
                df = pd.read_csv(selectedFilePath)
                list_of_columns = df.columns
                time = df[list_of_columns[0]].to_numpy()
                data = df[list_of_columns[1]].to_numpy()
                max_freq = (1 / (time[1] - time[0])) / 2
                sampling_frequency = 2 * max_freq
                self.plotOriginalSignal(time, data, sampling_frequency)

    def computeFFT(self, signal, fs):
        N = len(signal)
        if self.mode == "Uniform Range Mode" or self.mode == "ECG Abnormalities Mode":
            self.frequencies = np.fft.fftfreq(N, 1 / fs)
            self.fft_result = np.fft.fft(signal)
        else:
            self.frequencies = np.fft.rfftfreq(N, 1 / fs)
            self.fft_result = np.fft.rfft(signal)

        self.fft_magnitudes = np.abs(self.fft_result)
        self.phases = np.angle(self.fft_result)
        self.slider_changes = np.ones(len(self.fft_magnitudes))
        self.slider_changes_zeros = np.zeros_like(self.fft_magnitudes)
        self.plotFrequencyDomain(self.frequencies, self.fft_magnitudes)
        self.updateSpectrogram(signal, fs, 1)
    def restrictions (self,widget,xmin,xmax):
        mode = self.modeComboBox.currentText()
        if mode == "Uniform Range Mode":
          widget.plotItem.getViewBox().setLimits(xMin=xmin, xMax=xmax)
        elif mode == "Animal Sounds Mode" or '"Musical Instruments Mode"':
            widget.plotItem.getViewBox().setLimits(xMin=xmin, xMax=xmax)
        else :
            widget.plotItem.getViewBox().setLimits(xMin=xmin, xMax=xmax)
    def plotFrequencyDomain(self, frequency_components, frequency_magnitudes):
        self.frequencyWidget.clear()
        mode = self.modeComboBox.currentText()
        self.deleteButton.setEnabled(1)
        if mode == "Uniform Range Mode":
            self.restrictions( self.frequencyWidget,0,105)
            self.restrictions( self.originalSignalWidget,0,5.2)
            self.restrictions( self.outputSignalWidget,0,5.2)
        elif mode == "Animal Sounds Mode" or "Musical Instruments Mode":
            self.restrictions( self.frequencyWidget,0,23000)
            self.restrictions( self.originalSignalWidget,0,7)
            self.restrictions( self.outputSignalWidget,0,7)
            if mode ==  "Musical Instruments Mode":
                self.restrictions( self.originalSignalWidget,0,9)
                self.restrictions( self.outputSignalWidget,0,9)

        else :
            self.restrictions( self.frequencyWidget,0,205)
        min_magnitude = np.max(frequency_magnitudes)
        self.frequencyWidget.plotItem.getViewBox().setLimits(yMin=-80, yMax=(min_magnitude+100))
        self.frequencyWidget.plot(frequency_components, frequency_magnitudes, pen='b')
        self.frequencyWidget.setLabel('left', 'Magnitude')
        self.frequencyWidget.setLabel('bottom', 'Frequency (Hz)')
        self.frequencyWidget.showGrid(True, True)
        self.frequencyWidget.setYRange(0, max(frequency_magnitudes) * 1.2)
        self.reconstructSignalFromFFT()

    def reconstructSignalFromFFT(self):
        self.mode = self.modeComboBox.currentText()
        t = self.originalSignalWidget.getPlotItem().listDataItems()[0].getData()[0]
        modified_signal = self.frequencyWidget.getPlotItem().listDataItems()[0].getData()[1]
        combined_fft = modified_signal * np.exp(1j * self.phases)
        if self.mode == "Uniform Range Mode" or self.mode == "ECG Abnormalities Mode":
            self.reconstructed_signal = np.fft.ifft(combined_fft)
            if self.Normal ==len( self.reconstructed_signal):
                self.ecgFrequencyRanges[0] = [0, 0]
            else:
                self.ecgFrequencyRanges[0] = [0, 12]

        else:
            self.reconstructed_signal = np.fft.irfft(combined_fft)
        min_magnitude = np.min(self.reconstructed_signal)
        self.outputSignalWidget.plotItem.getViewBox().setLimits(yMin=min_magnitude, yMax=-(min_magnitude))
        if self.mode == "ECG Abnormalities Mode":
            max_magnitude = np.max(t)
            max_magnitude_signal = np.max(self.reconstructed_signal)
            self.outputSignalWidget.plotItem.getViewBox().setLimits(xMin=0, xMax=(max_magnitude))
            self.outputSignalWidget.plotItem.getViewBox().setLimits(yMin=min_magnitude, yMax=(max_magnitude_signal))
        self.plotReconstructedSignal(t, self.reconstructed_signal)

    def plotReconstructedSignal(self, t, reconstructed_signal):
        reconstructed_signal = np.real(reconstructed_signal)
        self.outputSignalWidget.clear()
        self.outputSignalWidget.plot(t, reconstructed_signal, pen='y')
        self.outputSignalWidget.setLabel('left', 'Amplitude')
        self.outputSignalWidget.setLabel('bottom', 'Time (s)')
        self.outputSignalWidget.showGrid(True, True)
        self.playheadLineOutput = pg.InfiniteLine(pos=self.playheadPosition, angle=90, movable=True, pen=pg.mkPen('r')) #new
        self.outputSignalWidget.addItem(self.playheadLineOutput)
        fs = (1 / (t[1] - t[0]))
        self.updateSpectrogram(reconstructed_signal, fs, 2)

    def updateSpectrogram(self, data, fs, choice):
        if choice == 2:
            self.clearLayout(self.outputSpectrogramLayout)
        else:
            self.clearLayout(self.originalSpectrogramLayout)

        fig, ax = plt.subplots()
        spec = ax.specgram(data, Fs=fs, cmap='viridis')
        cbar = fig.colorbar(spec[3], ax=ax)
        # Add the updated spectrogram to the layout
        canvas = FigureCanvas(fig)
        if choice == 2:
            self.outputSpectrogramLayout.addWidget(canvas)
        else:
            self.originalSpectrogramLayout.addWidget(canvas)

        self.toggleSpectrogramVisibility(self.spectrogramRadioButton.isChecked())

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def initiate_wave(self, index):
        if(index == 3):
            self.setVisibility(True)
            self.meanLabel.setText("Mean:")
            self.stdLabel.setText("Standard Deviation:")
            self.meanSlider.setMinimum(self.freqRangeSmoothing[0])
            self.meanSlider.setMaximum(self.freqRangeSmoothing[-1])
            self.meanSlider.setValue(np.mean(self.freqRangeSmoothing) + 1)
            self.standardDeviationSlider.setMinimum(1)
            self.standardDeviationSlider.setMaximum(30)
            self.standardDeviationSlider.setTickInterval(1)
            self.standardDeviationSlider.setValue(10)
            self.standardDeviationLCD.display(self.standardDeviationSlider.value() / 10.0)
            self.mu = self.meanSlider.value()
            self.std = self.standardDeviationSlider.value() / 10.0
        else:
            self.setVisibility(False)

        self.compose_wave(index)

    def converted(self):
        self.smoothing_window = self.smoothedSignalWidget.getPlotItem().listDataItems()[0].getData()[1]
        if self.smootherComboBox.currentIndex() != 0:  # gded
            self.frequencyWidget.plot(self.freqRangeSmoothing, self.smoothing_window * max(self.new_magnitudes),
                                      pen='r')  # gded
        self.tabWidget.setCurrentIndex(0)


    def setVisibility(self, state):
        self.meanLabel.setVisible(state)
        self.stdLabel.setVisible(state)
        self.meanSlider.setVisible(state)
        self.standardDeviationSlider.setVisible(state)
        self.meanLCD.setVisible(state)
        self.standardDeviationLCD.setVisible(state)

    def compose_wave(self, index):
        x = self.freqRangeSmoothing
        if index == 0:
            self.smoothing_window = np.ones_like(x)
        elif index == 1:
            self.smoothing_window = np.hamming(len(x))
        elif index == 2:
            self.smoothing_window = np.hanning(len(x))
        else:
            self.smoothing_window = np.exp(-(x - self.mu)**2 / (2 * self.std**2))

        self.smoothedSignalWidget.clear()
        self.smoothedSignalWidget.plot(x, self.smoothing_window, pen="g")

    def updateGaussianWindow(self):
        self.mu = self.meanSlider.value()
        self.std = self.standardDeviationSlider.value() / 10.0
        self.smoothedSignalWidget.clear()
        self.compose_wave(3)

    def setLabelImage(self, label, icon, width=55, height=18, offset_x=1, offset_y=1):
        pixmap = icon.pixmap(QSize(width, height))
        label.setPixmap(pixmap)
        label.setFixedSize(width, height)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setMode(self, indicesToHide, items):
        """
        Set mode for sliders, LCDs, and labels based on the index.

        Parameters:
        - indicesToHide (list): List of indices to hide.
        - items (list): List of icons or texts.
        """
        for index, (slider, lcd, label) in enumerate(zip(self.sliders, self.lcds, self.labels)):
            if index in indicesToHide:
                slider.hide()
                lcd.hide()
                label.hide()
                label_name = f"label_{index + 1}"
                found_label = self.findChild(QLabel, label_name)
                if found_label:
                    found_label.hide()
            else:
                slider.show()
                lcd.show()
                label.show()

                # Check if the item is an icon or text
                label.setWordWrap(True)
                if isinstance(items[index], QIcon):
                    self.setLabelImage(label, items[index])
                elif isinstance(items[index], str):
                    label.setText(items[index])
                    label.setFont(QFont("Segoe UI", 8, QFont.Bold))
                    label.setFixedSize(90,20)

    def uniformRangeMode(self):
        self.audioListWidget.clear()
        for signal in self.uniformSignals:
            self.audioListWidget.addItem(signal)
        # Show all sliders
        for i, (slider, lcd,label) in enumerate(zip(self.sliders, self.lcds,self.labels), start=1):
            slider.show()
            lcd.show()
            label_text = f"{(i - 1) * 10}-{i * 10} Hz"
            label.setText(label_text)
            label.setFixedSize(80,20)
            label.show()
            label.setWordWrap(True)

    def musicalInstrumentsMode(self):
        icons = [self.guitarIcon, self.drumsIcon, self.trumpetIcon, self.pianoIcon]
        self.audioIndices=[4,5,6,7,8,9]
        self.setMode(self.audioIndices, icons)
        self.audioListWidget.clear()
        for track in self.musicTracks:
            self.audioListWidget.addItem(track)

    def animalSoundsMode(self):
        icons = [self.elephantIcon, self.sheepIcon, self.wolfIcon, self.seaLionIcon]
        self.audioIndices=[4,5,6,7,8,9]
        self.setMode(self.audioIndices, icons)
        self.audioListWidget.clear()
        for index, sound in enumerate(self.animalSounds):
            self.audioListWidget.addItem(sound)

    def ECGAbnormalitiesMode(self):
        texts=["Arrhythmia #01", "Arrhythmia #02", "Arrhythmia #03"]
        self.indices=[3,4,5,6,7,8,9]
        self.setMode(self.indices, texts)
        self.audioListWidget.clear()

        # Font modifications for text items using HTML formatting
        for index, text in enumerate(texts):
            texts[index] = f'<font size="8" face="Segoe UI" weight="bold">{text}</font>'

        for ecgSignal in self.ecgSignals:
            self.audioListWidget.addItem(ecgSignal)

    def modeChanged(self):
        selectedMode = self.modeComboBox.currentText()
        self.slider_mode()
        # Call the corresponding method based on the selected mode
        if selectedMode == "Uniform Range Mode":
            self.uniformRangeMode()
            self.constructAudioButton.setEnabled(0)
        elif selectedMode == "Animal Sounds Mode":
            self.animalSoundsMode()
            self.constructAudioButton.setEnabled(1)
        elif selectedMode == "Musical Instruments Mode":
            self.musicalInstrumentsMode()
            self.constructAudioButton.setEnabled(1)
        elif selectedMode == "ECG Abnormalities Mode":
            self.ECGAbnormalitiesMode()
            self.constructAudioButton.setEnabled(0)

        self.clearWidgets()

    def clearWidgets(self):
        self.originalSignalWidget.clear()
        self.outputSignalWidget.clear()
        self.frequencyWidget.clear()
        for i in reversed(range(self.outputSpectrogramLayout.count())):
         self.outputSpectrogramLayout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.originalSpectrogramLayout.count())):
         self.originalSpectrogramLayout.itemAt(i).widget().setParent(None)


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
