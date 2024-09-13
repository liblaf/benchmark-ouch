import hashlib
import platform
import random
import time
from pathlib import Path
from string import Template

import prettytable
from prettytable import PrettyTable
from pydantic import BaseModel

MARKDOWN: Template = Template("""\
# Hashlib

Python ${version}

${table}
""")


class Record(BaseModel):
    algo: str
    length: int
    time: float


def main() -> None:
    data: bytes = random.randbytes(2**27)
    records: list[Record] = []
    for algo in hashlib.algorithms_guaranteed:
        if algo in ("shake_128", "shake_256"):
            continue
        hasher: hashlib._Hash = hashlib.new(algo)
        start: float = time.perf_counter()
        hasher.update(data)
        digest: bytes = hasher.digest()
        end: float = time.perf_counter()
        records.append(Record(algo=algo, length=8 * len(digest), time=end - start))
    records.sort(key=lambda r: r.time)
    sha256: Record = next(r for r in records if r.algo == "sha256")
    table: PrettyTable = PrettyTable(
        ("Algorithm", "Length", "Time [ms]", "Relative"), align="r"
    )
    table.align["Algorithm"] = "l"
    table.set_style(prettytable.MARKDOWN)
    for r in records:
        time_ms: float = r.time * 1e3
        rel: float = r.time / sha256.time * 100
        table.add_row([r.algo, r.length, f"{time_ms:.1f}", f"{rel:.1f}%"])
    markdown: str = MARKDOWN.substitute(
        {"version": platform.python_version(), "table": table.get_string()}
    )
    Path("docs/cksum.md").write_text(markdown)


if __name__ == "__main__":
    main()
