"""
  Parse btsnoop or Apple PacketLogger (.pklg) binary data (similar to wireshark)
  usage:
     ./parse.py <filename>
"""
import datetime
import sys
from time import sleep
import struct


"""
Record flags conform to:
    - bit 0         0 = sent, 1 = received
    - bit 1         0 = data, 1 = command/event
    - bit 2-31      reserved

Direction is relative to host / DTE. i.e. for Bluetooth controllers,
Send is Host->Controller, Receive is Controller->Host
"""
BTSNOOP_FLAGS = {
        0 : ("host", "controller", "data"),
        1 : ("controller", "host", "data"),
        2 : ("host", "controller", "command"),
        3 : ("controller", "host", "event")
    }


def parse(filename):
    """
    Parse a pklg packet capture file.

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

    Return a list of records, each holding a tuple of:
    * sequence nbr
    * record length (in bytes)
    * flags
    * timestamp
    * data
    """
    with open(filename, "rb") as f:

        # Read file header
        (identification, version, type) = _read_file_header(f)
        pklg_version2 = (identification[1] == b'\x01')

        # Validate and rewind because PacketLogger files have no file header
        _validate_is_packetlogger_file(identification)
        f.seek(0)
        # NEXT
        return list(_read_packetlogger_records(f, pklg_version2, live_capture=False))

def parse_streaming(filename):
    """
    Parse a pklg packet capture file that's still being captured.

    Return a generator of records, each holding a tuple of:
    * sequence nbr
    * record length (in bytes)
    * flags
    * timestamp
    * data
    """
    with open(filename, "rb") as f:

        # Read file header
        (identification, version, type) = _read_file_header(f)
        pklg_version2 = (identification[1] == b'\x01')

        # Validate and rewind because PacketLogger files have no file header
        _validate_is_packetlogger_file(identification)
        f.seek(0)
        # NEXT
        yield from _read_packetlogger_records(f, pklg_version2, live_capture=True)


def _read_file_header(f):
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

    All integer values are stored in "big-endian" order, with the high-order bits first.
    """
    ident = f.read(8)
    version, data_link_type = struct.unpack( ">II", f.read(4 + 4) )
    return (ident, version, data_link_type)


def _validate_btsnoop_header(identification, version, data_link_type):
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
    assert identification == b"btsnoop\0"
    assert version == 1
    assert data_link_type == 1002
    print("Btsnoop capture file version {0}, type {1}".format(version, data_link_type))

def _validate_is_packetlogger_file(identification):
    """
    Check for Apple PacketLoger format
    """
    assert (identification[0] != b"\x00" or (identification[1] != b"\x00" and identification[1] != b"\x01"))

def _read_btsnoop_records(f):
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

    All integer values are stored in "big-endian" order, with the high-order bits first.
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

def read_retry(f, length, retries):
    data = []
    retries = 12000000
    where = f.tell()
    while True:
        data = f.read(length)
        if (len(data) == length) or (retries <= 0):
            break
        sleep(0.01)
        f.seek(where)
        retries -= 1
    return data, retries

def _read_packetlogger_records(f, pklg_version2, live_capture=False):
    if live_capture:
        retries = 1000
    else:
        retries = 0
    seq_nbr = 1
    while True:
        # PacketLogger packet should be 4 byte len, 8 byte timestamp, 1 byte type
        pkt, retries_remaining = read_retry(f, 4 + 8 + 1, 120)
        if retries_remaining <= 0:
            print("exceeded pkt retries")
            break

        # PKLGv2 files are little endian
        if pklg_version2:
            length, timestamp, pkt_type = struct.unpack("<IqB", pkt)
        else:
            length, timestamp, pkt_type = struct.unpack(">IqB", pkt)

        data, retries_remaining = read_retry(f, length - (13 - 4), 120)
        if retries_remaining <= 0:
            print("exceeded data retries")
            break

        # This is not very clear, but the PacketLogger flags are different so we
        # translate them to the btsnoop flags. Also there are some special types
        # we don't care about so we drop those packets. To complicate things
        # further, it seems that PacketLogger doesn't specify the UART type but
        # this library depends on it, so we forge that
        # CMD
        if pkt_type == 0x00:
            pkt_type = 0x02
            uart_type = 0x01
        # EVT
        elif pkt_type == 0x01:
            pkt_type = 0x03
            uart_type = 0x04
        # ACL TX
        elif pkt_type == 0x02:
            pkt_type = 0x00
            uart_type = 0x02
        #ACL RX
        elif pkt_type == 0x03:
            pkt_type = 0x01
            uart_type = 0x02
        else:
            continue

        data = struct.pack('B',uart_type) + data

        secs = timestamp >> 32
        usecs = timestamp & 0xffffffff
        timestamp = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=secs, microseconds=usecs)
        yield (seq_nbr, length, pkt_type, timestamp, data)
        seq_nbr += 1

def _parse_time(time):
    """
    Record time is a 64-bit signed integer representing the time of packet arrival,
    in microseconds since midnight, January 1st, 0 AD nominal Gregorian.

    In order to avoid leap-day ambiguity in calculations, note that an equivalent
    epoch may be used of midnight, January 1st 2000 AD, which is represented in
    this field as 0x00E03AB44A676000.
    """
    time_betw_0_and_2000_ad = int("0x00E03AB44A676000", 16)
    time_since_2000_epoch = datetime.timedelta(microseconds=time) - datetime.timedelta(microseconds=time_betw_0_and_2000_ad)
    return datetime.datetime(2000, 1, 1) + time_since_2000_epoch


def flags_to_str(flags):
    """
    Returns a tuple of (src, dst, type)
    """
    assert flags in [0,1,2,3]
    return BTSNOOP_FLAGS[flags]


def print_hdr():
    """
    Print the script header
    """
    print("")
    print("##############################")
    print("#                            #")
    print("#    btsnoop parser v0.1     #")
    print("#                            #")
    print("##############################")
    print("")


def main(filename):
    records = parse(filename)
    print(records)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    print_hdr()
    sys.exit(main(sys.argv[1]))
