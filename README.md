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