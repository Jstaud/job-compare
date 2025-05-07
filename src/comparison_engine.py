"""
Job offer comparison engine that analyzes multiple job offers and provides comparison metrics.
"""
import json
import os
import pickle
from typing import Dict, List, Optional

from benefits_calculator import BenefitsCalculator
from tax_calculator import TaxCalculator
from job_offer import JobOffer, CommuteCalculationType, WorkLocationType, CompensationType, EmploymentType, Benefits
from commute_calculator import CommuteCalculator, DriveType


class ComparisonEngine:
    """Engine for comparing multiple job offers based on various compensation metrics"""
    
    def __init__(self, data_file: str = "job_offers.pkl"):
        """
        Initialize comparison engine
        
        Args:
            data_file: File path to store saved job offers
        """
        self.job_offers: List[JobOffer] = []
        self.data_file = data_file
        self.benefits_calculator = BenefitsCalculator()
        self.tax_calculator = TaxCalculator()
        self.commute_calculator = CommuteCalculator()
    
    def add_offer(self, offer: JobOffer) -> None:
        """
        Add a job offer to the comparison
        
        Args:
            offer: JobOffer object to add
        """
        self.job_offers.append(offer)
    
    def update_offer(self, index: int, offer: JobOffer) -> None:
        """
        Update an existing job offer
        
        Args:
            index: Index of offer to update
            offer: New JobOffer object to replace existing one
        """
        if 0 <= index < len(self.job_offers):
            self.job_offers[index] = offer
    
    def remove_offer(self, index: int) -> None:
        """
        Remove a job offer from the comparison
        
        Args:
            index: Index of offer to remove
        """
        if 0 <= index < len(self.job_offers):
            self.job_offers.pop(index)
    
    def clear_offers(self) -> None:
        """Remove all job offers from the comparison"""
        self.job_offers = []
    
    def save_offers(self) -> None:
        """Save job offers to file"""
        serialized_offers = []
        
        for offer in self.job_offers:
            offer_dict = {
                'title': offer.title,
                'company': offer.company,
                'location': offer.location,
                'work_location_type': offer.work_location_type.value,
                'employment_type': offer.employment_type.value,
                'compensation_type': offer.compensation_type.value,
                'base_compensation': offer.base_compensation,
                'hours_per_week': offer.hours_per_week,
                'weeks_per_year': offer.weeks_per_year,
                'bonus_amount': offer.bonus_amount,
                'bonus_guaranteed': offer.bonus_guaranteed,
                'signing_bonus': offer.signing_bonus,
                'relocation_package': offer.relocation_package,
                'state_tax_rate': offer.state_tax_rate,
                'local_tax_rate': offer.local_tax_rate,
                'self_employment_expenses': offer.self_employment_expenses,
                'business_expenses': offer.business_expenses,
                'cost_of_living_index': offer.cost_of_living_index,
                'commute_time_minutes': offer.commute_time_minutes,
                'commute_days_per_week': offer.commute_days_per_week,
                'commute_calc_type': offer.commute_calc_type.value,
                'commute_cost_monthly': offer.commute_cost_monthly,
                'commute_distance_miles': offer.commute_distance_miles,
                'commute_drive_type': offer.commute_drive_type.value if offer.commute_drive_type else None,
                'commute_fuel_cost': offer.commute_fuel_cost,
                'commute_city_mpg': offer.commute_city_mpg,
                'commute_highway_mpg': offer.commute_highway_mpg,
                'commute_combined_mpg': offer.commute_combined_mpg,
                'commute_include_maintenance': offer.commute_include_maintenance,
                'expected_hours_per_week': offer.expected_hours_per_week,
                'expected_tenure_years': offer.expected_tenure_years,
                'benefits': {
                    'retirement_match_percent': offer.benefits.retirement_match_percent,
                    'retirement_match_limit': offer.benefits.retirement_match_limit,
                    'health_insurance_monthly_premium': offer.benefits.health_insurance_monthly_premium,
                    'health_insurance_coverage_percent': offer.benefits.health_insurance_coverage_percent,
                    'dental_insurance_monthly_premium': offer.benefits.dental_insurance_monthly_premium,
                    'dental_insurance_coverage_percent': offer.benefits.dental_insurance_coverage_percent,
                    'vision_insurance_monthly_premium': offer.benefits.vision_insurance_monthly_premium,
                    'vision_insurance_coverage_percent': offer.benefits.vision_insurance_coverage_percent,
                    'life_insurance_coverage': offer.benefits.life_insurance_coverage,
                    'life_insurance_monthly_premium': offer.benefits.life_insurance_monthly_premium,
                    'paid_time_off_days': offer.benefits.paid_time_off_days,
                    'paid_holidays': offer.benefits.paid_holidays,
                    'paid_sick_days': offer.benefits.paid_sick_days,
                    'paid_parental_leave_weeks': offer.benefits.paid_parental_leave_weeks,
                    'equity_value': offer.benefits.equity_value,
                    'other_benefits_value': offer.benefits.other_benefits_value,
                    'other_benefits_description': offer.benefits.other_benefits_description
                }
            }
            serialized_offers.append(offer_dict)
        
        with open(self.data_file, 'wb') as f:
            pickle.dump(serialized_offers, f)
    
    def load_offers(self) -> bool:
        """
        Load job offers from file
        
        Returns:
            True if offers were loaded successfully, False otherwise
        """
        if not os.path.exists(self.data_file):
            return False
        
        try:
            with open(self.data_file, 'rb') as f:
                serialized_offers = pickle.load(f)
            
            self.job_offers = []
            
            for offer_dict in serialized_offers:
                # Map string values back to enums
                work_location_type = WorkLocationType(offer_dict['work_location_type'])
                employment_type = EmploymentType(offer_dict['employment_type'])
                compensation_type = CompensationType(offer_dict['compensation_type'])
                commute_calc_type = CommuteCalculationType(offer_dict['commute_calc_type'])
                
                # Map drive type if it exists
                commute_drive_type = None
                if offer_dict.get('commute_drive_type'):
                    commute_drive_type = DriveType(offer_dict['commute_drive_type'])
                
                # Create Benefits object
                benefits_dict = offer_dict.get('benefits', {})
                benefits = Benefits(
                    retirement_match_percent=benefits_dict.get('retirement_match_percent', 0),
                    retirement_match_limit=benefits_dict.get('retirement_match_limit', 0),
                    health_insurance_monthly_premium=benefits_dict.get('health_insurance_monthly_premium', 0),
                    health_insurance_coverage_percent=benefits_dict.get('health_insurance_coverage_percent', 0),
                    dental_insurance_monthly_premium=benefits_dict.get('dental_insurance_monthly_premium', 0),
                    dental_insurance_coverage_percent=benefits_dict.get('dental_insurance_coverage_percent', 0),
                    vision_insurance_monthly_premium=benefits_dict.get('vision_insurance_monthly_premium', 0),
                    vision_insurance_coverage_percent=benefits_dict.get('vision_insurance_coverage_percent', 0),
                    life_insurance_coverage=benefits_dict.get('life_insurance_coverage', 0),
                    life_insurance_monthly_premium=benefits_dict.get('life_insurance_monthly_premium', 0),
                    paid_time_off_days=benefits_dict.get('paid_time_off_days', 0),
                    paid_holidays=benefits_dict.get('paid_holidays', 0),
                    paid_sick_days=benefits_dict.get('paid_sick_days', 0),
                    paid_parental_leave_weeks=benefits_dict.get('paid_parental_leave_weeks', 0),
                    equity_value=benefits_dict.get('equity_value', 0),
                    other_benefits_value=benefits_dict.get('other_benefits_value', 0),
                    other_benefits_description=benefits_dict.get('other_benefits_description', "")
                )
                
                offer = JobOffer(
                    title=offer_dict['title'],
                    company=offer_dict['company'],
                    location=offer_dict['location'],
                    work_location_type=work_location_type,
                    employment_type=employment_type,
                    compensation_type=compensation_type,
                    base_compensation=offer_dict['base_compensation'],
                    hours_per_week=offer_dict.get('hours_per_week', 40.0),
                    weeks_per_year=offer_dict.get('weeks_per_year', 50.0),
                    bonus_amount=offer_dict.get('bonus_amount', 0),
                    bonus_guaranteed=offer_dict.get('bonus_guaranteed', False),
                    signing_bonus=offer_dict.get('signing_bonus', 0),
                    relocation_package=offer_dict.get('relocation_package', 0),
                    benefits=benefits,
                    state_tax_rate=offer_dict.get('state_tax_rate', 0),
                    local_tax_rate=offer_dict.get('local_tax_rate', 0),
                    self_employment_expenses=offer_dict.get('self_employment_expenses', 0),
                    business_expenses=offer_dict.get('business_expenses', 0),
                    cost_of_living_index=offer_dict.get('cost_of_living_index', 100),
                    commute_time_minutes=offer_dict.get('commute_time_minutes', 0),
                    commute_days_per_week=offer_dict.get('commute_days_per_week', 5),
                    commute_calc_type=commute_calc_type,
                    commute_cost_monthly=offer_dict.get('commute_cost_monthly', 0),
                    commute_distance_miles=offer_dict.get('commute_distance_miles', 0),
                    commute_drive_type=commute_drive_type,
                    commute_fuel_cost=offer_dict.get('commute_fuel_cost', 0),
                    commute_city_mpg=offer_dict.get('commute_city_mpg', 0),
                    commute_highway_mpg=offer_dict.get('commute_highway_mpg', 0),
                    commute_combined_mpg=offer_dict.get('commute_combined_mpg', 0),
                    commute_include_maintenance=offer_dict.get('commute_include_maintenance', True),
                    expected_hours_per_week=offer_dict.get('expected_hours_per_week', 40.0),
                    expected_tenure_years=offer_dict.get('expected_tenure_years', 3)
                )
                
                self.job_offers.append(offer)
            
            return True
        except Exception as e:
            print(f"Error loading offers: {e}")
            return False
    
    def get_offers(self) -> List[JobOffer]:
        """
        Get all job offers
        
        Returns:
            List of JobOffer objects
        """
        return self.job_offers
    
    def get_offer(self, index: int) -> Optional[JobOffer]:
        """
        Get a specific job offer
        
        Args:
            index: Index of offer to retrieve
            
        Returns:
            JobOffer object or None if index is invalid
        """
        if 0 <= index < len(self.job_offers):
            return self.job_offers[index]
        return None
    
    def calculate_effective_tax_rate(self, offer: JobOffer) -> float:
        """
        Calculate the effective tax rate for a job offer
        
        Args:
            offer: JobOffer object
            
        Returns:
            Effective tax rate as a decimal
        """
        # Extract state and locality from location if possible
        location_parts = offer.location.split(", ")
        
        # Handle state abbreviation - location typically has format "City, ST"
        state = location_parts[-1] if len(location_parts) > 1 else ""
        
        # For simplicity in testing, if state is more than 2 characters, 
        # we'll use the last 2 characters as the abbreviation
        if len(state) > 2:
            state = state[-2:]
            
        locality = location_parts[0] if len(location_parts) > 1 else ""
        
        # Use the tax calculator with parameters it expects
        return self.tax_calculator.calculate_effective_tax_rate(
            income=offer.base_salary,
            state=state,
            locality=locality,
            employment_type=offer.employment_type,
            filing_status="single"  # Default to single filing status
        )
    
    def calculate_total_benefits_value(self, offer: JobOffer) -> Dict:
        """
        Calculate the total value of benefits for a job offer
        
        Args:
            offer: JobOffer object
            
        Returns:
            Dictionary with benefits values and total
        """
        return self.benefits_calculator.calculate_total_benefits_value(
            benefits=offer.benefits,
            salary=offer.base_salary
        )
    
    def compare_offers(self) -> List[Dict]:
        """
        Compare job offers and return detailed analysis
        
        Returns:
            List of dictionaries with comparison results for each offer
        """
        results = []
        
        for offer in self.job_offers:
            # Calculate effective tax rate
            effective_tax_rate = self.calculate_effective_tax_rate(offer)
            
            # Calculate benefits value
            benefits_value = self.calculate_total_benefits_value(offer)
            
            # Calculate total compensation
            compensation = offer.calculate_total_compensation(
                effective_tax_rate=effective_tax_rate,
                commute_calculator=self.commute_calculator
            )
            
            # Add benefits value to total annual value
            total_benefits_value = benefits_value["total"]
            compensation["total_annual_value"] = compensation["annual_gross_income"] + total_benefits_value
            
            # Add metrics to results
            result = {
                "offer": offer,
                "effective_tax_rate": effective_tax_rate,
                "benefits_value": benefits_value,
                "compensation": compensation
            }
            
            results.append(result)
        
        return results

    def get_rankings(self, results: List[Dict]) -> Dict:
        """
        Generate rankings of job offers by different criteria
        
        Args:
            results: List of dictionaries with comparison results from compare_offers
            
        Returns:
            Dictionary with rankings by different criteria
        """
        rankings = {}
        
        # Check if we have results to rank
        if not results:
            return rankings
        
        # Rank by total annual value
        total_value_ranking = []
        sorted_by_value = sorted(
            results, 
            key=lambda x: x["compensation"]["total_annual_value"], 
            reverse=True
        )
        
        for i, result in enumerate(sorted_by_value):
            total_value_ranking.append({
                "rank": i + 1,
                "company": result["offer"].company,
                "title": result["offer"].title,
                "value": result["compensation"]["total_annual_value"]
            })
        
        rankings["total_annual_value"] = {
            "label": "Total Annual Value",
            "description": "Total annual value including salary, bonuses, and benefits",
            "ranking": total_value_ranking
        }
        
        # Rank by take-home pay
        take_home_ranking = []
        sorted_by_take_home = sorted(
            results, 
            key=lambda x: x["compensation"]["take_home_pay"], 
            reverse=True
        )
        
        for i, result in enumerate(sorted_by_take_home):
            take_home_ranking.append({
                "rank": i + 1,
                "company": result["offer"].company,
                "title": result["offer"].title,
                "value": result["compensation"]["take_home_pay"]
            })
        
        rankings["take_home_pay"] = {
            "label": "Take-Home Pay",
            "description": "Annual take-home pay after taxes and deductions",
            "ranking": take_home_ranking
        }
        
        # Rank by hourly rate
        hourly_ranking = []
        sorted_by_hourly = sorted(
            results, 
            key=lambda x: x["compensation"]["effective_hourly_rate"], 
            reverse=True
        )
        
        for i, result in enumerate(sorted_by_hourly):
            hourly_ranking.append({
                "rank": i + 1,
                "company": result["offer"].company,
                "title": result["offer"].title,
                "value": result["compensation"]["effective_hourly_rate"]
            })
        
        rankings["hourly_rate"] = {
            "label": "Effective Hourly Rate",
            "description": "Effective hourly rate based on total compensation and hours worked",
            "ranking": hourly_ranking
        }
        
        # Rank by benefits value
        benefits_ranking = []
        sorted_by_benefits = sorted(
            results, 
            key=lambda x: x["benefits_value"]["total"], 
            reverse=True
        )
        
        for i, result in enumerate(sorted_by_benefits):
            benefits_ranking.append({
                "rank": i + 1,
                "company": result["offer"].company,
                "title": result["offer"].title,
                "value": result["benefits_value"]["total"]
            })
        
        rankings["benefits_value"] = {
            "label": "Benefits Value",
            "description": "Total annual value of all benefits",
            "ranking": benefits_ranking
        }
        
        # Rank by adjusted cost of living
        cola_ranking = []
        for result in results:
            # Adjust salary by cost of living index
            cola_adjusted = result["compensation"]["total_annual_value"] * (100 / result["offer"].cost_of_living_index)
            result["cola_adjusted"] = cola_adjusted
        
        sorted_by_cola = sorted(
            results, 
            key=lambda x: x["cola_adjusted"], 
            reverse=True
        )
        
        for i, result in enumerate(sorted_by_cola):
            cola_ranking.append({
                "rank": i + 1,
                "company": result["offer"].company,
                "title": result["offer"].title,
                "value": result["cola_adjusted"]
            })
        
        rankings["cost_of_living_adjusted"] = {
            "label": "Cost of Living Adjusted Value",
            "description": "Total annual value adjusted for local cost of living",
            "ranking": cola_ranking
        }
        
        return rankings
    
    def get_recommendations(self, results: List[Dict]) -> Dict:
        """
        Generate recommendations based on comparison results
        
        Args:
            results: List of dictionaries with comparison results from compare_offers
            
        Returns:
            Dictionary with recommendations for different criteria
        """
        recommendations = {}
        
        # Check if we have results to recommend
        if not results:
            return recommendations
        
        # Get rankings
        rankings = self.get_rankings(results)
        
        # Best overall (total annual value)
        if "total_annual_value" in rankings:
            top_value = rankings["total_annual_value"]["ranking"][0]
            recommendations["best_overall"] = top_value["company"]
        
        # Best take-home pay
        if "take_home_pay" in rankings:
            top_take_home = rankings["take_home_pay"]["ranking"][0]
            recommendations["best_take_home_pay"] = top_take_home["company"]
        
        # Best hourly rate
        if "hourly_rate" in rankings:
            top_hourly = rankings["hourly_rate"]["ranking"][0]
            recommendations["best_hourly_rate"] = top_hourly["company"]
        
        # Best benefits
        if "benefits_value" in rankings:
            top_benefits = rankings["benefits_value"]["ranking"][0]
            recommendations["best_benefits"] = top_benefits["company"]
        
        # Best adjusted for cost of living
        if "cost_of_living_adjusted" in rankings:
            top_cola = rankings["cost_of_living_adjusted"]["ranking"][0]
            recommendations["best_cost_adjusted"] = top_cola["company"]
        
        # Best commute (shortest)
        commute_best = min(results, key=lambda x: x["offer"].commute_time_minutes)
        recommendations["best_commute"] = commute_best["offer"].company
        
        # Best work-life balance (simplified calculation)
        work_life_scores = []
        for result in results:
            offer = result["offer"]
            # Calculate a work-life score based on hours, commute, and PTO
            pto_days = offer.benefits.paid_time_off_days + offer.benefits.paid_holidays + offer.benefits.paid_sick_days
            weekly_hours = offer.hours_per_week
            commute_hours = (offer.commute_time_minutes / 60) * offer.commute_days_per_week
            
            # Lower score is better (fewer hours working/commuting, more time off)
            score = (weekly_hours + commute_hours) * 52 - (pto_days * 8)
            work_life_scores.append((offer.company, score))
        
        # Sort by score (lower is better)
        work_life_scores.sort(key=lambda x: x[1])
        if work_life_scores:
            recommendations["best_work_life_balance"] = work_life_scores[0][0]
        
        return recommendations