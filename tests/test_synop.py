import pytest
from synop.synop import synop

treport = "201809051400 AAXX 05141 10224 42680 50704 10230 20139 30174 40180 58010 81101 333 55309 22094 30345 81845 85080 91007 90710"

def test_class():
    report = synop(treport)
    print(report.toDF())
    print(report)
