# -*- coding: utf-8 -*-
from pupylib.PupyModule import *
from pupylib.PupyCmd import PupyCmd
from pupylib.utils.rpyc_utils import obtain
from pupylib.utils.term import colorize
from modules.lib.utils.shell_exec import shell_exec
from datetime import datetime, timedelta

import logging

__class_name__="WModule"

ADMINS = ('NT AUTHORITY\SYSTEM', 'root')

@config(cat="admin")
class WModule(PupyModule):
    """ list terminal sessions """

    dependencies = [ 'pupyps' ]
    is_module=False

    def init_argparse(self):
        self.arg_parser = PupyArgumentParser(prog="w", description=self.__doc__)

    def run(self, args):
        try:
            data = obtain(self.client.conn.modules.pupyps.users())

            tablein = []

            for user, hosts in reversed(sorted(data.iteritems())):
                for host, sessions in hosts.iteritems():
                    for session in sessions:
                        color = ""

                        if 'idle' in session:
                            idle = session['idle']
                            color = "cyan" if idle < 10*60 else (
                                "grey" if idle > 60*60*24 else ""
                            )

                        object = {
                            'HOST': colorize(host, color),
                            'USER': colorize(
                                user,
                                "yellow" if user in ADMINS else (
                                    "green" if session.get('me') else "")
                            ),
                            'LOGIN': colorize(
                                str(datetime.fromtimestamp(int(session['started']))), color
                            ),
                        }

                        if session.get('terminal'):
                            if session.get('name'):
                                what = '{} {}'.format(
                                    session['exe'] if session.get('exe') else ('{'+session.get('name')+'}'),
                                    ' '.join(session['cmdline'][1:] if session.get('cmdline') else '')
                                )
                            else:
                                what = ''

                            object.update({
                                'IDLE': colorize(
                                    str(timedelta(seconds=session['idle'])), color
                                ) if session.get('idle') else '',
                                'PID': colorize(str(session.get('pid', '')), color),
                                'WHAT': colorize(what[:30]+'…' if len(what) > 30 else what, color)
                            })

                        tablein.append(object)

            self.stdout.write(PupyCmd.table_format(tablein))

        except Exception, e:
            logging.exception(e)
