#!/usr/bin/env python

# Source - https://stackoverflow.com/a/18297623
# Posted by David, modified by community.
# See post 'Timeline' for change history
# Retrieved 2026-07-01, License - CC BY-SA 3.0

import socket

clientsocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# connect to the unix socket which IS mounted in all containers
clientsocket.connect("/tmp/podmanExample/tcp8089.socket")

clientsocket.send(b'hello-localhost-unix-tcp8089')

clientsocket.close()
