import asyncssh

from os import path

here_dir = path.abspath(path.dirname(__file__))
if not path.exists(path.join(here_dir, 'ssh_host_rsa_key')):
    key = asyncssh.generate_private_key('ssh-rsa')
    bytes = key.export_private_key()
    open('ssh_host_rsa_key', 'wb').write(bytes)
    print('ssh_host_rsa_key generated')
