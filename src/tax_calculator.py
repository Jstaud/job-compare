"""
Tax calculator module to estimate tax rates based on income and location
"""

from typing import Dict, List, Tuple
from job_offer import EmploymentType


class TaxCalculator:
    def __init__(self):
        # 2023 federal tax brackets (simplified for demo purposes)
        self.federal_brackets = [
            (0, 11000, 0.10),
            (11000, 44725, 0.12),
            (44725, 95375, 0.22),
            (95375, 182100, 0.24),
            (182100, 231250, 0.32),
            (231250, 578125, 0.35),
            (578125, float('inf'), 0.37)
        ]
        
        # State tax rates (simplified - would need to be expanded in real implementation)
        self.state_tax_rates = {
            "AL": 0.05, "AK": 0.00, "AZ": 0.045, "AR": 0.055, "CA": 0.093,
            "CO": 0.0455, "CT": 0.0699, "DE": 0.066, "FL": 0.00, "GA": 0.0575,
            "HI": 0.11, "ID": 0.058, "IL": 0.0495, "IN": 0.0323, "IA": 0.0625,
            "KS": 0.057, "KY": 0.05, "LA": 0.0425, "ME": 0.0715, "MD": 0.0575,
            "MA": 0.05, "MI": 0.0425, "MN": 0.0985, "MS": 0.05, "MO": 0.054,
            "MT": 0.0675, "NE": 0.0684, "NV": 0.00, "NH": 0.00, "NJ": 0.1075,
            "NM": 0.059, "NY": 0.109, "NC": 0.0499, "ND": 0.029, "OH": 0.0399,
            "OK": 0.045, "OR": 0.099, "PA": 0.0307, "RI": 0.0599, "SC": 0.07,
            "SD": 0.00, "TN": 0.00, "TX": 0.00, "UT": 0.0495, "VT": 0.066,
            "VA": 0.0575, "WA": 0.00, "WV": 0.065, "WI": 0.0765, "WY": 0.00
        }
        
        # Cities with local income taxes (simplified - would need more comprehensive data)
        self.local_tax_rates = {
            "New York City": 0.03648,
            "Philadelphia": 0.03687,
            "San Francisco": 0.01500,
            "Pittsburgh": 0.03000,
            "Columbus": 0.02500,
            "Cincinnati": 0.01800,
            "Cleveland": 0.02500,
            "Detroit": 0.02400,
            "Kansas City": 0.01000,
            "St. Louis": 0.01000
        }
        
        # FICA taxes
        self.social_security_rate = 0.062
        self.medicare_rate = 0.0145
        self.additional_medicare_rate = 0.009  # Additional Medicare tax for high earners
        self.social_security_wage_base = 160200  # 2023 wage base
        
        # Self-employment tax rates
        self.self_employment_tax_rate = 0.153  # 15.3% (Social Security + Medicare doubled)
        
    def calculate_effective_tax_rate(self, income: float, state: str, locality: str,
                                     employment_type: EmploymentType,
                                     filing_status: str = "single") -> float:
        """
        Calculate the effective tax rate including federal, state, and local taxes
        
        Args:
            income: Annual gross income
            state: State abbreviation (e.g., "CA", "NY")
            locality: City or county name
            employment_type: Type of employment (W2, 1099, etc.)
            filing_status: Tax filing status (single, married, etc.)
            
        Returns:
            Effective tax rate as a decimal (e.g., 0.28 for 28%)
        """
        # Calculate federal income tax
        federal_tax = self._calculate_federal_tax(income, filing_status)
        
        # Calculate state tax
        state_tax_rate = self.state_tax_rates.get(state.upper(), 0)
        state_tax = income * state_tax_rate
        
        # Calculate local tax if applicable
        local_tax_rate = self.local_tax_rates.get(locality, 0)
        local_tax = income * local_tax_rate
        
        # Calculate FICA taxes for W2 employees
        fica_tax = 0
        if employment_type == EmploymentType.W2:
            # Social Security tax (capped at wage base)
            ss_tax = min(income, self.social_security_wage_base) * self.social_security_rate
            
            # Medicare tax (no cap, additional rate for high earners)
            medicare_tax = income * self.medicare_rate
            if income > 200000:  # Additional Medicare tax threshold for single filers
                medicare_tax += (income - 200000) * self.additional_medicare_rate
                
            fica_tax = ss_tax + medicare_tax
        
        # Total tax
        total_tax = federal_tax + state_tax + local_tax + fica_tax
        
        # Effective tax rate
        effective_rate = total_tax / income if income > 0 else 0
        
        return effective_rate
    
    def _calculate_federal_tax(self, income: float, filing_status: str) -> float:
        """Calculate federal income tax based on income and filing status"""
        # This is a simplified progressive tax calculation
        tax = 0
        for lower, upper, rate in self.federal_brackets:
            if income > lower:
                taxable_in_bracket = min(income, upper) - lower
                tax += taxable_in_bracket * rate
                
        return tax
    
    def estimate_self_employment_tax(self, income: float) -> float:
        """Calculate self-employment tax for 1099 contractors"""
        # Self-employed individuals pay both employer and employee portions of FICA
        se_tax_base = income * 0.9235  # SE tax is calculated on 92.35% of net earnings
        
        # Social Security portion (capped)
        ss_tax = min(se_tax_base, self.social_security_wage_base) * self.social_security_rate * 2
        
        # Medicare portion (no cap)
        medicare_tax = se_tax_base * self.medicare_rate * 2
        
        # Additional Medicare tax for high earners
        if se_tax_base > 200000:
            medicare_tax += (se_tax_base - 200000) * self.additional_medicare_rate
            
        return ss_tax + medicare_tax
    
    def estimate_s_corp_tax_savings(self, income: float, reasonable_salary: float) -> float:
        """
        Calculate potential tax savings from S-Corp structure compared to 1099
        
        Args:
            income: Total business income
            reasonable_salary: Reasonable salary to pay yourself as an S-Corp
        
        Returns:
            Estimated annual tax savings
        """
        # Calculate self-employment tax if all income was 1099
        se_tax_1099 = self.estimate_self_employment_tax(income)
        
        # Calculate FICA taxes on S-Corp salary
        ss_tax = min(reasonable_salary, self.social_security_wage_base) * self.social_security_rate * 2
        medicare_tax = reasonable_salary * self.medicare_rate * 2
        
        # Additional Medicare tax
        if reasonable_salary > 200000:
            medicare_tax += (reasonable_salary - 200000) * self.additional_medicare_rate
            
        se_tax_s_corp = ss_tax + medicare_tax
        
        # Return the difference (savings)
        return se_tax_1099 - se_tax_s_corp