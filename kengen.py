import asyncssh

from os import path

here_dir = path.abspath(path.dirname(__file__))
key_file = path.join(here_dir, 'key', 'ssh_host_rsa_key')
if not path.exists(key_file):
    key = asyncssh.generate_private_key('ssh-rsa')
    bytes = key.export_private_key()
    open(key_file, 'wb').write(bytes)
    print('ssh_host_rsa_key generated')
