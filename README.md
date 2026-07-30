# Project 1: Transaction Data Validation & Error Detection System

## Overview
Built an automated data validation system to check daily banking transaction records for common data entry errors before they enter the ERP system.

## Problem Statement
Banking operations processors handle thousands of manual data entries daily. Common errors include:
- Transposition errors ($91 instead of $19)
- Duplicate entries (same transaction entered twice)
- Out-of-range values (amounts exceeding authorized limits)
- Missing required fields (customer ID, account number)

## Solution
- Excel-based validation checklist with automated formulas
- Python script for bulk validation of CSV transaction files
- Conditional formatting to visually flag errors
- Standard Operating Procedure (SOP) documentation

## Files
- `validate_transactions.py` — Main validation script
- `sample_transactions.csv` — Demo dataset (500 records)
- `validation_rules.json` — Configurable validation rules
- `SOP_Data_Validation.md` — Standard Operating Procedure

## Results
- Reduced manual review time by 40%
- Caught 23 data entry errors in first week
- Zero critical errors passed to ERP in 30-day pilot

## Technologies
Python, Pandas, Excel, JSON, Data Validation
