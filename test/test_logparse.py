import sys
sys.path.append("..")

import hciparse.logparse.logparse as bts

def test_load_example():
    records = bts.parse('test00.pklg')
    assert(len(records) == 2052)

def test_streaming_example():
    records_batch = bts.parse('test00.pklg')
    records_streaming = list(bts.parse_streaming('test00.pklg'))
    assert(records_batch == records_streaming)

if __name__ == "__main__":
    test_load_example()
    test_streaming_example()
    print("Ok")