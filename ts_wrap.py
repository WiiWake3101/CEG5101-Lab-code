#!/usr/bin/env python3
import subprocess, sys, datetime
if len(sys.argv) < 2:
    print("usage: ts_wrap.py <command> [args...]", file=sys.stderr); sys.exit(1)
proc = subprocess.Popen(sys.argv[1:], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
for line in proc.stdout:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    sys.stdout.write("%s %s" % (ts, line)); sys.stdout.flush()
proc.wait(); sys.exit(proc.returncode)
