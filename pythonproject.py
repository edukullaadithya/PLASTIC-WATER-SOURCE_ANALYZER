
"""Plastic Waste Source Analyzer - Python case study."""

import csv
from collections import defaultdict
import matplotlib.pyplot as plt


def load_and_clean(path):
    """Read CSV, standardise text, and remove invalid or duplicate rows."""
    clean, seen, log, canon = [], set(), defaultdict(int), {}

    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                year = int(r["year"])
                qty = float(r["waste_tonnes"])
            except (ValueError, TypeError):
                log["missing/non-numeric"] += 1
                continue

            if qty < 0:
                log["negative"] += 1
                continue

            src = r["source"].strip()
            cat = r["category"].strip()

            src = canon.setdefault(
                src.lower(),
                src.title() if src.islower() else src
            )

            if (year, src, cat) in seen:
                log["duplicate"] += 1
                continue

            seen.add((year, src, cat))

            clean.append({
                "year": year,
                "source": src,
                "category": cat,
                "qty": qty
            })

    return clean, dict(log)


def total_by(data, field, year=None):
    """Calculate total waste by source, category, or year."""
    t = defaultdict(float)

    for r in data:
        if year is None or r["year"] == year:
            t[r[field]] += r["qty"]

    return dict(t)


def cagr(first, last, n):
    """Calculate compound annual growth rate."""
    if first <= 0 or n <= 0:
        return 0

    return ((last / first) ** (1 / n) - 1) * 100


def ranked(t):
    """Rank sources or categories by total waste."""
    g = sum(t.values())

    if g == 0:
        return []

    return [
        (k, t[k], round(t[k] / g * 100, 2))
        for k in sorted(t, key=t.get, reverse=True)
    ]


def trends(data, field):
    """Calculate waste growth trends."""
    if not data:
        return []

    y0 = min(r["year"] for r in data)
    y1 = max(r["year"] for r in data)

    a = total_by(data, field, y0)
    b = total_by(data, field, y1)

    rows = [
        (
            k,
            a.get(k, 0),
            b.get(k, 0),
            round(cagr(a.get(k, 0), b.get(k, 0), y1 - y0), 2)
        )
        for k in a
    ]

    return sorted(rows, key=lambda r: -r[3])


def table(title, rows, fmt="{:30s}{:10.1f}{:8.2f}%"):
    """Display analysis results in a table."""
    print("\n" + title)

    for row in rows:
        print(fmt.format(*row))


def charts(data, ts, tc):
    """Generate charts using Matplotlib."""

    def save(name):
        plt.tight_layout()
        plt.savefig(name, dpi=150, bbox_inches="tight")
        plt.close()

    # Bar chart: plastic waste by source
    s = sorted(ts, key=ts.get)

    plt.figure(figsize=(7, 3.8))
    plt.barh(s, [ts[k] for k in s], color="#000000")
    plt.xlabel("Total tonnes")
    plt.title("Plastic Waste by Source")
    save("source_bar.png")

    # Pie chart: plastic waste by category
    plt.figure(figsize=(7, 4.2))
    plt.pie(
        tc.values(),
        labels=tc.keys(),
        autopct="%1.2f%%"
    )
    plt.title("Share of Plastic Waste by Category")
    save("category_pie.png")

    # Line graph: yearly trends by source
    years = sorted({r["year"] for r in data})

    plt.figure(figsize=(7, 4.2))

    for k in ts:
        plt.plot(
            years,
            [total_by(data, "source", y).get(k, 0) for y in years],
            marker="o",
            label=k
        )

    plt.xticks(years)
    plt.ylabel("Waste (tonnes)")
    plt.title("Yearly Trend by Source")
    plt.legend(
        fontsize=7,
        loc="upper left",
        bbox_to_anchor=(1, 1)
    )

    save("yearly_trend.png")


if __name__ == "__main__":

    data, log = load_and_clean("plastic_waste.csv")

    print("Rows kept:", len(data), "| Removed:", log)
    print(
        "Total (tonnes):",
        round(sum(r["qty"] for r in data), 1)
    )

    ts = total_by(data, "source")
    tc = total_by(data, "category")

    table(
        "BY SOURCE",
        ranked(ts),
        "{:30s}{:10.1f}{:8.2f}%"
    )

    table(
        "BY CATEGORY",
        ranked(tc),
        "{:30s}{:10.1f}{:8.2f}%"
    )

    yt = sorted(total_by(data, "year").items())
    table("YEARLY", yt, "{} {:.1f}")

    if len(yt) >= 2:
        print(
            "Overall CAGR %:",
            round(cagr(yt[0][1], yt[-1][1], len(yt) - 1), 2)
        )

    table(
        "SOURCE TREND (2021 -> 2025, CAGR %)",
        trends(data, "source")
    )

    table(
        "CATEGORY TREND",
        trends(data, "category")
    )

    charts(data, ts, tc)

    print("\nCharts saved: 3 PNG files")
```