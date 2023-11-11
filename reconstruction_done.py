# Import necessary modules
import sys  
from os import path  
import numpy as np
import pandas as pd
from PyQt6 import QtWidgets,QtGui
from PyQt6.QtWidgets import *  
from PyQt6.QtCore import *  
from PyQt6.uic import loadUiType
from PyQt6.QtGui import QIcon
import pyqtgraph as pg


FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "design3.ui"))

class MainApp(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("AudioAlchemy Equalizer")


        # Set default tab to Equalizer
        self.tabWidget.setCurrentIndex(0)
        
        # Set up icons for buttons
        self.playIcon = QtGui.QIcon("icons/playIcon.png")  
        self.pauseIcon = QtGui.QIcon("icons/pauseIcon.png")  
        self.resetIcon = QtGui.QIcon("icons/resetIcon.png")  
        self.confirmIcon = QtGui.QIcon("icons/confirmIcon.png") 
        self.zoomInIcon = QtGui.QIcon("icons/zoomInIcon.png")  
        self.zoomOutIcon = QtGui.QIcon("icons/zoomOutIcon.png")  
        self.soundIcon = QtGui.QIcon("icons/soundIcon.png")  
        self.muteIcon = QtGui.QIcon("icons/muteIcon.png")  
        # panIcon = QtGui.QIcon("icons/panIcon.png")  
        equalizerTab = QtGui.QIcon("icons/equalizerIcon.png")
        smootherTab = QtGui.QIcon("icons/smootherIcon.png")
        windowIcon = QtGui.QIcon("icons/windowIcon.png")
        
        # Set icons for tabs
        self.tabWidget.setTabIcon(0, equalizerTab)  # 0 is the index of the composerTab
        self.tabWidget.setTabIcon(1, smootherTab)   # 1 is the index of the viewerTab
        self.setWindowIcon(windowIcon)
        
        # Set icons for buttons
        self.playPauseButton.setIcon(self.pauseIcon)
        self.zoomInButton.setIcon(self.zoomInIcon)
        self.zoomOutButton.setIcon(self.zoomOutIcon)
        self.resetButton.setIcon(self.resetIcon)
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
        self.smoothedSignalWidget = pg.PlotWidget()
        self.frequencyWidget = pg.PlotWidget()
        
        self.originalSignalLayout.addWidget(self.originalSignalWidget)
        self.outputSignalLayout.addWidget(self.outputSignalWidget)
        self.originalSpectrogramLayout.addWidget(self.originalSpectrogramWidget)
        self.outputSpectrogramLayout.addWidget(self.outputSpectrogramWidget)
        self.smoothingLayout.addWidget(self.smoothedSignalWidget)
        self.frequencyLayout.addWidget(self.frequencyWidget)

        self.frequencyWidget.plotItem.getViewBox().setLimits(xMin =0, xMax= 105)
    
        # Disable panning and zooming on all plots
        # self.originalSignalWidget.setMouseEnabled(x=False, y=False)
        # self.outputSignalWidget.setMouseEnabled(x=False, y=False)
        # self.originalSpectrogramWidget.setMouseEnabled(x=False, y=False)
        # self.outputSpectrogramWidget.setMouseEnabled(x=False, y=False)
        # self.smoothedSignalWidget.setMouseEnabled(x=False, y=False)


        ##################### Sliders ##################
        self.setupSliders(10)
        
        self.speedSlider = self.findChild(QSlider, "speedSlider")
        self.speedLCD = self.findChild(QLCDNumber, "speedLCD")
        self.speedSlider.valueChanged.connect(lambda: self.speedLCD.display(self.speedSlider.value()))
        # self.speedSlider.valueChanged.connect(lambda: )
        self.speedSlider.setMinimum(0)
        self.speedSlider.setMaximum(100) 
        self.speedSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speedSlider.setTickInterval(1)  
        self.speedSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.speedSlider.setStyleSheet(self.slidersStyleHorizontal2) 

        self.meanSlider = self.findChild(QSlider, "meanSlider")
        self.meanLCD = self.findChild(QLCDNumber, "meanLCD")
        self.meanSlider.valueChanged.connect(lambda: self.meanLCD.display(self.meanSlider.value()))
        # self.meanSlider.valueChanged.connect(lambda: )
        self.meanSlider.setMinimum(0)  
        self.meanSlider.setMaximum(100)  
        self.meanSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.meanSlider.setTickInterval(1)  
        self.meanSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.meanSlider.setStyleSheet(self.slidersStyleHorizontal2)
        
        self.standardDeviationSlider = self.findChild(QSlider, "standardDeviationSlider")
        self.standardDeviationLCD = self.findChild(QLCDNumber, "standardDeviationLCD")
        self.standardDeviationSlider.valueChanged.connect(lambda: self.standardDeviationLCD.display(self.standardDeviationSlider.value()))
        # self.meanSlider.valueChanged.connect(lambda: )
        self.standardDeviationSlider.setMinimum(0)  
        self.standardDeviationSlider.setMaximum(100)  
        self.standardDeviationSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.standardDeviationSlider.setTickInterval(1) 
        self.standardDeviationSlider.setStyleSheet(self.slidersStyleHorizontal1)
        self.standardDeviationSlider.setStyleSheet(self.slidersStyleHorizontal2)
        self.confirmButton.pressed.connect(self.converted)
        ##################### Sliders ##################


        #################### Variables and data structures ####################
        self.playing = True
        self.originalSoundOn = True
        self.outputSoundOn = True
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
        self.smootherComboBox.currentIndexChanged.connect(lambda index: self.initiate_wave(index))
        #################### Smoothing Window ########################


        ############## Buttons and checkboxes connections ##############
        self.actionOpenSignal.triggered.connect(self.openFile)
        self.playPauseButton.clicked.connect(self.togglePlayPause)
        self.muteOriginalButton.clicked.connect(self.toggleMuteOriginal)
        self.muteOutputButton.clicked.connect(self.toggleMuteOutput)
        self.spectrogramRadioButton.setChecked(True)
        self.spectrogramRadioButton.toggled.connect(self.toggleSpectrogramVisibility)
        ############## Buttons and checkboxes connections ##############


    def setupSliders(self, num_sliders, option=1):
        self.sliders = []
        self.lcds = []

        for i in range(num_sliders):
            slider = self.findChild(QSlider, f"slider_{i+1}")
            lcd = self.findChild(QLCDNumber, f"lcd_{i+1}")

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
        
    def togglePlayPause(self):
        self.playing = not self.playing  

        if self.playing:
            self.playPauseButton.setIcon(self.pauseIcon)
        else:
            self.playPauseButton.setIcon(self.playIcon)

    def toggleMuteOriginal(self):
        self.originalSoundOn = not self.originalSoundOn

        if self.originalSoundOn:
            self.muteOriginalButton.setIcon(self.soundIcon)
        else:
            self.muteOriginalButton.setIcon(self.muteIcon)
            
    def toggleMuteOutput(self):
        self.outputSoundOn = not self.outputSoundOn  

        if self.outputSoundOn:
            self.muteOutputButton.setIcon(self.soundIcon)
        else:
            self.muteOutputButton.setIcon(self.muteIcon)

        self.muteOriginalButton.toggle()
        
    def toggleSpectrogramVisibility(self, checked):
        visible = checked  # Invert because radio buttons are exclusive

        # Save the current size
        originalSize = self.originalSpectrogramWidget.size()
        outputSize = self.outputSpectrogramWidget.size()

        # Set visibility
        self.originalSpectrogramWidget.setVisible(visible)
        self.outputSpectrogramWidget.setVisible(visible)

        # If becoming visible, set fixed size
        if visible:
            self.originalSpectrogramWidget.setFixedSize(originalSize)
            self.outputSpectrogramWidget.setFixedSize(outputSize)

        self.originalSpectrogramLayout.update()
        self.outputSpectrogramLayout.update()
    
    def openFile(self):
            file_name, _= QFileDialog.getOpenFileName(self, "Open Signal File", "", "Signal Files (*.csv);;All Files (*)")
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
                    # elif ext == 'wav':
                    #
                    #     ## ll voice files

    def plotOriginalSignal(self, t, signal, fs):
        self.originalSignalWidget.clear()
        self.originalSignalWidget.plot(t, signal, pen='g')
        self.originalSignalWidget.setLabel('left', 'Amplitude')
        self.originalSignalWidget.setLabel('bottom', 'Time (s)')
        self.originalSignalWidget.showGrid(True, True)
        self.computeFFT(signal, fs)

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
        self.outputSignalWidget.plot(t, reconstructed_signal, pen='r')
        self.outputSignalWidget.setLabel('left', 'Amplitude')
        self.outputSignalWidget.setLabel('bottom', 'Time (s)')
        self.outputSignalWidget.showGrid(True, True)

    def converted(self):
        self.frequencyWidget.clear()
        content = self.smoothedSignalWidget.getPlotItem().listDataItems()[0].getData()
        smooth_mag = np.fft.fft(content[1])
        smooth_mag = np.abs(smooth_mag)
        self.fft_result = self.fft_result * smooth_mag
        self.frequencyWidget.plot(self.frequencies, self.fft_result, pen=pg.mkPen('g'))
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


def main():
    app = QApplication(sys.argv) 
    window = MainApp() 
    window.show() 
    app.exec()  

if __name__ == "__main__":
    main()
