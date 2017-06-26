#!/usr/bin/env python3
"""
Bisect failing CPython tests.

Find failing test of "test_os", write the list of failing tests into the
"bisect" file:

    ./python bisect_test.py -o bisect test_os

Find a reference leak in "test_os", write the list of failing tests into the
"bisect" file:

    ./python bisect_test.py -o bisect -R 3:3 test_os

Load an existing list of tests from a file using -i option:

    ./python -m test --list-cases -m FileTests test_os > tests
    ./python bisect_test.py -i tests test_os
"""
import argparse
import datetime
import os.path
import math
import random
import re
import subprocess
import sys
import tempfile
import time


def write_tests(filename, tests):
    with open(filename, "w") as fp:
        for name in tests:
            print(name, file=fp)
        fp.flush()


def write_output(filename, tests):
    if not filename:
        return
    print("Write %s tests into %s" % (len(tests), filename))
    write_tests(filename, tests)


def format_shell_args(args):
    return ' '.join(args)


def list_cases(args):
    cmd = [sys.executable, '-m', 'test', '--list-cases']
    cmd.extend(args.test_args)
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          universal_newlines=True)
    exitcode = proc.returncode
    if exitcode:
        cmd = format_shell_args(cmd)
        print("Failed to list tests: %s failed with exit code %s"
              % (cmd, exitcode))
        sys.exit(exitcode)
    tests = proc.stdout.splitlines()
    return tests


def run_tests(args, tests, huntrleaks=None):
    tmp = tempfile.mktemp()
    try:
        write_tests(tmp, tests)

        cmd = [sys.executable, '-m', 'test', '--matchfile', tmp]
        cmd.extend(args.test_args)
        print("+ %s" % format_shell_args(cmd))
        proc = subprocess.run(cmd)
        return proc.returncode
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Test names produced by --list-tests written '
                             'into a file. If not set, run --list-tests')
    parser.add_argument('-o', '--output',
                        help='Result of the bisection')
    parser.add_argument('-n', '--max-tests', type=int, default=1,
                        help='Maximum number of tests to stop the bisection '
                             '(default: 1)')
    #parser.add_argument('test_args', action='append',
    #                    help='Parameters of python -m test, ex: -R 3:3 test_os')

    args, test_args = parser.parse_known_args()
    args.test_args = test_args
    return args


def main():
    args = parse_args()

    if args.input:
        with open(args.input) as fp:
            tests = [line.strip() for line in fp]
    else:
        tests = list_cases(args)

    write_output(args.output, tests)

    print("Start bisecting with %s tests" % len(tests))
    print("Test arguments: %s" % format_shell_args(args.test_args))
    print("Bisection will stop when getting %s or less tests (-n option)"
          % args.max_tests)
    print()

    start_time = time.monotonic()
    iteration = 1
    while len(tests) > args.max_tests:
        print("[+] Iteration %s: %s tests" % (iteration, len(tests)))
        print()

        ntest = len(tests)
        ntest = max(ntest // 2, 1)
        subtests = random.sample(tests, ntest)
        try:
            exitcode = run_tests(args, subtests)
        except KeyboardInterrupt:
            print()
            print("Interrupted, exit")
            return

        print("ran %s tests/%s" % (ntest, len(tests)))
        print("exit", exitcode)
        if exitcode:
            print("Tests failed: use this new subtest")
            tests = subtests
            write_output(args.output, tests)
        else:
            print("Tests succeeded: skip this subtest, try a new subbset")
        print()
        iteration += 1

    print("Failing tests (%s):" % len(tests))
    for test in tests:
        print("* %s" % test)
    print()

    dt = math.ceil(time.monotonic() - start_time)
    print("Bisection completed in %s iterations and %s"
          % (iteration, datetime.timedelta(seconds=dt)))


if __name__ == "__main__":
    main()
