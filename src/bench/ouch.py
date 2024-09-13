import shutil
import subprocess as sp
import time
from pathlib import Path
from string import Template

import prettytable
from icecream import ic
from prettytable import PrettyTable
from pydantic import BaseModel

DPATH: Path = Path("data/ICT-FaceKit-master")
OUCH_EXTENSIONS: list[str] = [
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
TAR_EXTENSIONS: list[str] = [
    ".tar",
    ".tar.gz",
    # ".tar.Z",
    ".tar.bz2",
    # ".tar.lz",
    ".tar.lzma",
    # ".tar.lzo",
    ".tar.xz",
    ".tar.zst",
]
MARKDOWN: Template = Template("""\
# Ouch

- C: Compression time
- D: Decompression time
- S: Size of the compressed file
- R: Relative

${table}
""")


class Record(BaseModel):
    compress_time: float
    decompress_time: float
    format: str
    program: str
    size: int


def bench_ouch(ext: str) -> Record:
    fpath: Path = DPATH.with_suffix(ext)
    fpath.unlink(missing_ok=True)
    start: float = time.perf_counter()
    sp.run(
        ["ouch", "compress", "--quiet", DPATH, fpath],
        stdin=sp.DEVNULL,
        stdout=sp.DEVNULL,
        check=True,
    )
    end: float = time.perf_counter()
    compress_time: float = end - start
    shutil.rmtree(DPATH, ignore_errors=True)
    start = time.perf_counter()
    sp.run(
        ["ouch", "decompress", "--dir", DPATH.parent, "--quiet", fpath],
        stdin=sp.DEVNULL,
        stdout=sp.DEVNULL,
        check=True,
    )
    end = time.perf_counter()
    decompress_time: float = end - start
    record: Record = Record(
        compress_time=compress_time,
        decompress_time=decompress_time,
        format=ext,
        program="ouch",
        size=fpath.stat().st_size,
    )
    ic(record)
    return record


def bench_tar(ext: str) -> Record:
    fpath: Path = DPATH.with_suffix(ext)
    fpath.unlink(missing_ok=True)
    start: float = time.perf_counter()
    sp.run(
        ["tar", "--create", "--file", fpath, "--auto-compress", DPATH],
        stdin=sp.DEVNULL,
        stdout=sp.DEVNULL,
        check=True,
    )
    end: float = time.perf_counter()
    compress_time: float = end - start
    shutil.rmtree(DPATH, ignore_errors=True)
    start = time.perf_counter()
    sp.run(
        ["tar", "--extract", "--file", fpath],
        stdin=sp.DEVNULL,
        stdout=sp.DEVNULL,
        check=True,
    )
    end = time.perf_counter()
    decompress_time: float = end - start
    record: Record = Record(
        compress_time=compress_time,
        decompress_time=decompress_time,
        format=ext,
        program="tar",
        size=fpath.stat().st_size,
    )
    ic(record)
    return record


def main() -> None:
    results: list[Record] = [bench_ouch(ext) for ext in OUCH_EXTENSIONS]
    results.extend(bench_tar(ext) for ext in TAR_EXTENSIONS)
    results[1:] = sorted(results[1:], key=lambda r: r.size)
    table: PrettyTable = PrettyTable(
        ["Program", "Format", "C [s]", "C [x]", "D [s]", "D [x]", "S [MB]", "S [%]"],
        align="r",
    )
    table.align.update({"Program": "l", "Format": "l"})
    table.set_style(prettytable.MARKDOWN)
    for r in results:
        compress_rel: float = r.compress_time / results[0].compress_time
        decompress_rel: float = r.decompress_time / results[0].decompress_time
        size_mb: float = r.size / 2**20
        size_rel: float = r.size / results[0].size * 100
        table.add_row(
            [
                f"`{r.program}`",
                f"`{r.format}`",
                f"{r.compress_time:.1f}",
                f"{compress_rel:.2f}x",
                f"{r.decompress_time:.1f}",
                f"{decompress_rel:.2f}x",
                f"{size_mb:.1f}",
                f"{size_rel:.2f}%",
            ]
        )
    markdown: str = MARKDOWN.substitute({"table": table.get_string()})
    Path("docs/ouch.md").write_text(markdown)


if __name__ == "__main__":
    main()
