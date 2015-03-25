"""
  Parse hci packet information from binary string

  This is done after parsing the HCI packet type, which is
  implementation specific (e.g. HCI UART).

  usage:
     ./hci.py <type> <data string>
"""
import sys
import struct
import hci_cmd
import hci_evt
import hci_acl


PKT_TYPE_PARSERS = {"HCI_CMD": hci_cmd.parse_cmd,
                    "ACL_DATA": hci_acl.parse_acl,
                    "ACL_SYNC_DATA": hci_acl.parse_sync_acl,
                    "HCI_EVT": hci_evt.parse_evt}


def parse(hci_pkt_type, data):
    """
    Convenience method for switching between parsing methods based on type
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