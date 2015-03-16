"""
  Parse hci information from binary string
  usage:
     ./hci_uart.py <data string>
"""
import sys


# HCI Packet types for UART Transport layer
# Core specification 4.1 [vol 4] Part A (Section 2) - Protocol
HCI_CMD = 0x01
ACL_DATA = 0x02
ACL_SYNC_DATA = 0x03
HCI_EVT = 0x04

def parse(data):
    """
    Parse a hci information from the specified data string

    There are four kinds of HCI packets that can be sent via the UART Transport
    Layer; i.e. HCI Command Packet, HCI Event Packet, HCI ACL Data Packet
    and HCI Synchronous Data Packet (see Host Controller Interface Functional
    Specification in Volume 2, Part E). HCI Command Packets can only be sent to
    the Bluetooth Host Controller, HCI Event Packets can only be sent from the
    Bluetooth Host Controller, and HCI ACL/Synchronous Data Packets can be
    sent both to and from the Bluetooth Host Controller.

    References can be found here:
    * https://www.bluetooth.org/en-us/specification/adopted-specifications - Core specification 4.1
    ** [vol 4] Part A (Section 2) Protocol

    Returns a list of all bytes in the data string, with the HCI type (the first byte) identified and
    converted to a string.
    """
    bytes = [ord (b) for b in data]
    return [ _parse_type(b) if i == 0 else b for i,b in enumerate(bytes)]

def _parse_type(type):
    """
    Parse HCI packet types to a proper description string
    """
    if type == HCI_CMD:
        return "HCI_CMD"
    elif type == ACL_DATA:
        return "ACL_DATA"
    elif type == ACL_SYNC_DATA:
        return "ACL_SYNC_DATA"
    elif type == HCI_EVT:
        return "HCI_EVT"
    else:
        raise ValueError("Illegal HCI UART packet type")

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


def main(data):
    parse(data)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)

    print_hdr()
    sys.exit(main(sys.argv[1]))