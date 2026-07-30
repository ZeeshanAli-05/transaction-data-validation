"""
Transaction Data Validation & Error Detection System
=====================================================
Validates banking transaction records for common data entry errors.

Usage:
    python validate_transactions.py --input sample_transactions.csv --output validated_output.csv
"""

import pandas as pd
import json
import argparse
from datetime import datetime
import re

# Load validation rules
with open('validation_rules.json', 'r') as f:
    RULES = json.load(f)


def check_transposition_error(amount):
    """
    Detects potential transposition errors by comparing digits.
    Example: $91 vs $19, $123 vs $132
    """
    amount_str = str(int(abs(amount)))
    if len(amount_str) >= 2:
        # Check if reversing last two digits gives a common pattern
        reversed_last_two = amount_str[:-2] + amount_str[-1] + amount_str[-2]
        if int(reversed_last_two) in RULES['common_amounts']:
            return True
    return False


def validate_transactions(df):
    """
    Main validation function. Checks all records and returns:
    - cleaned_df: records that passed validation
    - errors_df: records with errors + error descriptions
    - summary: validation statistics
    """
    errors = []

    for idx, row in df.iterrows():
        error_list = []

        # 1. Check for missing required fields
        required_fields = ['transaction_id', 'customer_id', 'account_number', 'amount', 'transaction_date']
        for field in required_fields:
            if pd.isna(row.get(field)) or str(row.get(field)).strip() == '':
                error_list.append(f"Missing required field: {field}")

        # 2. Check amount is within valid range
        amount = row.get('amount', 0)
        if amount < RULES['min_amount'] or amount > RULES['max_amount']:
            error_list.append(f"Amount out of range: {amount} (valid: {RULES['min_amount']}-{RULES['max_amount']})")

        # 3. Check for negative amounts (unless explicitly allowed)
        if amount < 0 and not RULES['allow_negative']:
            error_list.append(f"Negative amount not allowed: {amount}")

        # 4. Check account number format (10 digits)
        account = str(row.get('account_number', ''))
        if not re.match(r'^\d{10}$', account):
            error_list.append(f"Invalid account number format: {account} (expected 10 digits)")

        # 5. Check transaction date is not in future
        try:
            tx_date = pd.to_datetime(row.get('transaction_date'))
            if tx_date > datetime.now():
                error_list.append(f"Future transaction date: {tx_date.date()}")
        except:
            error_list.append("Invalid transaction date format")

        # 6. Check for transposition error
        if check_transposition_error(amount):
            error_list.append(f"Possible transposition error in amount: {amount}")

        # 7. Check customer ID format
        cust_id = str(row.get('customer_id', ''))
        if not re.match(r'^CUST_\d{6}$', cust_id):
            error_list.append(f"Invalid customer ID format: {cust_id} (expected CUST_######)")

        # Record errors
        if error_list:
            errors.append({
                'row_index': idx,
                'transaction_id': row.get('transaction_id', 'N/A'),
                'errors': ' | '.join(error_list),
                'error_count': len(error_list)
            })

    # Create errors DataFrame
    errors_df = pd.DataFrame(errors)

    # Clean data: remove rows with errors
    error_indices = errors_df['row_index'].tolist() if not errors_df.empty else []
    cleaned_df = df.drop(error_indices).reset_index(drop=True)

    # Generate summary
    summary = {
        'total_records': len(df),
        'valid_records': len(cleaned_df),
        'error_records': len(errors_df),
        'error_rate_pct': round(len(errors_df) / len(df) * 100, 2),
        'validation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'error_breakdown': {}
    }

    # Break down error types
    if not errors_df.empty:
        all_errors = ' | '.join(errors_df['errors'].tolist()).split(' | ')
        error_counts = {}
        for err in all_errors:
            err_type = err.split(':')[0] if ':' in err else err
            error_counts[err_type] = error_counts.get(err_type, 0) + 1
        summary['error_breakdown'] = error_counts

    return cleaned_df, errors_df, summary


def generate_report(summary, output_path='validation_report.txt'):
    """Generates a human-readable validation report."""
    with open(output_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("TRANSACTION DATA VALIDATION REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Validation Date: {summary['validation_timestamp']}\n")
        f.write(f"Total Records Processed: {summary['total_records']}\n")
        f.write(f"Valid Records: {summary['valid_records']}\n")
        f.write(f"Records with Errors: {summary['error_records']}\n")
        f.write(f"Error Rate: {summary['error_rate_pct']}%\n\n")

        f.write("-" * 40 + "\n")
        f.write("ERROR BREAKDOWN\n")
        f.write("-" * 40 + "\n")
        for err_type, count in summary['error_breakdown'].items():
            f.write(f"  {err_type}: {count}\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("RECOMMENDATIONS\n")
        f.write("=" * 60 + "\n")
        if summary['error_rate_pct'] > 5:
            f.write("⚠️  High error rate detected. Recommend:\n")
            f.write("   1. Review data entry training for operations team\n")
            f.write("   2. Implement field-level validation in ERP input forms\n")
            f.write("   3. Add real-time alerts for out-of-range values\n")
        else:
            f.write("✅ Error rate within acceptable limits.\n")
            f.write("   Continue monitoring and weekly audits.\n")

    print(f"✅ Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Validate transaction data')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', default='validated_output.csv', help='Output CSV file path')
    parser.add_argument('--report', default='validation_report.txt', help='Report file path')
    args = parser.parse_args()

    # Load data
    print(f"📂 Loading data from: {args.input}")
    df = pd.read_csv(args.input)
    print(f"📊 Loaded {len(df)} records")

    # Validate
    print("🔍 Running validation checks...")
    cleaned_df, errors_df, summary = validate_transactions(df)

    # Save outputs
    cleaned_df.to_csv(args.output, index=False)
    print(f"✅ Cleaned data saved to: {args.output} ({len(cleaned_df)} records)")

    if not errors_df.empty:
        errors_df.to_csv('error_records.csv', index=False)
        print(f"⚠️  Error records saved to: error_records.csv ({len(errors_df)} records)")

    # Generate report
    generate_report(summary, args.report)

    # Print summary to console
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total Records: {summary['total_records']}")
    print(f"Valid Records: {summary['valid_records']}")
    print(f"Errors Found: {summary['error_records']}")
    print(f"Error Rate: {summary['error_rate_pct']}%")


if __name__ == '__main__':
    main()
