from PIL import Image
import pytesseract
import base64
import requests
import os
import re
import json


if os.path.isfile('env.py'):
    import env
api_key = os.environ['OPENAI_API_KEY']



class AI_helper:
    def __init__(self,api_key,entries_to_sheet: dict={}):
        self.api_key = api_key
        self.entries_to_sheet = entries_to_sheet
     
        
    def encode_image(self,image_path):
        """
        Encodes an image file to base64 string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
        
    def extract_text(self,image_data, keywords,prompt):
        """
        Extracts text from an image using OpenAI Vision
        """
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",

                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_data}"}
                        }
                    ]
                }
            ]
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        print("API Response Status Code:", response.status_code)
        response_data = response.json()

        
        # Print token usage
        if "usage" in response_data:
            usage = response_data["usage"]
            print("Token Usage:")
            print(f"  Prompt Tokens: {usage.get('prompt_tokens', 0)}")
            print(f"  Completion Tokens: {usage.get('completion_tokens', 0)}")
            print(f"  Total Tokens: {usage.get('total_tokens', 0)}")
        if "choices" in response_data and len(response_data["choices"]) > 0:
            return response_data["choices"][0]["message"]["content"].strip()
        else:
            return "Could not extract text from image."




    def process_image(self, image_path, snip_count):
        """
        Process the image by extracting relevant text 
        and changing keywords based on snip count.
        """
        print("this is the snip count ", snip_count)

        if snip_count == 0:
            KEYWORDS = {
                "Median response time": "Median response time",
                "Median time to close": "Median time to close"
            }
        elif snip_count == 1:
            KEYWORDS = {
                "Conversation ratings": "Conversation ratings"
            }
        elif snip_count == 2:
            KEYWORDS = {
                "Conversations": "Conversations",
                "Closed Conversations": "Closed Conversations",
                "Replies Sent": "Replies Sent"
            }
        if snip_count == 3:
            KEYWORDS = {
                "Portfolio Project 1": "Portfolio Project 1",
                r"\b[2]\s*[-]?\s*Complexity\b": "2 - Complexity",
                r"\b[3]\s*[-]?\s*Complexity\b": "3 - Complexity",
                r"\b[4]\s*[-]?\s*Complexity\b": "4 - Complexity",
                r"\b[5]\s*[-]?\s*Complexity\b": "5 - Complexity",
                
            }
        # Extract text using Pytesseract
        image = Image.open(image_path)
        custom_config = r'--oem 3 --psm 6' 
        detected_text = pytesseract.image_to_string(image, config=custom_config) or ""
        print("Detected text:", detected_text)
        
        if detected_text == "":
            print("No text detected .")
            return None
            
        found_keywords = set()
        # adding expected values instead of reghex pattern
        for pattern, expected in KEYWORDS.items():
            match = re.search(pattern, detected_text, re.IGNORECASE)
            if match:
                found_keywords.add(expected)  # Add the expected value instead of the regex match

        print("Found keywords:", found_keywords)

        # Check for missing keywords
        expected_keywords = set(KEYWORDS.values())
        missing_keywords = expected_keywords - found_keywords
        print("missing keywords = ",missing_keywords)

        
        # if there is missing value(in best case one value), add that value from 
        # expected values and later LLM will ad 0 or None to that value
        if missing_keywords:
            print(f"Missing keywords: {', '.join(missing_keywords)}")
            if snip_count < 3:
                print("No Missing keywords allowed.")
                return None
                
            if snip_count == 3 and len(missing_keywords)<2:
                found_keywords = found_keywords.union(missing_keywords)
                print("found keywords after update = ", found_keywords)
            else:
                print("More than one  Missing keywords not allowed.")
                return None
                
 

        # when all values are present we  continue  
        # Encode the image to base64
        image_data = self.encode_image(image_path)

        # Call extract_text only if all keywords are found
        prompt = self.create_specific_prompt(KEYWORDS, snip_count)
        extracted_text = self.extract_text(image_data, KEYWORDS, prompt)
        print("Extracted text after prompt =", extracted_text)

        if extracted_text:
            try:
                valid_json_text = extracted_text.replace("'", '"')
                self.entries_to_sheet = json.loads(valid_json_text)
                print("Entries to sheet after update =", self.entries_to_sheet)

                if isinstance(self.entries_to_sheet, dict):
                    return self.entries_to_sheet
                else:
                    print("Extracted text is not in dictionary format.")
                    return None
            except json.JSONDecodeError as e:
                print("Failed to decode JSON:", e)
                return None
        else:
            print("Required keywords not found in the detected text.")
            return None


    
    def create_specific_prompt(self, keywords, snip_count):
        """
        Create a specific prompt based on the snip count and keywords.
        """
        if snip_count == 0:

            prompt = f"""Can you extract values {', '.join(keywords.keys())}? BE CAREFUL JUST TO EXTRACT CORRECT VALUES SINCE YOU 
            HAVE ONE CONFUSING VALUE (DO NOT EXTRACT 'Median first response time' PLEASE). ONLY IF VALUE IS IN MINUTES AND SECONDS 
            round it to the nearest minute! OTHERWISE, LEAVE IT AS SECONDS.
            Do not include any other comments or Markdown formatting. Just return the results as a dictionary 
            of key-value pairs, keys should be in order and values shouldn't have units please?"""
        
  
        elif snip_count == 1:
            prompt = f"""Can you extract percentage value for 'Conversation ratings' (written in bigger font)
            and round it to the nearest number? Do not include any other comments or Markdown formatting. 
            Just return the results as a dictionary of key-value pair 'Conversation ratings': value in percentages, adding % at the end of the value."""
        

        elif snip_count == 2:
            prompt = f"""Can you extract values for {', '.join(keywords.keys())}? 
            Do not include any other comments or Markdown formatting. 
            Just return the results as a dictionary of key-value pairs, keys should be exactly 
            {', '.join(keywords.keys())} and values their values you extracted."""
    
        elif snip_count == 3:
            prompt = f"""Can you extract values IN THIS ORDER for {', '.join(keywords.values())}? 
                    BE CAREFUL, THE DICTIONARY KEYS SHOULD BE IN THIS ORDER: {', '.join(keywords.values())}.
                    Do not include any other comments or Markdown formatting. 
                    Just return the results as a dictionary of key-value pairs, keys should be 
                    {', '.join(keywords.values())} and values their values you extracted. THE RESULT SHOULD BE 
                    A DICTIONARY IN THIS ORDER: {', '.join(keywords.values())}. IF THERE ARE NO VALUES FOR A KEYWORD SET VALUE AS 0"""
        

        return prompt

