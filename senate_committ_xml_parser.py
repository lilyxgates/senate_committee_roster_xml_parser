# Senate Committee Roster XML Scraper
# Written by Lily Gates
# Originally Created 2/2026

import pandas as pd
import xml.etree.ElementTree as ET
from glob import glob
import os

import pandas as pd
import xml.etree.ElementTree as ET
from glob import glob
import os


def load_committee_memberships():

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

            # ---- MAIN COMMITTEE MEMBERS ----
            members = committee.find("members")
            if members is not None:
                for member in members.findall("member"):
                    all_rows.append({
                        "file_committee_abbrev": file_committee_abbrev,
                        "committee_name": committee_name,
                        "committee_code": committee_code,
                        "subcommittee_name": None,
                        "member_first": member.findtext("name/first"),
                        "member_last": member.findtext("name/last"),
                        "state": member.findtext("state"),
                        "party": member.findtext("party"),
                        "position": member.findtext("position"),
                        "majority_party": majority_party,
                        "source_file": os.path.basename(file_path)
                    })

            # ---- SUBCOMMITTEES ----
            for sub in committee.findall("subcommittee"):
                subcommittee_name = sub.findtext("subcommittee_name")
                subcommittee_code = sub.findtext("committee_code")

                sub_members = sub.find("members")
                if sub_members is not None:
                    for member in sub_members.findall("member"):
                        all_rows.append({
                            "file_committee_abbrev": file_committee_abbrev,
                            "committee_name": committee_name,
                            "committee_code": committee_code,
                            "subcommittee_name": subcommittee_name,
                            "subcommittee_code": subcommittee_code,
                            "member_first": member.findtext("name/first"),
                            "member_last": member.findtext("name/last"),
                            "state": member.findtext("state"),
                            "party": member.findtext("party"),
                            "position": member.findtext("position"),
                            "majority_party": majority_party,
                            "source_file": os.path.basename(file_path)
                        })

    df = pd.DataFrame(all_rows)
    return df



# --- Preview ---

df = load_committee_memberships()

df.head()
df.info()

# --- Clean Names ---

# Create full name column and sort by last name

df["full_name"] = df["member_first"].str.strip() + " " + df["member_last"].str.strip()

df = df.sort_values(
    ["file_committee_abbrev", "committee_name", "subcommittee_name", "member_last"]
)


# --- Filtered Versions ---

# Main committee members only
main_committee = df[df["subcommittee_name"].isna()]

# Subcommittee members only
subcommittee_members = df[df["subcommittee_name"].notna()]

# All members of a specific committee (e.g., SSAF)
ssaf = df[df["file_committee_abbrev"] == "SSAF"]

# All members of a specific committee (e.g., Commodities)
commodities_sub = df[
    df["subcommittee_name"].str.contains("Commodities", na=False)
]

# All chair
chairs = df[df["position"] == "Chairman"]

# All ranking members
ranking = df[df["position"] == "Ranking"]

# Count members per committee
df.groupby("committee_name")["full_name"].nunique()

# Count members per sub committee
df.groupby("subcommittee_name")["full_name"].nunique().dropna()
