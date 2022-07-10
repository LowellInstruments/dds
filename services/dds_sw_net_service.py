#!/usr/bin/env python3


import datetime
import logging
import time
import subprocess as sp
from mat.ddh_shared import get_dds_folder_path_logs


date_fmt = "%Y-%b-%d %H:%M:%S"
t = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
_f = str(get_dds_folder_path_logs() / 'aws' / '{}.log'.format(str(t)))
logging.basicConfig(filename=_f,
                    filemode='w',
                    datefmt=date_fmt,
                    format='%(asctime)s [ %(levelname)s ] %(message)s',
                    level=logging.INFO)
_li = logging.info


def _sh(s: str) -> bool:
    rv = sp.run(s, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return rv.returncode == 0


def _p(s):
    s = 'NET | ' + s
    _li(s)
    print(s)


def main():

    # wi-fi can go internet and we already use it
    wlan_has_via = _sh('timeout 2 ping -c 1 -I wlan0 www.google.com')
    if wlan_has_via and _sh('ip route get 8.8.8.8 | grep wlan0'):
        _p('wi-fi')
        time.sleep(60)
        return

    # wi-fi cannot go internet, are we really using it
    if not _sh('/usr/sbin/ifmetric ppp0 400'):
        _p('ifmetric error ppp0 400')
        time.sleep(2)

    # wi-fi, try again
    wlan_has_via = _sh('timeout 2 ping -c 1 -I wlan0 www.google.com')
    if wlan_has_via and _sh('ip route get 8.8.8.8 | grep wlan0'):
        _p('* wi-fi *')
        time.sleep(60)
        return

    # wi-fi does NOT work, make sure we try cell
    if not _sh('/usr/sbin/ifmetric ppp0 0'):
        _p('ifmetric error ppp0 0')
        time.sleep(2)

    # check cell can go to internet
    ppp_has_via = _sh('timeout 2 ping -c 1 -I ppp0 www.google.com')
    if ppp_has_via and _sh('ip route get 8.8.8.8 | grep ppp0'):
        _p('cell')
        time.sleep(300)
        return

    _p('none')


if __name__ == '__main__':
    # see all services -> systemctl list-units --type=service
    while 1:
        main()