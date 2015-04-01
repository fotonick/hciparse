"""
Parse L2CAP packets
"""
import struct
import hci_acl


"""
Fixed channel ids for L2CAP packets

References can be found here:
    * https://www.bluetooth.org/en-us/specification/adopted-specifications - Core specification 4.1
    ** [vol 3] Part A (Section 2.1) - Channel identifiers
"""
L2CAP_CID_NUL = 0x0000
L2CAP_CID_SCH = 0x0001
L2CAP_CID_ATT = 0x0004
L2CAP_CID_LE_SCH = 0x0005
L2CAP_CID_SMP = 0x0006


L2CAP_CHANNEL_IDS = {
	L2CAP_CID_NUL : "L2CAP_CID_NUL",
	L2CAP_CID_SCH : "L2CAP_CID_SCH",
	L2CAP_CID_ATT : "L2CAP_CID_ATT",
	L2CAP_CID_LE_SCH : "L2CAP_CID_LE_SCH",
	L2CAP_CID_SMP : "L2CAP_CID_SMP"
}


def parse_hdr(data):
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

    Returns a tuple of (length, cid, data)
    """
    length, cid = struct.unpack("<HH", data[:4])
    data = data[4:]
    return length, cid, data


PKT_TYPE_PARSERS = { hci_acl.START_NON_AUTO_L2CAP_PDU : parse_hdr,
                     hci_acl.CONT_FRAG_MSG : parse_hdr,
                     hci_acl.START_AUTO_L2CAP_PDU : parse_hdr,
                     hci_acl.COMPLETE_L2CAP_PDU : parse_hdr }


def parse(l2cap_pkt_type, data):
    """
    Convenience method for switching between parsing methods based on type
    """
    parser = PKT_TYPE_PARSERS[l2cap_pkt_type]
    if parser is None:
        raise ValueError("Illegal L2CAP packet type")
    return parser(data)


def cid_to_str(cid):
	"""
	Return a string representing the L2CAP channel id
	"""
	return L2CAP_CHANNEL_IDS[cid]