"""
Parse L2CAP packets
"""
import struct

def parse(data):
    """
    Parse L2CAP packet

     0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 
	-----------------------------------------------------------------
	|            length             |          channel id           |
	-----------------------------------------------------------------

    L2CAP is packet-based but follows a communication model based on channels.
    A channel represents a data flow between L2CAP entities in remote devices.
    Channels may be connection-oriented or connectionless. Fixed channels
    other than the L2CAP connectionless channel (CID 0x0002) and the two L2CAP
    signaling channels (CIDs 0x0001 and 0x0005) are considered connection-oriented.

    All L2CAP layer packet fields shall use Little Endian byte order with the exception of the 
    information payload field. The endian-ness of higher layer protocols encapsulated within 
    L2CAP information payload is protocol-specific

    References can be found here:
    * https://www.bluetooth.org/en-us/specification/adopted-specifications - Core specification 4.1
    ** [vol 3] Part A (Section 3) - Data Packet Format

    Returns a tuple of (opcode, length, data)
    """
    length, cid = struct.unpack("<HH", data[:4])
    data = data[4:]
    return length, cid, data