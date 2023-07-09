import asyncio
import os
import random
import string
import sys
from os import path
import getopt
import json
import asyncssh
from asyncssh.listener import create_unix_forward_listener

config_dir = path.abspath(path.dirname(__file__))
server_name = 'app.pywebio.online'
sock_dir = None
server_port = 1022
https = False


def keygen():
    key_file = path.join(config_dir, 'ssh_host_key')
    if not path.exists(key_file):
        key = asyncssh.generate_private_key('ssh-rsa')
        bytes = key.export_private_key()
        open(key_file, 'wb').write(bytes)
        print('ssh_host_key generated')


def parse_ssh_arguments(arguments):
    try:
        optlist, _ = getopt.getopt(arguments, '', ['output='])
    except getopt.GetoptError:
        return {}
    return dict(optlist)


async def handle_client(process):
    print('command', process.command)
    sock_name = process.get_extra_info('sock_name')
    if not sock_name:
        usage = f"ssh -R /:host:port -p {server_port} {server_name}"
        process.stderr.write(f'Missing "-R" argument for ssh command.\nUsage: {usage}\n')
        process.exit(1)
        return

    entrypoint = '%s://%s.%s' % ('https' if https else 'http', sock_name, server_name)
    kwargs = parse_ssh_arguments((process.command or '').split())
    if kwargs.get('--output', 'text') == 'json':
        response = json.dumps({'address': entrypoint, 'status': 'success'})
    else:
        response = 'The public entrypoint for your local web service is:\n%s' % entrypoint
    process.stdout.write(response + '\n')
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

    def new_sock_path(self):
        sock_name = get_random(12)
        sock_path = os.path.join(sock_dir, '%s.sock' % sock_name)
        self.conn.set_extra_info(sock_name=sock_name)
        return sock_path

    def unix_server_requested(self, listen_path):
        rewrite_path = self.new_sock_path()

        async def tunnel_connection(session_factory):
            """Forward a local connection over SSH"""
            # listen_path is a fake path
            return await self.conn.create_unix_connection(session_factory, listen_path)

        try:
            return create_unix_forward_listener(self.conn, asyncio.get_event_loop(),
                                                tunnel_connection,
                                                rewrite_path)
        except OSError as exc:
            raise

    def server_requested(self, listen_host, listen_port):
        """use sock forward even request port forward"""
        sock_path = self.new_sock_path()

        async def tunnel_connection(session_factory):
            """Forward a local connection over SSH"""
            fake_orig_host, fake_orig_port = '127.0.0.1', 8080
            return (await self.conn.create_connection(session_factory, listen_host, listen_port,
                                                      fake_orig_host, fake_orig_port))

        try:
            return create_unix_forward_listener(self.conn, asyncio.get_event_loop(),
                                                tunnel_connection, sock_path)
        except OSError as exc:
            raise


async def start_server(host='0.0.0.0', port=1022):
    key_file = path.join(config_dir, 'ssh_host_key')
    await asyncssh.create_server(
        MySSHServer, host=host, port=port,
        server_host_keys=[key_file],
        process_factory=handle_client,
        # allow_pty=False,  # no allocation of a pseudo-tty
        agent_forwarding=False,
        allow_scp=False,
        keepalive_interval=30,
        # The time in seconds to wait before sending a keepalive message if no data has been received from the client.
    )


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=1022, help='The port for ssh server')
    parser.add_argument("--config-dir", type=str, default='.', help='The dir to provide the required files')
    parser.add_argument("--socket-dir", type=str, default='/tmp/localshare', help='The dir to save the socket files')
    parser.add_argument("--https", action="store_true", help='Whether to enable https')
    parser.add_argument("server_name", type=str, help='The domain name of the server')
    args = parser.parse_args()

    sock_dir = args.socket_dir
    server_name = args.server_name
    config_dir = args.config_dir
    server_port = args.port
    https = args.https or os.environ.get('HTTPS', '').lower() == 'true'

    os.umask(0o000)

    keygen()

    if not path.exists(sock_dir):
        os.mkdir(sock_dir)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_server(port=args.port))
    except (OSError, asyncssh.Error) as exc:
        sys.exit('Error starting server: ' + str(exc))
    loop.run_forever()
