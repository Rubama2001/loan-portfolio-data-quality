-- Database schema for the Loan Portfolio project
DROP TABLE IF EXISTS repayments;
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS branches;

CREATE TABLE branches (
    branch_id   INTEGER PRIMARY KEY,
    branch_name TEXT NOT NULL,
    division    TEXT NOT NULL
);

CREATE TABLE customers (
    customer_id  INTEGER PRIMARY KEY,
    full_name    TEXT NOT NULL,
    nid          TEXT,
    phone        TEXT,
    branch_id    INTEGER,
    created_date TEXT,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE loans (
    loan_id           INTEGER PRIMARY KEY,
    customer_id       INTEGER NOT NULL,
    product           TEXT NOT NULL,
    principal         REAL NOT NULL,
    interest_rate     REAL NOT NULL,
    disbursement_date TEXT NOT NULL,
    tenure_months     INTEGER NOT NULL,
    status            TEXT NOT NULL
);

CREATE TABLE repayments (
    repayment_id INTEGER PRIMARY KEY,
    loan_id      INTEGER NOT NULL,
    due_date     TEXT NOT NULL,
    paid_date    TEXT,
    amount_due   REAL NOT NULL,
    amount_paid  REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
);
