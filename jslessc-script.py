#!E:\EHPEA\Odoo10_virtual\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'js.lesscss==1.3.0','console_scripts','jslessc'
__requires__ = 'js.lesscss==1.3.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('js.lesscss==1.3.0', 'console_scripts', 'jslessc')()
    )
