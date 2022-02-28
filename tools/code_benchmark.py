# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2022 thiswillbeyourgithub user of github.com

"""
put the code you want to compare in the content of f1 and f2
then use './wasptool --exec code_benchmark.py'
to see which is faster on the watch
"""

import wasp
wasp.gc.collect()
t = wasp.machine.Timer(id=1, period=8000000)

# example : comparing pow(5, 5) with 5**5
from math import pow

def f1():
    return 5**5
def f2():
    return pow(5, 5)

vals1 = []
vals2 = []
a = 0
for i in range(100):
    t.start()
    a = f1()
    vals1.append(t.time())
    t.stop()
    t.start()
    a = f2()
    vals2.append(t.time())
    t.stop()

print("Benchmark results:")
print("Function 1: {:5f}".format(sum(vals1)/len(vals1)))
print("Function 2: {:5f}".format(sum(vals2)/len(vals2)))
wasp.gc.collect()
