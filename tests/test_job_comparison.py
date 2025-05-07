#!/usr/bin/env python3
"""
Test script to generate sample job offer spreadsheets and test the commute calculator functionality.
"""

import os
import sys
import pandas as pd
import unittest

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from job_offer import JobOffer, EmploymentType, WorkLocationType, CompensationType
from commute_calculator import CommuteCalculator, DriveType
from spreadsheet_parser import SpreadsheetParser
from comparison_engine import ComparisonEngine
from benefits_calculator import BenefitsCalculator
from tax_calculator import TaxCalculator


class TestJobComparisonTool(unittest.TestCase):
    """Test case for the job comparison tool"""
    
    def setUp(self):
        """Set up the test environment"""
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        self.parser = SpreadsheetParser()
        self.commute_calculator = CommuteCalculator()
        self.comparison_engine = ComparisonEngine()
        
    def test_generate_and_parse_test_data(self):
        """Generate test data spreadsheets and verify parsing"""
        # Generate test data spreadsheet
        csv_path = os.path.join(self.test_data_dir, 'test_job_offers.csv')
        xlsx_path = os.path.join(self.test_data_dir, 'test_job_offers.xlsx')
        
        # Create a template first
        self.parser.create_template_file(csv_path)
        
        # Load the template and modify it with our test data
        df = pd.read_csv(csv_path)
        
        # Clear the initial sample data and create our own test rows
        df = pd.DataFrame(columns=df.columns)
        
        # Add test job offers
        test_offers = [
            # W2 Employee with salary compensation and on-site work
            {
                'title': 'Software Engineer',
                'company': 'TechCorp',
                'location': 'Austin, TX',
                'work_location_type': 'Onsite',
                'employment_type': 'W2',
                'compensation_type': 'Salary',
                'base_compensation': 120000,
                'hours_per_week': 40,
                'weeks_per_year': 50,
                'bonus_amount': 15000,
                'bonus_guaranteed': False,
                'signing_bonus': 10000,
                'relocation_package': 5000,
                'state_tax_rate': 0.05,
                'local_tax_rate': 0.01,
                'self_employment_expenses': 0,
                'business_expenses': 0,
                'cost_of_living_index': 110,
                'commute_time_minutes': 30,
                'commute_cost_monthly': 250,
                'commute_days_per_week': 5,
                'expected_tenure_years': 3,
                'retirement_match_percent': 0.06,
                'retirement_match_limit': 7000,
                'health_insurance_monthly_premium': 150,
                'health_insurance_coverage_percent': 0.9,
                'dental_insurance_monthly_premium': 15,
                'dental_insurance_coverage_percent': 0.8,
                'vision_insurance_monthly_premium': 10,
                'vision_insurance_coverage_percent': 0.8,
                'life_insurance_coverage': 100000,
                'life_insurance_monthly_premium': 20,
                'paid_time_off_days': 20,
                'paid_holidays': 10,
                'paid_sick_days': 10,
                'paid_parental_leave_weeks': 8,
                'equity_value': 15000,
                'other_benefits_value': 3000,
                'other_benefits_description': 'Fitness allowance, education budget'
            },
            # 1099 Contractor with hourly compensation and remote work
            {
                'title': 'DevOps Consultant',
                'company': 'RemoteOps',
                'location': 'Remote',
                'work_location_type': 'Remote',
                'employment_type': '1099',
                'compensation_type': 'Hourly',
                'base_compensation': 85,
                'hours_per_week': 35,
                'weeks_per_year': 48,
                'bonus_amount': 0,
                'bonus_guaranteed': False,
                'signing_bonus': 0,
                'relocation_package': 0,
                'state_tax_rate': 0.06,
                'local_tax_rate': 0.0,
                'self_employment_expenses': 12000,
                'business_expenses': 8000,
                'cost_of_living_index': 90,
                'commute_time_minutes': 0,
                'commute_cost_monthly': 0,
                'commute_days_per_week': 0,
                'expected_tenure_years': 2,
                'retirement_match_percent': 0.0,
                'retirement_match_limit': 0,
                'health_insurance_monthly_premium': 800,
                'health_insurance_coverage_percent': 0.0,
                'dental_insurance_monthly_premium': 50,
                'dental_insurance_coverage_percent': 0.0,
                'vision_insurance_monthly_premium': 25,
                'vision_insurance_coverage_percent': 0.0,
                'life_insurance_coverage': 0,
                'life_insurance_monthly_premium': 0,
                'paid_time_off_days': 0,
                'paid_holidays': 0,
                'paid_sick_days': 0,
                'paid_parental_leave_weeks': 0,
                'equity_value': 0,
                'other_benefits_value': 0,
                'other_benefits_description': ''
            },
            # S-Corp with salary compensation and hybrid work
            {
                'title': 'Product Manager',
                'company': 'FlexiTech',
                'location': 'San Francisco, CA',
                'work_location_type': 'Hybrid',
                'employment_type': 'S-Corp',
                'compensation_type': 'Salary',
                'base_compensation': 150000,
                'hours_per_week': 45,
                'weeks_per_year': 50,
                'bonus_amount': 30000,
                'bonus_guaranteed': True,
                'signing_bonus': 20000,
                'relocation_package': 10000,
                'state_tax_rate': 0.09,
                'local_tax_rate': 0.02,
                'self_employment_expenses': 20000,
                'business_expenses': 15000,
                'cost_of_living_index': 180,
                'commute_time_minutes': 45,
                'commute_days_per_week': 3,
                'expected_tenure_years': 4,
                'retirement_match_percent': 0.0,
                'retirement_match_limit': 0,
                'health_insurance_monthly_premium': 600,
                'health_insurance_coverage_percent': 0.0,
                'dental_insurance_monthly_premium': 45,
                'dental_insurance_coverage_percent': 0.0,
                'vision_insurance_monthly_premium': 20,
                'vision_insurance_coverage_percent': 0.0,
                'life_insurance_coverage': 0,
                'life_insurance_monthly_premium': 0,
                'paid_time_off_days': 0,
                'paid_holidays': 10,
                'paid_sick_days': 5,
                'paid_parental_leave_weeks': 0,
                'equity_value': 50000,
                'other_benefits_value': 5000,
                'other_benefits_description': 'Home office allowance, wellness program'
            }
        ]
        
        # Add each test offer to the dataframe - using a different approach to avoid the FutureWarning
        # Create a new DataFrame from all offers at once instead of concatenating one by one
        df = pd.DataFrame(test_offers)
        
        # Save as both CSV and XLSX
        df.to_csv(csv_path, index=False)
        df.to_excel(xlsx_path, index=False)
        
        print(f"Test data generated: {csv_path} and {xlsx_path}")
        
        # Now test parsing the CSV file
        job_offers = self.parser.parse_file(csv_path)
        self.assertEqual(len(job_offers), 3, "Should have parsed 3 job offers")
        
        # Verify the first job offer
        offer1 = job_offers[0]
        self.assertEqual(offer1.title, "Software Engineer")
        self.assertEqual(offer1.company, "TechCorp")
        self.assertEqual(offer1.work_location_type, WorkLocationType.ONSITE)
        self.assertEqual(offer1.employment_type, EmploymentType.W2)
        self.assertEqual(offer1.compensation_type, CompensationType.SALARY)
        self.assertEqual(offer1.base_compensation, 120000)
        
        # Verify the second job offer
        offer2 = job_offers[1]
        self.assertEqual(offer2.title, "DevOps Consultant")
        self.assertEqual(offer2.company, "RemoteOps")
        self.assertEqual(offer2.work_location_type, WorkLocationType.REMOTE)
        self.assertEqual(offer2.employment_type, EmploymentType.CONTRACTOR_1099)
        self.assertEqual(offer2.compensation_type, CompensationType.HOURLY)
        self.assertEqual(offer2.base_compensation, 85)
        
        # Verify the third job offer
        offer3 = job_offers[2]
        self.assertEqual(offer3.title, "Product Manager")
        self.assertEqual(offer3.company, "FlexiTech")
        self.assertEqual(offer3.work_location_type, WorkLocationType.HYBRID)
        self.assertEqual(offer3.employment_type, EmploymentType.S_CORP)
        self.assertEqual(offer3.compensation_type, CompensationType.SALARY)
        self.assertEqual(offer3.base_compensation, 150000)
        
        print("Successfully parsed job offers from CSV file.")
        
        # Also test parsing the XLSX file
        job_offers_xlsx = self.parser.parse_file(xlsx_path)
        self.assertEqual(len(job_offers_xlsx), 3, "Should have parsed 3 job offers from XLSX")
        
        print("Successfully parsed job offers from XLSX file.")
        
        # Instead of returning job_offers, store them as an instance variable
        self.parsed_job_offers = job_offers

    def test_commute_calculator(self):
        """Test the commute calculator functionality"""
        # Test various commute calculations
        
        # Case 1: City driving
        city_result = self.commute_calculator.calculate_monthly_commute_cost(
            distance_miles=15,
            drive_type=DriveType.CITY,
            days_per_week=5,
            fuel_cost_per_gallon=3.50,
            city_mpg=25.0,
            include_maintenance=True
        )
        
        print(f"City driving commute cost: ${city_result['total_cost']:.2f} per month")
        self.assertGreater(city_result['total_cost'], 0, "Commute cost should be positive")
        
        # Case 2: Highway driving
        highway_result = self.commute_calculator.calculate_monthly_commute_cost(
            distance_miles=30,
            drive_type=DriveType.HIGHWAY,
            days_per_week=5,
            fuel_cost_per_gallon=3.50,
            highway_mpg=32.0,
            include_maintenance=True
        )
        
        print(f"Highway driving commute cost: ${highway_result['total_cost']:.2f} per month")
        self.assertGreater(highway_result['total_cost'], 0, "Commute cost should be positive")
        
        # Case 3: Mixed driving
        mixed_result = self.commute_calculator.calculate_monthly_commute_cost(
            distance_miles=20,
            drive_type=DriveType.MIXED,
            days_per_week=5,
            fuel_cost_per_gallon=3.50,
            city_mpg=25.0,
            highway_mpg=32.0,
            combined_mpg=28.0,
            include_maintenance=True
        )
        
        print(f"Mixed driving commute cost: ${mixed_result['total_cost']:.2f} per month")
        self.assertGreater(mixed_result['total_cost'], 0, "Commute cost should be positive")
        
        # Case 4: Hybrid work schedule (3 days per week)
        hybrid_result = self.commute_calculator.calculate_monthly_commute_cost(
            distance_miles=20,
            drive_type=DriveType.MIXED,
            days_per_week=3,
            fuel_cost_per_gallon=3.50,
            combined_mpg=28.0,
            include_maintenance=True
        )
        
        print(f"Hybrid schedule commute cost: ${hybrid_result['total_cost']:.2f} per month")
        self.assertGreater(hybrid_result['total_cost'], 0, "Commute cost should be positive")
        self.assertLess(hybrid_result['total_cost'], mixed_result['total_cost'], 
                       "Hybrid schedule should cost less than full-time")
                       
        # Verify the ratio is proportional to days worked
        expected_ratio = 3 / 5
        actual_ratio = hybrid_result['total_cost'] / mixed_result['total_cost']
        self.assertAlmostEqual(actual_ratio, expected_ratio, delta=0.01, 
                              msg="Hybrid schedule cost should be proportional to days worked")
    
    def test_comparison_engine(self):
        """Test the comparison engine with job offers"""
        # Get the test job offers
        self.test_generate_and_parse_test_data()
        
        # Add them to the comparison engine
        for offer in self.parsed_job_offers:
            self.comparison_engine.add_offer(offer)
        
        # Generate the comparison
        results = self.comparison_engine.compare_offers()
        
        # Validate results
        self.assertEqual(len(results), 3, "Should have 3 result entries")
        
        # Print out the summary of each offer for manual verification
        for i, result in enumerate(results):
            offer = self.parsed_job_offers[i]
            comp = result["compensation"]
            
            print(f"\nOffer #{i+1}: {offer.company} - {offer.title}")
            print(f"  Base Compensation: ${offer.base_compensation:,.2f} " +
                  f"({'hourly' if offer.compensation_type == CompensationType.HOURLY else 'annual'})")
            print(f"  Annual Salary Equivalent: ${offer.base_salary:,.2f}")
            print(f"  Total Annual Value: ${comp['total_annual_value']:,.2f}")
            print(f"  Take-Home Pay: ${comp['take_home_pay']:,.2f}")
            print(f"  Effective Tax Rate: {result['effective_tax_rate'] * 100:.1f}%")
            
            # Verify specific calculations
            self.assertGreater(comp['total_annual_value'], 0, "Total annual value should be positive")
            self.assertGreaterEqual(comp['annual_gross_income'], offer.base_salary, 
                                  "Annual gross income should be at least the base salary")
            
            # Commute cost verification
            if offer.work_location_type == WorkLocationType.REMOTE:
                self.assertEqual(comp['annual_commute_cost'], 0, 
                                "Remote work should have no commute cost")
            elif offer.work_location_type == WorkLocationType.HYBRID:
                self.assertEqual(offer.commute_days_per_week, 3, 
                                "Hybrid role should have 3 office days per week")
                
        # Verify rankings
        print("\nOffer Rankings:")
        for ranking_type, ranking_data in self.comparison_engine.get_rankings(results).items():
            print(f"  {ranking_data['label']}:")
            for rank in ranking_data['ranking']:
                print(f"    {rank['rank']}. {rank['company']} - ${rank['value']:,.2f}")
                
        # Verify recommendations
        recommendations = self.comparison_engine.get_recommendations(results)
        print("\nRecommendations:")
        for key, company in recommendations.items():
            print(f"  {key.replace('_', ' ').title()}: {company}")


if __name__ == "__main__":
    unittest.main()