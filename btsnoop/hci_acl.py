"""
Parse hci acl packets
"""
import struct


def parse_acl(data):
    """
    Parse HCI ACL data

    References can be found here:
    * https://www.bluetooth.org/en-us/specification/adopted-specifications - Core specification 4.1
    ** [vol 2] Part E (Section 5) - HCI Data Formats
    ** [vol 2] Part E (Section 5.4) - Exchange of HCI-specific information

    """
    handle, length = struct.unpack("<HH", data[:4])
    return (handle, length, data[4:])


def parse_sync_acl(data):
    """
    Parse HCI synchronous ACL data

    References can be found here:
    * https://www.bluetooth.org/en-us/specification/adopted-specifications - Core specification 4.1
    ** [vol 2] Part E (Section 5) - HCI Data Formats
    ** [vol 2] Part E (Section 5.4) - Exchange of HCI-specific information

    """
    handle, length = struct.unpack("<HB", data[:3])
    return (handle, length, data[3:])