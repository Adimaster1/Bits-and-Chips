import subprocess
import re
from dataclasses import dataclass, field
from typing import List

@dataclass
class TimingPath:
    startpoint: str
    endpoint: str
    slack: float
    path_delay: float
    cells: List[str] = field(default_factory=list)

    def print_summary(self):
        print("\n" + "="*60)
        print("TIMING PATH EXTRACTED FOR RAG PIPELINE")
        print("="*60)
        print(f"Startpoint: {self.startpoint}")
        print(f"Endpoint:   {self.endpoint}")
        print(f"Path Delay: {self.path_delay} ns")
        print(f"Slack:      {self.slack} ns")
        print(f"Gate Count: {len(self.cells)} cells")
        if self.cells:
            print(f"Cell Path:  {' -> '.join(self.cells)}")
        print("="*60 + "\n")


def parse_sta_report(report_text: str) -> TimingPath:
    # Extract Startpoint
    start_match = re.search(r"Startpoint:\s+(\S+)", report_text)
    startpoint = start_match.group(1) if start_match else "Unknown"

    # Extract Endpoint
    end_match = re.search(r"Endpoint:\s+(\S+)", report_text)
    endpoint = end_match.group(1) if end_match else "Unknown"

    # Extract Slack (Look for number BEFORE the word 'slack')
    slack_match = re.search(r"([-+]?\d*\.\d+|\d+)\s+slack", report_text)
    slack = float(slack_match.group(1)) if slack_match else 0.0

    # Extract Path Delay (Data Arrival Time)
    delay_match = re.search(r"([\d\.]+)\s+data arrival time", report_text)
    path_delay = float(delay_match.group(1)) if delay_match else 0.0

    # Extract Cell Names (_XXXX_/Y)
    raw_cells = re.findall(r"(\_\d+\_)/[a-zA-Z]+", report_text)
    
    unique_cells = []
    seen = set()
    for cell in raw_cells:
        if cell not in seen:
            seen.add(cell)
            unique_cells.append(cell)

    return TimingPath(
        startpoint=startpoint,
        endpoint=endpoint,
        slack=slack,
        path_delay=path_delay,
        cells=unique_cells
    )


def run_pipeline() -> TimingPath:
    print("Step 1: Synthesizing netlist with Yosys...")
    yosys_res = subprocess.run(["yosys", "run_synth.ys"], capture_output=True, text=True)
    
    if yosys_res.returncode != 0:
        print("Yosys Failed\n", yosys_res.stderr)
        return None

    print("Step 2: Executing STA with OpenSTA...")
    sta_res = subprocess.run(["sta", "run_sta.tcl"], capture_output=True, text=True)
    
    if sta_res.returncode != 0:
        print("OpenSTA Failed\n", sta_res.stderr)
        return None

    print("Step 3: Parsing Timing Report...")
    timing_path_obj = parse_sta_report(sta_res.stdout)
    timing_path_obj.print_summary()
    
    return timing_path_obj


if __name__ == "__main__":
    extracted_path_object = run_pipeline()
