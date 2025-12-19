"""
JSON Generator for PAS System
Reads extraction_results.xlsx and generates JSON from 'Final Data for PAS System' column

Environment Variables Required:
- JSON_RECIPIENTS: Comma-separated list of email addresses for JSON delivery
  Example: JSON_RECIPIENTS=prakhar.singh1@qualtechedge.com,yourmltales@gmail.com,rakeshaiconsult@gmail.com
"""

import pandas as pd
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class PASJSONGenerator:
    """Generate JSON from extraction results and send via email"""
    
    # Recipient email addresses from environment variable
    @staticmethod
    def get_recipients():
        """Get recipient emails from environment variable"""
        recipients_str = os.getenv('JSON_RECIPIENTS', 'prakhar.singh1@qualtechedge.com,yourmltales@gmail.com,rakeshaiconsult@gmail.com')
        return [email.strip() for email in recipients_str.split(',') if email.strip()]
    
    # Field mapping from PAS Field Name to JSON path
    # Format: 'PAS Field Name': ('json_path', 'field_name')
    FIELD_MAPPING = {
        # Loan Details
        'Loan Number': ('Loan_Details', 'Loan_Number'),
        'Sourcing City Name': ('Loan_Details', 'Sourcing_City_Name'),
        'Branch Name': ('Loan_Details', 'Branch_Name'),
        'Sourcing Channel': ('Loan_Details', 'Sourcing_Channel'),
        'Final Sanctioned Amount': ('Loan_Details', 'Final_Sanctioned_Amount'),
        'Sanction Loan Period': ('Loan_Details', 'Sanction_Loan_Period'),
        'Repayment Structure': ('Loan_Details', 'Repayment_Structure'),
        'Sanction Interest Rate': ('Loan_Details', 'Sanction_Interest_Rate'),
        'Sanction Interest Type': ('Loan_Details', 'Sanction_Interest_Type'),
        'Loan Type': ('Loan_Details', 'Loan_Type'),
        'Loan Purpose': ('Loan_Details', 'Loan_Purpose'),
        'Type Of Employment Loan': ('Loan_Details', 'Type_Of_Employment_Loan'),
        'Total Net Monthly Income Considered Across All Borrowers': ('Loan_Details', 'Total_Net_Monthly_Income_Considered_Across_All_Borrowers'),
        'Foir': ('Loan_Details', 'Foir'),
        'Is Collateral Crosslinked': ('Loan_Details', 'Is_Collateral_Crosslinked'),
        'Loan Account Number': ('Loan_Details', 'Loan_Account_Number'),
        'Lender Promo Code': ('Loan_Details', 'Lender_Promo_Code'),
        'Govt Scheme': ('Loan_Details', 'Govt_Scheme'),
        'LoanID Of Cross linked loan': ('Loan_Details', 'LoanID_Of_Cross_linked_loan'),
        'Combined LTV': ('Loan_Details', 'Combined_LTV'),
        'Total Exposure': ('Loan_Details', 'Total_Exposure'),
        'Sourcing Region': ('Loan_Details', 'Sourcing_Region'),
        'EMI TO ABB RATIO': ('Loan_Details', 'EMI_TO_ABB_RATIO'),
        'Lender Scheme Code': ('Loan_Details', 'Lender_Scheme_Code'),
        'Lender Internal Score': ('Loan_Details', 'Lender_Internal_Score'),
        'Refinance Payment Period In Months': ('Loan_Details', 'Refinance_Payment_Period_In_Months'),
        'Refinance Original Mode Of payment': ('Loan_Details', 'Refinance_Original_Mode_Of_payment'),
        'CRE Applicable': ('Loan_Details', 'CRE_Applicable'),
        'Manual ABB': ('Loan_Details', 'Manual_ABB'),
        'Final AMC': ('Loan_Details', 'Final_AMC'),
        'Total Monthly Obligations Considered': ('Loan_Details', 'Total_Monthly_Obligations_Considered'),
        'Branch Sales Manager': ('Loan_Details', 'Branch_Sales_Manager'),
        'Branch Credit Manager': ('Loan_Details', 'Branch_Credit_Manager'),
        'Original Sanction Tenor Of BT Loan': ('Loan_Details', 'Original_Sanction_Tenor_Of_BT_Loan'),
        'Date Of Legal': ('Loan_Details', 'Date_Of_Legal'),
        'Developer Name': ('Loan_Details', 'Developer_Name'),
        'Date Of Title': ('Loan_Details', 'Date_Of_Title'),
        'Legal Vendor': ('Loan_Details', 'Legal_Vendor'),
        
        # Borrower Details (will be in array)
        'Borrower First Name': ('BorrowersDetails', 'Borrower_First_Name'),
        'Borrower Surname': ('BorrowersDetails', 'Borrower_Surname'),
        'Date Of Birth Of The Borrower': ('BorrowersDetails', 'Date_Of_Birth_Of_The_Borrower'),
        'Gender': ('BorrowersDetails', 'Gender'),
        'Marital Status': ('BorrowersDetails', 'Marital_Status'),
        'Borrower City': ('BorrowersDetails', 'Borrower_City'),
        'Borrower PIN': ('BorrowersDetails', 'Borrower_PIN'),
        'Borrower MobileNo': ('BorrowersDetails', 'Borrower_MobileNo'),
        'Borrower Address1': ('BorrowersDetails', 'Borrower_Address1'),
        'Borrower Address2': ('BorrowersDetails', 'Borrower_Address2'),
        'Borrower Address3': ('BorrowersDetails', 'Borrower_Address3'),
        'Resident Status': ('BorrowersDetails', 'Resident_Status'),
        'Current Residence': ('BorrowersDetails', 'Current_Residence'),
        'Id Proof Type': ('BorrowersDetails', 'Id_Proof_Type'),
        'Id Number': ('BorrowersDetails', 'Id_Number'),
        'Type Of Employment Borrower': ('BorrowersDetails', 'Type_Of_Employment_Borrower'),
        'Borrower Entity Type': ('BorrowersDetails', 'Borrower_Entity_Type'),
        'Level Of Studies': ('BorrowersDetails', 'Level_Of_Studies'),
        'Number Of Dependents': ('BorrowersDetails', 'Number_Of_Dependents'),
        'SE Type': ('BorrowersDetails', 'SE_Type'),
        'Borrower Retirement Date': ('BorrowersDetails', 'Borrower_Retirement_Date'),
        'Work Details': ('BorrowersDetails', 'Work_Details'),
        'Relationship Of Coborrower To The Borrower': ('BorrowersDetails', 'Relationship_Of_Coborrower_To_The_Borrower'),
        'Office Ownership': ('BorrowersDetails', 'Office_Ownership'),
        'Satisfactory TPC Check': ('BorrowersDetails', 'Satisfactory_TPC_Check'),
        'Years In Current Employment': ('BorrowersDetails', 'Years_In_Current_Employment'),
        'Months In Current Employment': ('BorrowersDetails', 'Months_In_Current_Employment'),
        'Years In Total Employment': ('BorrowersDetails', 'Years_In_Total_Employment'),
        'Contractual PartTime Employment': ('BorrowersDetails', 'Contractual_PartTime_Employment'),
        'Nature Of Employment': ('BorrowersDetails', 'Nature_Of_Employment'),
        'Pensionable Borrower': ('BorrowersDetails', 'Pensionable_Borrower'),
        'Personal Discussion': ('BorrowersDetails', 'Personal_Discussion'),
        'Mode Of Salary': ('BorrowersDetails', 'Mode_Of_Salary'),
        'Office SetUp': ('BorrowersDetails', 'Office_SetUp'),
        'Lender PD Status': ('BorrowersDetails', 'Lender_PD_Status'),
        'Place Of PD Conducted': ('BorrowersDetails', 'Place_Of_PD_Conducted'),
        'Comment Negative Remark Redflag': ('BorrowersDetails', 'Comment_Negative_Remark_Redflag'),
        'CPV Resi': ('BorrowersDetails', 'CPV_Resi'),
        'CPV Office': ('BorrowersDetails', 'CPV_Office'),
        'DEDUPE': ('BorrowersDetails', 'DEDUPE'),
        'RCU FCU': ('BorrowersDetails', 'RCU_FCU'),
        'Income Considered': ('BorrowersDetails', 'Income_Considered'),
        'Program Borrower': ('BorrowersDetails', 'Program_Borrower'),
        'Hunter Status': ('BorrowersDetails', 'Hunter_Status'),
        'Basic Salary': ('BorrowersDetails', 'Basic_Salary'),
        'DA': ('BorrowersDetails', 'DA'),
        'HRA': ('BorrowersDetails', 'HRA'),
        'Fixed Component': ('BorrowersDetails', 'Fixed_Component'),
        'Incentives': ('BorrowersDetails', 'Incentives'),
        'Performance Linked Bonus': ('BorrowersDetails', 'Performance_Linked_Bonus'),
        'Any Other Variable Component': ('BorrowersDetails', 'Any_Other_Variable_Component'),
        'Fixed Bonus': ('BorrowersDetails', 'Fixed_Bonus'),
        'Other Annual Benefits': ('BorrowersDetails', 'Other_Annual_Benefits'),
        'Cash Salary': ('BorrowersDetails', 'Cash_Salary'),
        'Rental Income Bank ITR': ('BorrowersDetails', 'Rental_Income_Bank_ITR'),
        'Rental Income Cash': ('BorrowersDetails', 'Rental_Income_Cash'),
        'Agricultural Income': ('BorrowersDetails', 'Agricultural_Income'),
        'Interest Dividend Income': ('BorrowersDetails', 'Interest_Dividend_Income'),
        'Future Rental': ('BorrowersDetails', 'Future_Rental'),
        'Rental Income Source Document Bank': ('BorrowersDetails', 'Rental_Income_Source_Document_Bank'),
        'Other Income': ('BorrowersDetails', 'Other_Income'),
        'Employer Name': ('BorrowersDetails', 'Employer_Name'),
        'Employer City': ('BorrowersDetails', 'Employer_City'),
        'Employer Pin': ('BorrowersDetails', 'Employer_Pin'),
        'Employer Address1': ('BorrowersDetails', 'Employer_Address1'),
        'Employer Address2': ('BorrowersDetails', 'Employer_Address2'),
        'Employer Address3': ('BorrowersDetails', 'Employer_Address3'),
        'Employer Department': ('BorrowersDetails', 'Employer_Department'),
        'Employer Designation': ('BorrowersDetails', 'Employer_Designation'),
        'Employer Type': ('BorrowersDetails', 'Employer_Type'),
        'Score': ('BorrowersDetails', 'Score'),
    }
    
    def __init__(self, extraction_file, smtp_config):
        print(f"[JSON] Initializing PASJSONGenerator")
        self.extraction_file = extraction_file
        self.smtp_config = smtp_config
        self.df = None
        self.loan_number = None
        self.recipients = self.get_recipients()
        print(f"[JSON] Recipients configured: {', '.join(self.recipients)}")
        
    def load_extraction_data(self):
        """Load extraction_results.xlsx"""
        try:
            self.df = pd.read_excel(self.extraction_file)
            print(f"[JSON] Loaded extraction file: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            print(f"[JSON] Columns in file: {list(self.df.columns)}")
            
            # Check if required columns exist
            if 'PAS Field Name' not in self.df.columns:
                print(f"[JSON ERROR] 'PAS Field Name' column not found!")
                return False
            
            if 'Final Data for PAS System' not in self.df.columns:
                print(f"[JSON ERROR] 'Final Data for PAS System' column not found!")
                return False
            
            # Show sample data for debugging
            print(f"[JSON] Sample PAS Field Names: {list(self.df['PAS Field Name'].head(10))}")
            
            # Count non-empty values in Final Data for PAS System
            non_empty = self.df['Final Data for PAS System'].notna() & (self.df['Final Data for PAS System'] != '')
            print(f"[JSON] Non-empty values in 'Final Data for PAS System': {non_empty.sum()} out of {len(self.df)}")
            
            # Extract loan number
            if 'PAS Field Name' in self.df.columns and 'Final Data for PAS System' in self.df.columns:
                loan_row = self.df[self.df['PAS Field Name'] == 'Loan Number']
                if not loan_row.empty:
                    self.loan_number = str(loan_row.iloc[0]['Final Data for PAS System'])
                    print(f"[JSON] Loan Number: {self.loan_number}")
            
            return True
        except Exception as e:
            print(f"[JSON ERROR] Failed to load extraction file: {e}")
            return False
    
    def get_field_value(self, field_name):
        """Get value from 'Final Data for PAS System' column for a given PAS Field Name"""
        if self.df is None:
            return ""
        
        row = self.df[self.df['PAS Field Name'] == field_name]
        if row.empty:
            # Field not found in extraction results
            return ""
        
        value = row.iloc[0].get('Final Data for PAS System', '')
        
        # Handle NaN, None, empty values
        if pd.isna(value) or value is None:
            return ""
        
        value_str = str(value).strip()
        
        # Log non-empty values for debugging
        if value_str and value_str not in ['', 'nan', 'None']:
            print(f"[JSON] Found value for '{field_name}': {value_str[:50]}...")
        
        return value_str
    
    def generate_json(self):
        """Generate JSON structure from extraction data"""
        print(f"[JSON] Generating JSON structure...")
        print(f"[JSON] Total fields to map: {len(self.FIELD_MAPPING)}")
        
        # Initialize JSON structure
        json_data = {
            "Loan_Details": {},
            "BorrowersDetails": [{}]
        }
        
        # Track statistics
        populated_count = 0
        empty_count = 0
        
        # Map fields to JSON
        for pas_field, (section, json_field) in self.FIELD_MAPPING.items():
            value = self.get_field_value(pas_field)
            
            if value and value not in ['', 'nan', 'None']:
                populated_count += 1
            else:
                empty_count += 1
            
            if section == 'Loan_Details':
                json_data['Loan_Details'][json_field] = value
            elif section == 'BorrowersDetails':
                json_data['BorrowersDetails'][0][json_field] = value
        
        # Add empty nested arrays/objects as per sample
        json_data['Loan_Details']['LoanDeviationDetails'] = []
        json_data['Loan_Details']['NotesDetails'] = []
        json_data['Loan_Details']['RemkarsDetails'] = []
        
        json_data['BorrowersDetails'][0]['LoanObligationDetails'] = []
        json_data['BorrowersDetails'][0]['BorrowerDeviationDetails'] = []
        json_data['BorrowersDetails'][0]['BankWiseBorrowerDetails'] = []
        json_data['BorrowersDetails'][0]['BankingDetails'] = []
        
        print(f"[JSON] JSON structure generated: {populated_count} fields populated, {empty_count} fields empty")
        return json_data
    
    def save_json_file(self, output_folder):
        """Save JSON to file"""
        json_data = self.generate_json()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        loan_suffix = f"_{self.loan_number}" if self.loan_number else ""
        filename = os.path.join(output_folder, f"PAS_Data{loan_suffix}_{timestamp}.json")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            print(f"[JSON] JSON file saved: {filename}")
            return filename
        except Exception as e:
            print(f"[JSON ERROR] Failed to save JSON file: {e}")
            return None
    
    def send_json_email(self, json_file):
        """Send JSON file as attachment to recipients"""
        print(f"[JSON] Preparing to send JSON email...")
        
        if not self.smtp_config:
            print("[JSON ERROR] SMTP config not available")
            return False
        
        try:
            # Prepare subject with loan number
            subject = f"PAS Data - Loan No: {self.loan_number if self.loan_number else 'N/A'}"
            
            # Email body
            body = f"""Dear Team,

Please find attached the PAS system data in JSON format.

Loan Number: {self.loan_number if self.loan_number else 'N/A'}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated email.

Best regards,
PAS Extraction System
"""
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['address']
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach JSON file
            if json_file and os.path.exists(json_file):
                print(f"[JSON] Attaching JSON file: {json_file}")
                with open(json_file, 'rb') as attachment:
                    part = MIMEBase('application', 'json')
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                filename = os.path.basename(json_file)
                part.add_header('Content-Disposition', f'attachment; filename= {filename}')
                msg.attach(part)
            
            # Send email
            print(f"[JSON] Connecting to SMTP server: {self.smtp_config['smtp_server']}:{self.smtp_config['smtp_port']}")
            server = smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port'])
            server.starttls()
            print(f"[JSON] Logging in with email: {self.smtp_config['address']}")
            server.login(self.smtp_config['address'], self.smtp_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.smtp_config['address'], self.recipients, text)
            server.quit()
            
            print(f"[JSON] ✅ JSON email sent successfully to: {', '.join(self.recipients)}")
            return True
            
        except Exception as e:
            print(f"[JSON ERROR] Failed to send email: {e}")
            return False
    
    def generate_and_send(self, output_folder, send_email=True):
        """Main workflow: load data, generate JSON, save file, send email"""
        print("\n" + "="*80)
        print("PAS JSON GENERATION AND EMAIL")
        print("="*80 + "\n")
        
        # Load extraction data
        if not self.load_extraction_data():
            print("[JSON ERROR] Failed to load extraction data")
            return None
        
        # Save JSON file
        json_file = self.save_json_file(output_folder)
        if not json_file:
            print("[JSON ERROR] Failed to save JSON file")
            return None
        
        # Send email
        email_sent = False
        if send_email:
            email_sent = self.send_json_email(json_file)
        
        print("\n" + "="*80)
        print("JSON GENERATION SUMMARY")
        print("="*80)
        print(f"✅ JSON File: {json_file}")
        print(f"✅ Loan Number: {self.loan_number if self.loan_number else 'N/A'}")
        if send_email:
            print(f"{'✅ Email Sent' if email_sent else '❌ Email Failed'} to: {', '.join(self.recipients)}")
        print("="*80 + "\n")
        
        return {
            'json_file': json_file,
            'loan_number': self.loan_number,
            'email_sent': email_sent
        }
