btsnoop
=======

Parsing module for BtSnoop packet capture files and encapsulated Bluetooth packets

Documentation
-------------

Specifications
- BtSnoop format
	- http://tools.ietf.org/html/rfc1761
	- http://www.fte.com/webhelp/NFC/Content/Technical_Information/BT_Snoop_File_Format.htm
- Bluetooth specification
	- https://www.bluetooth.org/en-us/specification/adopted-specifications

Module overview
---------------

The `btsnoop` module contains three submodules; `android`, `bt` and `btsnoop`.

The `android` submodule contains functionality for connecting to, and fetching data from, an Android device. It requires an installation of the Android `adb` tool available in `PATH`.

The `btsnoop` submodule contains functionality for parsing a btsnoop file.

The `bt` submodule contains functionality for parsing the Bluetooth data parsed from the btsnoop file.

Usage
-----

### android

Getting the btsnoop log from an android device

```python
>>> import os
>>> from btsnoop.android.snoopphone import SnoopPhone
>>>
>>> phone = SnoopPhone()
>>> filename = phone.pull_btsnoop()
>>>
>>> print filename
/tmp/tmp7t971D/btsnoop_hci.log
```

You can also specify the output file

```python
>>> import os
>>> from btsnoop.android.snoopphone import SnoopPhone
>>>
>>> phone = SnoopPhone()
>>> home = os.path.expanduser("~")
>>> dst = os.path.join(home, 'tmp', 'mysnoop.log')
>>> filename = phone.pull_btsnoop(dst)
>>>
>>> print filename
/home/joekickass/tmp/mysnoop.log
```

### btsnoop

Parsing a btsnoop capture file

```python
>>> import os
>>> import btsnoop.btsnoop.btsnoop as bts
>>>
>>> home = os.path.expanduser("~")
>>> filename = os.path.join(home, 'tmp', 'mysnoop.log')
>>>
>>> records = bts.parse(filename)
>>>
>>> print len(records)
24246
>>> print records[0]
(1, 4, 2, datetime.datetime(2015, 4, 2, 6, 29, 25, 914577), '\x01\x03\x0c\x00')
>>> print records[24245]
(24246, 8, 3, datetime.datetime(2015, 4, 2, 9, 9, 57, 655656), '\x04\x13\x05\x01@\x00\x01\x00')
```

Some of the information in a record can be printed as human readable strings

```python
>>> import btsnoop.btsnoop.btsnoop as bts
...
>>> print len(records)
24246
>>> print records[0]
(1, 4, 2, datetime.datetime(2015, 4, 2, 6, 29, 25, 914577), '\x01\x03\x0c\x00')
>>> record = records[0]
>>> seq_nbr = record[0]
>>> pkt_len = record[1]
>>> flags = bts.flags_to_str(record[2])
>>> timestamp = record[3]
>>> data = record[4]
>>> print seq_nbr
1
>>> print pkt_len
4
>>> print flags
('host', 'controller', 'command')
>>> print timestamp
2015-04-02 06:29:25.914577
>>> print data

```

### bt

TODO