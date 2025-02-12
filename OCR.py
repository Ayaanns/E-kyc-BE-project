import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Set path to Tesseract OCR executable (change this based on your system)
# Example for Windows: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# For Linux/Mac, ensure tesseract is installed and available in PATH

def capture_card():
    cap = cv2.VideoCapture(0)  # Open webcam
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    print("Press 's' to capture the card image.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break
        
        cv2.imshow('Capture Card', frame)
        key = cv2.waitKey(1)
        if key == ord('s'):  # Press 's' to save image
            cv2.imwrite("card.jpg", frame)
            print("Image captured successfully!")
            break
    
    cap.release()
    cv2.destroyAllWindows()

def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding - you can experiment with the threshold values
    # Option 1: Simple Binary Thresholding
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Option 2: Adaptive Thresholding (useful for uneven lighting)
    # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    #                                cv2.THRESH_BINARY, 11, 2)
    
    # Save the preprocessed image for debugging purposes
    cv2.imwrite("preprocessed.jpg", thresh)
    
    # Tesseract configuration - you might experiment with page segmentation mode (psm)
    config = '--psm 6'  # Assume a uniform block of text. Change as needed.
    text = pytesseract.image_to_string(thresh, config=config)
    
    return text

if __name__ == "__main__":
    capture_card()
    extracted_text = extract_text_from_image("card.jpg")
    print("Extracted Text:")
    print(extracted_text)
