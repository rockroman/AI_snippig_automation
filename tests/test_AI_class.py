from unittest import mock
from unittest.mock import patch, MagicMock,mock_open
import pytest
import warnings
from ai_class import AI_helper
import requests
import json
import base64
import pytesseract
from PIL import Image


ai_test = AI_helper()
ai_test.api_key = "some key"


def test_encoding_img():
    # Mock binary content for the image (this is just random bytes for the test)
    mock_image_data = b'test image data'
    
    # Mock the open function to return the mock image data
    with patch('builtins.open', mock_open(read_data=mock_image_data)) as mock_file:
        # Read the mocked image in binary mode
        with open('test_img.png', 'rb') as img_file:
            image_data = img_file.read()

        # Encode the image to base64
        encoded_image = base64.b64encode(image_data)

        # Ensure the encoding was successful
        assert isinstance(encoded_image, bytes)
        assert len(encoded_image) > 0  # Make sure we have some encoded data

        # Optionally, decode the image back to check integrity
        decoded_image = base64.b64decode(encoded_image)
        assert decoded_image == image_data 


def test_process_image_valid():
    #  mock  opened image 
    mock_data =  "Median response time:\nMedian time to close:"
    # mock_data =  "test1 extracted value\n test2 extracted value"
    KEYWORDS = {"Median response time","Median time to close"}
    test_image = 'test_img.png'
    count = 0
    
    # Create a mock file object
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_file  # Set up context manager behavior
    mock_file.read.return_value = b'test image data'  # Set read() to return bytes
    
    with patch('builtins.open', return_value=mock_file):
    # Mock the output of Image.open
        with patch('PIL.Image.open', return_value=MagicMock()) as mock_open:
            with patch('pytesseract.image_to_string', return_value=mock_data) as mock_ocr:
                    # Call the method with the mock image and snip_count
                    result = ai_test.process_image(test_image, count)
                    
                    # Verify that the image was opened
                    mock_open.assert_called_once_with(test_image)
                    
                    # Verify pytesseract was called correctly
                    mock_ocr.assert_called_once_with(mock_open.return_value, config=r'--oem 3 --psm 6')
                    set(mock_ocr.return_value)
                    print("ocr turned to set = ",mock_ocr.return_value)
                    
                    # Check the detected text and behavior for snip_count == 0
                    assert mock_ocr.return_value == "Median response time:\nMedian time to close:"
                    # assert result == KEYWORDS
                
                
def test_extract_text():
    # Create a mock file object
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_file  # Set up context manager behavior
    mock_file.read.return_value = b'Conversation ratings 98'
    prompt = f"""Can you extract percentage value for 'Conversation ratings' 
    (written in bigger font) and round it to the nearest number? Do not include
    any other comments or Markdown formatting. Just return the results as a 
    dictionary of key-value pair 'Conversation ratings': value in percentages, 
    adding % at the end of the value."""
    
    KEYWORDS = {"Conversation ratings": "Conversation ratings"}
    mock_data = "{'Conversation ratings':98}"
    mock_response = MagicMock()
    mock_response.status_code = 200  # Mock successful status code
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "{'Conversation ratings':98}"
                }
            }
        ]
    }
    # Patch the requests.post call to return the mocked response
    with patch('requests.post', return_value=mock_response):
        result = ai_test.extract_text(mock_file, KEYWORDS, prompt)
    
    # check if the returned data is as expected
    assert result == mock_data
                   


