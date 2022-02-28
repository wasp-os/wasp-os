# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2022 thiswillbeyourgithub user of github.com

#put the code you want to compare in the for loop
#then use './wasptool --exec code_benchmark.py'
#to see which is faster on the watch

wasp.gc.collect()
t = wasp.machine.Timer(id=1, period=8000000)
n_iterations = 20
from array import array
vals1 = array("f")
vals2 = array("f")

for i in range(n_iterations):
    t.start()
    # put code #1 here
    vals1.append(t.time())
    t.stop()

    t.start()
    # put code #2 here
    vals2.append(t.time())
    t.stop()

print("Benchmark results:")
print("Function 1: {:3f}".format(sum(vals1)/n_iterations))
print("Function 2: {:3f}".format(sum(vals2)/n_iterations))
del t, n_iterations, vals1, vals2, i
wasp.gc.collect()
