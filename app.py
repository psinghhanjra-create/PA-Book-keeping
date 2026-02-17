from flask import Flask, render_template, request
import csv
import requests
from io import StringIO
from datetime import datetime

app = Flask(__name__)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1i-92YdC6DnenVza8z7ch3iqDHFzaqZq1P3162gdUdDk/export?format=csv"


def get_data():
    response = requests.get(SHEET_URL)
    data = response.text
    reader = csv.DictReader(StringIO(data))
    rows = []

    for row in reader:
        if not row["Amount"]:
            continue

        row["Amount"] = float(row["Amount"])
        row["Date"] = datetime.strptime(row["Date"], "%d-%m-%Y")
        rows.append(row)

    return rows


@app.route("/", methods=["GET"])
def dashboard():

    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    category = request.args.get("category")
    payment = request.args.get("payment")
    show_details = request.args.get("details")

    # Always load categories/payments
    rows = get_data()
    categories = sorted(set(r["Category"] for r in rows))
    payments = sorted(set(r["Payment Method"] for r in rows))

    # Default blank state
    if not from_date or not to_date:
        return render_template(
            "dashboard.html",
            total=0,
            rows=[],
            summary={},
            show_details=False,
            categories=categories,
            payments=payments
        )

    filtered_rows = []
    total = 0
    category_summary = {}

    from_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_dt = datetime.strptime(to_date, "%Y-%m-%d")

    for row in rows:
        if row["Date"] < from_dt:
            continue
        if row["Date"] > to_dt:
            continue
        if category and category != "All":
            if row["Category"] != category:
                continue
        if payment and payment != "All":
            if row["Payment Method"] != payment:
                continue

        total += row["Amount"]
        filtered_rows.append(row)

        cat = row["Category"]
        if cat not in category_summary:
            category_summary[cat] = 0
        category_summary[cat] += row["Amount"]

    return render_template(
        "dashboard.html",
        total=total,
        rows=filtered_rows,
        summary=category_summary,
        show_details=show_details,
        categories=categories,
        payments=payments
    )


if __name__ == "__main__":
    app.run(debug=True)
