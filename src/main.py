#!/usr/bin/env python3
"""
Job Offer Comparison Tool

This tool helps compare multiple job offers considering various factors like:
- Base salary
- Bonuses
- Benefits (401k, insurance, PTO, etc.)
- Tax implications of different employment types (W2, 1099, S-Corp)
- Cost of living adjustments
"""

import sys
import argparse
from job_offer import JobOffer
from comparison_engine import ComparisonEngine
from tax_calculator import TaxCalculator
from benefits_calculator import BenefitsCalculator
from ui_handler import ConsoleUI

# Import spreadsheet parser with error handling
try:
    from spreadsheet_parser import SpreadsheetParser
    spreadsheet_support = True
except ImportError:
    spreadsheet_support = False

def parse_args():
    parser = argparse.ArgumentParser(description='Compare job offers with various factors')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--load', type=str, help='Load job offers from a JSON file')
    parser.add_argument('--save', type=str, help='Save job offers to a JSON file')
    
    # Add spreadsheet-related arguments
    parser.add_argument('--spreadsheet', type=str, help='Load job offers from a spreadsheet file (CSV or Excel)')
    parser.add_argument('--create-template', type=str, 
                        help='Create a template spreadsheet file (specify output path with .csv or .xlsx extension)')
    
    return parser.parse_args()

def main():
    args = parse_args()
    ui = ConsoleUI()
    
    # Initialize the comparison engine with a default data file
    # Note: The engine internally creates its own tax_calculator and benefits_calculator
    comparison_engine = ComparisonEngine()
    
    # Check if any spreadsheet operations were requested
    if (args.spreadsheet or args.create_template) and not spreadsheet_support:
        ui.display_error(
            "Spreadsheet functionality requires additional packages.\n"
            "Please install with: pip install pandas openpyxl"
        )
        return 1
    
    # Create template spreadsheet if requested
    if args.create_template:
        try:
            ui.display_message(f"Creating template spreadsheet at {args.create_template}...")
            spreadsheet_parser = SpreadsheetParser()
            spreadsheet_parser.create_template_file(args.create_template)
            ui.display_message(f"Template created successfully! You can now fill it with your job offers.")
            return 0
        except Exception as e:
            ui.display_error(f"Failed to create template: {e}")
            return 1
    
    # Initialize empty job offers list
    job_offers = []
    
    # Load from JSON file if specified
    if args.load:
        try:
            # Update the ComparisonEngine to use the specified file path
            comparison_engine.data_file = args.load
            job_offers = comparison_engine.load_offers()
            ui.display_message(f"Loaded job offers from {args.load}")
        except Exception as e:
            ui.display_error(f"Failed to load job offers from JSON: {e}")
            return 1
    
    # Load from spreadsheet if specified
    if args.spreadsheet:
        try:
            spreadsheet_parser = SpreadsheetParser()
            spreadsheet_job_offers = spreadsheet_parser.parse_file(args.spreadsheet)
            ui.display_message(f"Loaded {len(spreadsheet_job_offers)} job offers from spreadsheet {args.spreadsheet}")
            
            # Add to existing job offers or replace
            if job_offers:
                job_offers.extend(spreadsheet_job_offers)
                ui.display_message(f"Combined with previously loaded offers for a total of {len(job_offers)} offers.")
            else:
                job_offers = spreadsheet_job_offers
                
            # Add job offers to the comparison engine
            for offer in spreadsheet_job_offers:
                comparison_engine.add_offer(offer)
        except Exception as e:
            ui.display_error(f"Failed to load job offers from spreadsheet: {e}")
            return 1
    
    # Interactive mode or empty job offers list
    if args.interactive or not job_offers:
        interactive_job_offers = ui.collect_job_offers()
        
        # Add to existing job offers or replace
        if job_offers and interactive_job_offers:
            job_offers.extend(interactive_job_offers)
            ui.display_message(f"Combined with previously loaded offers for a total of {len(job_offers)} offers.")
        elif interactive_job_offers:
            job_offers = interactive_job_offers
            
        # Add interactive job offers to the comparison engine
        for offer in interactive_job_offers:
            comparison_engine.add_offer(offer)
    
    # Compare offers
    if len(job_offers) < 2:
        ui.display_error("At least two job offers are needed for comparison")
        return 1
    
    # Get comparison results and format them for the UI
    raw_comparison_results = comparison_engine.compare_offers()
    
    # Transform results into the format expected by the UI
    comparison_results = {
        "offers": [],
        "comparison_metrics": {
            "highest_total_value": {"company": "", "amount": 0},
            "lowest_total_value": {"company": "", "amount": 0},
            "value_range": 0,
            "value_range_percent": 0
        },
        "rankings": {},
        "recommendations": {
            "best_total_comp": "",
            "best_overall": "",
            "best_after_tax": "",
            "best_col_adjusted": "",
            "best_benefits": "",
            "best_work_life_balance": ""
        }
    }
    
    # Extract offer data for UI
    max_value = 0
    min_value = float('inf')
    
    for result in raw_comparison_results:
        offer = result["offer"]
        compensation = result["compensation"]
        
        # Format offer data for UI
        offer_data = {
            "company": offer.company,
            "title": offer.title,
            "location": offer.location,
            "work_location_type": offer.work_location_type.value,
            "employment_type": offer.employment_type.value,
            "compensation": {
                "compensation_type": offer.compensation_type.value,
                "base_salary": compensation.get("annual_gross_income", 0),
                "hourly_rate": compensation.get("hourly_rate", 0),
                "total_direct_compensation": compensation.get("total_direct_compensation", 0),
                "take_home_pay": compensation.get("take_home_pay", 0),
                "effective_hourly_rate": compensation.get("effective_hourly_rate", 0),
                "monthly_commute_cost": compensation.get("monthly_commute_cost", 0),
                "annual_commute_cost": compensation.get("annual_commute_cost", 0),
                "total_annual_value": compensation.get("total_annual_value", 0)
            },
            "benefits_value": result["benefits_value"],
            "tax_rate": result["effective_tax_rate"]
        }
        
        # Add contractor-specific data if applicable
        if "self_employment_tax" in compensation:
            offer_data["compensation"]["self_employment_tax"] = compensation["self_employment_tax"]
        if "s_corp_tax_savings" in compensation:
            offer_data["compensation"]["s_corp_tax_savings"] = compensation["s_corp_tax_savings"]
            
        comparison_results["offers"].append(offer_data)
        
        # Track min and max values for metrics
        total_value = compensation.get("total_annual_value", 0)
        if total_value > max_value:
            max_value = total_value
            comparison_results["comparison_metrics"]["highest_total_value"] = {
                "company": offer.company,
                "amount": total_value
            }
        
        if total_value < min_value:
            min_value = total_value
            comparison_results["comparison_metrics"]["lowest_total_value"] = {
                "company": offer.company,
                "amount": total_value
            }
    
    # Calculate value range metrics
    if min_value < float('inf') and max_value > 0:
        value_range = max_value - min_value
        value_range_percent = (value_range / min_value) * 100 if min_value > 0 else 0
        
        comparison_results["comparison_metrics"]["value_range"] = value_range
        comparison_results["comparison_metrics"]["value_range_percent"] = value_range_percent
    
    # Get rankings and recommendations
    # Note: These would normally come from comparison_engine.get_rankings() and get_recommendations(),
    # but for simplicity we'll set values based on specific metrics for each category

    # Total value ranking (simplified)
    sorted_by_value = sorted(
        comparison_results["offers"], 
        key=lambda x: x["compensation"]["total_annual_value"], 
        reverse=True
    )

    # Create a simple ranking
    total_value_ranking = []
    for i, offer in enumerate(sorted_by_value):
        total_value_ranking.append({
            "rank": i + 1,
            "company": offer["company"],
            "title": offer["title"],
            "value": offer["compensation"]["total_annual_value"]
        })

    comparison_results["rankings"]["total_annual_value"] = {
        "label": "Total Annual Value",
        "description": "Total annual value including salary, bonuses, and benefits",
        "ranking": total_value_ranking
    }

    # Create additional rankings for different metrics
    # Take home pay ranking
    sorted_by_take_home = sorted(
        comparison_results["offers"], 
        key=lambda x: x["compensation"]["take_home_pay"], 
        reverse=True
    )
    take_home_ranking = []
    for i, offer in enumerate(sorted_by_take_home):
        take_home_ranking.append({
            "rank": i + 1,
            "company": offer["company"],
            "title": offer["title"],
            "value": offer["compensation"]["take_home_pay"]
        })
    comparison_results["rankings"]["take_home_pay"] = {
        "label": "Take-Home Pay",
        "description": "Annual take-home pay after taxes",
        "ranking": take_home_ranking
    }

    # Benefits value ranking
    sorted_by_benefits = sorted(
        comparison_results["offers"], 
        key=lambda x: x["benefits_value"]["total"], 
        reverse=True
    )
    benefits_ranking = []
    for i, offer in enumerate(sorted_by_benefits):
        benefits_ranking.append({
            "rank": i + 1,
            "company": offer["company"],
            "title": offer["title"],
            "value": offer["benefits_value"]["total"]
        })
    comparison_results["rankings"]["benefits_value"] = {
        "label": "Benefits Value",
        "description": "Total value of all benefits",
        "ranking": benefits_ranking
    }

    # Hourly rate ranking
    sorted_by_hourly = sorted(
        comparison_results["offers"], 
        key=lambda x: x["compensation"]["hourly_rate"], 
        reverse=True
    )
    hourly_ranking = []
    for i, offer in enumerate(sorted_by_hourly):
        hourly_ranking.append({
            "rank": i + 1,
            "company": offer["company"],
            "title": offer["title"],
            "value": offer["compensation"]["hourly_rate"]
        })
    comparison_results["rankings"]["hourly_rate"] = {
        "label": "Hourly Rate",
        "description": "Base hourly compensation rate",
        "ranking": hourly_ranking
    }

    # Work-life balance ranking (simplistic implementation)
    # For this example, we'll use a simple heuristic: remote > hybrid > onsite,
    # and consider commute time and effective hours (including commute)
    work_life_scores = []
    for offer in comparison_results["offers"]:
        score = 0
        # Remote work is preferred
        if offer["work_location_type"] == "Remote":
            score += 10
        elif offer["work_location_type"] == "Hybrid":
            score += 5
        
        # Account for commute time
        if "monthly_commute_cost" in offer["compensation"]:
            # Lower commute cost is better
            score -= offer["compensation"]["monthly_commute_cost"] / 100
        
        work_life_scores.append((offer, score))

    # Sort by score (higher is better)
    sorted_by_work_life = sorted(work_life_scores, key=lambda x: x[1], reverse=True)
    work_life_ranking = []
    for i, (offer, score) in enumerate(sorted_by_work_life):
        work_life_ranking.append({
            "rank": i + 1,
            "company": offer["company"],
            "title": offer["title"],
            "value": score
        })
    comparison_results["rankings"]["work_life_balance"] = {
        "label": "Work-Life Balance",
        "description": "Score based on work location type, commute, and flexibility",
        "ranking": work_life_ranking
    }

    # Now set specific recommendations based on the appropriate rankings
    if sorted_by_value and len(sorted_by_value) > 0:
        comparison_results["recommendations"]["best_overall"] = sorted_by_value[0]["company"]

    if sorted_by_take_home and len(sorted_by_take_home) > 0:
        comparison_results["recommendations"]["best_after_tax"] = sorted_by_take_home[0]["company"]
        comparison_results["recommendations"]["best_total_comp"] = sorted_by_take_home[0]["company"]

    if sorted_by_benefits and len(sorted_by_benefits) > 0:
        comparison_results["recommendations"]["best_benefits"] = sorted_by_benefits[0]["company"]

    if sorted_by_work_life and len(sorted_by_work_life) > 0:
        comparison_results["recommendations"]["best_work_life_balance"] = sorted_by_work_life[0][0]["company"]

    # Cost of living adjusted value
    # Note: This is a simplistic approach. A real implementation would do a more
    # sophisticated calculation based on actual cost of living differences
    col_adjusted_values = []
    for offer in comparison_results["offers"]:
        col_index = 100  # Default
        # Use cost of living index if available in the data (not currently passed through)
        adjusted_value = offer["compensation"]["total_annual_value"] * (100 / col_index)
        col_adjusted_values.append((offer, adjusted_value))

    sorted_by_col = sorted(col_adjusted_values, key=lambda x: x[1], reverse=True)
    if sorted_by_col and len(sorted_by_col) > 0:
        comparison_results["recommendations"]["best_col_adjusted"] = sorted_by_col[0][0]["company"]
    
    # Display the transformed comparison results
    ui.display_comparison_results(comparison_results)
    
    # Save to file if requested
    if args.save:
        try:
            # Update the data file path in the comparison engine
            comparison_engine.data_file = args.save
            comparison_engine.save_offers()
            ui.display_message(f"Saved job offers to {args.save}")
        except Exception as e:
            ui.display_error(f"Failed to save job offers: {e}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())