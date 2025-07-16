from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QPalette, QMovie
from PyQt5.QtWidgets import QLabel, QSizePolicy, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QDialog, QVBoxLayout, QProgressBar
from gif2ASCII import process_frames, convert_to_ascii, convert_to_img, save_as_gif


class QImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.scaleFactor = 0.0

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)


        self.setCentralWidget(self.imageLabel)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("GIF to ASCII Converter")
        self.resize(800, 600)

    def open(self):
        options = QFileDialog.Options()
        # fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        self.fileName, _ = QFileDialog.getOpenFileName(self, 'select image', '',
                                                  'Images (*.gif)', options=options)
        if self.fileName:
            if self.fileName.endswith('.gif'):
                movie = QMovie(self.fileName)
                self.imageLabel.setMovie(movie)
                movie.start()
                gif_size = movie.currentImage().size()
                self.resize(gif_size.width(),gif_size.height())
            else:
                QMessageBox.information(self, "Image Viewer", "Cannot load %s. Only GIF files are supported" % self.fileName)
                return

                
            self.scaleFactor = 1.0
            self.updateActions()


    def convert_to_gif(self):
        options = QFileDialog.Options
        fileName_out, _ = QFileDialog.getSaveFileName(self, "Save Image", '',"GIF Files (*.gif)")
        if not fileName_out:
            return
        
        if not fileName_out.lower().endswith('.gif'):
            fileName_out += '.gif'
        
        self.progress_dialog = QDialog(self)
        self.progress_dialog.setWindowTitle("Converting")
        layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0,100)
        layout.addWidget(self.progress_bar)
        self.progress_dialog.setLayout(layout)
        self.progress_dialog.setModal(True)

        self.worker = ConversionWorker(self.fileName, fileName_out)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.worker.progress_changed.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.progress_dialog.accept)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.started.connect(self.worker.run)
        self.thread.start()
        
        self.progress_dialog.exec_()

        movie = QMovie(fileName_out)
        self.imageLabel.setMovie(movie)
        movie.start()
        gif_size = movie.currentImage().size()
        self.resize(gif_size.width(),gif_size.height())


    def about(self):
        QMessageBox.about(self, "About GIF2ASCII Converter",
                          "<p> <b>Benjamin Nichols (2025)</b> </p>"
                          "<p>Convert any gif to ASCII art. Contributions Welcome!</p>"
                          )

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.aboutAct = QAction("&About", self, triggered=self.about)
        self.convert_to_gifAct = QAction("Convert to &GIF", self, shortcut="Ctrl+G", enabled=False, triggered = self.convert_to_gif)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.convert_to_gifAct)


        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.convert_to_gifAct.setEnabled(self.fileName.endswith(".gif"))






class ConversionWorker(QObject):
    progress_changed = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, file_name, output_name):
        super().__init__()
        self.file_name = file_name
        self.output_name = output_name
    
    def run(self):
        frames, ms_per_frame = process_frames(self.file_name)
        total = len(frames)
        processed = 0

        text_frames = []
        for frame in frames:
            text_frame = convert_to_ascii([frame])[0]
            text_frames.append(text_frame)
            processed += 1
            percent = int((processed/total) * 80)
            self.progress_changed.emit(percent)

        self.progress_changed.emit(90)
        gif_frames = convert_to_img(text_frames)
        save_as_gif(gif_frames,ms_per_frame, self.output_name)
        self.progress_changed.emit(100)

        self.finished.emit()




if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    imageViewer = QImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())