#!/usr/bin/env python3

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DAYS_DIR = ROOT / "days"
README_FILE = ROOT / "README.md"
PROGRESS_FILE = ROOT / "PROGRESS.md"

CATEGORIES = [
    "Linux",
    "Git & GitHub",
    "Docker",
    "Kubernetes",
    "CI/CD",
    "Ansible",
    "Terraform / IaC",
    "AWS / Cloud",
    "Monitoring",
    "DevSecOps",
]


def read_day(day_number):
    """Read metadata from a day's README."""
    day_dir = DAYS_DIR / f"day-{day_number:02d}"
    day_file = day_dir / "README.md"

    if not day_file.exists():
        return None

    content = day_file.read_text(encoding="utf-8")

    metadata = {}

    # Read simple front-matter fields:
    # day: 1
    # topic: Linux
    # category: Linux
    # status: completed

    match = re.search(
        r"^---\s*\n(.*?)\n---",
        content,
        re.MULTILINE | re.DOTALL,
    )

    if match:
        frontmatter = match.group(1)

        for line in frontmatter.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

    return {
        "day": day_number,
        "topic": metadata.get("topic", "—"),
        "category": metadata.get("category", ""),
        "status": metadata.get("status", "").lower(),
    }


def get_days():
    days = []

    for number in range(1, 101):
        data = read_day(number)

        if data:
            days.append(data)

    return days


def is_completed(day):
    return day["status"] in {
        "completed",
        "complete",
        "done",
    }


def progress_bar(completed, total=100, width=20):
    percentage = round((completed / total) * 100)

    filled = round((percentage / 100) * width)
    empty = width - filled

    return "█" * filled + "░" * empty, percentage


def generate_category_table(days):
    completed_days = [d for d in days if is_completed(d)]

    rows = [
        "| Category | Days | Status |",
        "|---|---:|:---:|",
    ]

    for category in CATEGORIES:
        count = sum(
            1
            for day in completed_days
            if day["category"].lower() == category.lower()
        )

        if count > 0:
            status = "✅"
        else:
            status = "⬜"

        rows.append(
            f"| {category} | {count} | {status} |"
        )

    return "\n".join(rows)


def generate_daily_table(days):
    day_lookup = {
        day["day"]: day
        for day in days
    }

    rows = [
        "| Day | Topic | Status |",
        "|---:|---|:---:|",
    ]

    for number in range(1, 101):
        day = day_lookup.get(number)

        if day and is_completed(day):
            topic = day["topic"]
            status = "✅"
        elif day:
            topic = day["topic"]
            status = "🔄"
        else:
            topic = "—"
            status = "⬜"

        rows.append(
            f"| {number:02d} | {topic} | {status} |"
        )

    return "\n".join(rows)


def generate_progress_section(days):
    completed = sum(
        1 for day in days
        if is_completed(day)
    )

    bar, percentage = progress_bar(completed)

    category_table = generate_category_table(days)
    daily_table = generate_daily_table(days)

    return f"""## 📊 Progress

### Overall Progress

**{completed} / 100 Days Completed**

`{bar}` **{percentage}%**

### 🧰 Category Progress

{category_table}

### 🗓️ Daily Progress

{daily_table}

> This section is automatically updated by `scripts/update-progress.py`.

"""


def update_readme(days):
    content = README_FILE.read_text(encoding="utf-8")

    new_section = generate_progress_section(days)

    pattern = r"## 📊 Progress.*?(?=## 🧰 Technologies)"

    updated, count = re.subn(
        pattern,
        new_section,
        content,
        flags=re.DOTALL,
    )

    if count == 0:
        print("⚠️ Could not find the Progress section in README.md")
        return

    README_FILE.write_text(
        updated,
        encoding="utf-8",
    )


def update_progress_file(days):
    completed = sum(
        1 for day in days
        if is_completed(day)
    )

    bar, percentage = progress_bar(completed)

    category_table = generate_category_table(days)
    daily_table = generate_daily_table(days)

    content = f"""# 📊 100 Days of DevOps — Progress Tracker

My day-by-day progress through the 100 Days of DevOps challenge.

## Overall Progress

**{completed} / 100 Days Completed**

`{bar}` **{percentage}%**

## Category Progress

{category_table}

## Daily Progress

{daily_table}

---

### Legend

- ⬜ Not started
- 🔄 In progress
- ✅ Completed

> This file is automatically updated by `scripts/update-progress.py`.
"""

    PROGRESS_FILE.write_text(
        content,
        encoding="utf-8",
    )


def main():
    days = get_days()

    completed = sum(
        1 for day in days
        if is_completed(day)
    )

    update_readme(days)
    update_progress_file(days)

    print()
    print("🚀 DevOps progress updated!")
    print()
    print(f"Completed: {completed}/100")
    print(f"Progress:  {completed}%")
    print()
    print("Updated:")
    print("  ✓ README.md")
    print("  ✓ PROGRESS.md")
    print()


if __name__ == "__main__":
    main()
