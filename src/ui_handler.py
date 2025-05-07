"""
UI Handler for the job comparison tool
"""

import os
import sys
from typing import Dict, List, Optional, Tuple
from job_offer import JobOffer, EmploymentType, Benefits, WorkLocationType, CompensationType, CommuteCalculationType
from commute_calculator import DriveType, CommuteCalculator


class ConsoleUI:
    def __init__(self):
        """Initialize the console UI"""
        self.commute_calculator = CommuteCalculator()
    
    def display_message(self, message: str) -> None:
        """Display a message to the user"""
        print(message)
    
    def display_error(self, message: str) -> None:
        """Display an error message to the user"""
        print(f"ERROR: {message}", file=sys.stderr)
    
    def _collect_commute_info(self, work_location_type: WorkLocationType) -> Tuple[CommuteCalculationType, float, float, DriveType, float, float, float, float, bool]:
        """
        Collect commute information including distance-based calculation option
        
        Args:
            work_location_type: Type of work location (on-site, hybrid, remote)
            
        Returns:
            Tuple of commute calculation parameters
        """
        # Default values
        calc_type = CommuteCalculationType.DIRECT
        monthly_cost = 0.0
        distance_miles = 0.0
        drive_type = DriveType.MIXED
        fuel_cost = self.commute_calculator.default_fuel_cost
        city_mpg = self.commute_calculator.default_city_mpg
        highway_mpg = self.commute_calculator.default_highway_mpg
        combined_mpg = self.commute_calculator.default_combined_mpg
        include_maintenance = True
        
        # Skip if remote
        if work_location_type == WorkLocationType.REMOTE:
            return (calc_type, monthly_cost, distance_miles, drive_type, fuel_cost, city_mpg, highway_mpg, combined_mpg, include_maintenance)
        
        # Commute cost calculation method
        self.display_message("\n--- Commute Cost Calculation ---")
        print("How would you like to calculate commute costs?")
        print("1. Enter monthly cost directly")
        print("2. Calculate based on distance and vehicle details")
        
        choice = self._get_int_input("Select option (1-2): ", 1, 2)
        
        if choice == 1:
            # Direct cost entry
            calc_type = CommuteCalculationType.DIRECT
            monthly_cost = self._get_float_input("Monthly commute cost ($): ")
        else:
            # Distance-based calculation
            calc_type = CommuteCalculationType.DISTANCE_BASED
            distance_miles = self._get_float_input("One-way commute distance (miles): ")
            
            # Drive type
            print("\nDrive Type:")
            print("1. City driving")
            print("2. Highway driving")
            print("3. Mixed (city and highway)")
            
            drive_type_choice = self._get_int_input("Select drive type (1-3): ", 1, 3)
            drive_type = [
                DriveType.CITY,
                DriveType.HIGHWAY,
                DriveType.MIXED
            ][drive_type_choice - 1]
            
            # Vehicle details
            self.display_message("\n--- Vehicle Details ---")
            
            fuel_cost = self._get_float_input(f"Fuel cost per gallon ($): ", default=fuel_cost)
            
            if drive_type == DriveType.CITY or drive_type == DriveType.MIXED:
                city_mpg = self._get_float_input(f"City MPG: ", default=city_mpg)
            
            if drive_type == DriveType.HIGHWAY or drive_type == DriveType.MIXED:
                highway_mpg = self._get_float_input(f"Highway MPG: ", default=highway_mpg)
                
            if drive_type == DriveType.MIXED:
                combined_mpg = self._get_float_input(f"Combined MPG: ", default=combined_mpg)
            
            include_maintenance = self._get_yes_no_input("Include maintenance costs in calculation? (y/n): ")
            
            # Show estimated cost
            estimated_cost = self.commute_calculator.calculate_monthly_commute_cost(
                distance_miles=distance_miles,
                drive_type=drive_type,
                days_per_week=5,  # Default to 5, will be adjusted for hybrid roles
                fuel_cost_per_gallon=fuel_cost,
                city_mpg=city_mpg,
                highway_mpg=highway_mpg,
                combined_mpg=combined_mpg,
                include_maintenance=include_maintenance
            )
            
            self.display_message(f"\nEstimated monthly commute cost: ${estimated_cost['total_cost']:.2f}")
            self.display_message(f"  Fuel cost: ${estimated_cost['fuel_cost']:.2f}")
            self.display_message(f"  Maintenance cost: ${estimated_cost['maintenance_cost']:.2f}")
            self.display_message(f"  Monthly distance: {estimated_cost['monthly_distance']:.1f} miles")
            # Output cost per mile if distance is greater than zero
            if estimated_cost['monthly_distance'] > 0:
                self.display_message(f"  Cost per mile: ${estimated_cost['cost_per_mile']:.2f}")
        
        return (calc_type, monthly_cost, distance_miles, drive_type, fuel_cost, city_mpg, highway_mpg, combined_mpg, include_maintenance)
    
    def _collect_job_details(self) -> JobOffer:
        """Collect details for a single job offer"""
        # Basic job details
        company = self._get_input("Company name: ")
        title = self._get_input("Job title: ")
        location = self._get_input("Location (City, State): ")
        
        # Work location type
        print("\nWork Location Type:")
        print("1. On-site")
        print("2. Remote")
        print("3. Hybrid")
        work_location_choice = self._get_int_input("Select work location type (1-3): ", 1, 3)
        work_location_type = [
            WorkLocationType.ONSITE, 
            WorkLocationType.REMOTE,
            WorkLocationType.HYBRID
        ][work_location_choice - 1]
        
        # Employment type
        print("\nEmployment Type:")
        print("1. W2 Employee")
        print("2. 1099 Contractor")
        print("3. S-Corporation")
        
        employment_type_choice = self._get_int_input("Select employment type (1-3): ", 1, 3)
        employment_type = [
            EmploymentType.W2, 
            EmploymentType.CONTRACTOR_1099,
            EmploymentType.S_CORP
        ][employment_type_choice - 1]
        
        # Compensation type
        print("\nCompensation Type:")
        print("1. Annual Salary")
        print("2. Hourly Rate")
        comp_type_choice = self._get_int_input("Select compensation type (1-2): ", 1, 2)
        compensation_type = [
            CompensationType.SALARY,
            CompensationType.HOURLY
        ][comp_type_choice - 1]
        
        # Compensation details
        if compensation_type == CompensationType.SALARY:
            base_compensation = self._get_float_input("Base annual salary ($): ")
            hours_per_week = self._get_float_input("Expected hours per week: ", default=40.0)
            weeks_per_year = self._get_float_input("Weeks worked per year: ", default=50.0)
        else:  # HOURLY
            base_compensation = self._get_float_input("Hourly rate ($): ")
            hours_per_week = self._get_float_input("Expected hours per week: ", default=40.0)
            weeks_per_year = self._get_float_input("Weeks worked per year: ", default=50.0)
            self.display_message(f"Calculated annual salary: ${base_compensation * hours_per_week * weeks_per_year:,.2f}")
        
        bonus_amount = self._get_float_input("Annual bonus amount ($, 0 if none): ")
        bonus_guaranteed = False
        if bonus_amount > 0:
            bonus_guaranteed = self._get_yes_no_input("Is the bonus guaranteed? (y/n): ")
        
        signing_bonus = self._get_float_input("Signing bonus ($, 0 if none): ")
        relocation_package = self._get_float_input("Relocation package value ($, 0 if none): ")
        
        # Benefits
        self.display_message("\n--- Benefits Information ---")
        benefits = self._collect_benefits_info()
        
        # Tax information
        self.display_message("\n--- Tax Information ---")
        state_tax_rate = self._get_float_input("State income tax rate (%, 0 if none): ") / 100
        local_tax_rate = self._get_float_input("Local/city income tax rate (%, 0 if none): ") / 100
        
        # Additional expenses for contractors
        self_employment_expenses = 0
        business_expenses = 0
        if employment_type in [EmploymentType.CONTRACTOR_1099, EmploymentType.S_CORP]:
            self.display_message("\n--- Contractor/Business Expenses ---")
            self_employment_expenses = self._get_float_input(
                "Annual self-employment expenses ($, costs of being self-employed like health insurance, " +
                "retirement contributions, etc.): "
            )
            business_expenses = self._get_float_input(
                "Annual deductible business expenses ($, costs you can deduct from taxes like home office, " +
                "equipment, professional services, etc.): "
            )
        
        # Cost of living
        cost_of_living_index = self._get_float_input("Cost of living index (100 is average): ", default=100)
        
        # Work conditions
        self.display_message("\n--- Work Conditions ---")
        commute_time_minutes = 0
        commute_days_per_week = 5  # Default
        
        if work_location_type in [WorkLocationType.ONSITE, WorkLocationType.HYBRID]:
            commute_time_minutes = self._get_int_input("One-way commute time (minutes): ")
            
            # For hybrid roles, ask about commute frequency
            if work_location_type == WorkLocationType.HYBRID:
                commute_days_per_week = self._get_int_input("Number of days per week in the office: ", 1, 5)
        
        # Collect commute cost information
        (commute_calc_type, commute_cost_monthly, commute_distance_miles, 
         commute_drive_type, commute_fuel_cost, commute_city_mpg, 
         commute_highway_mpg, commute_combined_mpg, commute_include_maintenance) = self._collect_commute_info(work_location_type)
        
        expected_tenure_years = self._get_float_input("Expected years at this job: ", default=3)
        
        # Create JobOffer object
        return JobOffer(
            title=title,
            company=company,
            location=location,
            work_location_type=work_location_type,
            employment_type=employment_type,
            compensation_type=compensation_type,
            base_compensation=base_compensation,
            hours_per_week=hours_per_week,
            weeks_per_year=weeks_per_year,
            bonus_amount=bonus_amount,
            bonus_guaranteed=bonus_guaranteed,
            signing_bonus=signing_bonus,
            relocation_package=relocation_package,
            benefits=benefits,
            state_tax_rate=state_tax_rate,
            local_tax_rate=local_tax_rate,
            self_employment_expenses=self_employment_expenses,
            business_expenses=business_expenses,
            cost_of_living_index=cost_of_living_index,
            commute_time_minutes=commute_time_minutes,
            commute_days_per_week=commute_days_per_week,
            commute_calc_type=commute_calc_type,
            commute_cost_monthly=commute_cost_monthly,
            commute_distance_miles=commute_distance_miles,
            commute_drive_type=commute_drive_type,
            commute_fuel_cost=commute_fuel_cost,
            commute_city_mpg=commute_city_mpg,
            commute_highway_mpg=commute_highway_mpg,
            commute_combined_mpg=commute_combined_mpg,
            commute_include_maintenance=commute_include_maintenance,
            expected_hours_per_week=hours_per_week,
            expected_tenure_years=expected_tenure_years
        )
    
    def collect_job_offers(self) -> List[JobOffer]:
        """Collect job offer information interactively from the user"""
        job_offers = []
        
        self.display_message("\n===== Job Offer Comparison Tool =====\n")
        self.display_message("Enter information for each job offer. Press Ctrl+C to cancel at any time.\n")
        
        try:
            while True:
                self.display_message(f"\n--- Job Offer #{len(job_offers) + 1} ---")
                
                job_offer = self._collect_job_details()
                job_offers.append(job_offer)
                
                # Ask if user wants to add another offer
                if len(job_offers) >= 2:
                    add_another = self._get_yes_no_input("\nAdd another job offer? (y/n): ")
                    if not add_another:
                        break
                else:
                    self.display_message("\nYou need at least two job offers for comparison.")
                    
        except KeyboardInterrupt:
            self.display_message("\nInput cancelled by user.")
            if len(job_offers) < 2:
                self.display_error("At least two job offers are needed for comparison.")
                return []
        
        return job_offers
    
    def _collect_benefits_info(self) -> Benefits:
        """Collect benefits information from the user"""
        # Retirement benefits
        retirement_match_percent = self._get_float_input("401(k) match percentage (%, 0 if none): ") / 100
        retirement_match_limit = 0
        if retirement_match_percent > 0:
            retirement_match_limit = self._get_float_input("401(k) match annual limit ($): ")
        
        # Insurance
        self.display_message("\n--- Health Insurance ---")
        health_insurance_monthly_premium = self._get_float_input("Monthly health insurance premium you pay ($): ")
        health_insurance_coverage_percent = self._get_float_input("Health insurance coverage percentage (%): ") / 100
        
        self.display_message("\n--- Dental Insurance ---")
        dental_insurance_monthly_premium = self._get_float_input("Monthly dental insurance premium you pay ($): ")
        dental_insurance_coverage_percent = self._get_float_input("Dental insurance coverage percentage (%): ") / 100
        
        self.display_message("\n--- Vision Insurance ---")
        vision_insurance_monthly_premium = self._get_float_input("Monthly vision insurance premium you pay ($): ")
        vision_insurance_coverage_percent = self._get_float_input("Vision insurance coverage percentage (%): ") / 100
        
        self.display_message("\n--- Life Insurance ---")
        life_insurance_coverage = self._get_float_input("Life insurance coverage amount ($, 0 if none): ")
        life_insurance_monthly_premium = self._get_float_input("Monthly life insurance premium you pay ($): ")
        
        # Time off
        self.display_message("\n--- Paid Time Off ---")
        paid_time_off_days = self._get_int_input("Annual PTO days: ")
        paid_holidays = self._get_int_input("Annual paid holidays: ")
        paid_sick_days = self._get_int_input("Annual paid sick days: ")
        paid_parental_leave_weeks = self._get_int_input("Paid parental leave (weeks, 0 if none): ")
        
        # Other benefits
        self.display_message("\n--- Other Benefits ---")
        equity_value = self._get_float_input("Estimated annual value of equity/stock options ($, 0 if none): ")
        other_benefits_value = self._get_float_input("Estimated annual value of other benefits ($, 0 if none): ")
        other_benefits_description = ""
        if other_benefits_value > 0:
            other_benefits_description = self._get_input("Description of other benefits: ")
        
        # Create and return Benefits object
        return Benefits(
            retirement_match_percent=retirement_match_percent,
            retirement_match_limit=retirement_match_limit,
            health_insurance_monthly_premium=health_insurance_monthly_premium,
            health_insurance_coverage_percent=health_insurance_coverage_percent,
            dental_insurance_monthly_premium=dental_insurance_monthly_premium,
            dental_insurance_coverage_percent=dental_insurance_coverage_percent,
            vision_insurance_monthly_premium=vision_insurance_monthly_premium,
            vision_insurance_coverage_percent=vision_insurance_coverage_percent,
            life_insurance_coverage=life_insurance_coverage,
            life_insurance_monthly_premium=life_insurance_monthly_premium,
            paid_time_off_days=paid_time_off_days,
            paid_holidays=paid_holidays,
            paid_sick_days=paid_sick_days,
            paid_parental_leave_weeks=paid_parental_leave_weeks,
            equity_value=equity_value,
            other_benefits_value=other_benefits_value,
            other_benefits_description=other_benefits_description
        )
    
    def display_comparison_results(self, results: Dict) -> None:
        """Display comparison results to the user"""
        self.display_message("\n========== JOB OFFER COMPARISON RESULTS ==========\n")
        
        # Display basic info for each offer
        self.display_message("--- OFFER SUMMARY ---")
        for idx, offer in enumerate(results["offers"]):
            self.display_message(f"\nOffer #{idx+1}: {offer['company']} - {offer['title']}")
            self.display_message(f"Location: {offer['location']} ({offer['work_location_type']})")
            self.display_message(f"Employment Type: {offer['employment_type']}")
            
            # Display compensation type-specific information
            comp_type = offer['compensation']['compensation_type']
            if "Annual Salary" in comp_type:
                self.display_message(f"Base Salary: ${offer['compensation']['base_salary']:,.2f} per year")
                self.display_message(f"Hourly Equivalent: ${offer['compensation']['hourly_rate']:,.2f} per hour")
            else:  # Hourly Rate
                self.display_message(f"Hourly Rate: ${offer['compensation']['hourly_rate']:,.2f} per hour")
                self.display_message(f"Annual Equivalent: ${offer['compensation']['base_salary']:,.2f} per year")
            
            self.display_message(f"Total Compensation: ${offer['compensation']['total_direct_compensation']:,.2f}")
            self.display_message(f"Take-Home Pay: ${offer['compensation']['take_home_pay']:,.2f}")
            self.display_message(f"Benefits Value: ${offer['benefits_value']['total']:,.2f}")
            
            # Display commute costs
            if "monthly_commute_cost" in offer["compensation"]:
                self.display_message(f"Monthly Commute Cost: ${offer['compensation']['monthly_commute_cost']:,.2f}")
                self.display_message(f"Annual Commute Cost: ${offer['compensation']['annual_commute_cost']:,.2f}")
            
            self.display_message(f"Total Annual Value: ${offer['compensation']['total_annual_value']:,.2f}")
            self.display_message(f"Effective Tax Rate: {offer['tax_rate']*100:.1f}%")
            self.display_message(f"Effective Hourly Rate: ${offer['compensation']['effective_hourly_rate']:,.2f} " +
                            f"(including benefits and adjustments)")
            
            # Show special calculations for different employment types
            if "self_employment_tax" in offer["compensation"]:
                self.display_message(f"Self-Employment Tax: ${offer['compensation']['self_employment_tax']:,.2f}")
            if "s_corp_tax_savings" in offer["compensation"]:
                self.display_message(f"S-Corp Tax Savings: ${offer['compensation']['s_corp_tax_savings']:,.2f}")
        
        # Display comparative metrics
        self.display_message("\n\n--- COMPARISON METRICS ---")
        metrics = results["comparison_metrics"]
        
        self.display_message(f"\nHighest Total Value: {metrics['highest_total_value']['company']} " +
                            f"(${metrics['highest_total_value']['amount']:,.2f})")
                            
        self.display_message(f"Lowest Total Value: {metrics['lowest_total_value']['company']} " +
                            f"(${metrics['lowest_total_value']['amount']:,.2f})")
                            
        self.display_message(f"Value Range: ${metrics['value_range']:,.2f} ({metrics['value_range_percent']:.1f}%)")
        
        # Display rankings
        self.display_message("\n\n--- RANKINGS ---")
        for criterion, ranking_data in results["rankings"].items():
            self.display_message(f"\n{ranking_data['label']}:")
            for rank_info in ranking_data["ranking"]:
                self.display_message(f"  {rank_info['rank']}. {rank_info['company']} - ${rank_info['value']:,.2f}")
        
        # Display recommendations
        self.display_message("\n\n--- RECOMMENDATIONS ---")
        recommendations = results["recommendations"]
        
        self.display_message(f"Best Total Compensation: {recommendations['best_total_comp']}")
        self.display_message(f"Best Overall Value: {recommendations['best_overall']}")
        self.display_message(f"Best After-Tax Income: {recommendations['best_after_tax']}")
        self.display_message(f"Best Cost-of-Living Adjusted Value: {recommendations['best_col_adjusted']}")
        self.display_message(f"Best Benefits Package: {recommendations['best_benefits']}")
        self.display_message(f"Best Work-Life Balance: {recommendations['best_work_life_balance']}")
        
        self.display_message("\n========== END OF COMPARISON ==========\n")
    
    def _get_input(self, prompt: str, default: str = "") -> str:
        """Get text input from the user with an optional default value"""
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        else:
            while True:
                user_input = input(prompt).strip()
                if user_input:
                    return user_input
                self.display_error("Input cannot be empty. Please try again.")
    
    def _get_float_input(self, prompt: str, default: Optional[float] = None) -> float:
        """Get float input from the user with validation"""
        prompt_with_default = f"{prompt} [{default}]: " if default is not None else prompt
        
        while True:
            try:
                user_input = input(prompt_with_default).strip()
                if not user_input and default is not None:
                    return default
                return float(user_input)
            except ValueError:
                self.display_error("Please enter a valid number.")
    
    def _get_int_input(self, prompt: str, min_value: int = 0, max_value: int = None, default: Optional[int] = None) -> int:
        """Get integer input from the user with validation and range checking"""
        prompt_with_default = f"{prompt} [{default}]: " if default is not None else prompt
        
        while True:
            try:
                user_input = input(prompt_with_default).strip()
                if not user_input and default is not None:
                    return default
                    
                value = int(user_input)
                
                if min_value is not None and value < min_value:
                    self.display_error(f"Value must be at least {min_value}.")
                    continue
                    
                if max_value is not None and value > max_value:
                    self.display_error(f"Value must be at most {max_value}.")
                    continue
                    
                return value
            except ValueError:
                self.display_error("Please enter a valid integer.")
    
    def _get_yes_no_input(self, prompt: str) -> bool:
        """Get a yes/no response from the user"""
        while True:
            response = input(prompt).strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                self.display_error("Please enter 'y' or 'n'.")