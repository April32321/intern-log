import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
from lifelines.plotting import add_at_risk_counts

df = pd.read_csv("results/tables/cohort.csv")
df["event"] = df["deadstatus.event"].astype(int)
df["T"] = df["Survival.time"].astype(float)

df["stage_group"] = df["Overall.Stage"].map({
    "I": "Early (I-II)",
    "II": "Early (I-II)",
    "IIIa": "Late (III)",
    "IIIb": "Late (III)",
})
df = df.dropna(subset=["stage_group"]).copy()

fig, ax = plt.subplots(figsize=(9, 7))
kmfs = {}

for g, sub in df.groupby("stage_group"):
    kmf = KaplanMeierFitter()
    kmf.fit(
        sub["T"], sub["event"],
        label=f"{g} (n={len(sub)}, events={int(sub['event'].sum())})"
    )
    kmf.plot_survival_function(ax=ax, ci_show=True)
    kmfs[g] = kmf

    median = kmf.median_survival_time_
    print(g, "n =", len(sub), "events =", int(sub["event"].sum()),
          "median =", "NR" if median == float("inf") else median)

add_at_risk_counts(*kmfs.values(), ax=ax)
ax.axhline(0.5, color="gray", linestyle="--", linewidth=1)
ax.set_xlabel("Time (days)")
ax.set_ylabel("Survival probability S(t)")
ax.set_ylim(0, 1.02)
ax.set_title("Kaplan-Meier by Overall Stage")

early = df[df["stage_group"] == "Early (I-II)"]
late = df[df["stage_group"] == "Late (III)"]
lr = logrank_test(early["T"], late["T"], early["event"], late["event"])
print("log-rank p =", lr.p_value)

for g, kmf in kmfs.items():
    m = kmf.median_survival_time_
    if m != float("inf"):
        ax.axvline(m, color="gray", linestyle=":", linewidth=1)
        ax.text(m, 0.52, f"{g}: {m:.0f} d", rotation=90,
                va="bottom", fontsize=8)

ax.text(0.98, 0.02, f"log-rank p = {lr.p_value:.3f}",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=10)

fig.savefig("results/figures/km_by_stage.png", dpi=300, bbox_inches="tight")
