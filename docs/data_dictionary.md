# Data Dictionary

## branches
| Column | Type | Description |
|---|---|---|
| branch_id | INTEGER (PK) | Unique branch ID |
| branch_name | TEXT | Branch name |
| division | TEXT | Division of Bangladesh the branch is in |

## customers
| Column | Type | Description |
|---|---|---|
| customer_id | INTEGER (PK) | Unique customer ID |
| full_name | TEXT | Customer name (fake) |
| nid | TEXT | 13-digit National ID (fake). Must be present and unique |
| phone | TEXT | Mobile number, must be 11 digits |
| branch_id | INTEGER (FK) | Branch that serves the customer |
| created_date | TEXT (YYYY-MM-DD) | Date the customer was registered |

## loans
| Column | Type | Description |
|---|---|---|
| loan_id | INTEGER (PK) | Unique loan ID |
| customer_id | INTEGER (FK) | Borrower. Must exist in customers |
| product | TEXT | Personal / SME / Auto / Home Loan |
| principal | REAL | Amount lent in BDT. Must be > 0 |
| interest_rate | REAL | Annual interest rate (0.12 = 12%) |
| disbursement_date | TEXT | Date the money was given |
| tenure_months | INTEGER | Loan length: 12, 24 or 36 months |
| status | TEXT | Active / Closed / Written-off |

## repayments
| Column | Type | Description |
|---|---|---|
| repayment_id | INTEGER (PK) | Unique installment record |
| loan_id | INTEGER (FK) | Loan this installment belongs to |
| due_date | TEXT | Date the installment is due |
| paid_date | TEXT | Date paid. NULL means not paid. Must not be before disbursement_date |
| amount_due | REAL | Installment amount (EMI) in BDT |
| amount_paid | REAL | Amount actually paid. 0 if unpaid |

## Relationships
branches 1 - many customers 1 - many loans 1 - many repayments
