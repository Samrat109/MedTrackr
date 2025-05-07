import os
from datetime import datetime

import pytesseract
from PIL import Image


class OCRProcessor:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def process_image(self, image_path):
        """
        Process an image file and extract text using OCR
        """
        try:
            # Open the image
            image = Image.open(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            # Extract relevant information
            extracted_data = self._extract_prescription_data(text)
            
            return {
                'success': True,
                'text': text,
                'extracted_data': extracted_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_prescription_data(self, text):
        """
        Extract relevant information from OCR text
        """
        # This is a basic implementation. In a real application,
        # you would want to use more sophisticated NLP techniques
        # or machine learning to extract structured data.
        
        extracted_data = {
            'doctor_name': None,
            'medications': [],
            'dosage': [],
            'frequency': [],
            'date': None
        }

        # Split text into lines
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for doctor's name (assuming it's followed by "MD" or "Dr.")
            if 'Dr.' in line or 'MD' in line:
                extracted_data['doctor_name'] = line
            
            # Look for medication names (this is a very basic implementation)
            common_medications = ['amoxicillin', 'ibuprofen', 'aspirin', 'metformin']
            for med in common_medications:
                if med.lower() in line.lower():
                    extracted_data['medications'].append(med)
            
            # Look for dosage information
            if 'mg' in line.lower() or 'ml' in line.lower():
                extracted_data['dosage'].append(line)
            
            # Look for frequency
            frequency_indicators = ['daily', 'twice', 'three times', 'every']
            for indicator in frequency_indicators:
                if indicator in line.lower():
                    extracted_data['frequency'].append(line)
            
            # Look for date
            try:
                # Try to parse date in various formats
                date_formats = ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d']
                for date_format in date_formats:
                    try:
                        date = datetime.strptime(line, date_format)
                        extracted_data['date'] = date.strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        continue
            except:
                pass

        return extracted_data

    def save_processed_image(self, image_path, output_dir):
        """
        Save the processed image with a unique filename
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'prescription_{timestamp}.jpg'
            output_path = os.path.join(output_dir, filename)
            
            # Copy the image to the output directory
            with Image.open(image_path) as img:
                img.save(output_path)
            
            return output_path
        except Exception as e:
            raise Exception(f"Error saving processed image: {str(e)}")

# Example usage:
if __name__ == "__main__":
    processor = OCRProcessor()
    result = processor.process_image("path_to_prescription_image.jpg")
    print(result) 