"""
  Parse btsnoop_hci.log binary data (similar to wireshark)
  usage:
     ./parse.py <filename>
"""
import datetime
import sys
import struct

def print_hdr():
    """
    Print the script header
    """
    print ""
    print "##############################"
    print "#                            #"
    print "#    btsnoop parser v0.1     #"
    print "#                            #"
    print "##############################"
    print ""

def main(filename):
    """ 
    Btsnoop packet capture file is structured as:
    
    -----------------------
    | header              |
    -----------------------
    | packet record nbr 1 |
    -----------------------
    | packet record nbr 2 |
    -----------------------
    | ...                 |
    -----------------------
    | packet record nbr n |
    -----------------------
    
    References can be found here:
    * http://tools.ietf.org/html/rfc1761
    * http://www.fte.com/webhelp/NFC/Content/Technical_Information/BT_Snoop_File_Format.htm
    """
    with open(filename, "rb") as f:
    
        # Validate file header
        (identification, version, type) = read_file_header(f)
        validate_file_header(identification, version, type)
        
        # Read packet records
        records = [ record for record in read_packet_records(f) ]
        for seq, flags, time in map(lambda record: (record[0], parse_flags(record[3]), record[5]), records):
            print parse_time(time)
            #print "{0}\t{1:10} -> {2:10}\t{3}".format(seq, flags["src"], flags["dst"], flags["type"])

def read_file_header(f):
    """
    Header should conform to the following format
    
    ----------------------------------------
    | identification pattern|
    | 8 bytes                              |
    ----------------------------------------
    | version number                   |
    | 4 bytes                              |
    ----------------------------------------
    | data link type = HCI UART (H4)       |
    | 4 bytes                              |
    ----------------------------------------
    """
    ident = f.read(8)
    version, data_link_type = struct.unpack( ">II", f.read(4 + 4) )
    return (ident, version, data_link_type)
    
def validate_file_header(identification, version, data_link_type):
    """
    The identification pattern should be:
        'btsnoop\0' 
    
    The version number should be:
        1
    
    The data link type can be:
        - Reserved	0 - 1000
        - Un-encapsulated HCI (H1)	1001
        - HCI UART (H4)	1002
        - HCI BSCP	1003
        - HCI Serial (H5)	1004
        - Unassigned	1005 - 4294967295
        
    For SWAP, data link type should be:
        HCI UART (H4)	1002
    """
    assert identification == "btsnoop\0"
    assert version == 1
    assert data_link_type == 1002
    print "Btsnoop capture file version {0}, type {1}".format(version, data_link_type)
    
def read_packet_records(f):
    """
    A record should confirm to the following format
    
    --------------------------
    | original length        |
    | 4 bytes   
    --------------------------
    | included length        |
    | 4 bytes   
    --------------------------
    | packet flags           |
    | 4 bytes   
    --------------------------
    | cumulative drops       |
    | 4 bytes   
    --------------------------
    | timestamp microseconds |
    | 8 bytes
    --------------------------
    | packet data            |
    --------------------------
    
    """
    seq_nbr = 1
    while True:
        pkt_hdr = f.read(4 + 4 + 4 + 4 + 8)
        if not pkt_hdr or len(pkt_hdr) != 24:
            # EOF
            break
    
        orig_len, inc_len, flags, drops, time64 = struct.unpack( ">IIIIq", pkt_hdr)
        assert orig_len == inc_len
        
        data = f.read(inc_len)
        assert len(data) == inc_len
    
        yield ( seq_nbr, orig_len, inc_len, flags, drops, time64, data )
        seq_nbr += 1

        
def parse_flags(flags):
    """
    Record flags conform to:
        - bit 0         0 = sent, 1 = received
        - bit 1         0 = data, 1 = command/event
        - bit 2-31      reserved
        
    Direction is relative to host / DTE. i.e. for Bluetooth controllers, 
    Send is Host->Controller, Receive is Controller->Host
    """
    assert flags in [0,1,2,3]
    if flags == 0:
        return { "src": "host",  "dst": "controller", "type": "data" }
    elif flags == 1:
        return { "src": "controller", "dst": "host", "type": "data" }
    elif flags == 2:
        return { "src": "host", "dst": "controller", "type": "command" }
    else:
        return { "src": "controller", "dst": "host", "type": "event" }
    
def parse_time(t):
    """
    Record time is a 64-bit signed integer representing the time of packet arrival, 
    in microseconds since midnight, January 1st, 0 AD nominal Gregorian.

    In order to avoid leap-day ambiguity in calculations, note that an equivalent 
    epoch may be used of midnight, January 1st 2000 AD, which is represented in 
    this field as 0x00E03AB44A676000.
    """
    t_since_2000_epoch = datetime.timedelta(microseconds=t) - datetime.timedelta(microseconds=int("0x00E03AB44A676000", 16))
    return datetime.datetime(2000, 1, 1) + t_since_2000_epoch
        
def parseBTSnoop( f ):
    i = 0
    startTime = None
    while True:
        header = f.read(4*6)
        if len(header) < 24:
            break
        origLen, incLen, flags, drops, time64 = struct.unpack( 
                ">IIIIq", header )
        assert origLen == incLen, (origLen, incLen)
        assert drops == 0, drops
        assert flags in [0,1,2,3], (i,flags)
        # bit 0 ... 0 = sent, 1 = received
        # bit 1 ... 0 = data, 1 = command/event
        if startTime is None:
            startTime = time64
        data = f.read(origLen)
        assert len(data) == origLen, (len(data), origLen)
        if flags == 0:
            tmp = [ord(x) for x in data]
            t = ((time64-startTime)/1000)/1000.
            print "%.03f" % t, hexStr( tmp )
            assert tmp[:3] == [0x2, 0x40, 0x00,]
            # well tmp[3] it is the lengh of data (maybe 16bit?)
            assert len(tmp)-5 == tmp[3], (len(tmp), tmp[3])
            assert tmp[4] == 0, tmp[4]
            assert len(tmp)-9 == tmp[5], (len(tmp), tmp[5])
            assert tmp[6] == 0, tmp[6]
            #print flags, ((time64-startTime)/1000)/1000.
            #print [hex(x) for x in tmp[5:]]
            if tmp[5] == 0x12:
                # looks like it is similar to AR Drone2 AT*PCMD
                assert tmp[5:5+8] == [0x12, 0x0, 0x4, 0x0, 0x52, 0x40, 0x0, 0x2], tmp[5:5+8]
                # BHH unknown, B=on/off, forward/backward, tilt left/right, turn right/left, up/down, f multiply?
                # all signed byte values are in interval -100..100
                print struct.unpack("=BHHBbbbbf", data[5+8:]) 
        elif flags == 1:
            print "In:", [hex(ord(x)) for x in data]
        else:
            print "%d:"%flags, hexStr( [ord(x) for x in data] )
        i += 1
    print "Records", i

def hexStr( arr ):
    "hexdump of byte array"
    return " ".join( ["%02X" % x for x in arr] )
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
        
    print_hdr()
    sys.exit(main(sys.argv[1]))

# vim: expandtab sw=4 ts=4

