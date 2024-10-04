from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QGroupBox
from PyQt5.QtCore import pyqtSignal, QObject,Qt
from PyQt5 import QtWidgets, QtCore, QtGui
from unittest import mock
from unittest.mock import patch, MagicMock
import pytest
import warnings
import tkinter as tk




# Suppress all warnings in tests
warnings.filterwarnings("ignore")

class CommunicateTest(QObject):
    snip_saved = pyqtSignal()

class MyWindowTest(QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(MyWindowTest, self).__init__(*args, **kwargs)
        self.win_width = 340
        self.win_height = 200
        self.setGeometry(50, 50, self.win_width, self.win_height)
        self.setWindowTitle("Test Title")
        self.snip_count = 0

           
       # Create QLabel for dynamic text
        self.text_label = QLabel(self)
        self.text_label.setGeometry(50, 15, 240, 50)
        self.text_label.setStyleSheet("color: black; font-size: 15px; font-weight: bold;")
        self.text_label.setWordWrap(True)
        self.update_text()  # Set initial text
        self.initUI()
        
    def update_text(self):
        """Update the text based on snip_count."""
        text = self.get_text_based_on_snip_count()
        self.text_label.setText(text)
        
    def get_text_based_on_snip_count(self):
        """Return text based on the current snip_count."""
        if self.snip_count == 0:
            return "Capture Test 0"
        elif self.snip_count == 1:
            return "Capture Test 1"
        elif self.snip_count == 2:
            return "Capture Test 2"
        elif self.snip_count == 3:
            return "Capture Test 3"
        else:
            return "Capture the next set of values"
        
        
    def initUI(self):
        # Define buttons
        self.snipButton = QPushButton(self)
        self.snipButton.setText("Test text")
        self.snipButton.move(10, 75)
        self.snipButton.setFixedSize(self.win_width-20, 40)
        self.snipButton.clicked.connect(self.snip_and_save) 

        self.notificationBox = QGroupBox("Test Box", self)
        self.notificationBox.move(10, 135)
        self.notificationBox.setFixedSize(self.win_width-20, 55)
        
        self.notificationText = QLabel(self)
        self.notificationText.move(20, 145)
        self.reset_notif_text()
        
    def reset_notif_text(self):
        self.notificationText.setText("Idle...")
        self.update_notif()
        
        
    def update_notif(self):
        self.notificationText.move(20, 155)
        self.notificationText.adjustSize()
        
        
    def snip_and_save(self):
        if self.snip_count < 4:
            self.update_text()  # Update the label text
            self.notificationText.setText(f"Snipping in progress... Snip count: {self.snip_count}")
            self.update_notif()
        if self.snip_count >= 4:
            self.notificationText.setText("Snip limit reached.")
            self.update_notif()
            

class SnipWidgetTest(QMainWindow):
    notification_signal = pyqtSignal()

    def __init__(self, parent):
        super(SnipWidgetTest, self).__init__()
        self.parent_widget = parent
        self.snip_count = parent.snip_count
        self.snipped_image = None
        self.ai_helper = MagicMock()
        self.my_sheet = MagicMock()
        
    def save_image_and_process(self):
        image_path = './test_snipped_image.png'
        # Simulate saving image
        if self.snipped_image is not None:
            # Process the image with the current snip count and update 
            updated_entries = self.ai_helper.process_image(image_path, self.snip_count)

            if updated_entries is None:
                self.notification_signal.emit()
                self.parent_widget.update_text()
                self.parent_widget.notificationText.setText("Required keywords missing. Please snip again.")
                return

            # Only increment snip_count if entries are valid
            self.parent_widget.snip_count += 1 

            # Define columns based on the current snip count
            if self.snip_count == 0:
                self.my_sheet.update_date()
                my_columns = ['B', 'C']
            elif self.snip_count == 1:
                my_columns = ['G']
            elif self.snip_count == 2:
                my_columns = ['D', 'E', 'F']
            elif self.snip_count == 3:
                my_columns = ['H', 'I', 'J', 'K', 'L']

            self.my_sheet.find_empty_cells_and_write_values(self.my_sheet.worksheet, my_columns, list(updated_entries.values()))
            self.parent_widget.update_text()
            
            if self.parent_widget.snip_count >= 4:
                self.parent_widget.notificationText.setText("Snip limit reached.")
                self.parent_widget.update_notif()
        else:
            self.notification_signal.emit()
            self.parent_widget.notificationText.setText("No image captured. Please try again.")
        


       
@pytest.fixture(scope="module")
def app():
    app = QApplication([])
    yield app
    app.quit()

# my MyWindowTest class
@pytest.fixture
def my_window(app):
    window = MyWindowTest()
    window.show()
    return window


# SnipWidgetTest  class
@pytest.fixture
def snip_widget(my_window):
    widget = SnipWidgetTest(my_window)  # my_window instance
    return widget



def test_window_initialization(my_window):
    assert my_window.windowTitle() == "Test Title"
    assert my_window.geometry().x() == 50
    assert my_window.geometry().y() == 50
    assert my_window.geometry().width() == my_window.win_width
    assert my_window.geometry().height() == my_window.win_height
    assert my_window.snip_count == 0
    assert my_window.text_label.styleSheet() == "color: black; font-size: 15px; font-weight: bold;"

def test_dynamic_text_update(my_window):
    my_window.snip_count = 1
    my_window.update_text()  
    assert my_window.get_text_based_on_snip_count() == "Capture Test 1"
    assert my_window.text_label.text() == "Capture Test 1"
    
    

def test_UI_fuctionality(my_window):
    assert my_window.snipButton.text() == 'Test text'
   
    
def test_button_connection(my_window):
    assert my_window.snipButton.isChecked() is False  # Button  not  checked
    # button clicked 
    my_window.snipButton.click()  
    # assert my_window.snip_count == 1

def test_snip_and_save(my_window,snip_widget):
    """Test that the snip limit is enforced at 4 snips."""

    for i in range(4): # Should increment to 4
        my_window.snip_and_save()
        snip_widget.snipped_image = MagicMock()  # Simulate a captured image
        snip_widget.ai_helper.process_image.return_value = {'key1': 'value1', 'key2': 'value2'}
        snip_widget.save_image_and_process()
        assert my_window.snip_count == i + 1

         
    assert my_window.snip_count == 4
    assert my_window.notificationText.text() == "Snip limit reached."

def test_save_image_and_process_valid(snip_widget):
    # Test with valid image and valid AI processing
    for i in range(4):
        snip_widget.snipped_image = MagicMock()  # Simulate a captured image
        snip_widget.ai_helper.process_image.return_value = {'key1': 'value1', 'key2': 'value2'}

        snip_widget.save_image_and_process()
        
        assert snip_widget.parent_widget.snip_count == i+1
        assert snip_widget.my_sheet.update_date.called_once()
        assert snip_widget.my_sheet.find_empty_cells_and_write_values.called_once()
        assert snip_widget.my_sheet.find_empty_cells_and_write_values.called_once()
        if i == 3:
            assert snip_widget.parent_widget.text_label.text() == f"Capture the next set of values"
        
        else:   
            assert snip_widget.parent_widget.text_label.text() == f"Capture Test {i+1}"
    

    
def test_save_image_and_process_invalid(snip_widget):
    snip_widget.parent_widget.snip_count == 0
    # Test when snipped_image is None
    snip_widget.save_image_and_process()
    assert snip_widget.parent_widget.notificationText.text()=="No image captured. Please try again."
    
    assert snip_widget.parent_widget.snip_count == 0
    
    # Test with valid image but invalid AI processing
    snip_widget.snipped_image = MagicMock() 
    snip_widget.ai_helper.process_image.return_value = None

    snip_widget.save_image_and_process()

    assert snip_widget.parent_widget.snip_count == 0  # Should not increment
    assert snip_widget.parent_widget.notificationText.text() == "Required keywords missing. Please snip again."  

    
    

#  run the tests
if __name__ == "__main__":
    pytest.main()
        
        

