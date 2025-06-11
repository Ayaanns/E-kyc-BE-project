import pandas as pd
import re
from typing import Dict, Tuple, Optional

class KYCVerifier:
    """
    Standalone KYC Verification Module
    Can be integrated with any existing system
    """
    
    def __init__(self, csv_file_path: str = "DATA for E-kyc project (Responses) - Form Responses 1 changes.csv"):
        """
        Initialize KYC Verifier with CSV database
        
        Args:
            csv_file_path (str): Path to the KYC database CSV file
        """
        self.csv_file_path = csv_file_path
        self.kyc_data = None
        self.is_loaded = self.load_kyc_database()
    
    def load_kyc_database(self) -> bool:
        """
        Load KYC data from CSV file
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            self.kyc_data = pd.read_csv(self.csv_file_path)
            # Clean column names
            self.kyc_data.columns = self.kyc_data.columns.str.strip()
            print(f"KYC Database loaded: {len(self.kyc_data)} records")
            return True
        except Exception as e:
            print(f"Error loading KYC database: {e}")
            return False
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if pd.isna(text) or text is None:
            return ""
        return str(text).strip().lower()
    
    def normalize_phone(self, phone: str) -> str:
        """Normalize phone number by removing non-digits"""
        if pd.isna(phone) or phone is None:
            return ""
        return re.sub(r'\D', '', str(phone))
    
    def normalize_aadhar(self, aadhar: str) -> str:
        """Normalize Aadhar number by removing non-digits"""
        if pd.isna(aadhar) or aadhar is None:
            return ""
        return re.sub(r'\D', '', str(aadhar))
    
    def normalize_pan(self, pan: str) -> str:
        """Normalize PAN number to uppercase"""
        if pd.isna(pan) or pan is None:
            return ""
        return str(pan).strip().upper()
    
    def verify_user_data(self, user_data: Dict[str, str]) -> Tuple[bool, str, Dict]:
        """
        Verify user data against KYC database
        
        Args:
            user_data (dict): Dictionary containing user information
                Required keys: 'name', 'father_name', 'phone', 'aadhar', 'pan'
                Optional keys: 'age', 'dob'
        
        Returns:
            tuple: (is_verified: bool, message: str, match_details: dict)
        """
        if not self.is_loaded:
            return False, "KYC database not loaded", {}
        
        # Extract and normalize user data
        user_name = self.normalize_text(user_data.get('name', ''))
        user_father_name = self.normalize_text(user_data.get('father_name', ''))
        user_phone = self.normalize_phone(user_data.get('phone', ''))
        user_aadhar = self.normalize_aadhar(user_data.get('aadhar', ''))
        user_pan = self.normalize_pan(user_data.get('pan', ''))
        
        # Search through database
        for index, row in self.kyc_data.iterrows():
            # Normalize database values
            db_name = self.normalize_text(row.get('Name', ''))
            db_father_name = self.normalize_text(row.get("Father's name", ''))
            db_phone = self.normalize_phone(row.get('Whatsapp Phone Number', ''))
            db_aadhar = self.normalize_aadhar(row.get('Aadhar Number', ''))
            db_pan = self.normalize_pan(row.get('Pan Number', ''))
            
            # Check matches
            matches = self._check_field_matches(
                user_name, user_father_name, user_phone, user_aadhar, user_pan,
                db_name, db_father_name, db_phone, db_aadhar, db_pan
            )
            
            # Verify based on matching criteria
            if self._is_verification_successful(matches):
                match_details = {
                    'record_index': index + 1,
                    'matched_fields': [field for field, matched in matches.items() if matched],
                    'total_matches': sum(matches.values()),
                    'database_record': {
                        'name': row.get('Name', ''),
                        'father_name': row.get("Father's name", ''),
                        'age': row.get('Age', ''),
                        'phone': row.get('Whatsapp Phone Number', ''),
                        'aadhar': row.get('Aadhar Number', ''),
                        'pan': row.get('Pan Number', '')
                    }
                }
                return True, f"KYC Verified against record #{index + 1}", match_details
        
        return False, "No matching records found in KYC database", {}
    
    def _check_field_matches(self, user_name, user_father_name, user_phone, user_aadhar, user_pan,
                           db_name, db_father_name, db_phone, db_aadhar, db_pan) -> Dict[str, bool]:
        """Check which fields match between user and database"""
        return {
            'name': self._fuzzy_name_match(user_name, db_name),
            'father_name': self._fuzzy_name_match(user_father_name, db_father_name),
            'phone': user_phone == db_phone and user_phone != "",
            'aadhar': user_aadhar == db_aadhar and user_aadhar != "",
            'pan': user_pan == db_pan and user_pan != ""
        }
    
    def _fuzzy_name_match(self, name1: str, name2: str) -> bool:
        """Perform fuzzy matching for names"""
        if not name1 or not name2:
            return False
        # Check if names contain each other or have significant overlap
        return (name1 in name2 or name2 in name1 or 
                len(set(name1.split()) & set(name2.split())) >= 1)
    
    def _is_verification_successful(self, matches: Dict[str, bool]) -> bool:
        """Determine if verification is successful based on matches"""
        critical_matches = sum([matches['phone'], matches['aadhar'], matches['pan']])
        total_matches = sum(matches.values())
        
        # Require at least 1 critical match and 3 total matches
        return critical_matches >= 1 and total_matches >= 3
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get statistics about the KYC database"""
        if not self.is_loaded:
            return {}
        
        return {
            'total_records': len(self.kyc_data),
            'records_with_phone': self.kyc_data['Whatsapp Phone Number'].notna().sum(),
            'records_with_aadhar': self.kyc_data['Aadhar Number'].notna().sum(),
            'records_with_pan': self.kyc_data['Pan Number'].notna().sum()
        }

# Integration helper functions
def verify_user_kyc(name: str, father_name: str, phone: str, aadhar: str, pan: str, 
                   age: str = "", csv_path: str = None) -> Tuple[bool, str]:
    """
    Simple function to verify user KYC - Easy integration point
    
    Args:
        name (str): User's full name
        father_name (str): Father's name
        phone (str): Phone number
        aadhar (str): Aadhar number
        pan (str): PAN number
        age (str): Age (optional)
        csv_path (str): Path to CSV file (optional)
    
    Returns:
        tuple: (is_verified: bool, message: str)
    """
    verifier = KYCVerifier(csv_path) if csv_path else KYCVerifier()
    
    user_data = {
        'name': name,
        'father_name': father_name,
        'phone': phone,
        'aadhar': aadhar,
        'pan': pan,
        'age': age
    }
    
    is_verified, message, _ = verifier.verify_user_data(user_data)
    return is_verified, message

def create_user_data_dict(name: str = "", father_name: str = "", phone: str = "", 
                         aadhar: str = "", pan: str = "", age: str = "") -> Dict[str, str]:
    """
    Helper function to create user data dictionary
    
    Returns:
        dict: Formatted user data dictionary
    """
    return {
        'name': name,
        'father_name': father_name,
        'phone': phone,
        'aadhar': aadhar,
        'pan': pan,
        'age': age
    }

# Example usage and testing
if __name__ == "__main__":
    # Example 1: Using the KYCVerifier class directly
    print("=== KYC Verification Module Test ===\n")
    
    verifier = KYCVerifier()
    
    if verifier.is_loaded:
        print("Database Stats:", verifier.get_database_stats())
        print()
        
        # Test with data from your CSV
        test_user = {
            'name': 'Tanay Lovekush Soni',
            'father_name': 'Lovekush Soni',
            'phone': '7028734849',
            'aadhar': '456989977431',
            'pan': 'OLEPS7801A'
        }
        
        is_verified, message, details = verifier.verify_user_data(test_user)
        print(f"Test User: {test_user['name']}")
        print(f"Verification Result: {'✓ VERIFIED' if is_verified else '✗ NOT VERIFIED'}")
        print(f"Message: {message}")
        if details:
            print(f"Matched Fields: {details['matched_fields']}")
        print()
        
        # Example 2: Using the simple helper function
        is_verified2, message2 = verify_user_kyc(
            name="shreyash kale",
            father_name="sanjay",
            phone="9552405737",
            aadhar="496280674871",
            pan="LJNPK7394G"
        )
        
        print("Using helper function:")
        print(f"Verification Result: {'✓ VERIFIED' if is_verified2 else '✗ NOT VERIFIED'}")
        print(f"Message: {message2}")
        
    else:
        print("Failed to load KYC database")
