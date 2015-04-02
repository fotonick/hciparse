import os
import tempfile

from phone import Phone


BTSNOOP_FILE = 'btsnoop_hci.log'
BTSNOOP_SRC = os.path.join('/sdcard', BTSNOOP_FILE)


class SnoopPhone(Phone):

    def __init__(self, serial=None):
        super(SnoopPhone, self).__init__(serial=serial)
        self._src = BTSNOOP_SRC
        tmp_dir = tempfile.mkdtemp()
        self._dst = os.path.join(tmp_dir, BTSNOOP_FILE)

    def pull_btsnoop(self, dst=None):
        if not dst:
            dst = self._dst
        ret = super(SnoopPhone, self).pull(self._src, dst)
        print ret
        return dst