"""
Job Offer class to represent a single job offer with all its details
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from commute_calculator import DriveType


class EmploymentType(Enum):
    W2 = "W2 Employee"
    CONTRACTOR_1099 = "1099 Contractor"
    S_CORP = "S-Corporation"


class WorkLocationType(Enum):
    ONSITE = "On-site"
    REMOTE = "Remote"
    HYBRID = "Hybrid"


class CompensationType(Enum):
    SALARY = "Annual Salary"
    HOURLY = "Hourly Rate"


class CommuteCalculationType(Enum):
    DIRECT = "Direct Cost"
    DISTANCE_BASED = "Distance-Based Calculation"


@dataclass
class Benefits:
    # 401k matching as a percentage
    retirement_match_percent: float = 0.0
    retirement_match_limit: float = 0.0  # Annual dollar limit
    
    # Insurance monthly premiums and coverage
    health_insurance_monthly_premium: float = 0.0
    health_insurance_coverage_percent: float = 0.0
    dental_insurance_monthly_premium: float = 0.0
    dental_insurance_coverage_percent: float = 0.0
    vision_insurance_monthly_premium: float = 0.0
    vision_insurance_coverage_percent: float = 0.0
    life_insurance_coverage: float = 0.0
    life_insurance_monthly_premium: float = 0.0  # Added life insurance premium
    
    # Time off
    paid_time_off_days: int = 0
    paid_holidays: int = 0
    paid_sick_days: int = 0
    paid_parental_leave_weeks: int = 0
    
    # Other benefits
    equity_value: float = 0.0  # Estimated value of equity/stock options
    other_benefits_value: float = 0.0  # Estimated value of other benefits
    other_benefits_description: str = ""
    
    def calculate_annual_value(self) -> Dict[str, float]:
        """Calculate the estimated annual value of all benefits"""
        benefit_values = {}
        
        # These are placeholder calculations that should be refined
        benefit_values["retirement"] = self.retirement_match_percent * self.retirement_match_limit
        
        health_annual = 12 * self.health_insurance_monthly_premium
        dental_annual = 12 * self.dental_insurance_monthly_premium
        vision_annual = 12 * self.vision_insurance_monthly_premium
        life_annual = 12 * self.life_insurance_monthly_premium
        
        benefit_values["health_insurance"] = health_annual * self.health_insurance_coverage_percent
        benefit_values["dental_insurance"] = dental_annual * self.dental_insurance_coverage_percent
        benefit_values["vision_insurance"] = vision_annual * self.vision_insurance_coverage_percent
        benefit_values["life_insurance"] = self.life_insurance_coverage / 1000 - life_annual  # Adjusted to consider premium
        
        # Time off value is calculated in the job offer based on daily rate
        benefit_values["equity"] = self.equity_value
        benefit_values["other"] = self.other_benefits_value
        
        return benefit_values


@dataclass
class CommuteDetails:
    """Details about commute for cost calculations"""
    distance_miles: float = 0.0
    drive_type: DriveType = DriveType.MIXED
    fuel_cost_per_gallon: float = 3.50
    city_mpg: float = 25.0
    highway_mpg: float = 32.0
    combined_mpg: float = 28.0
    include_maintenance: bool = True


class JobOffer:
    def __init__(
        self,
        title: str,
        company: str,
        location: str,
        work_location_type: WorkLocationType,
        employment_type: EmploymentType,
        compensation_type: CompensationType,
        base_compensation: float,
        hours_per_week: float = 40.0,
        weeks_per_year: float = 50.0,
        bonus_amount: float = 0,
        bonus_guaranteed: bool = False,
        signing_bonus: float = 0,
        relocation_package: float = 0,
        benefits: Optional[Benefits] = None,
        state_tax_rate: float = 0,
        local_tax_rate: float = 0,
        self_employment_expenses: float = 0,
        business_expenses: float = 0,
        cost_of_living_index: float = 100,
        commute_time_minutes: int = 0,
        commute_days_per_week: int = 5,
        commute_calc_type: CommuteCalculationType = CommuteCalculationType.DIRECT,
        commute_cost_monthly: float = 0,
        commute_distance_miles: float = 0,
        commute_drive_type: Any = None,  # DriveType enum from commute_calculator.py
        commute_fuel_cost: float = 0,
        commute_city_mpg: float = 0,
        commute_highway_mpg: float = 0,
        commute_combined_mpg: float = 0,
        commute_include_maintenance: bool = True,
        commute_details: CommuteDetails = None,  # Added for detailed commute calculations
        use_calculated_commute_cost: bool = False,  # Whether to use calculated commute cost or manual entry
        expected_hours_per_week: float = 40.0,
        expected_tenure_years: float = 3
    ):
        """
        Initialize a JobOffer object
        
        Args:
            title: Job title
            company: Company name
            location: Location (city, state)
            work_location_type: Whether the job is on-site, remote, or hybrid
            employment_type: Type of employment (W2, 1099, etc.)
            compensation_type: Type of compensation (salary, hourly)
            base_compensation: Base compensation amount (annual salary or hourly rate)
            hours_per_week: Expected hours worked per week
            weeks_per_year: Expected weeks worked per year
            bonus_amount: Annual bonus amount
            bonus_guaranteed: Whether the bonus is guaranteed
            signing_bonus: One-time signing bonus
            relocation_package: Value of relocation package
            benefits: Benefits package details
            state_tax_rate: State income tax rate (decimal)
            local_tax_rate: Local/city income tax rate (decimal)
            self_employment_expenses: Annual self-employment expenses for contractors
            business_expenses: Annual deductible business expenses for contractors
            cost_of_living_index: Cost of living index (100 is average)
            commute_time_minutes: One-way commute time in minutes
            commute_days_per_week: Number of days commuting to the office per week
            commute_calc_type: Method to calculate commute costs
            commute_cost_monthly: Monthly commute cost (if directly entered)
            commute_distance_miles: One-way commute distance in miles
            commute_drive_type: Type of driving (city, highway, mixed)
            commute_fuel_cost: Cost of fuel per gallon
            commute_city_mpg: Vehicle's city miles per gallon
            commute_highway_mpg: Vehicle's highway miles per gallon
            commute_combined_mpg: Vehicle's combined miles per gallon
            commute_include_maintenance: Whether to include maintenance costs
            commute_details: Detailed commute information
            use_calculated_commute_cost: Whether to use calculated commute cost or manual entry
            expected_hours_per_week: Expected actual hours worked per week
            expected_tenure_years: Expected years at this job
        """
        self.title = title
        self.company = company
        self.location = location
        self.work_location_type = work_location_type
        self.employment_type = employment_type
        self.compensation_type = compensation_type
        self.base_compensation = base_compensation
        self.hours_per_week = hours_per_week
        self.weeks_per_year = weeks_per_year
        self.bonus_amount = bonus_amount
        self.bonus_guaranteed = bonus_guaranteed
        self.signing_bonus = signing_bonus
        self.relocation_package = relocation_package
        self.benefits = benefits if benefits else Benefits()
        self.state_tax_rate = state_tax_rate
        self.local_tax_rate = local_tax_rate
        self.self_employment_expenses = self_employment_expenses
        self.business_expenses = business_expenses
        self.cost_of_living_index = cost_of_living_index
        self.commute_time_minutes = commute_time_minutes
        self.commute_days_per_week = commute_days_per_week
        self.commute_calc_type = commute_calc_type
        self.commute_cost_monthly = commute_cost_monthly
        self.commute_distance_miles = commute_distance_miles
        self.commute_drive_type = commute_drive_type
        self.commute_fuel_cost = commute_fuel_cost
        self.commute_city_mpg = commute_city_mpg
        self.commute_highway_mpg = commute_highway_mpg
        self.commute_combined_mpg = commute_combined_mpg
        self.commute_include_maintenance = commute_include_maintenance
        self.commute_details = commute_details if commute_details else CommuteDetails()
        self.use_calculated_commute_cost = use_calculated_commute_cost
        self.expected_hours_per_week = expected_hours_per_week
        self.expected_tenure_years = expected_tenure_years
    
    @property
    def is_remote(self) -> bool:
        """Returns True if the job is remote, False otherwise"""
        return self.work_location_type == WorkLocationType.REMOTE
    
    @property
    def base_salary(self) -> float:
        """Returns the annual base salary, calculated from hourly rate if needed"""
        if self.compensation_type == CompensationType.SALARY:
            return self.base_compensation
        else:  # HOURLY
            return self.base_compensation * self.hours_per_week * self.weeks_per_year
    
    @property
    def hourly_rate(self) -> float:
        """Returns the hourly rate, calculated from annual salary if needed"""
        if self.compensation_type == CompensationType.HOURLY:
            return self.base_compensation
        else:  # SALARY
            return self.base_compensation / (self.hours_per_week * self.weeks_per_year)
    
    def calculate_annual_gross_income(self) -> float:
        """Calculate annual gross income including salary and bonuses"""
        annual_income = self.base_salary
        
        # Add bonus if guaranteed
        if self.bonus_guaranteed:
            annual_income += self.bonus_amount
        
        # Amortize signing bonus and relocation over expected tenure
        if self.expected_tenure_years > 0:
            annual_income += (self.signing_bonus + self.relocation_package) / self.expected_tenure_years
        
        return annual_income
    
    def calculate_total_compensation(self, effective_tax_rate: float, commute_calculator=None) -> Dict:
        """
        Calculate total compensation and adjusted values
        
        Args:
            effective_tax_rate: Combined effective tax rate as a decimal
            commute_calculator: Optional commute calculator instance for distance-based calculations
            
        Returns:
            Dictionary with compensation calculations
        """
        # Base calculations
        base_salary = self.base_salary
        hourly_rate = self.hourly_rate
        
        # Calculate annual gross income
        gross_income = self.calculate_annual_gross_income()
        
        # Calculate take-home pay (after taxes)
        tax_amount = gross_income * effective_tax_rate
        take_home_pay = gross_income - tax_amount
        
        # Calculate commute cost
        if self.is_remote:
            monthly_commute_cost = 0
        elif self.commute_calc_type == CommuteCalculationType.DISTANCE_BASED and commute_calculator:
            # Use the commute calculator for distance-based calculation
            commute_result = commute_calculator.calculate_monthly_commute_cost(
                distance_miles=self.commute_details.distance_miles,
                drive_type=self.commute_details.drive_type,
                days_per_week=self.commute_days_per_week,
                fuel_cost_per_gallon=self.commute_details.fuel_cost_per_gallon,
                city_mpg=self.commute_details.city_mpg,
                highway_mpg=self.commute_details.highway_mpg,
                combined_mpg=self.commute_details.combined_mpg,
                include_maintenance=self.commute_details.include_maintenance
            )
            monthly_commute_cost = commute_result["total_cost"]
        else:
            # Use the direct cost entry
            monthly_commute_cost = self.commute_cost_monthly
        
        annual_commute_cost = monthly_commute_cost * 12
        
        # Calculate total direct compensation
        total_direct_compensation = gross_income
        
        # Cost of living adjustments
        col_adjusted_income = gross_income * (100 / self.cost_of_living_index)
        col_adjusted_take_home = take_home_pay * (100 / self.cost_of_living_index)
        
        # Account for commute time as lost compensation
        weekly_commute_hours = 0
        if not self.is_remote:
            one_way_hours = self.commute_time_minutes / 60
            weekly_commute_hours = one_way_hours * 2 * self.commute_days_per_week
        
        total_weekly_hours = self.expected_hours_per_week + weekly_commute_hours
        
        # Effective hourly rates (accounting for commute time and cost)
        if total_weekly_hours > 0:
            commute_adjusted_annual_value = gross_income - annual_commute_cost
            commute_adjusted_hourly_rate = commute_adjusted_annual_value / (total_weekly_hours * self.weeks_per_year)
        else:
            commute_adjusted_hourly_rate = 0
        
        # Basic effective hourly rate (no commute adjustment)
        if self.expected_hours_per_week > 0:
            effective_hourly_rate = gross_income / (self.expected_hours_per_week * self.weeks_per_year)
        else:
            effective_hourly_rate = 0
        
        # Adjust for cost of living
        col_adjusted_value = gross_income * (100 / self.cost_of_living_index)
        
        # Calculate value per day
        workdays_per_year = self.weeks_per_year * 5  # Assume 5-day work week
        daily_value = gross_income / workdays_per_year if workdays_per_year > 0 else 0
        
        # Total annual value including benefits (will be filled in by comparison engine)
        total_annual_value = gross_income
        
        return {
            "compensation_type": self.compensation_type.value,
            "base_salary": base_salary,
            "hourly_rate": hourly_rate,
            "annual_gross_income": gross_income,
            "tax_amount": tax_amount,
            "take_home_pay": take_home_pay,
            "monthly_commute_cost": monthly_commute_cost,
            "annual_commute_cost": annual_commute_cost,
            "total_direct_compensation": total_direct_compensation,
            "col_adjusted_income": col_adjusted_income,
            "col_adjusted_take_home": col_adjusted_take_home,
            "weekly_commute_hours": weekly_commute_hours,
            "total_weekly_hours": total_weekly_hours,
            "effective_hourly_rate": effective_hourly_rate,
            "commute_adjusted_hourly_rate": commute_adjusted_hourly_rate,
            "col_adjusted_value": col_adjusted_value,
            "daily_value": daily_value,
            "total_annual_value": total_annual_value  # Will be updated by comparison engine
        }