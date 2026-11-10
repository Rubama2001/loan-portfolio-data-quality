"""
Step 2: Run every SQL query, export an Excel report, and draw a dashboard image.
Run:  python run_checks.py
"""
import re
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DB_PATH = "loans.db"
SQL_FILE = "sql/queries.sql"
EXCEL_OUT = "output/data_quality_report.xlsx"
DASH_OUT = "output/dashboard.png"


def load_queries(path):
    """Split queries.sql into {name: sql} using the '-- name:' markers."""
    text = open(path, encoding="utf-8").read()
    parts = re.split(r"^-- name:\s*(\w+)\s*$", text, flags=re.MULTILINE)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def main():
    con = sqlite3.connect(DB_PATH)
    queries = load_queries(SQL_FILE)
    results = {name: pd.read_sql_query(sql, con) for name, sql in queries.items()}

    # ---- Summary of data-quality checks ----
    summary = pd.DataFrame(
        [{"check": n, "issues_found": len(df), "status": "PASS" if len(df) == 0 else "FAIL"}
         for n, df in results.items() if n.startswith("dq_")]
    )
    print("\nDATA QUALITY SUMMARY")
    print(summary.to_string(index=False))

    # ---- Excel report ----
    with pd.ExcelWriter(EXCEL_OUT, engine="openpyxl") as xl:
        summary.to_excel(xl, sheet_name="summary", index=False)
        for name, df in results.items():
            df.to_excel(xl, sheet_name=name[:31], index=False)
    print("\nExcel report saved:", EXCEL_OUT)

    # ---- Dashboard image (4 charts) ----
    fig, ax = plt.subplots(2, 2, figsize=(13, 8))
    fig.suptitle("Loan Portfolio Dashboard (synthetic data)", fontsize=15, fontweight="bold")

    m = results["monthly_disbursement"]
    ax[0, 0].plot(m["month"], m["total_disbursed"] / 1e6, marker="o")
    ax[0, 0].set_title("Monthly disbursement (BDT million)")
    ax[0, 0].set_xticks(range(0, len(m), 4))
    ax[0, 0].set_xticklabels(m["month"][::4], rotation=45)

    o = results["overdue_ratio_by_branch"]
    ax[0, 1].barh(o["branch_name"], o["overdue_pct"], color="indianred")
    ax[0, 1].set_title("Unpaid installments by branch (%)")
    ax[0, 1].invert_yaxis()

    t = results["top5_branches_repayment_rate"]
    ax[1, 0].bar(t["branch_name"], t["repayment_rate_pct"], color="seagreen")
    ax[1, 0].set_title("Top 5 branches by repayment rate (%)")
    ax[1, 0].set_ylim(60, 100)
    ax[1, 0].tick_params(axis="x", rotation=30)

    p = results["product_mix"]
    ax[1, 1].bar(p["product"], p["total_principal"] / 1e6, color="steelblue")
    ax[1, 1].set_title("Loan amount by product (BDT million)")
    ax[1, 1].tick_params(axis="x", rotation=20)

    plt.tight_layout()
    plt.savefig(DASH_OUT, dpi=130)
    print("Dashboard saved:", DASH_OUT)
    con.close()


if __name__ == "__main__":
    main()
