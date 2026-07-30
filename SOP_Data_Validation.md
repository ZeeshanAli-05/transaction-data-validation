# Standard Operating Procedure (SOP)
## Transaction Data Validation & Error Detection

### Purpose
Ensure all transaction records are validated for accuracy before entry into the ERP system.

### Scope
All operations processors handling daily transaction data entry.

### Procedure

#### Step 1: Data Collection
- Download daily transaction batch from internal operations portal
- Save as CSV file in `\Operations\Daily_Batches\YYYY-MM-DD\`

#### Step 2: Run Validation Script
```bash
python validate_transactions.py --input daily_batch.csv --output validated.csv
```

#### Step 3: Review Error Report
- Open `validation_report.txt`
- If error rate > 5%, escalate to Operations Manager
- If error rate ≤ 5%, proceed to Step 4

#### Step 4: Correct Errors
- Open `error_records.csv`
- Correct each error at source (re-check original documents)
- Re-run validation on corrected records

#### Step 5: Upload to ERP
- Upload `validated.csv` to ERP via standard import procedure
- Confirm upload success in ERP import log

#### Step 6: Archive
- Move original batch, validated file, and report to `\Archive\`
- Retention period: 7 years (regulatory requirement)

### Error Types & Resolution

| Error Type | Cause | Resolution |
|------------|-------|------------|
| Missing required field | Incomplete data entry | Re-check source document |
| Amount out of range | Typo or unauthorized transaction | Verify with supervisor |
| Invalid account number | Wrong account entered | Re-check customer file |
| Future date | System clock error or typo | Correct to actual transaction date |
| Transposition error | Digits swapped during entry | Re-read source amount carefully |
| Invalid customer ID | Wrong format or missing prefix | Use standard CUST_###### format |

### Contact
For script issues: IT Operations Desk (ext. 4500)
For policy questions: Operations Manager
