import cv2
import easyocr
import re
import os
import numpy as np
from PIL import Image
import time

def enhance_image_for_ocr(image):
    """Apply preprocessing to enhance image for better OCR results"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY, 11, 2)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
    
    # Increase contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    return enhanced

def capture_image_with_guide():
    """Capture image with guide frame for better positioning"""
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None
    
    # Get camera frame dimensions
    ret, frame = cap.read()
    if not ret:
        print("Error: Couldn't read frame.")
        cap.release()
        return None
    
    height, width = frame.shape[:2]
    
    # Calculate guide rectangle (80% of frame size)
    rect_width = int(width * 0.8)
    rect_height = int(height * 0.5)  # Aadhar cards are typically landscape
    x = (width - rect_width) // 2
    y = (height - rect_height) // 2
    
    print("Position your Aadhar card within the rectangle and press 's' to capture")
    print("Press 'q' to quit without capturing")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error reading frame")
            break
            
        # Draw guide rectangle
        cv2.rectangle(frame, (x, y), (x + rect_width, y + rect_height), (0, 255, 0), 2)
        
        # Add instructions text
        cv2.putText(frame, "Position Aadhar card inside rectangle", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "Press 's' to capture, 'q' to quit", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow("Aadhar Card Scanner", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            # Capture the image
            image_path = "captured_aadhar.jpg"
            
            # Only save the region of interest for better OCR
            roi = frame[y:y+rect_height, x:x+rect_width]
            cv2.imwrite(image_path, roi)
            
            # Show confirmation
            cv2.putText(frame, "Image Captured!", (width//2-100, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
            cv2.imshow("Aadhar Card Scanner", frame)
            cv2.waitKey(1000)
            break
        elif key == ord('q'):
            print("Capture cancelled")
            cap.release()
            cv2.destroyAllWindows()
            return None
    
    cap.release()
    cv2.destroyAllWindows()
    return image_path

def extract_text_with_confidence(image_path, min_confidence=0.4):
    """Extract text with confidence filtering and multiple language support"""
    try:
        print("Loading OCR engine (this may take a moment)...")
        # Use both English and Hindi for better Aadhar card recognition
        reader = easyocr.Reader(['en', 'hi'])
        
        # Read image and get detailed results including confidence scores
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image at {image_path}")
            return []
            
        # Preprocess the image for better OCR
        enhanced_img = enhance_image_for_ocr(image)
        
        print("Performing OCR (this may take a minute)...")
        results = reader.readtext(enhanced_img)
        
        # Filter results by confidence and sort by position (top to bottom)
        filtered_results = [(text, conf) for bbox, text, conf in results if conf > min_confidence]
        filtered_results.sort(key=lambda x: x[1], reverse=True)  # Sort by confidence
        
        # Return text and confidence pairs
        return filtered_results
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        return []

def extract_aadhar_details(text_results):
    """Extract Aadhar card details using regex patterns and confidence scores"""
    details = {
        "Name": "", 
        "Father's Name": "", 
        "DOB": "",
        "Gender": "",
        "Aadhar Number": "",
        "Address": "",
        "Confidence": {}
    }
    
    # Regex patterns for Aadhar card fields
    patterns = {
        "Aadhar Number": r'(?<!\d)(\d{4}\s\d{4}\s\d{4})(?!\d)',
        "DOB": r'\b(\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})\b',
        "Gender": r'\b(?:MALE|FEMALE|TRANSGENDER)\b',
        "Father Name Indicator": r'\b(?:S/O|D/O|W/O|C/O)\b'
    }
    
    # Process each text line with confidence
    address_lines = []
    name_candidates = []
    father_name_line = None
    
    for text, confidence in text_results:
        text = text.strip().upper()
        
        # Skip very short or irrelevant lines
        if len(text) < 3 or "GOVERNMENT OF INDIA" in text or "UNIQUE IDENTIFICATION" in text:
            continue
            
        # Check for Aadhar number
        if re.search(patterns["Aadhar Number"], text) and not details["Aadhar Number"]:
            aadhar_match = re.search(patterns["Aadhar Number"], text)
            details["Aadhar Number"] = aadhar_match.group(0)
            details["Confidence"]["Aadhar Number"] = confidence
            continue
            
        # Check for DOB
        if re.search(patterns["DOB"], text) and not details["DOB"]:
            dob_match = re.search(patterns["DOB"], text)
            details["DOB"] = dob_match.group(0)
            
            # Check if gender is in the same line as DOB (common format)
            gender_match = re.search(patterns["Gender"], text)
            if gender_match and not details["Gender"]:
                details["Gender"] = gender_match.group(0)
                details["Confidence"]["Gender"] = confidence
            
            details["Confidence"]["DOB"] = confidence
            continue
            
        # Check for gender separately if not found with DOB
        if re.search(patterns["Gender"], text) and not details["Gender"]:
            gender_match = re.search(patterns["Gender"], text)
            details["Gender"] = gender_match.group(0)
            details["Confidence"]["Gender"] = confidence
            continue
            
        # Check for Father's name line
        if re.search(patterns["Father Name Indicator"], text) and not father_name_line:
            father_name_line = text
            details["Confidence"]["Father's Name"] = confidence
            continue
            
        # Collect potential name candidates (typically at the top of the card)
        if not details["Name"] and len(name_candidates) < 3 and len(text) > 3:
            name_candidates.append((text, confidence))
            continue
            
        # Everything else might be part of the address
        if "ADDRESS" in text or len(address_lines) > 0:
            address_lines.append(text)
            if not details["Confidence"].get("Address"):
                details["Confidence"]["Address"] = confidence
    
    # Process collected information
    
    # Process name (usually the first non-header text with high confidence)
    if name_candidates:
        # Sort by confidence and position
        name_candidates.sort(key=lambda x: x[1], reverse=True)
        details["Name"] = name_candidates[0][0]
        details["Confidence"]["Name"] = name_candidates[0][1]
    
    # Process Father's name
    if father_name_line:
        # Extract the name part after S/O, D/O, etc.
        parts = re.split(patterns["Father Name Indicator"], father_name_line, maxsplit=1)
        if len(parts) > 1:
            details["Father's Name"] = parts[1].strip()
        else:
            details["Father's Name"] = father_name_line
    
    # Process address
    if address_lines:
        # Remove "ADDRESS:" prefix if present
        if "ADDRESS:" in address_lines[0]:
            address_lines[0] = address_lines[0].replace("ADDRESS:", "").strip()
        details["Address"] = " ".join(address_lines).strip()
    
    return details

def display_results(details):
    """Display extracted details in a formatted way"""
    print("\n" + "="*50)
    print(" AADHAR CARD INFORMATION EXTRACTION RESULTS ")
    print("="*50 + "\n")
    
    for field, value in details.items():
        if field != "Confidence":
            confidence = details["Confidence"].get(field, "N/A")
            confidence_str = f"{confidence:.2f}" if isinstance(confidence, float) else confidence
            if value:
                print(f"{field}: {value}")
                print(f"Confidence: {confidence_str}\n")
            
    print("="*50)
    print("Note: Lower confidence values indicate less reliable extraction")
    print("="*50)

def main():
    try:
        print("\nWelcome to Aadhar Card OCR System")
        print("----------------------------------")
        
        # Capture image with guide frame
        image_path = capture_image_with_guide()
        if not image_path:
            return
            
        print(f"Image captured successfully at: {image_path}")
        
        # Extract text with confidence scores
        text_results = extract_text_with_confidence(image_path)
        if not text_results:
            print("No text could be extracted from the image.")
            return
            
        print(f"Extracted {len(text_results)} text elements")
        
        # Extract Aadhar details
        details = extract_aadhar_details(text_results)
        
        # Display results
        display_results(details)
        
        # Option to save results
        save_option = input("\nDo you want to save the extraction results? (y/n): ").lower()
        if save_option == 'y':
            output_file = "aadhar_extraction_result.txt"
            with open(output_file, 'w') as f:
                f.write("AADHAR CARD EXTRACTION RESULTS\n")
                f.write("=" * 30 + "\n\n")
                for field, value in details.items():
                    if field != "Confidence" and value:
                        confidence = details["Confidence"].get(field, "N/A")
                        confidence_str = f"{confidence:.2f}" if isinstance(confidence, float) else confidence
                        f.write(f"{field}: {value}\n")
                        f.write(f"Confidence: {confidence_str}\n\n")
            print(f"Results saved to {output_file}")
            
        print("\nThank you for using Aadhar Card OCR System")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":  
    main()