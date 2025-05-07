"""
Module for calculating commute costs based on various factors like distance, 
fuel efficiency, and maintenance costs.
"""
from enum import Enum
from typing import Dict, Optional


class DriveType(Enum):
    CITY = "City Driving"
    HIGHWAY = "Highway Driving"
    MIXED = "Mixed Driving"


class CommuteCalculator:
    """Calculator for vehicle commute costs"""
    
    # Constants for standard calculations
    DEFAULT_MAINTENANCE_COST_PER_MILE = 0.10  # $0.10 per mile for maintenance, depreciation, etc.
    
    def __init__(self, default_fuel_cost: float = 3.50, 
                default_city_mpg: float = 25.0,
                default_highway_mpg: float = 32.0,
                default_combined_mpg: float = 28.0,
                default_maintenance_cost_per_mile: float = DEFAULT_MAINTENANCE_COST_PER_MILE):
        """
        Initialize the commute calculator with default values
        
        Args:
            default_fuel_cost: Default fuel cost per gallon in dollars
            default_city_mpg: Default city miles per gallon
            default_highway_mpg: Default highway miles per gallon
            default_combined_mpg: Default combined miles per gallon
            default_maintenance_cost_per_mile: Default cost per mile for maintenance and wear
        """
        self.default_fuel_cost = default_fuel_cost
        self.default_city_mpg = default_city_mpg
        self.default_highway_mpg = default_highway_mpg
        self.default_combined_mpg = default_combined_mpg
        self.default_maintenance_cost_per_mile = default_maintenance_cost_per_mile
    
    def calculate_monthly_commute_cost(self, 
                                      distance_miles: float,
                                      drive_type: DriveType = DriveType.MIXED,
                                      days_per_week: int = 5,
                                      fuel_cost_per_gallon: Optional[float] = None,
                                      city_mpg: Optional[float] = None,
                                      highway_mpg: Optional[float] = None,
                                      combined_mpg: Optional[float] = None,
                                      include_maintenance: bool = True) -> Dict:
        """
        Calculate the monthly cost of commuting based on distance and vehicle specifications
        
        Args:
            distance_miles: One-way distance in miles
            drive_type: Type of driving (city, highway, or mixed)
            days_per_week: Number of days commuting per week
            fuel_cost_per_gallon: Cost of fuel per gallon
            city_mpg: Vehicle's city miles per gallon
            highway_mpg: Vehicle's highway miles per gallon
            combined_mpg: Vehicle's combined miles per gallon
            include_maintenance: Whether to include maintenance and depreciation costs
            
        Returns:
            Dictionary with fuel cost, maintenance cost, and total cost
        """
        # Use provided values or fall back to defaults
        fuel_cost = fuel_cost_per_gallon if fuel_cost_per_gallon else self.default_fuel_cost
        city = city_mpg if city_mpg else self.default_city_mpg
        highway = highway_mpg if highway_mpg else self.default_highway_mpg
        combined = combined_mpg if combined_mpg else self.default_combined_mpg
        
        # Determine which MPG to use based on drive type
        if drive_type == DriveType.CITY:
            effective_mpg = city
        elif drive_type == DriveType.HIGHWAY:
            effective_mpg = highway
        else:  # MIXED
            effective_mpg = combined
        
        # Calculate total monthly distance (round trip * days per week * weeks per month)
        monthly_distance = distance_miles * 2 * days_per_week * 4.33  # 4.33 weeks average per month
        
        # Calculate monthly fuel cost
        if effective_mpg > 0:
            monthly_fuel_gallons = monthly_distance / effective_mpg
            monthly_fuel_cost = monthly_fuel_gallons * fuel_cost
        else:
            monthly_fuel_cost = 0
        
        # Calculate monthly maintenance cost
        if include_maintenance:
            monthly_maintenance_cost = monthly_distance * self.default_maintenance_cost_per_mile
        else:
            monthly_maintenance_cost = 0
        
        # Calculate total monthly cost
        total_monthly_cost = monthly_fuel_cost + monthly_maintenance_cost
        
        return {
            "monthly_distance": monthly_distance,
            "fuel_cost": monthly_fuel_cost,
            "maintenance_cost": monthly_maintenance_cost,
            "total_cost": total_monthly_cost,
            "cost_per_mile": total_monthly_cost / monthly_distance if monthly_distance > 0 else 0
        }