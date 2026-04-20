from groq import Groq
import easyocr
from PIL import Image
import PyPDF2
import base64
import os

class AIProcessor:
    def __init__(self, api_key, model='meta-llama/llama-4-scout-17b-16e-instruct'):
        self.client = Groq(api_key=api_key)
        self.model = model
        
        print("Loading EasyOCR...")
        self.reader = easyocr.Reader(['en'])
        print("✓ EasyOCR loaded")
    
    def extract_text_from_image(self, image_path):
        try:
            result = self.reader.readtext(image_path)
            text = ' '.join([item[1] for item in result])
            return text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def extract_text_from_pdf(self, pdf_path):
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def encode_image(self, image_path):
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_mime_type(self, file_path):
        ext = file_path.lower().split('.')[-1]
        if ext == 'jpg':
            return 'image/jpeg'
        return f'image/{ext}'
    
    def process_prescription(self, file_path, language):
        try:
            if file_path.lower().endswith('.pdf'):
                extracted_text = self.extract_text_from_pdf(file_path)
                prompt = f"""You are a medical AI assistant. Analyze this prescription.

Extracted Text:
{extracted_text}

Provide:
1. List of medicines prescribed
2. Dosage for each medicine
3. Instructions for taking each medicine
4. Warnings and precautions
5. General health advice

Output in HTML format with inline CSS.
Language: {language}"""
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            else:
                extracted_text = self.extract_text_from_image(file_path)
                base64_image = self.encode_image(file_path)
                mime_type = self.get_mime_type(file_path)
                
                prompt = f"""You are a medical AI assistant. Analyze this prescription image.

OCR Extracted Text:
{extracted_text}

Provide:
1. List of medicines prescribed
2. Dosage for each medicine
3. Instructions for taking each medicine
4. Warnings and precautions
5. General health advice

Output in HTML format with inline CSS.
Language: {language}"""
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"<p>Error: {str(e)}</p>"
    
    def process_lab_report(self, file_path, language):
        try:
            if file_path.lower().endswith('.pdf'):
                extracted_text = self.extract_text_from_pdf(file_path)
                prompt = f"""You are a medical AI assistant. Analyze this lab report.

Extracted Text:
{extracted_text}

Provide:
1. Summary of all test results
2. Explanation of each test parameter
3. Normal vs Abnormal values (use color: green for normal, red for abnormal)
4. Health implications
5. Recommendations
6. When to consult a doctor

Output in HTML format with inline CSS.
Language: {language}"""
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            else:
                extracted_text = self.extract_text_from_image(file_path)
                base64_image = self.encode_image(file_path)
                mime_type = self.get_mime_type(file_path)
                
                prompt = f"""You are a medical AI assistant. Analyze this lab report image.

OCR Extracted Text:
{extracted_text}

Provide:
1. Summary of all test results
2. Explanation of each test parameter
3. Normal vs Abnormal values (use color: green for normal, red for abnormal)
4. Health implications
5. Recommendations
6. When to consult a doctor

Output in HTML format with inline CSS.
Language: {language}"""
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"<p>Error: {str(e)}</p>"
    
    def process_drug_guidance(self, medicine_name, age, language):
        try:
            prompt = f"""You are a medical AI assistant. Provide guidance about this medicine.

Medicine Name: {medicine_name}
Patient Age: {age} years

Provide:
1. What is this medicine used for?
2. How to take it (dosage for age {age})
3. Common side effects
4. Precautions and warnings
5. Drug interactions to avoid
6. Storage instructions
7. What to do if a dose is missed
8. Important safety information

Output in HTML format with inline CSS.
Language: {language}
Include disclaimer: This is general information, consult your doctor."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"<p>Error: {str(e)}</p>"
    
    def chat_response(self, user_message, language="English"):
        try:
            prompt = f"""You are a helpful medical AI chatbot. Answer the question.

User Question: {user_message}

Provide:
- Direct answer
- Important warnings or precautions
- Suggest consulting healthcare professional if needed

Language: {language}
Keep response conversational."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, error: {str(e)}"