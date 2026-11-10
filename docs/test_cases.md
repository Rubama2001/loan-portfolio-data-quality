# Test Cases

Data is generated with a fixed random seed, so results are repeatable.

| ID | What is tested | Steps | Expected result | Result |
|---|---|---|---|---|
| TC01 | Data generation | Run `python generate_data.py` | loans.db created with 10 branches, 515 customers, 760 loans | Pass |
| TC02 | Missing NID check | Run `dq_missing_nid` | 12 rows | Pass |
| TC03 | Duplicate NID check | Run `dq_duplicate_nid` | 15 rows | Pass |
| TC04 | Invalid phone check | Run `dq_invalid_phone` | 10 rows | Pass |
| TC05 | Invalid principal check | Run `dq_invalid_principal` | 8 rows | Pass |
| TC06 | Orphan loan check | Run `dq_orphan_loans` | 6 rows | Pass |
| TC07 | Payment before disbursement | Run `dq_payment_before_disbursement` | 10 rows | Pass |
| TC08 | Overpayment check | Run `dq_overpayment` | 10 rows | Pass |
| TC09 | Report export | Run `python run_checks.py` | Excel file with a summary sheet and one sheet per query | Pass |
| TC10 | Dashboard export | Run `python run_checks.py` | dashboard.png with 4 charts | Pass |
| TC11 | Clean-data sanity | Check analysis queries exclude loans with principal <= 0 | Bad loans do not appear in branch or product totals | Pass |

## Defect log
| ID | Defect | Found in | Status |
|---|---|---|---|
| D01 | Planted missing-NID customers overlapped with duplicate-NID customers, so duplicates were under-counted | generate_data.py | Fixed |
