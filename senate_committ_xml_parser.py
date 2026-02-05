# Senate Committee Roster XML Scraper
# Written by Lily Gates
# Originally Created 2/2026

"""
NOTE:
Requires user to have XML documents pulled from senate.gov
XML docs should be saved in current working directory before running script

SCRIPT:
1. Load all committee member XMLs

2. Clean and create full_name

3. Build the committee/subcommittee hierarchy map

4. Merge members with hierarchy

5. Return three DataFrames for flexible use:
    - committee_members → raw member info with full_name
    - committee_hierarchy_map → normalized hierarchy table
    - members_with_hierarchy → fully merged, analysis-ready table

"""

import pandas as pd
import xml.etree.ElementTree as ET
from glob import glob
import os

# -------------------------------------
# 1. Load all committee members
# -------------------------------------
def load_committee_memberships():
    """
    Parse all committee_memberships_*.xml files in the cwd
    and return a DataFrame of members.
    """
    xml_files = glob("committee_memberships_*.xml")
    all_rows = []

    for file_path in xml_files:
        file_committee_abbrev = os.path.basename(file_path)\
            .replace("committee_memberships_", "")\
            .replace(".xml", "")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError:
            print(f"Skipping invalid XML file: {file_path}")
            continue

        for committee in root.findall(".//committees"):
            committee_name = committee.findtext("committee_name")
            committee_code = committee.findtext("committee_code")
            majority_party = committee.findtext("majority_party")

            # --- Main Committee Members ---
            members = committee.find("members")
            if members is not None:
                for member in members.findall("member"):
                    all_rows.append({
                        "file_committee_abbrev": file_committee_abbrev,
                        "committee_name": committee_name,
                        "committee_code": committee_code,
                        "subcommittee_name": None,
                        "subcommittee_code": None,
                        "member_first": member.findtext("name/first"),
                        "member_last": member.findtext("name/last"),
                        "state": member.findtext("state"),
                        "party": member.findtext("party"),
                        "position": member.findtext("position"),
                        "majority_party": majority_party,
                        "source_file": os.path.basename(file_path)
                    })

            # --- Subcommittee Members ---
            for sub in committee.findall("subcommittee"):
                sub_name = sub.findtext("subcommittee_name")
                sub_code = sub.findtext("committee_code")

                sub_members = sub.find("members")
                if sub_members is not None:
                    for member in sub_members.findall("member"):
                        all_rows.append({
                            "file_committee_abbrev": file_committee_abbrev,
                            "committee_name": committee_name,
                            "committee_code": committee_code,
                            "subcommittee_name": sub_name,
                            "subcommittee_code": sub_code,
                            "member_first": member.findtext("name/first"),
                            "member_last": member.findtext("name/last"),
                            "state": member.findtext("state"),
                            "party": member.findtext("party"),
                            "position": member.findtext("position"),
                            "majority_party": majority_party,
                            "source_file": os.path.basename(file_path)
                        })

    members_df = pd.DataFrame(all_rows)

    # Clean full_name
    members_df["full_name"] = members_df["member_first"].str.strip() + " " + members_df["member_last"].str.strip()

    # Sort
    members_df = members_df.sort_values(
        ["file_committee_abbrev", "committee_name", "subcommittee_name", "member_last"]
    ).reset_index(drop=True)

    return members_df

# -------------------------------------
# 2. Build committee hierarchy map
# -------------------------------------
def build_committee_hierarchy_map():
    """
    Builds a hierarchical map of committees and subcommittees.
    Returns a DataFrame with:
    file_committee_abbrev, committee_code, committee_name,
    subcommittee_code, subcommittee_name, level
    """
    xml_files = glob("committee_memberships_*.xml")
    hierarchy_rows = []

    for file_path in xml_files:
        file_committee_abbrev = os.path.basename(file_path)\
            .replace("committee_memberships_", "")\
            .replace(".xml", "")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError:
            print(f"Skipping invalid XML file: {file_path}")
            continue

        for committee in root.findall(".//committees"):
            committee_name = committee.findtext("committee_name")
            committee_code = committee.findtext("committee_code")

            # Main committee row
            hierarchy_rows.append({
                "file_committee_abbrev": file_committee_abbrev,
                "committee_code": committee_code,
                "committee_name": committee_name,
                "subcommittee_code": "MAIN",
                "subcommittee_name": "Main Committee",
                "level": "Main Committee"
            })

            # Subcommittees
            for sub in committee.findall("subcommittee"):
                sub_name = sub.findtext("subcommittee_name")
                sub_code = sub.findtext("committee_code")

                hierarchy_rows.append({
                    "file_committee_abbrev": file_committee_abbrev,
                    "committee_code": committee_code,
                    "committee_name": committee_name,
                    "subcommittee_code": sub_code,
                    "subcommittee_name": sub_name,
                    "level": "Subcommittee"
                })

    hierarchy_df = pd.DataFrame(hierarchy_rows)
    hierarchy_df = hierarchy_df.drop_duplicates().sort_values(
        ["file_committee_abbrev", "committee_code", "subcommittee_code"]
    ).reset_index(drop=True)

    return hierarchy_df

# -------------------------------------
# 3. Merge members with hierarchy
# -------------------------------------
def get_members_with_hierarchy():
    """
    Returns a merged DataFrame of members + hierarchy info
    """
    # Load members and hierarchy
    members_df = load_committee_memberships()
    hierarchy_df = build_committee_hierarchy_map()

    # Fill missing subcommittee codes for main committee members
    members_df["subcommittee_code"] = members_df["subcommittee_code"].fillna("MAIN")

    # Merge
    merged_df = pd.merge(
        members_df,
        hierarchy_df,
        how="left",
        on=["file_committee_abbrev", "committee_code", "subcommittee_code"],
        suffixes=("", "_hierarchy")
    )

    # Sort nicely
    merged_df = merged_df.sort_values(
        ["file_committee_abbrev", "committee_name", "subcommittee_name", "member_last"]
    ).reset_index(drop=True)

    return merged_df

# -------------------------------------
# 4. Example usage
# -------------------------------------
if __name__ == "__main__":
    # Raw members
    committee_members = load_committee_memberships()
    print("Members DF preview:")
    print(committee_members.head())

    # Committee hierarchy map
    committee_hierarchy_map = build_committee_hierarchy_map()
    print("\nHierarchy map preview:")
    print(committee_hierarchy_map.head())

    # Merged members with hierarchy
    members_with_hierarchy = get_members_with_hierarchy()
    print("\nMerged members with hierarchy preview:")
    print(members_with_hierarchy.head())

    # ------------------------------
    # Export merged members to CSV
    # ------------------------------
    members_with_hierarchy.to_csv("committee_members_with_hierarchy.csv", index=False)
    print("\n[INFO] Exported members_with_hierarchy to committee_members_with_hierarchy.csv")