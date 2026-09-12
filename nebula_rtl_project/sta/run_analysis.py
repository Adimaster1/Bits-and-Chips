import subprocess
import re
from dataclasses import dataclass, field
from typing import List

from dataclasses import dataclass, field
from typing import List
from collections import Counter


@dataclass
class TimingCell:
    instance: str
    pin: str
    cell_type: str
    delay: float
    cumulative_time: float
    transition: str


@dataclass
class TimingPath:
    startpoint: str
    endpoint: str
    slack: float
    path_delay: float
    cells: List[TimingCell] = field(default_factory=list)

    def get_cell_type_counts(self):
        """
        Count the different standard-cell types
        on the critical path.
        """

        return Counter(
            cell.cell_type
            for cell in self.cells
        )

    def print_summary(self):

        print("\n" + "=" * 60)
        print("TIMING PATH EXTRACTED FOR RAG PIPELINE")
        print("=" * 60)

        print(f"Startpoint: {self.startpoint}")
        print(f"Endpoint:   {self.endpoint}")
        print(f"Path Delay: {self.path_delay} ns")
        print(f"Slack:      {self.slack} ns")
        print(f"Gate Count: {len(self.cells)} cells")

        print("\nCell Type Summary:")

        cell_counts = self.get_cell_type_counts()

        for cell_type, count in cell_counts.most_common():
            print(f"  {cell_type}: {count}")

        print("\nCritical Path:")

        for cell in self.cells:
            print(
                f"  {cell.instance}/{cell.pin} "
                f"({cell.cell_type}) "
                f"Delay: {cell.delay} ns"
            )

        print("=" * 60 + "\n")


def parse_sta_report(report_text: str) -> TimingPath:

    # -----------------------------
    # Extract Startpoint
    # -----------------------------

    start_match = re.search(
        r"Startpoint:\s+(\S+)",
        report_text
    )

    startpoint = (
        start_match.group(1)
        if start_match
        else "Unknown"
    )

    # -----------------------------
    # Extract Endpoint
    # -----------------------------

    end_match = re.search(
        r"Endpoint:\s+(\S+)",
        report_text
    )

    endpoint = (
        end_match.group(1)
        if end_match
        else "Unknown"
    )

    # -----------------------------
    # Extract Slack
    # -----------------------------

    slack_match = re.search(
        r"([-+]?\d*\.?\d+)\s+slack",
        report_text
    )

    slack = (
        float(slack_match.group(1))
        if slack_match
        else 0.0
    )

    # -----------------------------
    # Extract Data Arrival Time
    # -----------------------------

    delay_match = re.search(
        r"([\d.]+)\s+data arrival time",
        report_text
    )

    path_delay = (
        float(delay_match.group(1))
        if delay_match
        else 0.0
    )

    # -----------------------------
    # Extract Critical Path Cells
    # -----------------------------

    cell_pattern = re.compile(
        r"""
        ^\s*
        ([\d.]+)
        \s+
        ([\d.]+)
        \s+
        ([\^v])
        \s+
        (\S+?)
        /
        ([A-Za-z0-9_]+)
        \s+
        \(
        ([A-Za-z0-9_]+)
        \)
        """,
        re.MULTILINE | re.VERBOSE
    )

    cells = []

    for match in cell_pattern.finditer(report_text):

        incremental_delay = float(match.group(1))
        cumulative_time = float(match.group(2))
        transition = match.group(3)
        instance = match.group(4)
        pin = match.group(5)
        cell_type = match.group(6)

        cells.append(
            TimingCell(
                instance=instance,
                pin=pin,
                cell_type=cell_type,
                delay=incremental_delay,
                cumulative_time=cumulative_time,
                transition=transition
            )
        )

    return TimingPath(
        startpoint=startpoint,
        endpoint=endpoint,
        slack=slack,
        path_delay=path_delay,
        cells=cells
    )


def run_pipeline() -> TimingPath:
    print("Step 1: Synthesizing netlist with Yosys...")
    yosys_res = subprocess.run(["yosys", "sta/run_synth.ys"], capture_output=True, text=True)
    
    if yosys_res.returncode != 0:
        print("Yosys Failed.")
        return None

    print("Step 2: Executing STA with OpenSTA...")
    sta_res = subprocess.run(["sta", "sta/run_sta.tcl"], capture_output=True, text=True)
    
    if sta_res.returncode != 0:
        print("OpenSTA Failed")
        return None

    print("Step 3: Parsing Timing Report...")
    timing_path_obj = parse_sta_report(sta_res.stdout)
    #timing_path_obj.print_summary()                                                         #Commented for simplifying output
    
    return timing_path_obj


if __name__ == "__main__":
    extracted_path_object = run_pipeline()
