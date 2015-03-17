"""
  Parse hci packet information from binary string

  This is done after parsing the HCI packet type, which is
  implementation specific (e.g. HCI UART).

  usage:
     ./hci.py <type> <data string>
"""
import sys
import struct
from hci_cmd import HCI_COMMANDS
from hci_evt import HCI_EVENTS


def parse_cmd(data):
    """
    Parse HCI command

	References can be found here:
    * https://www.bluetooth.org/en-us/specification/adopted-specifications - Core specification 4.1
    ** [vol 2] Part E (Section 5) - HCI Data Formats
    ** [vol 2] Part E (Section 5.4) - Exchange of HCI-specific information

    All integer values are stored in "little-endian" order.
    """
    opcode = struct.unpack("<H", data[:2])[0]
    return HCI_COMMANDS[opcode]


def parse_acl(data):
    """
    Parse HCI ACL data

    References can be found here:
    * https://www.bluetooth.org/en-us/specification/adopted-specifications - Core specification 4.1
    ** [vol 2] Part E (Section 5) - HCI Data Formats
    ** [vol 2] Part E (Section 5.4) - Exchange of HCI-specific information

    """
    bytes = [ord(x) for x in data]
    return bytes


def parse_sync_acl(data):
    """
    Parse HCI synchronous ACL data

    References can be found here:
    * https://www.bluetooth.org/en-us/specification/adopted-specifications - Core specification 4.1
    ** [vol 2] Part E (Section 5) - HCI Data Formats
    ** [vol 2] Part E (Section 5.4) - Exchange of HCI-specific information

    """
    bytes = [ord(x) for x in data]
    return bytes


def parse_evt(data):
    """
    Parse HCI event data

    References can be found here:
    * https://www.bluetooth.org/en-us/specification/adopted-specifications - Core specification 4.1
    ** [vol 2] Part E (Section 5) - HCI Data Formats
    ** [vol 2] Part E (Section 5.4) - Exchange of HCI-specific information

    All integer values are stored in "little-endian" order.
    """
    evtcode = struct.unpack("<B", data[:1])[0]
    return HCI_EVENTS[evtcode]


PKT_TYPE_PARSERS = {"HCI_CMD": parse_cmd,
                    "ACL_DATA": parse_acl,
                    "ACL_SYNC_DATA": parse_sync_acl,
                    "HCI_EVT": parse_evt}


def parse(hci_pkt_type, data):
    """
    Conveniance method for switching between parsing methods based on type
    """
    parser = PKT_TYPE_PARSERS[hci_pkt_type]
    if parser is None:
        raise ValueError("Illegal HCI packet type")
    return parser(data)


def print_hdr():
    """
    Print the script header
    """
    print ""
    print "##############################"
    print "#                            #"
    print "#    hci parser v0.1         #"
    print "#                            #"
    print "##############################"
    print ""


def main(hci_pkt_type, data):
    print parse(hci_pkt_type, data)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print __doc__
        sys.exit(1)

    print_hdr()
    sys.exit(main(sys.argv[1], sys.argv[2]))