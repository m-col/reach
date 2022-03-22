#!/usr/bin/env python3
"""
Example script plotting metrics to illustrate how well a cohort of mice are training
across sessions.

Usage:
    training_summary.py /path/to/data_dir mouse1 mouse2 ...

"""

import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import typer
from matplotlib.ticker import MultipleLocator

from reach import Cohort
from reach.session import Outcomes, Targets


def main(
    data_dir: Path = typer.Argument(..., help="Folder containing task data."),
    mouse_ids: list[str] = typer.Argument(..., help="The IDs of mice to summarise."),
    no_collapse_days: bool = typer.Option(
        False, "-n", help="Don't merge sessions with the same date"
    ),
) -> None:
    """
    Plot training summaries for a cohort of mice using matplotlib.
    """
    cohort = Cohort.init_from_files(
        data_dir=data_dir,
        mouse_ids=mouse_ids,
    )

    sns.set_style("darkgrid")
    results = pd.DataFrame(cohort.get_results(not no_collapse_days))
    trials = pd.DataFrame(cohort.get_trials(not no_collapse_days))

    _, axes = plt.subplots(6, 1, sharex=True)

    # NaN-ify results for any sessions that didn't have any trials
    results.loc[
        results["trials"] == 0,
        ["correct_r", "correct_l", "incorrect_l", "incorrect_r", "d_prime", "trials"],
    ] = np.nan

    # Number of trials
    sns.lineplot(
        data=results,
        x="day",
        y="trials",
        hue="mouse_id",
        legend="brief",
        ax=axes[0],
        markers=True,
    )
    axes[0].set_ylabel("No.\ntrials", rotation="horizontal", ha="right")
    axes[0].set_ylim(bottom=0)

    # Number of correct trials
    sns.lineplot(
        data=results,
        x="day",
        y="correct_l",
        hue="mouse_id",
        legend=False,
        ax=axes[1],
        markers=True,
    )
    sns.lineplot(
        data=results,
        x="day",
        y="correct_r",
        hue="mouse_id",
        legend=False,
        ax=axes[1],
        markers=True,
    )
    axes[1].set_ylabel("No.\ncorrect", rotation="horizontal", ha="right")

    # Hit rate
    results["Hit rate"] = (results["correct_l"] + results["correct_r"]) / results[
        "trials"
    ]
    sns.lineplot(
        data=results,
        x="day",
        y="Hit rate",
        hue="mouse_id",
        legend=False,
        ax=axes[2],
        markers=True,
    )
    axes[2].set_ylabel("Hit rate", rotation="horizontal", ha="right")

    # Number of incorrect trials
    sns.lineplot(
        data=results,
        x="day",
        y="incorrect_l",
        hue="mouse_id",
        legend=False,
        ax=axes[3],
        markers=True,
    )
    sns.lineplot(
        data=results,
        x="day",
        y="incorrect_r",
        hue="mouse_id",
        legend=False,
        ax=axes[3],
        markers=True,
    )
    axes[3].set_ylabel("No.\nincorrect", rotation="horizontal", ha="right")

    # d'
    if not no_collapse_days and results["d_prime"].isna().any():
        # We have to re-calcuate d' for days that had multiple (merged) sessions using
        # the trial data.
        def z(p):
            return -NormalDist().inv_cdf(p)

        for _, data in results.loc[results["d_prime"].isna()].iterrows():
            day_trials = trials.loc[
                (trials.day == data.day) & (trials.mouse_id == data.mouse_id)
            ]
            # Trials preceded by an incorrect trial are considered to be correction trials,
            # and are therefore ignored. Remove missed trials to help identify these.
            day_trials = day_trials.loc[
                (day_trials.outcome == Outcomes.CORRECT)
                | (day_trials.outcome == Outcomes.INCORRECT)
            ]

            lefts = []
            rights = []
            prev = None
            for _, trial in day_trials.iterrows():
                outcome = trial.outcome
                if prev != Outcomes.INCORRECT:
                    if trial.spout == Targets.LEFT:
                        lefts.append(outcome)
                    else:
                        rights.append(outcome)
                prev = outcome

            H = (lefts.count(Outcomes.CORRECT) + 0.5) / (len(lefts) + 1)
            FA = (rights.count(Outcomes.INCORRECT) + 0.5) / (len(rights) + 1)
            d_prime = z(FA) - z(H)
            results.loc[
                (results.mouse_id == data.mouse_id) & (results.day == data.day),
                "d_prime",
            ] = d_prime

        assert not results["d_prime"].isna().any()

    axes[4].axhline(0, color="#aaaaaa", alpha=0.5, ls="--")
    # 1.5 here is an arbitrary threshold of ability to discriminate
    axes[4].axhline(1.5, color="#aaaaaa", alpha=0.5, ls=":")
    sns.lineplot(
        data=results,
        x="day",
        y="d_prime",
        hue="mouse_id",
        legend=False,
        ax=axes[4],
        markers=True,
    )
    axes[4].set_ylabel("d'", rotation="horizontal", ha="right")

    # Spout position
    axes[5].axhline(7, color="#aaaaaa", alpha=0.5, ls="--")
    sns.lineplot(
        data=trials,
        x="day",
        y="spout_position_0",
        hue="mouse_id",
        legend=False,
        ax=axes[5],
        markers=True,
    )
    sns.lineplot(
        data=trials,
        x="day",
        y="spout_position_1",
        hue="mouse_id",
        legend=False,
        ax=axes[5],
        markers=True,
        linestyle="dashed",
    )
    axes[5].set_ylim(bottom=0, top=8)
    axes[5].set_ylabel("Spout\nposition\n(mm)", rotation="horizontal", ha="right")

    axes[5].xaxis.set_major_locator(MultipleLocator(2))

    plt.suptitle("Training summary for: " + ", ".join(mouse_ids))
    plt.show()


if __name__ == "__main__":
    typer.run(main)
