"""
Step 1: Create a FAKE loan database (SQLite) with deliberately planted errors.
No real customer data is used anywhere in this project.
Run:  python generate_data.py
"""
import random
import sqlite3
from datetime import date, timedelta

import pandas as pd
from faker import Faker

random.seed(42)
fake = Faker()
Faker.seed(42)

AS_OF = date(2026, 11, 9)  # the "today" of our dataset
DB_PATH = "loans.db"

# ---------- 1. Branches ----------
branches = [
    (1, "Gulshan", "Dhaka"), (2, "Motijheel", "Dhaka"), (3, "Uttara", "Dhaka"),
    (4, "Dhanmondi", "Dhaka"), (5, "Agrabad", "Chattogram"), (6, "Khulshi", "Chattogram"),
    (7, "Zindabazar", "Sylhet"), (8, "Rajshahi Sadar", "Rajshahi"),
    (9, "Khulna Sadar", "Khulna"), (10, "Bogura Sadar", "Rajshahi"),
]
# how reliable customers are in each branch (chance of paying on time)
branch_reliability = {1: .93, 2: .88, 3: .90, 4: .91, 5: .82,
                      6: .85, 7: .78, 8: .80, 9: .75, 10: .83}

# ---------- 2. Customers ----------
customers = []
for cid in range(1, 501):
    customers.append({
        "customer_id": cid,
        "full_name": fake.name(),
        "nid": str(random.randint(10**12, 10**13 - 1)),   # 13-digit fake NID
        "phone": "01" + str(random.randint(3, 9)) + str(random.randint(10**7, 10**8 - 1)),
        "branch_id": random.choice(branches)[0],
        "created_date": (date(2023, 1, 1) + timedelta(days=random.randint(0, 900))).isoformat(),
    })
cust_by_id = {c["customer_id"]: c for c in customers}

# ---------- 3. Loans ----------
products = {"Personal Loan": (0.13, 0.16), "SME Loan": (0.11, 0.14),
            "Auto Loan": (0.10, 0.12), "Home Loan": (0.09, 0.11)}
loans = []
for lid in range(1, 761):
    prod = random.choice(list(products))
    rate = round(random.uniform(*products[prod]), 3)
    loans.append({
        "loan_id": lid,
        "customer_id": random.randint(1, 500),
        "product": prod,
        "principal": random.choice(range(50_000, 2_000_001, 25_000)),
        "interest_rate": rate,
        "disbursement_date": (date(2024, 1, 1) + timedelta(days=random.randint(0, 880))).isoformat(),
        "tenure_months": random.choice([12, 24, 36]),
        "status": "Active",
    })

# ---------- 4. Repayments ----------
repayments, rid = [], 1
for loan in loans:
    branch = cust_by_id[loan["customer_id"]]["branch_id"]
    p_on_time = branch_reliability[branch]
    emi = loan["principal"] * (1 + loan["interest_rate"] * loan["tenure_months"] / 12) / loan["tenure_months"]
    start = date.fromisoformat(loan["disbursement_date"])
    paid_count = 0
    for k in range(1, loan["tenure_months"] + 1):
        due = start + timedelta(days=30 * k)
        if due > AS_OF:
            break
        r = random.random()
        if r < p_on_time:
            paid = due + timedelta(days=random.randint(-2, 5)); amt = round(emi, 2)
        elif r < p_on_time + 0.10:
            paid = due + timedelta(days=random.randint(10, 45)); amt = round(emi, 2)
        else:
            paid, amt = None, 0.0
        if paid and paid > AS_OF:
            paid, amt = None, 0.0
        repayments.append({"repayment_id": rid, "loan_id": loan["loan_id"],
                           "due_date": due.isoformat(),
                           "paid_date": paid.isoformat() if paid else None,
                           "amount_due": round(emi, 2), "amount_paid": amt})
        rid += 1
        paid_count += 1
    if paid_count >= loan["tenure_months"]:
        loan["status"] = "Closed"
for loan in random.sample(loans, 12):
    loan["status"] = "Written-off"

# ---------- 5. Plant data-quality errors (the checks must find these) ----------
planted = {}

# 5a. duplicate NIDs (same person registered twice)
dups = random.sample(customers[:500], 15)
next_id = 501
for c in dups:
    copy = dict(c); copy["customer_id"] = next_id; next_id += 1
    customers.append(copy)
planted["duplicate_nid (pairs)"] = 15

# 5b. missing NID
dup_ids = {c["customer_id"] for c in dups}
for c in random.sample([c for c in customers[:500] if c["customer_id"] not in dup_ids], 12):
    c["nid"] = None
planted["missing_nid"] = 12

# 5c. invalid phone numbers (not 11 digits)
for c in random.sample(customers[:500], 10):
    c["phone"] = c["phone"][:8]
planted["invalid_phone"] = 10

# 5d. negative / zero principal
for l in random.sample(loans, 8):
    l["principal"] = random.choice([-100_000, 0, -50_000])
planted["invalid_principal"] = 8

# 5e. orphan loans (customer does not exist)
for l in random.sample(loans, 6):
    l["customer_id"] = 99_000 + l["loan_id"]
planted["orphan_loans"] = 6

# 5f. payment made BEFORE the loan was disbursed
loan_by_id = {l["loan_id"]: l for l in loans}
paid_rows = [r for r in repayments if r["paid_date"]]
for r in random.sample(paid_rows, 10):
    disb = date.fromisoformat(loan_by_id[r["loan_id"]]["disbursement_date"])
    r["paid_date"] = (disb - timedelta(days=random.randint(5, 40))).isoformat()
planted["payment_before_disbursement"] = 10

# 5g. overpayments
paid_rows = [r for r in repayments if r["paid_date"] and r["amount_paid"] == r["amount_due"]]
for r in random.sample(paid_rows, 10):
    r["amount_paid"] = round(r["amount_due"] * random.uniform(1.6, 3.0), 2)
planted["overpayment"] = 10

# ---------- 6. Write to SQLite ----------
con = sqlite3.connect(DB_PATH)
with open("sql/schema.sql") as f:
    con.executescript(f.read())
pd.DataFrame(branches, columns=["branch_id", "branch_name", "division"]).to_sql("branches", con, if_exists="append", index=False)
pd.DataFrame(customers).to_sql("customers", con, if_exists="append", index=False)
pd.DataFrame(loans).to_sql("loans", con, if_exists="append", index=False)
pd.DataFrame(repayments).to_sql("repayments", con, if_exists="append", index=False)
con.commit()

print("Database created:", DB_PATH)
for t in ["branches", "customers", "loans", "repayments"]:
    print(f"  {t:<12} {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]} rows")
print("\nErrors we planted on purpose (your SQL checks should find these):")
for k, v in planted.items():
    print(f"  {k}: {v}")
con.close()
