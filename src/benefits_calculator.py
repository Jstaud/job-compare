"""
Benefits calculator to estimate the monetary value of various benefits
"""

from typing import Dict, List, Optional
from job_offer import Benefits


class BenefitsCalculator:
    def __init__(self):
        # Average costs for different types of insurance
        self.avg_health_insurance_cost = 7739  # Average annual premium for single coverage
        self.avg_family_health_insurance_cost = 22221  # Average annual premium for family coverage
        self.avg_dental_insurance_cost = 456  # Average annual premium for single dental
        self.avg_vision_insurance_cost = 168  # Average annual vision premium
        self.avg_life_insurance_cost = 160  # Average annual life insurance premium (basic coverage)
        
        # Average retirement match statistics
        self.avg_401k_match_percent = 0.04  # 4% is a common match rate
        self.avg_401k_match_limit = 5000  # Rough estimate in dollars
        
        # Average PTO values
        self.avg_pto_days = 15  # U.S. average PTO days
        self.avg_paid_holidays = 10  # U.S. average paid holidays
        self.avg_sick_days = 8  # U.S. average sick leave
        
        # Parental leave
        self.avg_parental_leave_weeks = 12  # FMLA standard
    
    def estimate_insurance_value(self, coverage_type: str, premium: float, 
                                coverage_percent: float, family_coverage: bool = False) -> float:
        """
        Estimate the value of insurance benefits
        
        Args:
            coverage_type: Type of insurance ("health", "dental", "vision")
            premium: Monthly premium cost to employee
            coverage_percent: Percentage of expenses covered by plan
            family_coverage: Whether this is individual or family coverage
            
        Returns:
            Estimated annual value of the benefit
        """
        # Annual premium paid by employee
        annual_premium = premium * 12
        
        # Estimate the market value based on average costs
        if coverage_type.lower() == "health":
            market_value = self.avg_family_health_insurance_cost if family_coverage else self.avg_health_insurance_cost
        elif coverage_type.lower() == "dental":
            market_value = self.avg_dental_insurance_cost * (2 if family_coverage else 1)
        elif coverage_type.lower() == "vision":
            market_value = self.avg_vision_insurance_cost * (2 if family_coverage else 1)
        else:
            market_value = 0
        
        # Value to employee is market value times coverage quality minus premiums paid
        value = market_value * coverage_percent - annual_premium
        
        return max(0, value)  # Ensure value isn't negative
    
    def estimate_life_insurance_value(self, coverage_amount: float, monthly_premium: float) -> float:
        """
        Estimate the value of life insurance benefits
        
        Args:
            coverage_amount: Coverage amount in dollars
            monthly_premium: Monthly premium cost to employee
            
        Returns:
            Estimated annual value of the benefit
        """
        # Convert to annual premium
        annual_premium = monthly_premium * 12
        
        # Basic value estimation: $1 per $1000 of coverage, minus premium
        estimated_value = (coverage_amount / 1000) - annual_premium
        
        return max(0, estimated_value)  # Ensure value isn't negative
    
    def estimate_retirement_value(self, match_percent: float, match_limit: float,
                                 salary: float) -> float:
        """
        Estimate the value of retirement benefits
        
        Args:
            match_percent: Employer match percentage
            match_limit: Maximum annual employer match
            salary: Annual salary
            
        Returns:
            Estimated annual value of retirement benefits
        """
        # Calculate the match amount based on salary and match percentage
        potential_match = salary * match_percent
        
        # Cap at the match limit
        actual_match = min(potential_match, match_limit)
        
        return actual_match
    
    def estimate_time_off_value(self, daily_rate: float, pto_days: int, 
                               holidays: int, sick_days: int) -> float:
        """
        Estimate the value of paid time off
        
        Args:
            daily_rate: Daily pay rate
            pto_days: Annual PTO days
            holidays: Annual paid holidays
            sick_days: Annual paid sick days
            
        Returns:
            Estimated annual value of paid time off
        """
        total_days = pto_days + holidays + sick_days
        return total_days * daily_rate
    
    def estimate_parental_leave_value(self, weekly_rate: float, weeks: int) -> float:
        """
        Estimate the value of paid parental leave
        
        Args:
            weekly_rate: Weekly pay rate
            weeks: Number of weeks of paid leave
            
        Returns:
            Value of paid parental leave (amortized over typical career span)
        """
        # Assuming average of 2 children per employee over career
        # and amortizing over 20 years of work
        value_per_leave = weekly_rate * weeks
        amortized_value = value_per_leave * 2 / 20
        
        return amortized_value
    
    def calculate_total_benefits_value(self, benefits: Benefits, salary: float) -> Dict[str, float]:
        """
        Calculate the total annual value of all benefits
        
        Args:
            benefits: Benefits object with all benefit details
            salary: Annual salary for calculations
            
        Returns:
            Dictionary with values for each benefit type and total
        """
        daily_rate = salary / 260  # Approximate workdays in a year
        weekly_rate = salary / 52
        
        result = {}
        
        # Retirement
        result["retirement"] = self.estimate_retirement_value(
            benefits.retirement_match_percent, 
            benefits.retirement_match_limit,
            salary
        )
        
        # Health insurance
        result["health_insurance"] = self.estimate_insurance_value(
            "health", 
            benefits.health_insurance_monthly_premium,
            benefits.health_insurance_coverage_percent
        )
        
        # Dental insurance
        result["dental_insurance"] = self.estimate_insurance_value(
            "dental", 
            benefits.dental_insurance_monthly_premium,
            benefits.dental_insurance_coverage_percent
        )
        
        # Vision insurance
        result["vision_insurance"] = self.estimate_insurance_value(
            "vision", 
            benefits.vision_insurance_monthly_premium,
            benefits.vision_insurance_coverage_percent
        )
        
        # Life insurance (updated to use new method)
        result["life_insurance"] = self.estimate_life_insurance_value(
            benefits.life_insurance_coverage,
            benefits.life_insurance_monthly_premium
        )
        
        # Time off
        result["time_off"] = self.estimate_time_off_value(
            daily_rate,
            benefits.paid_time_off_days,
            benefits.paid_holidays,
            benefits.paid_sick_days
        )
        
        # Parental leave
        result["parental_leave"] = self.estimate_parental_leave_value(
            weekly_rate,
            benefits.paid_parental_leave_weeks
        )
        
        # Other benefits
        result["equity"] = benefits.equity_value
        result["other"] = benefits.other_benefits_value
        
        # Calculate total
        result["total"] = sum(result.values())
        
        return result