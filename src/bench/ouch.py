# ruff: noqa: UP007
import subprocess as sp
import time
from pathlib import Path
from string import Template
from typing import Annotated, Optional

import prettytable
import typer
from prettytable import PrettyTable
from pydantic import BaseModel

EXTENSIONS: list[str] = [
    ".tar",
    ".zip",
    ".7z",
    ".tar.gz",
    ".tar.xz",
    ".tar.lzma",
    ".tar.bz",
    ".tar.bz2",
    ".tar.lz4",
    ".tar.sz",
    ".tar.zst",
    # ".rar",
]


MARKDOWN: Template = Template("""\
# Ouch

${version}

- C: Compression time
- D: Decompression time
- S: Size of the compressed file
- R: Relative

${table}
""")


def version() -> str:
    proc: sp.CompletedProcess[str] = sp.run(
        ["ouch", "--version"], stdout=sp.PIPE, check=True, text=True
    )
    return proc.stdout.strip()


class Record(BaseModel):
    compress_time: float
    decompress_time: float
    ext: str
    size: int


def run(ext: str) -> Record:
    start: float = time.perf_counter()
    fpath: Path = Path("data/ICT-FaceKit-master" + ext)
    sp.run(
        [
            "ouch",
            "compress",
            "--yes",
            "--quiet",
            "data/ICT-FaceKit-master/",
            fpath,
        ],
        stdout=sp.DEVNULL,
        check=True,
    )
    end: float = time.perf_counter()
    compress_time: float = end - start
    start: float = time.perf_counter()
    fpath: Path = Path("data/ICT-FaceKit-master" + ext)
    sp.run(
        ["ouch", "decompress", "--dir", "data/", "--yes", "--quiet", fpath],
        stdin=sp.DEVNULL,
        stdout=sp.DEVNULL,
        check=True,
    )
    end: float = time.perf_counter()
    decompress_time: float = end - start
    return Record(
        compress_time=compress_time,
        decompress_time=decompress_time,
        ext=ext,
        size=fpath.stat().st_size,
    )


def main(
    output: Annotated[
        Optional[Path], typer.Option(dir_okay=False, writable=True)
    ] = None,
) -> None:
    results: list[Record] = [run(ext) for ext in EXTENSIONS]
    results[:1] = sorted(results[:1], key=lambda r: r.decompress_time)
    table: PrettyTable = PrettyTable(
        ["Format", "C [s]", "R (C)", "D [s]", "R (D)", "S [MB]", "R (S)"],
        align="r",
    )
    table.align["Format"] = "l"
    table.set_style(prettytable.MARKDOWN)
    for r in results:
        table.add_row(
            [
                f"`{r.ext}`",
                f"{r.compress_time:.1f}",
                f"{r.compress_time / results[0].compress_time:.2f}",
                f"{r.decompress_time:.1f}",
                f"{r.decompress_time / results[0].decompress_time:.2f}",
                f"{r.size / 2**20:.1f}",
                f"{r.size / results[0].size:.2f}",
            ]
        )
    markdown: str = MARKDOWN.substitute(
        {"version": version(), "table": table.get_string()}
    )
    if output is not None:
        output.write_text(markdown)
    else:
        print(markdown)


if __name__ == "__main__":
    typer.run(main)
