-- ============================================================
-- All SQL for the project. run_checks.py reads this file.
-- Each query starts with a line:  -- name: <query_name>
-- Dataset "today" = 2026-11-09
-- ============================================================

-- PART A: DATA-QUALITY CHECKS (each should return the planted errors)

-- name: dq_missing_nid
SELECT customer_id, full_name, branch_id
FROM customers
WHERE nid IS NULL OR TRIM(nid) = '';

-- name: dq_duplicate_nid
SELECT nid, COUNT(*) AS times_registered, GROUP_CONCAT(customer_id) AS customer_ids
FROM customers
WHERE nid IS NOT NULL
GROUP BY nid
HAVING COUNT(*) > 1;

-- name: dq_invalid_phone
SELECT customer_id, full_name, phone
FROM customers
WHERE phone IS NULL OR LENGTH(phone) <> 11;

-- name: dq_invalid_principal
SELECT loan_id, customer_id, product, principal
FROM loans
WHERE principal <= 0;

-- name: dq_orphan_loans
SELECT l.loan_id, l.customer_id, l.product, l.principal
FROM loans l
LEFT JOIN customers c ON c.customer_id = l.customer_id
WHERE c.customer_id IS NULL;

-- name: dq_payment_before_disbursement
SELECT r.repayment_id, r.loan_id, l.disbursement_date, r.paid_date
FROM repayments r
JOIN loans l ON l.loan_id = r.loan_id
WHERE r.paid_date < l.disbursement_date;

-- name: dq_overpayment
SELECT repayment_id, loan_id, amount_due, amount_paid
FROM repayments
WHERE amount_paid > amount_due * 1.5;

-- PART B: BUSINESS ANALYSIS

-- name: overdue_ratio_by_branch
-- Share of installments that are due but still unpaid, per branch
SELECT b.branch_name,
       COUNT(*) AS installments_due,
       SUM(CASE WHEN r.paid_date IS NULL THEN 1 ELSE 0 END) AS unpaid,
       ROUND(100.0 * SUM(CASE WHEN r.paid_date IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS overdue_pct
FROM repayments r
JOIN loans l     ON l.loan_id = r.loan_id
JOIN customers c ON c.customer_id = l.customer_id
JOIN branches b  ON b.branch_id = c.branch_id
WHERE r.due_date <= '2026-11-09'
  AND l.principal > 0
GROUP BY b.branch_name
ORDER BY overdue_pct DESC;

-- name: monthly_disbursement
SELECT STRFTIME('%Y-%m', disbursement_date) AS month,
       COUNT(*) AS loans_disbursed,
       SUM(principal) AS total_disbursed
FROM loans
WHERE principal > 0
GROUP BY month
ORDER BY month;

-- name: top5_branches_repayment_rate
SELECT b.branch_name,
       ROUND(100.0 * SUM(r.amount_paid) / SUM(r.amount_due), 2) AS repayment_rate_pct
FROM repayments r
JOIN loans l     ON l.loan_id = r.loan_id
JOIN customers c ON c.customer_id = l.customer_id
JOIN branches b  ON b.branch_id = c.branch_id
WHERE l.principal > 0
  AND r.amount_paid <= r.amount_due * 1.5
GROUP BY b.branch_name
ORDER BY repayment_rate_pct DESC
LIMIT 5;

-- name: top3_loans_per_branch
-- Window function: rank loans by size inside each branch
SELECT *
FROM (
    SELECT b.branch_name, l.loan_id, l.product, l.principal,
           ROW_NUMBER() OVER (PARTITION BY b.branch_id ORDER BY l.principal DESC) AS rank_in_branch
    FROM loans l
    JOIN customers c ON c.customer_id = l.customer_id
    JOIN branches b  ON b.branch_id = c.branch_id
    WHERE l.principal > 0
)
WHERE rank_in_branch <= 3
ORDER BY branch_name, rank_in_branch;

-- name: cumulative_disbursement
-- Window function: running total of money lent over time
SELECT month, total_disbursed,
       SUM(total_disbursed) OVER (ORDER BY month) AS running_total
FROM (
    SELECT STRFTIME('%Y-%m', disbursement_date) AS month,
           SUM(principal) AS total_disbursed
    FROM loans
    WHERE principal > 0
    GROUP BY month
);

-- name: product_mix
SELECT product, COUNT(*) AS loans, SUM(principal) AS total_principal
FROM loans
WHERE principal > 0
GROUP BY product
ORDER BY total_principal DESC;
