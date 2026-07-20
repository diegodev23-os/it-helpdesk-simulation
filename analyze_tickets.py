"""
IT Helpdesk Simulation — Ticket Analysis
Reads the Jira CSV export and calculates key support metrics:
- Average resolution time
- SLA compliance
- Incident type breakdown
"""

import pandas as pd
import matplotlib.pyplot as plt

# --- Load data ---
df = pd.read_csv("Jira.csv")

# --- Clean up dates ---
# Jira exports dates like "18/jul/26 9:08 AM" — we need to parse them manually
# because the month is written in Spanish abbreviation (jul, ago, etc.)
month_map = {
    "ene": "Jan", "feb": "Feb", "mar": "Mar", "abr": "Apr",
    "may": "May", "jun": "Jun", "jul": "Jul", "ago": "Aug",
    "sep": "Sep", "oct": "Oct", "nov": "Nov", "dic": "Dec"
}

def parse_jira_date(value):
    if pd.isna(value):
        return pd.NaT
    text = str(value)
    for es, en in month_map.items():
        text = text.replace(f"/{es}/", f"/{en}/")
    return pd.to_datetime(text, format="%d/%b/%y %I:%M %p")

df["Creada_dt"] = df["Creada"].apply(parse_jira_date)
df["Actualizada_dt"] = df["Actualizada"].apply(parse_jira_date)

# --- Resolution time (in hours) ---
df["Resolution Time (hrs)"] = (
    df["Actualizada_dt"] - df["Creada_dt"]
).dt.total_seconds() / 3600

# --- SLA target: 24 hours ---
SLA_TARGET_HOURS = 24
df["SLA Met"] = df["Resolution Time (hrs)"] <= SLA_TARGET_HOURS

# --- Key metrics ---
avg_resolution = df["Resolution Time (hrs)"].mean()
sla_compliance_rate = df["SLA Met"].mean() * 100
most_common_type = df["Tipo de Incidencia"].value_counts().idxmax()
total_tickets = len(df)

print("=" * 50)
print("IT HELPDESK SIMULATION — TICKET ANALYSIS")
print("=" * 50)
print(f"Total tickets analyzed:     {total_tickets}")
print(f"Average resolution time:   {avg_resolution:.2f} hours")
print(f"SLA compliance rate:       {sla_compliance_rate:.0f}%")
print(f"Most common incident type: {most_common_type}")
print("=" * 50)

# --- Per-ticket detail table ---
summary = df[["Clave de incidencia", "Tipo de Incidencia", "Resolution Time (hrs)", "SLA Met"]]
summary = summary.rename(columns={
    "Clave de incidencia": "Ticket",
    "Tipo de Incidencia": "Type",
})
print("\nPer-ticket breakdown:")
print(summary.to_string(index=False))

# Save the summary to a CSV for reference
summary.to_csv("ticket_summary.csv", index=False)

# --- Chart 1: Resolution time per ticket ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].bar(summary["Ticket"], summary["Resolution Time (hrs)"], color="#2563eb")
axes[0].axhline(y=SLA_TARGET_HOURS, color="red", linestyle="--", label=f"SLA target ({SLA_TARGET_HOURS}h)")
axes[0].set_title("Resolution Time per Ticket")
axes[0].set_ylabel("Hours")
axes[0].legend()

# --- Chart 2: Incident type breakdown ---
type_counts = df["Tipo de Incidencia"].value_counts()
axes[1].pie(type_counts, labels=type_counts.index, autopct="%1.0f%%", colors=["#2563eb", "#f97316", "#16a34a"])
axes[1].set_title("Incident Type Breakdown")

plt.tight_layout()
plt.savefig("dashboard.png", dpi=150)
print("\nChart saved as dashboard.png")
