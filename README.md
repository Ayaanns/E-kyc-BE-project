# eKYC Project - Type the Perfect Name AYAAN...!

A Django-based electronic Know Your Customer (eKYC) system.

## Features

- Real-time face detection with blink and wave verification
- Voice-based information collection
- Progress indicator for verification steps
- User transcript generation
- Secure data handling

## Prerequisites

- Python 3.8 or higher
- Webcam access
- Microphone access
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ekyc_project
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv env
.\env\Scripts\activate

# Linux/MacOS
python3 -m venv env
source env/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Database Setup

1. Install MySQL Server:
```bash
# Windows
# Download and install MySQL Server from https://dev.mysql.com/downloads/mysql/

# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server
```

2. Create Database and User:
```sql
mysql -u root -p

CREATE DATABASE ekyc;
CREATE USER 'ekyc_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ekyc.* TO 'ekyc_user'@'localhost';
FLUSH PRIVILEGES;
```

3. Install MySQL Python connector:
```bash
pip install mysqlclient
```

## Email Configuration

1. Generate Google App Password:
   - Go to your Google Account settings (https://myaccount.google.com/)
   - Navigate to Security > 2-Step Verification
   - Scroll to bottom and select "App passwords"
   - Select "Mail" and "Other (Custom name)"
   - Enter "Django eKYC" as the name
   - Click "Generate"
   - Copy the 16-character password

2. Store Email Credentials:
   Add to your `.env` file:
   ```
   E_USER=your.email@gmail.com
   E_PSWD=your_16_char_app_password
   ```

## Secret Key Generation

1. Generate a new Django secret key:
```python
# Run in Python console
import secrets
secrets.token_urlsafe(32)
```

2. Add to Environment:
   Add the generated key to your `.env` file:
   ```
   SECRET_KEY=your_generated_secret_key
   DEBUG=True
   
   DB_NAME=ekyc
   DB_USER=ekyc_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   
   ```

## Configuration

1. Create a `.env` file in the project root:
```bash
SECRET_KEY=your_django_secret_key
DEBUG=True
DB_NAME=ekyc
DB_USER=ekyc_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
E_USER=your.email@gmail.com
E_PSWD=your_16_char_app_password
```

2. Apply database migrations:
```bash
python manage.py migrate
```

## Running the Application

1. Start the Django development server:
```bash
python manage.py runserver
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:8000/
```

## Usage

1. **Face Verification**
   - Allow camera access when prompted
   - Follow the on-screen instructions to complete wave and blink verifications
   - Wait for the verification progress to reach 100%

2. **Voice Recognition**
   - Allow microphone access when prompted
   - Clearly speak your information when asked:
     - First Name
     - Last Name
     - Age (must be 18 or older)
     - Phone Number (10 digits)

3. **Review Information**
   - Check the transcript section for collected information
   - Press 'q' in the webcam window to exit

## Troubleshooting

1. **Camera Access Issues**
   - Ensure your browser has camera permissions
   - Check if another application is using the camera
   - Try restarting your browser

2. **Voice Recognition Issues**
   - Ensure your microphone is properly connected
   - Check microphone permissions in your system settings
   - Speak clearly and in a quiet environment

## Project Structure

```
ekyc_project/
│
├── ekyc/                   # Main application directory
│   ├── NLP.py             # Voice recognition and processing
│   ├── views.py           # View controllers
│   └── urls.py            # URL configurations
│
├── templates/             # HTML templates
│   └── home.html         # Main interface template
│
├── static/               # Static files (CSS, JS)
│   └── styles.css       # Custom styles
│
├── requirements.txt      # Project dependencies
└── README.md            # Project documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
