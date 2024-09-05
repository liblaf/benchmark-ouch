# ruff: noqa: UP007
import hashlib
import platform
import random
import time
from pathlib import Path
from string import Template
from typing import Annotated, Optional

import prettytable
import typer
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


def main(
    output: Annotated[
        Optional[Path], typer.Option(dir_okay=False, writable=True)
    ] = None,
) -> None:
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
    table: PrettyTable = PrettyTable(["Algorithm", "Length", "Time [ms]"], align="r")
    table.align["Algorithm"] = "l"
    table.set_style(prettytable.MARKDOWN)
    for r in records:
        table.add_row([r.algo, r.length, f"{r.time * 1e3:.1f}"])
    markdown: str = MARKDOWN.substitute(
        {"version": platform.python_version(), "table": table.get_string()}
    )
    if output:
        output.write_text(markdown)
    else:
        print(markdown)


if __name__ == "__main__":
    typer.run(main)
