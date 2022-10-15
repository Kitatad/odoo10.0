#!E:\EHPEA\Odoo10_virtual\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'ws-grid-pager==0.2','console_scripts','gp-switch-workspace'
__requires__ = 'ws-grid-pager==0.2'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('ws-grid-pager==0.2', 'console_scripts', 'gp-switch-workspace')()
    )
