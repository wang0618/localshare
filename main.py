import asyncio
import os
import random
import string
import sys
from os import path

import asyncssh
from asyncssh.listener import create_unix_forward_listener
here_dir = path.abspath(path.dirname(__file__))

server_host = 'app.pywebio.online'
sock_dir = '/tmp/ltun'


async def handle_client(process):
    process.stdout.write('The public entrypoint for your local web service is:\nhttp://%s.%s\n' %
                         (process.get_extra_info('sock_name'), server_host))
    # process.exit(0)
    try:
        async for line in process.stdin:
            line = line.rstrip('\n')
            if line:
                print(line)
    except asyncssh.BreakReceived:
        pass
    process.exit(0)
    # process.wait_closed()


def get_random(len=16):
    chars = string.ascii_lowercase + string.digits
    s = [random.choice(chars) for _ in range(len)]
    return ''.join(s)


class MySSHServer(asyncssh.SSHServer):
    conn = None

    def connection_made(self, conn):
        self.conn = conn

    def connection_lost(self, exc):
        if exc:
            print('SSH connection error: ' + str(exc), file=sys.stderr)

    def begin_auth(self, username):
        # No auth is required
        return False

    def password_auth_supported(self):
        return True

    def unix_server_requested(self, listen_path):
        sock_name = get_random(12)
        rewrite_path = os.path.join(sock_dir, '%s.sock' % sock_name)
        self.conn.set_extra_info(sock_name=sock_name)

        async def tunnel_connection(session_factory):
            """Forward a local connection over SSH"""
            return await self.conn.create_unix_connection(session_factory, listen_path)

        try:
            return create_unix_forward_listener(self.conn, asyncio.get_event_loop(),
                                                tunnel_connection,
                                                rewrite_path)
        except OSError as exc:
            raise


async def start_server():
    key_file = path.join(here_dir, 'key', 'ssh_host_rsa_key')
    await asyncssh.create_server(
        MySSHServer, host='0.0.0.0', port=1022,
        server_host_keys=[key_file],
        process_factory=handle_client,
        # allow_pty=False,  # no allocation of a pseudo-tty
        agent_forwarding=False,
        allow_scp=False,
        keepalive_interval=30,
        # The time in seconds to wait before sending a keepalive message if no data has been received from the client.
    )


if __name__ == '__main__':
    os.umask(0o000)

    if not path.exists(sock_dir):
        os.mkdir(sock_dir)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(start_server())
    except (OSError, asyncssh.Error) as exc:
        sys.exit('Error starting server: ' + str(exc))

    loop.run_forever()
