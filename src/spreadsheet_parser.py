"""
Spreadsheet Parser module for importing job offers from spreadsheet files

This module supports loading job offers from CSV and Excel files.
Dependencies:
- pandas (for data processing)
- openpyxl (for Excel file support)
"""

import os
from typing import List, Dict, Optional, Any
from job_offer import JobOffer, EmploymentType, Benefits, WorkLocationType, CompensationType

# Try importing pandas, provide helpful error message if missing
try:
    import pandas as pd
except ImportError:
    pd = None


class SpreadsheetParser:
    """Parser for importing job offers from spreadsheets"""
    
    def __init__(self):
        if pd is None:
            raise ImportError(
                "Pandas package is required for spreadsheet support.\n"
                "Please install with: pip install pandas openpyxl"
            )
    
    def parse_file(self, filepath: str) -> List[JobOffer]:
        """
        Parse a spreadsheet file and return a list of JobOffer objects
        
        Args:
            filepath: Path to the spreadsheet file (CSV or Excel)
            
        Returns:
            List of JobOffer objects
        """
        _, ext = os.path.splitext(filepath)
        
        if ext.lower() in ['.csv']:
            df = pd.read_csv(filepath)
        elif ext.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Use .csv, .xlsx, or .xls")
        
        return self._dataframe_to_job_offers(df)
    
    def _dataframe_to_job_offers(self, df: 'pd.DataFrame') -> List[JobOffer]:
        """
        Convert a pandas DataFrame to a list of JobOffer objects
        
        Required columns:
        - title: Job title
        - company: Company name
        - location: Job location
        - work_location_type: Type of work location ("onsite", "remote", "hybrid")
        - employment_type: Type of employment ("W2", "1099", "S-Corp")
        - compensation_type: Type of compensation ("salary" or "hourly")
        - base_compensation: Base annual salary or hourly rate
        
        Optional columns: See the detailed mapping in the implementation
        """
        job_offers = []
        
        # Validate required columns
        required_columns = ['title', 'company', 'location', 'work_location_type', 
                            'employment_type', 'compensation_type', 'base_compensation']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Process each row
        for _, row in df.iterrows():
            # Create Benefits object first
            benefits = self._create_benefits_from_row(row)
            
            # Map work location type string to enum
            work_location_type_str = str(row['work_location_type']).strip().upper()
            if work_location_type_str in ['ONSITE', 'ON-SITE', 'ON SITE']:
                work_location_type = WorkLocationType.ONSITE
            elif work_location_type_str == 'REMOTE':
                work_location_type = WorkLocationType.REMOTE
            elif work_location_type_str == 'HYBRID':
                work_location_type = WorkLocationType.HYBRID
            else:
                # Default to onsite if unrecognized
                work_location_type = WorkLocationType.ONSITE
            
            # Map employment type string to enum
            employment_type_str = str(row['employment_type']).strip().upper()
            if employment_type_str == 'W2':
                employment_type = EmploymentType.W2
            elif employment_type_str == '1099':
                employment_type = EmploymentType.CONTRACTOR_1099
            elif employment_type_str == 'S-CORP':
                employment_type = EmploymentType.S_CORP
            else:
                # Default to W2 if unrecognized
                employment_type = EmploymentType.W2
            
            # Map compensation type string to enum
            compensation_type_str = str(row['compensation_type']).strip().upper()
            if compensation_type_str in ['SALARY', 'ANNUAL']:
                compensation_type = CompensationType.SALARY
            elif compensation_type_str in ['HOURLY', 'HOUR']:
                compensation_type = CompensationType.HOURLY
            else:
                # Default to salary if unrecognized
                compensation_type = CompensationType.SALARY
            
            # Handle boolean fields
            bonus_guaranteed = self._get_bool_value(row, 'bonus_guaranteed', False)
            
            # Handle hours and weeks
            hours_per_week = self._get_float_value(row, 'hours_per_week', 40.0)
            weeks_per_year = self._get_float_value(row, 'weeks_per_year', 50.0)
            
            # Create the JobOffer object
            job_offer = JobOffer(
                title=str(row['title']),
                company=str(row['company']),
                location=str(row['location']),
                work_location_type=work_location_type,
                employment_type=employment_type,
                compensation_type=compensation_type,
                base_compensation=float(row['base_compensation']),
                hours_per_week=hours_per_week,
                weeks_per_year=weeks_per_year,
                bonus_amount=self._get_float_value(row, 'bonus_amount', 0.0),
                bonus_guaranteed=bonus_guaranteed,
                signing_bonus=self._get_float_value(row, 'signing_bonus', 0.0),
                relocation_package=self._get_float_value(row, 'relocation_package', 0.0),
                benefits=benefits,
                state_tax_rate=self._get_float_value(row, 'state_tax_rate', 0.0),
                local_tax_rate=self._get_float_value(row, 'local_tax_rate', 0.0),
                self_employment_expenses=self._get_float_value(row, 'self_employment_expenses', 0.0),
                business_expenses=self._get_float_value(row, 'business_expenses', 0.0),
                cost_of_living_index=self._get_float_value(row, 'cost_of_living_index', 100.0),
                commute_time_minutes=self._get_int_value(row, 'commute_time_minutes', 0),
                commute_cost_monthly=self._get_float_value(row, 'commute_cost_monthly', 0.0),
                commute_days_per_week=self._get_int_value(row, 'commute_days_per_week', 5),
                # Add commute calculator parameters
                commute_distance_miles=self._get_float_value(row, 'commute_distance_miles', 0.0),
                # Import DriveType and CommuteCalculationType if they exist in the row
                commute_drive_type=self._get_drive_type(row),
                commute_calc_type=self._get_commute_calc_type(row),
                commute_fuel_cost=self._get_float_value(row, 'commute_fuel_cost', 3.50),
                commute_city_mpg=self._get_float_value(row, 'commute_city_mpg', 25.0),
                commute_highway_mpg=self._get_float_value(row, 'commute_highway_mpg', 32.0),
                commute_combined_mpg=self._get_float_value(row, 'commute_combined_mpg', 28.0),
                commute_include_maintenance=self._get_bool_value(row, 'commute_include_maintenance', True),
                expected_hours_per_week=hours_per_week,
                expected_tenure_years=self._get_float_value(row, 'expected_tenure_years', 3.0)
            )
            
            job_offers.append(job_offer)
        
        return job_offers
    
    def _create_benefits_from_row(self, row: Dict[str, Any]) -> Benefits:
        """Create a Benefits object from a row of spreadsheet data"""
        return Benefits(
            retirement_match_percent=self._get_float_value(row, 'retirement_match_percent', 0.0),
            retirement_match_limit=self._get_float_value(row, 'retirement_match_limit', 0.0),
            health_insurance_monthly_premium=self._get_float_value(row, 'health_insurance_monthly_premium', 0.0),
            health_insurance_coverage_percent=self._get_float_value(row, 'health_insurance_coverage_percent', 0.0),
            dental_insurance_monthly_premium=self._get_float_value(row, 'dental_insurance_monthly_premium', 0.0),
            dental_insurance_coverage_percent=self._get_float_value(row, 'dental_insurance_coverage_percent', 0.0),
            vision_insurance_monthly_premium=self._get_float_value(row, 'vision_insurance_monthly_premium', 0.0),
            vision_insurance_coverage_percent=self._get_float_value(row, 'vision_insurance_coverage_percent', 0.0),
            life_insurance_coverage=self._get_float_value(row, 'life_insurance_coverage', 0.0),
            life_insurance_monthly_premium=self._get_float_value(row, 'life_insurance_monthly_premium', 0.0),
            paid_time_off_days=self._get_int_value(row, 'paid_time_off_days', 0),
            paid_holidays=self._get_int_value(row, 'paid_holidays', 0),
            paid_sick_days=self._get_int_value(row, 'paid_sick_days', 0),
            paid_parental_leave_weeks=self._get_int_value(row, 'paid_parental_leave_weeks', 0),
            equity_value=self._get_float_value(row, 'equity_value', 0.0),
            other_benefits_value=self._get_float_value(row, 'other_benefits_value', 0.0),
            other_benefits_description=self._get_str_value(row, 'other_benefits_description', '')
        )
    
    def create_template_file(self, filepath: str) -> None:
        """
        Create a template spreadsheet file with all expected columns
        
        Args:
            filepath: Path where the template should be saved (.csv or .xlsx)
        """
        # Define all columns with sample values
        data = {
            # Required fields
            'title': ['Software Engineer'],
            'company': ['Example Corp'],
            'location': ['Austin, TX'],
            'work_location_type': ['Onsite'],  # 'Onsite', 'Remote', or 'Hybrid'
            'employment_type': ['W2'],  # 'W2', '1099', or 'S-Corp'
            'compensation_type': ['Salary'],  # 'Salary' or 'Hourly'
            'base_compensation': [100000],  # Annual salary or hourly rate
            
            # Time calculation fields
            'hours_per_week': [40],
            'weeks_per_year': [50],
            
            # Optional fields - job details
            'bonus_amount': [10000],
            'bonus_guaranteed': [False],
            'signing_bonus': [5000],
            'relocation_package': [2000],
            
            # Tax information
            'state_tax_rate': [0.05],  # 5%
            'local_tax_rate': [0.01],  # 1%
            'self_employment_expenses': [0],  # Costs of being self-employed (health insurance, retirement contributions)
            'business_expenses': [0],  # Deductible expenses (home office, equipment, professional services)
            
            # Cost of living and work conditions
            'cost_of_living_index': [100],
            'commute_time_minutes': [30],
            'commute_cost_monthly': [150],
            'commute_days_per_week': [5],  # Added for hybrid roles
            'expected_tenure_years': [3],
            
            # Commute calculator fields
            'commute_calc_type': ['Direct'],  # 'Direct' or 'Distance-Based'
            'commute_distance_miles': [15],
            'commute_drive_type': ['Mixed'],  # 'City', 'Highway', or 'Mixed'
            'commute_fuel_cost': [3.50],
            'commute_city_mpg': [25.0],
            'commute_highway_mpg': [32.0],
            'commute_combined_mpg': [28.0],
            'commute_include_maintenance': [True],
            
            # Benefits - retirement
            'retirement_match_percent': [0.04],  # 4%
            'retirement_match_limit': [5000],
            
            # Benefits - insurance
            'health_insurance_monthly_premium': [200],
            'health_insurance_coverage_percent': [0.8],  # 80%
            'dental_insurance_monthly_premium': [20],
            'dental_insurance_coverage_percent': [0.8],  # 80%
            'vision_insurance_monthly_premium': [10],
            'vision_insurance_coverage_percent': [0.8],  # 80%
            'life_insurance_coverage': [50000],
            'life_insurance_monthly_premium': [15],
            
            # Benefits - time off
            'paid_time_off_days': [15],
            'paid_holidays': [10],
            'paid_sick_days': [5],
            'paid_parental_leave_weeks': [6],
            
            # Benefits - other
            'equity_value': [10000],
            'other_benefits_value': [2000],
            'other_benefits_description': ['Gym membership, learning budget']
        }
        
        df = pd.DataFrame(data)
        
        # Add a second example row for hourly compensation
        hourly_row = data.copy()
        hourly_row['title'] = ['Web Developer']
        hourly_row['company'] = ['Contractor LLC']
        hourly_row['compensation_type'] = ['Hourly']
        hourly_row['base_compensation'] = [50]  # Hourly rate
        hourly_row['employment_type'] = ['1099']
        
        # Append to dataframe
        hourly_df = pd.DataFrame(hourly_row)
        df = pd.concat([df, hourly_df], ignore_index=True)
        
        # Save the template
        _, ext = os.path.splitext(filepath)
        if ext.lower() == '.csv':
            df.to_csv(filepath, index=False)
        elif ext.lower() in ['.xlsx', '.xls']:
            df.to_excel(filepath, index=False)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Use .csv, .xlsx, or .xls")
    
    def _get_float_value(self, row: Dict[str, Any], column: str, default: float = 0.0) -> float:
        """Safely extract a float value from a row"""
        if column in row and pd.notna(row[column]):
            try:
                return float(row[column])
            except (ValueError, TypeError):
                return default
        return default
    
    def _get_int_value(self, row: Dict[str, Any], column: str, default: int = 0) -> int:
        """Safely extract an integer value from a row"""
        if column in row and pd.notna(row[column]):
            try:
                return int(row[column])
            except (ValueError, TypeError):
                return default
        return default
    
    def _get_bool_value(self, row: Dict[str, Any], column: str, default: bool = False) -> bool:
        """Safely extract a boolean value from a row"""
        if column in row and pd.notna(row[column]):
            if isinstance(row[column], bool):
                return row[column]
            elif isinstance(row[column], (int, float)):
                return bool(row[column])
            elif isinstance(row[column], str):
                return row[column].lower() in ['true', 'yes', 'y', '1', 't']
        return default
    
    def _get_str_value(self, row: Dict[str, Any], column: str, default: str = '') -> str:
        """Safely extract a string value from a row"""
        if column in row and pd.notna(row[column]):
            return str(row[column])
        return default

    def _get_drive_type(self, row: Dict[str, Any]) -> Optional['DriveType']:
        """
        Get drive type enum from row data
        
        Args:
            row: Dictionary of row data
            
        Returns:
            DriveType enum or None if not specified
        """
        from commute_calculator import DriveType
        
        if 'commute_drive_type' not in row or pd.isna(row['commute_drive_type']):
            return None
        
        drive_type_str = str(row['commute_drive_type']).strip().upper()
        
        if drive_type_str == 'CITY':
            return DriveType.CITY
        elif drive_type_str == 'HIGHWAY':
            return DriveType.HIGHWAY
        elif drive_type_str in ['MIXED', 'COMBINED']:
            return DriveType.MIXED
        else:
            # Default to mixed if unrecognized
            return DriveType.MIXED
    
    def _get_commute_calc_type(self, row: Dict[str, Any]) -> 'CommuteCalculationType':
        """
        Get commute calculation type enum from row data
        
        Args:
            row: Dictionary of row data
            
        Returns:
            CommuteCalculationType enum
        """
        from job_offer import CommuteCalculationType
        
        if 'commute_calc_type' not in row or pd.isna(row['commute_calc_type']):
            # Default based on available data
            if 'commute_distance_miles' in row and pd.notna(row['commute_distance_miles']) and float(row['commute_distance_miles']) > 0:
                return CommuteCalculationType.DISTANCE_BASED
            else:
                return CommuteCalculationType.DIRECT
        
        calc_type_str = str(row['commute_calc_type']).strip().upper()
        
        if calc_type_str in ['DISTANCE', 'DISTANCE_BASED', 'DISTANCE-BASED']:
            return CommuteCalculationType.DISTANCE_BASED
        elif calc_type_str in ['DIRECT', 'MANUAL']:
            return CommuteCalculationType.DIRECT
        else:
            # Default to direct if unrecognized
            return CommuteCalculationType.DIRECT