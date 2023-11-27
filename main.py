# Import necessary modules
import time
import sys  
import os
from os import path  
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtMultimedia
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer  # Updated line
from PyQt5.QtWidgets import *  
from PyQt5.QtCore import *  
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from pydub import AudioSegment
from pydub.playback import play


FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "design.ui"))

class MainApp(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("AudioAlchemy Equalizer")
        self.originalSpectrogramWidget.setVisible(1)
        self.outputSpectrogramWidget.setVisible(1)
        self.spectrogramRadioButton.setChecked(True)
        self.stopButton.setEnabled(0)
        self.horizontalLayout_67.setEnabled(False)


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
        # panIcon = QtGui.QIcon("icons/panIcon.png")  
        equalizerTab = QtGui.QIcon("icons/equalizerIcon.png")
        smootherTab = QtGui.QIcon("icons/smootherIcon.png")
        windowIcon = QtGui.QIcon("icons/windowIcon.png")
        self.elephantIcon = QtGui.QIcon("icons/elephantIcon.png")  
        self.sheepIcon = QtGui.QIcon("icons/sheepIcon.png") 
        self.wolfIcon = QtGui.QIcon("icons/wolfIcon.png")  
        self.tigerIcon = QtGui.QIcon("icons/tigerIcon.png")  
        self.seaLionIcon = QtGui.QIcon("icons/seaLionIcon.png")
        self.guitarIcon = QtGui.QIcon("icons/guitarIcon.png") 
        self.drumsIcon = QtGui.QIcon("icons/drumsIcon.png")  
        self.trumpetIcon = QtGui.QIcon("icons/trumpetIcon.png")  
        self.pianoIcon = QtGui.QIcon("icons/pianoIcon.png")
        
        # Set icons for tabs
        self.tabWidget.setTabIcon(0, equalizerTab)  # 0 is the index of the composerTab
        self.tabWidget.setTabIcon(1, smootherTab)   # 1 is the index of the viewerTab
        self.setWindowIcon(windowIcon)
        
        # Set icons for buttons
        self.playPauseButton.setIcon(self.playIcon)
        self.stopButton.setIcon(self.stopIcon)
        self.zoomInButton.setIcon(self.zoomInIcon)
        self.zoomOutButton.setIcon(self.zoomOutIcon)
        self.replayButton.setIcon(self.replayIcon)
        self.confirmButton.setIcon(self.confirmIcon)
        self.muteOriginalButton.setIcon(self.soundIcon)
        self.muteOutputButton.setIcon(self.soundIcon)
        # self.panButton.setIcon(panIcon)
        
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
        self.originalSpectrogramLayout.addWidget(self.originalSpectrogramWidget)
        self.outputSpectrogramLayout.addWidget(self.outputSpectrogramWidget)
        self.frequencyLayout.addWidget(self.frequencyWidget)
        self.smoothingLayout.addWidget(self.smoothedSignalWidget)

        self.frequencyWidget.plotItem.getViewBox().setLimits(xMin =0, xMax= 105)
        # Disable panning and zooming on all plots
        self.originalSignalWidget.setMouseEnabled(x=False, y=False)
        self.outputSignalWidget.setMouseEnabled(x=False, y=False)
        self.originalSpectrogramWidget.setMouseEnabled(x=False, y=False)
        self.outputSpectrogramWidget.setMouseEnabled(x=False, y=False)
        self.frequencyWidget.setMouseEnabled(x=False, y=False)
        self.smoothedSignalWidget.setMouseEnabled(x=False, y=False) 
        

        ##################### Sliders ##################
        self.setupSliders(10)
        
        self.speedSlider = self.findChild(QSlider, "speedSlider")
        self.speedLCD = self.findChild(QLCDNumber, "speedLCD")
        self.speedSlider.valueChanged.connect(lambda: self.speedLCD.display(self.speedSlider.value()))
        # self.speedSlider.valueChanged.connect(lambda: )
        self.speedSlider.setMinimum(1)
        self.speedSlider.setMaximum(100) 
        self.speedSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speedSlider.setTickInterval(1)  
        self.speedSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.speedSlider.setStyleSheet(self.slidersStyleHorizontal2) 

        self.meanSlider = self.findChild(QSlider, "meanSlider")
        self.meanLCD = self.findChild(QLCDNumber, "meanLCD")
        self.meanSlider.valueChanged.connect(lambda: self.meanLCD.display(self.meanSlider.value()))
        self.meanSlider.valueChanged.connect(self.updateGraphs)
        self.meanSlider.setMinimum(0)  
        self.meanSlider.setMaximum(100)  
        self.meanSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.meanSlider.setTickInterval(1)  
        self.meanSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.meanSlider.setStyleSheet(self.slidersStyleHorizontal2)
        
        self.standardDeviationSlider = self.findChild(QSlider, "standardDeviationSlider")
        self.standardDeviationLCD = self.findChild(QLCDNumber, "standardDeviationLCD")
        self.standardDeviationSlider.valueChanged.connect(lambda: self.standardDeviationLCD.display(self.standardDeviationSlider.value()))
        self.standardDeviationSlider.valueChanged.connect(self.updateGraphs)
        self.standardDeviationSlider.setMinimum(0)  
        self.standardDeviationSlider.setMaximum(100)  
        self.standardDeviationSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.standardDeviationSlider.setTickInterval(1) 
        self.standardDeviationSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.standardDeviationSlider.setStyleSheet(self.slidersStyleHorizontal2)
        
        self.originalTimer=QTimer(self)
        self.originalTimer.start(1000)
        self.originalTimer.timeout.connect(self.originalMediaProgress)
        self.originalProgressSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.originalProgressSlider.setStyleSheet(self.slidersStyleHorizontal2)
        
        self.outputProgressSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.outputProgressSlider.setStyleSheet(self.slidersStyleHorizontal2)
        
        ##################### Sliders ##################


        #################### Variables and data structures ####################
        self.playing = False
        self.originalSoundOn = True
        self.outputSoundOn = True
        self.fft_result = None
        self.playheadPosition = 0 
        self.elapsedTime = 0 
        self.originalSignalDuration = 0 
        self.outputSignalDuration = 0 
        self.uniformSignals = []#new
        self.animalSounds = [] #new
        self.musicTracks = []#new
        self.ecgSignals = []#new
        self.currentVolume = 50#new
        self.mediaDuration = 0 
        self.mediaPausePosition = 0
        self.playheadLineOriginal=0
        self.playheadLineOutput=0

        # global stopped
        # stopped = False
        
        #################### Variables and data structures ####################

        #################### Smoothing Window ########################
        self.start = -0.001
        self.end = 1
        self.t = np.linspace(self.start, self.end, 1000)
        self.A = 1.0
        self.f = 1.0
        self.mu = 0.0
        self.sigma = 0.4
        self.smootherComboBox.setCurrentIndex(self.smootherComboBox.findText("Rectangle"))
        self.initiate_wave(0)
        self.compose_wave(0, self.t, self.A, self.f, self.mu, self.sigma)
        #################### Smoothing Window ########################


        ############## Buttons and checkboxes connections ##############
        self.actionOpenUniformSignal.triggered.connect(self.openUniformSignal)
        self.actionOpenAnimalSounds.triggered.connect(self.openAnimalSounds) #new
        self.actionOpenInstrumentsSounds.triggered.connect(self.openInstrumentsSounds) #new
        self.actionOpenECGSignal.triggered.connect(self.openMedicalSignal) #new
        self.playPauseButton.clicked.connect(self.playPauseToggling)
        self.muteOriginalButton.clicked.connect(self.toggleMuteOriginal)
        self.muteOutputButton.clicked.connect(self.toggleMuteOutput)
        self.spectrogramRadioButton.toggled.connect(self.toggleSpectrogramVisibility)
        self.modeComboBox.currentIndexChanged.connect(self.modeChanged)
        # self.modeComboBox.currentIndexChanged.connect(self.playMedia)
        self.smootherComboBox.currentIndexChanged.connect(lambda index: self.initiate_wave(index))
        self.changeWindowButton.clicked.connect(lambda _ : self.tabWidget.setCurrentIndex(1))
        self.confirmButton.pressed.connect(self.converted)
        self.playheadUpdateTimer = QTimer(self)
        self.playheadUpdateTimer.timeout.connect(self.updatePlayheadPosition)
        self.speedSlider.valueChanged.connect(lambda: self.updatePlayheadSpeed(self.speedSlider.value()))
        self.playheadUpdateInterval = 1
        self.replayButton.clicked.connect(self.replayToggle)
        self.mediaPlayer=QtMultimedia.QMediaPlayer()#new
        self.mediaPlayer.setVolume(self.currentVolume)#new
        self.mediaPlayer.pause()
        self.originalProgressSlider.sliderMoved[int].connect(lambda: self.mediaPlayer.setPosition(self.originalProgressSlider.value()))
        self.originalVolumeSpinBox.valueChanged[int].connect(lambda : self.originalVolumeChange())
        self.stopButton.clicked.connect(self.stopMedia)
        self.replayButton.clicked.connect(self.replayMedia)

        ############## Buttons and checkboxes connections ##############

    


    def openUniformSignal(self): #done
            file_name, _= QFileDialog.getOpenFileName(self, "Open Uniform Signal File", "", "Signal Files (*.csv);;All Files (*)")
            self.audioListWidget.clear() 
            self.clearWidgets()
            if file_name:
                    ext = file_name.split(".")[-1]
                    if ext == 'csv':
                        df = pd.read_csv(file_name)
                        list_of_columns = df.columns
                        time = df[list_of_columns[0]].to_numpy()
                        data = df[list_of_columns[1]].to_numpy()
                        max_freq = (1 / (time[1] - time[0])) / 2 
                        sampling_frequency = 2 * max_freq
                        self.plotOriginalSignal(time, data, sampling_frequency)
                        self.uniformSignals.append(file_name)
            self.modeComboBox.setCurrentText("Uniform Range Mode")
                    
    def openAnimalSounds(self): #done
        files, _ = QFileDialog.getOpenFileNames(
            self, caption='Add Animal Sounds',
            directory='://', filter="Supported Files (*.mp3;*.m4a;*.wma;*.mpeg;*.ogg;*.MP3)"
        )
        # Print the files obtained from the dialog
        # print("Files obtained:", files)
        
        self.audioListWidget.clear()
        self.clearWidgets()        
        if files:
            for file in files:
                self.animalSounds.append(file)

        self.modeComboBox.setCurrentText("Animal Sounds Mode")
        # Print the contents of self.animalSounds after adding items
        # print("Animal Sounds after adding to animalSounds list:", self.animalSounds)
                
    def openInstrumentsSounds(self): #done
        files,_=QFileDialog.getOpenFileNames(
            self,caption='Add Music Tracks',
            directory='://', filter="Supported Files (*.mp3;*.m4a;*.wma;*.mpeg;*.ogg;*.MP3)"
        )
        self.audioListWidget.clear() 
        self.clearWidgets()
        self.modeComboBox.setCurrentText("Musical Instruments Mode")
        if files:
            for file in files:
                self.musicTracks.append(file)

    def openMedicalSignal(self): #done
        files,_=QFileDialog.getOpenFileNames(
            self,caption='Add Medical Signals',
            directory='://', filter="Supported Files (*.csv);;All Files (*)"
        )
        self.audioListWidget.clear() 
        self.clearWidgets()
        if files:
            for file in files:
                self.ecgSignals.append(file)
        self.modeComboBox.setCurrentText("ECG Abnormalities Mode")
        
    def playMedia(self):
        try:
            self.currentSelection=self.audioListWidget.currentRow()
            self.mode=self.modeComboBox.currentText()
            if self.mode=="Uniform Range Mode":
                self.currentSound=self.uniformSignals[self.currentSelection]
            elif self.mode=="Animal Sounds Mode":
                self.currentSound=self.animalSounds[self.currentSelection]
            elif self.mode=="Musical Instruments Mode":
                self.currentSound=self.musicTracks[self.currentSelection]
            else:
                self.clearWidgets() #nooo
            
            if self.originalProgressSlider.value()==0 :
                
                mediaURL=QMediaContent(QUrl.fromLocalFile(self.currentSound))
                self.mediaPlayer.setMedia(mediaURL)
                self.originalMediaProgress()
                print("yarab la2")


            
            if self.stopButton.isEnabled():
                print("wahed")
                self.mediaPlayer.pause()
                self.stopButton.setEnabled(0)
                self.playPauseButton.setIcon(self.playIcon)
            else :
                print("etnen")
                self.mediaPlayer.setPosition(self.originalProgressSlider.value())
                self.mediaPlayer.play()
                self.stopButton.setEnabled(1)
                self.playPauseButton.setIcon(self.pauseIcon)
            
        except Exception as e:
            print(f"Play media error: {e}")            

    def setupSliders(self, num_sliders, option=1):
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
            slider.valueChanged.connect(lambda value, idx=i: self.sliderValueChanged(idx, value, num_sliders))
            slider.valueChanged.connect(lambda value, lcd=lcd: lcd.display(value))
            self.sliders.append(slider)
            self.lcds.append(lcd)
            self.labels.append(label)

    def sliderValueChanged(self, slider_idx, value, num_sliders, option=1):
        frequency_step =  (len(self.frequencies) / 2) // num_sliders

        if(slider_idx == 9):
                min_frequency = slider_idx * frequency_step
                max_frequency = ((slider_idx + 1) * frequency_step) + 2
        else:
                min_frequency = slider_idx * frequency_step
                max_frequency = (slider_idx + 1) * frequency_step

        min_idx = int(min_frequency)
        max_idx = int(max_frequency)
        self.slider_changes[min_idx:max_idx] = value
        new_magnitudes = self.fft_result * self.slider_changes

        self.frequencyWidget.clear()
        self.frequencyWidget.plot(self.frequencies, new_magnitudes, pen=pg.mkPen('b'))
        self.reconstructSignalFromFFT()    
             
    def playPauseToggling(self):
        mode=self.modeComboBox.currentText()
        if mode=="Uniform Range Mode":
            self.playSignal()
        else:
            self.playMedia()
         
    def playSignal(self):
        self.playing = not self.playing  
        
        if self.playing:
            self.playPauseButton.setIcon(self.pauseIcon)
            self.stopButton.setEnabled(1)
            self.playheadUpdateTimer.start(self.playheadUpdateInterval)
        
        else:
            self.stopButton.setEnabled(0)
            self.playPauseButton.setIcon(self.playIcon)
          
    def stopMedia(self):
        if self.stopButton.isEnabled():
            self.mediaPlayer.stop()
            self.playPauseButton.setIcon(self.playIcon)
            self.stopButton.setEnabled(0)
            self.originalProgressSlider.setValue(0)
            self.outputProgressSlider.setValue(0)
            self.originalStartLabel.setText(f"0:00 /")  
            self.outputStartLabel.setText(f"0:00 /")
            self.originalEndLabel.setText(f"0:00")  
            self.outputEndLabel.setText(f"0:00") 
            
    def replayMedia(self):
        self.mediaPlayer.play()
        self.playPauseButton.setIcon(self.pauseIcon)
        self.stopButton.setEnabled(1)
        self.originalProgressSlider.setValue(0)
        self.outputProgressSlider.setValue(0)
        self.originalStartLabel.setText(f"0:00 /")  
        self.outputStartLabel.setText(f"0:00 /")
        self.originalEndLabel.setText(f"{self.mediaDuration}")  
        self.outputEndLabel.setText(f"0:00") 

    def replayToggle(self):
        self.elapsedTime = 0
        # Reset the playhead position to the beginning
        self.playheadLineOriginal.setPos(self.elapsedTime)
        self.playheadLineOutput.setPos(self.elapsedTime)
    
    def updatePlayheadSpeed(self, speed):
        self.playheadUpdateInterval = speed  
        # Update the playhead update interval for the QTimer
        self.playheadUpdateTimer.setInterval(self.playheadUpdateInterval)
       
    def updatePlayheadPosition(self):
        if self.playing:
            # Update the elapsed time based on the playhead update interval
            self.elapsedTime += self.playheadUpdateInterval / 1000.0  # Convert milliseconds to seconds
            
            if self.elapsedTime > self.originalSignalDuration:
                        self.elapsedTime = self.originalSignalDuration
                        self.playing = False  # Stop playing when the end is reached
                        self.playPauseButton.setIcon(self.playIcon)
                        
                        self.replayToggle()

            # Update the position of the playhead line directly
            self.playheadLineOriginal.setPos(self.elapsedTime) 
            self.playheadLineOutput.setPos(self.elapsedTime) 
    
    def originalMediaProgress(self):
        if self.mediaPlayer.state()==QMediaPlayer.PausedState:
            return
        else:
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
            self.mediaPlayer.setMuted(True)  # Mute
       
    def toggleMuteOutput(self):
        self.outputSoundOn = not self.outputSoundOn  

        if self.outputSoundOn:
            self.muteOutputButton.setIcon(self.soundIcon)
        else:
            self.muteOutputButton.setIcon(self.muteIcon)

        self.muteOriginalButton.toggle()
        
    def toggleSpectrogramVisibility(self, checked):
        originalSize = self.originalSpectrogramWidget.size()
        outputSize = self.outputSpectrogramWidget.size()

        self.originalSpectrogramWidget.setVisible(checked)
        self.outputSpectrogramWidget.setVisible(checked)

        if checked:
            self.originalSpectrogramWidget.setFixedSize(originalSize)
            self.outputSpectrogramWidget.setFixedSize(outputSize)

    def plotOriginalSignal(self, t, signal, fs):
        self.originalSignalWidget.clear()
        self.originalSignalDuration = t[-1] - t[0]
        self.originalSignalWidget.plot(t, signal, pen='g')
        self.originalSignalWidget.setLabel('left', 'Amplitude')
        self.originalSignalWidget.setLabel('bottom', 'Time (s)')
        self.originalSignalWidget.showGrid(True, True)
        self.computeFFT(signal, fs)
        self.playheadLineOriginal = pg.InfiniteLine(pos=self.playheadPosition, angle=90, movable=True, pen=pg.mkPen('r'))
        self.originalSignalWidget.addItem(self.playheadLineOriginal)

    def computeFFT(self, signal, fs, option=1):
        N = len(signal)
        self.frequencies = np.fft.fftfreq(N, 1 / fs)
        self.fft_result = np.fft.fft(signal)
        self.fft_result = np.abs(self.fft_result)
        if option == 1:
            # self.frequencies = self.frequencies[:len(self.frequencies) // 2]
            # self.fft_result = self.fft_result[:len(self.frequencies) ]
            self.slider_changes = np.ones(len(self.fft_result))
            
        self.plotFrequencyDomain(self.frequencies, self.fft_result)

    def plotFrequencyDomain(self, frequency_components, frequency_magnitudes):
        self.frequencyWidget.clear()
        self.frequencyWidget.plot(frequency_components, frequency_magnitudes, pen='b')
        self.frequencyWidget.setLabel('left', 'Magnitude')
        self.frequencyWidget.setLabel('bottom', 'Frequency (Hz)')
        self.frequencyWidget.showGrid(True, True)
        self.frequencyWidget.setYRange(0, max(frequency_magnitudes) * 1.2)
        self.reconstructSignalFromFFT()
        
    def reconstructSignalFromFFT(self):
        t = self.originalSignalWidget.getPlotItem().listDataItems()[0].getData()[0]
        modified_signal = self.frequencyWidget.getPlotItem().listDataItems()[0].getData()[1]
        reconstructed_signal = np.fft.ifft(modified_signal)
        self.plotReconstructedSignal(t, reconstructed_signal)

    def plotReconstructedSignal(self, t, reconstructed_signal):
        reconstructed_signal = np.real(reconstructed_signal)
        self.outputSignalWidget.clear()
        # self.outputSignalDuration = t[-1] - t[0]
        self.outputSignalWidget.plot(t, reconstructed_signal, pen='y')
        self.outputSignalWidget.setLabel('left', 'Amplitude')
        self.outputSignalWidget.setLabel('bottom', 'Time (s)')
        self.outputSignalWidget.showGrid(True, True)
        self.playheadLineOutput = pg.InfiniteLine(pos=self.playheadPosition, angle=90, movable=True, pen=pg.mkPen('r')) #new 
        self.outputSignalWidget.addItem(self.playheadLineOutput) #new

    def converted(self):
        self.frequencyWidget.clear()
        content = self.smoothedSignalWidget.getPlotItem().listDataItems()[0].getData()
        smooth_mag = np.fft.fft(content[1])
        smooth_mag = np.abs(smooth_mag)
        self.fft_result = self.fft_result * smooth_mag
        self.frequencyWidget.plot(self.frequencies, self.fft_result, pen=pg.mkPen('b'))
        self.tabWidget.setCurrentIndex(0)

    def initiate_wave(self, index):
        self.meanLabel.setText("Amplitude:" if index in {0, 1, 2} else "Mean:")
        self.stdLabel.setText("Frequency:" if index in {0, 1, 2} else "Standard Deviation:")
        self.meanSlider.setValue(1)
        
        if index in {0, 1, 2}:
            self.standardDeviationSlider.setMinimum(1)
            self.standardDeviationSlider.setMaximum(100)
            self.standardDeviationSlider.valueChanged.connect(lambda: self.standardDeviationLCD.display(self.standardDeviationSlider.value()))
            self.standardDeviationSlider.setValue(1)
            self.standardDeviationSlider.valueChanged.connect(lambda: self.standardDeviationLCD.display(self.standardDeviationSlider.value()))
            self.standardDeviationSlider.setValue(1)
        else:
            self.standardDeviationSlider.setMinimum(0)
            self.standardDeviationSlider.setMaximum(200)
            self.standardDeviationSlider.setTickInterval(1)
            self.standardDeviationSlider.setValue(4)
            self.standardDeviationLCD.display(self.standardDeviationSlider.value() / 10.0)
            self.standardDeviationSlider.valueChanged.connect(lambda: self.standardDeviationLCD.display(self.standardDeviationSlider.value() / 10.0))

    def compose_wave(self, index, t, A, f, mu, sigma):
        omega = 2 * np.pi * f
        if index == 0:
            y = A * np.sign(np.sin(omega * t))
        elif index == 1:
            y = A * (0.54 - 0.46 * np.cos(omega * t))
        elif index == 2:
            y = A * 0.5 * (1 - np.cos(2 * np.pi * (t * (f))))
        else:
            y = A / (sigma * (2 * np.pi) ** .5) * np.exp(-(t - mu) ** 2 / (2 * sigma ** 2))
        self.smoothedSignalWidget.clear()
        self.smoothedSignalWidget.plot(t, y)

    def updateGraphs(self):
        index = self.smootherComboBox.currentIndex()
        A = self.meanSlider.value()
        f = self.standardDeviationSlider.value()
        if index in {0, 1, 2}:
            t = np.linspace(self.start, self.end, len(self.fft_result))
            self.smoothedSignalWidget.clear()
            self.compose_wave(index, t, A, f, self.mu, self.sigma)
        else:
            mu = self.meanSlider.value()
            sigma = self.standardDeviationSlider.value() / 10.0
            start = mu - 1
            end = mu + 1
            t = np.linspace(start, end, len(self.fft_result))
            self.smoothedSignalWidget.clear()
            self.compose_wave(index, t, A, f, mu, sigma)
            
    def setLabelImage(self, label, icon, width=55, height=18, offset_x=1, offset_y=1):
        pixmap = icon.pixmap(QSize(width, height))
        label.setPixmap(pixmap)
        label.setFixedSize(width, height)  # Set the fixed size for the label
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align the label to the right

    def setMode(self, indicesToHide, icons): #needs adjustments
        # Save the original size policies of the sliders, LCDs, and labels
        original_size_policies = []

        # Iterate through the sliders, LCDs, and labels to hide/show them based on the index
        for index, (slider, lcd,label) in enumerate(zip(self.sliders, self.lcds,self.labels)):
            original_size_policies.append(((slider.sizePolicy().horizontalPolicy(), slider.sizePolicy().verticalPolicy()),
                                        (lcd.sizePolicy().horizontalPolicy(), lcd.sizePolicy().verticalPolicy())))

            # Check if the current index should be hidden
            if index in indicesToHide:
                slider.hide()
                lcd.hide()
                label.hide()
                # Find the corresponding label and hide it
                label_name = f"label_{index + 1}"
                label = self.findChild(QLabel, label_name)
                if label:
                    label.hide()
            else:
                slider.show()
                lcd.show()

        # Set images for specific labels
        self.setLabelImage(self.label_1, icons[0])
        self.setLabelImage(self.label_4, icons[1])
        self.setLabelImage(self.label_7, icons[2])
        self.setLabelImage(self.label_10, icons[3])

        # You might also want to adjust the layout after hiding/showing the sliders and LCDs
        # self.updateGeometry()

    def uniformRangeMode(self): #not sure yet
        frequency_range = 10

        # Show all sliders
        for i, (slider, lcd,label) in enumerate(zip(self.sliders, self.lcds,self.labels), start=1):
            slider.show()
            lcd.show()
            label_text = f"{(i - 1) * frequency_range}-{i * frequency_range} Hz"
            label.setText(label_text)
            label.setFixedSize(61,20)
            label.show()
        self.audioListWidget.clear()
        for signal in self.uniformSignals:
            item = QListWidgetItem(signal)
            self.audioListWidget.addItem(item)
            
    def musicalInstrumentsMode(self): #done
        # List of indices to hide
        indicesToHide = [1, 2, 4, 5, 7, 8]
        # Icons for musical instruments mode
        icons = [self.guitarIcon, self.drumsIcon, self.trumpetIcon, self.pianoIcon]
        self.setMode(indicesToHide, icons)
        
        self.audioListWidget.clear()
        for track in self.musicTracks:
            self.audioListWidget.addItem(track)

    def animalSoundsMode(self): #done
        # List of indices to hide
        indicesToHide = [1, 2, 4, 5, 7, 8]
        # Icons for animal sounds mode
        icons = [self.elephantIcon, self.sheepIcon, self.wolfIcon, self.seaLionIcon]
        self.setMode(indicesToHide, icons)

        # # Print the contents of self.animalSounds before adding items
        # print("Animal Sounds before adding to audioListWidget:", self.animalSounds)
        # # Print the contents of audioListWidget before adding items
        # print("audioListWidget content before adding items:", [self.audioListWidget.item(i).text() for i in range(self.audioListWidget.count())])

        self.audioListWidget.clear()
        for index, sound in enumerate(self.animalSounds):
            self.audioListWidget.addItem(sound)
            # print(f"Added sound at index {index}: {sound}")

        # # Print the contents of audioListWidget after adding items
        # print("audioListWidget content after adding items:", [self.audioListWidget.item(i).text() for i in range(self.audioListWidget.count())])
        # # Print the contents of self.animalSounds after adding items
        # print("Animal Sounds after adding to audioListWidget:", self.animalSounds)

    def ECGAbnormalitiesMode(self): #missing
        print("ahh yany")

    def modeChanged(self): #done
        # Handle mode changes here
        selectedMode = self.modeComboBox.currentText()
        print(f"Selected mode: {selectedMode}")

        # Call the corresponding method based on the selected mode
        if selectedMode == "Uniform Range Mode":
            self.uniformRangeMode()
        elif selectedMode == "Animal Sounds Mode":
            self.clearWidgets()
            self.animalSoundsMode()
        elif selectedMode == "Musical Instruments Mode":
            self.clearWidgets()
            self.musicalInstrumentsMode()
        elif selectedMode == "ECG Abnormalities Mode":
            self.clearWidgets()
            self.ECGAbnormalitiesMode()
            
    def clearWidgets(self): #done
        self.originalSignalWidget.clear()
        self.outputSignalWidget.clear()
        self.frequencyWidget.clear()


# ------------------------------Trials------------------------------------------------------------
    # def extractSignal(self): 
    #         # Function to load an MP3 file and plot the signal on originalSignalWidget
    #         mp3_file_path = r'C:\Raghda\dsp\task3\animalsSounds\seaLionSound.mp3'

    #         # Set the PYDUB_FFPROBE environment variable
    #         os.environ["PYDUB_FFPROBE"] = r'C:\Program Files (x86)\ffmpeg-6.0.1\fftools\ffprobe.exe'

    #         # Load the MP3 file using pydub
    #         audio = AudioSegment.from_mp3(mp3_file_path)

    #         # Convert the audio to NumPy array
    #         signal = np.array(audio.get_array_of_samples())

    #         # Calculate time vector based on sample rate
    #         t = np.linspace(0, len(signal) / audio.frame_rate, len(signal))

    #         # Plot the signal on originalSignalWidget
    #         self.plotOriginalSignal(t, signal, audio.frame_rate)

    #         # Play the audio (optional)
    #         play(audio)
    
# ------------------------------Trials------------------------------------------------------------


def main():
    app = QApplication(sys.argv) 
    window = MainApp() 
    window.show() 
    app.exec()  

if __name__ == "__main__":
    main()


