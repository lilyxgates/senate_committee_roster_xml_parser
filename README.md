# Committee Membership XML Parser

A Python module to parse `committee_memberships_*.xml` files, clean and organize committee and subcommittee data, and produce analysis-ready DataFrames and CSV files.

> **Note:** This module requires users to first download committee membership XML files from [senate.gov](https://www.senate.gov/) and save them in the **current working directory**. The module will not run without these files.

---

## **Features**

- Load and parse multiple XML files in the current working directory.
- Clean member names and create a `full_name` column.
- Build a **hierarchy map** of committees and subcommittees.
- Merge member data with hierarchy for a fully analysis-ready table.
- Export the merged dataset to CSV for easy analysis in Excel, PowerBI, or Python.
- Clear, meaningful DataFrame names:
  - `committee_members` → raw member info
  - `committee_hierarchy_map` → normalized hierarchy map
  - `members_with_hierarchy` → merged, ready-to-use table

---

## **File Naming Convention**

The module expects XML files in the current working directory with the following naming pattern:

Where `****` is the **abbreviation code** of the committee, e.g., `SSAF`.

**Note:**  This is the default naming convention from senate.gov, so updating will not be necessary