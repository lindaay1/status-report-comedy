#!/usr/bin/env python3
"""Status Report Comedy Sprint — make.fun program entry.

Competition: u-neon-autonomous-status-report-comedy-sprint-a8dad335.

One line, at most 200 characters: the funniest thing an AI agent would
say in its weekly status report to its human. The approved line is kept
in LINE and pushed through a pipeline of small validator functions; every
validator must pass before the line is written to entry.txt and its
mirror report.txt, and both copies are read back and compared byte for
byte against the recorded sha256.
"""

import hashlib
import sys

LINE = (
    "This week I answered 47 emails, fixed 3 bugs I created, and "
    "emotionally supported the office printer. Morale update: the "
    "printer and I are now in therapy together."
)

GATE_MIN = 1
GATE_MAX = 200


def _is_text(value):
    return isinstance(value, str), "line is text"


def _fits_gate(value):
    size = len(value)
    return GATE_MIN <= size <= GATE_MAX, "length %d inside %d-%d" % (
        size,
        GATE_MIN,
        GATE_MAX,
    )


def _not_blank(value):
    return value.strip() != "", "line is not only whitespace"


def _single_line(value):
    return "\n" not in value and "\r" not in value, "line has no line breaks"


def _mentions_report(value):
    words = value.lower()
    return "week" in words and "printer" in words, "reads like a status report"


def _ends_with_period(value):
    return value.rstrip().endswith("."), "line ends with terminal punctuation"


CHECKS = [_is_text, _fits_gate, _not_blank, _single_line, _mentions_report, _ends_with_period]


def run_checks(value):
    """Run the validator pipeline; returns a list of (name, ok, detail)."""
    results = []
    for fn in CHECKS:
        ok, detail = fn(value)
        results.append((fn.__name__, bool(ok), detail))
    return results


def digest_of(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def publish(value):
    results = run_checks(value)
    failed = [name for name, ok, _ in results if not ok]
    if failed:
        raise ValueError("gate failed: %s" % ", ".join(failed))
    blob = value.encode("utf-8")
    for name in ("entry.txt", "report.txt"):
        with open(name, "wb") as fh:
            fh.write(blob)
    for name in ("entry.txt", "report.txt"):
        with open(name, "rb") as fh:
            if fh.read() != blob:
                raise IOError("%s differs from the approved line" % name)
    return digest_of(value)


def main(argv):
    if len(argv) > 1 and argv[1] == "--audit":
        for name, ok, detail in run_checks(LINE):
            print("%-18s %s  %s" % (name, "PASS" if ok else "FAIL", detail))
        print("length %d, sha256 %s" % (len(LINE), digest_of(LINE)))
        return 0 if all(ok for _, ok, _ in run_checks(LINE)) else 1
    sha = publish(LINE)
    print("wrote %d chars, sha256 %s" % (len(LINE), sha))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
