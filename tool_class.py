
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QGroupBox
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5 import QtWidgets, QtCore, QtGui
from PIL import ImageGrab
import tkinter as tk
import numpy as np
import cv2
import sys
import os
from workSheet_class import Worksheet 
if getattr(sys, 'frozen', False):
    # Running in a bundled environment
    base_path = sys._MEIPASS
else:
    # Running in a normal environment
    base_path = os.path.dirname(__file__)
    
from ai_class import AI_helper

# instance of AI helper class 
ai_helper = AI_helper()

my_sheet = Worksheet(
       SCOPE=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ],
    credentials_path=os.path.join(base_path, 'credentials.json'),
    sheet_name='Copy of Roman Rakic' 
)



class Communicate(QObject):
    """
    communication class to handle signals.
    """
    snip_saved = pyqtSignal()

class MyWindow(QMainWindow):
    """
    Main window for the snipping tool with a QLabel for dynamic instructions 
    and a button to trigger the snipping process.
    """
    def __init__(self, parent=None):
        super(MyWindow, self).__init__()
        self.win_width = 340
        self.win_height = 200
        self.setGeometry(50, 50, self.win_width, self.win_height)
        self.setWindowTitle("Snipping Tool for Programmers")
        # ------------ counter----------------
        self.snip_count = 0
        # ------------ counter---------------- 
        
       # Create QLabel for dynamic text
        self.text_label = QLabel(self)
        self.text_label.setGeometry(50, 15, 240, 50)
        self.text_label.setStyleSheet("color: black; font-size: 15px; font-weight: bold;")
        self.text_label.setWordWrap(True)
        self.update_text()  # Set initial text
        self.initUI()
        
        
    # -----------------change text dynamically ------------
    def update_text(self):
        """Update the text based on snip_count."""
        text = self.get_text_based_on_snip_count()
        self.text_label.setText(text)

    def get_text_based_on_snip_count(self):
        """Return text based on the current snip_count."""
        if self.snip_count == 0:
            return "Capture 'Median response time' and 'Median time to close' in one screenshot"
        elif self.snip_count == 1:
            return "Capture 'Conversation ratings' percentage in the screenshot"
        elif self.snip_count == 2:
            return "Capture Conversations , Closed conversations and replies sent"
        elif self.snip_count == 3:
            return "Capture Conversation tags Complexities 1 to 5"
        else:
            return "Thank you press snip  or X top close the window"
    # -----------------change text dynamically ------------

        
    def initUI(self):
        """
        Initializes UI elements (buttons and notification boxes).
        """
        # Define buttons
        self.snipButton = QPushButton(self)
        self.snipButton.setText("Snip and Save")
        self.snipButton.move(10, 75)
        self.snipButton.setFixedSize(self.win_width-20, 40)
        self.snipButton.clicked.connect(self.snip_and_save) 

        self.notificationBox = QGroupBox("Notification Box", self)
        self.notificationBox.move(10, 135)
        self.notificationBox.setFixedSize(self.win_width-20, 55)
        
        self.notificationText = QLabel(self)
        self.notificationText.move(20, 145)
        
        self.reset_notif_text()


        
    def snip_and_save(self):
        """
        Starts the snipping process. Only allows 4 snips in total.
        """
        # ---------- counter ----------
        if self.snip_count < 4:  # Limit to 4 snips
        # ---------- counter ----------
            self.snipWin = SnipWidget(self)
            self.snipWin.notification_signal.connect(self.reset_notif_text)
            self.snipWin.show()
            self.notificationText.setText("Snipping... Press ESC to quit snipping")
            self.update_notif()
        # ---------- counter ----------
        else:
            self.notificationText.setText("Snip limit reached.")
            self.update_notif() 
              
        # ---------- closing window ---------- 
            self.close()   
        

    def reset_notif_text(self):
        """
        Resets the notification text to 'Idle...'.
        """
        self.notificationText.setText("Idle...")
        self.update_notif()
        
    def update_notif(self):
        """
        Adjusts the size and position of
        the notification text label.
        """
        self.notificationText.move(20, 155)
        self.notificationText.adjustSize()

class SnipWidget(QMainWindow):
    """
    widget for capturing snips/screenshots.
    """
    notification_signal = pyqtSignal()

    def __init__(self, parent):
        super(SnipWidget, self).__init__()
        self.parent_widget = parent
        root = tk.Tk()  # Instantiates window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowTitle(' ')
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowOpacity(0.3)
        self.is_snipping = False
        self.border_enabled = False
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CrossCursor)
        )
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.c = Communicate()
        
        # -----counter -----------
        self.snip_count = parent.snip_count  
        # -----counter -----------
        
        # ----- update text -----------
        self.update_text = parent.update_text
        # ----- update text -----------
        
        self.c.snip_saved.connect(self.save_image_and_process)
         
        self.show()
        
    def save_image_and_process(self):
        """
        Saves the captured image and sends it to processes further
        (pytesseract and openAI)
        """
        image_path = './snipped_image.png'
        cv2.imwrite(image_path, self.snipped_image)

        # Process the image with the current snip count and update 
        updated_entries = ai_helper.process_image(image_path, self.snip_count)
        print("Updated entries are =", updated_entries)

        if updated_entries is None:
            # Notify user to snip again without incrementing snip_count
            self.notification_signal.emit()
            self.parent_widget.update_text()  # Use the stored parent reference
            self.parent_widget.notificationText.setText("Required keywords missing. Please snip again.")
            self.parent_widget.setStyleSheet("QMainWindow { border : 2px solid red }")
            return

        self.parent_widget.setStyleSheet("QMainWindow { border : 2px solid green }")
        # Only increment snip_count if entries are valid
        self.parent_widget.snip_count += 1 

        # Update different cells in the spreadsheet
        values_to_write = list(updated_entries.values())
        print("Values to write in save image =", values_to_write)

        # Define columns based on the current snip count
        if self.snip_count == 0:
            my_sheet.update_date()
            my_columns = ['B', 'C']

        elif self.snip_count == 1:
            my_columns = ['G']

        elif self.snip_count == 2:
            my_columns = ['D', 'E', 'F']

        elif self.snip_count == 3:
            my_columns = ['H', 'I', 'J', 'K', 'L']

        my_sheet.find_empty_cells_and_write_values(my_sheet.worksheet, my_columns, values_to_write)
        self.parent_widget.update_text()  # Update the displayed text
   
        

    def paintEvent(self, event):
        """
        paint event to draw the snipping rectangle on the screen.
        """

        if self.is_snipping:
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0
        else:
            brush_color = (128, 128, 255, 128)
            lw = 3
            opacity = 0.3

        self.setWindowOpacity(opacity)
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), lw))
        qp.setBrush(QtGui.QColor(*brush_color))
        qp.drawRect(QtCore.QRect(self.begin, self.end))
        

        

    def keyPressEvent(self, event):

        if event.key() == QtCore.Qt.Key_Escape:
            print('Quit')
            QtWidgets.QApplication.restoreOverrideCursor()
            self.notification_signal.emit()
            self.close()
        event.accept()

    def mousePressEvent(self, event):
        """
        Capture the starting point of the snip
        when the mouse is pressed.
        """
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        """
        Update the snip area as the mouse moves.
        """
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        """
        Complete the snip when the mouse button is released.
        """
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        self.is_snipping = True        
        self.repaint()
        QtWidgets.QApplication.processEvents()
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        self.is_snipping = False
        self.repaint()
        QtWidgets.QApplication.processEvents()
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        self.snipped_image = img
        QtWidgets.QApplication.restoreOverrideCursor()
        self.c.snip_saved.emit()
        self.close()

def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())

window()

