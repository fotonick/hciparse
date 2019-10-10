import sys
sys.path.append("..")

import hciparse.logparse.logparse as bts

def test_load_example():
    records = bts.parse('test00.pklg')
    assert(len(records) == 2052)

if __name__ == "__main__":
    test_load_example()
    print("Ok")