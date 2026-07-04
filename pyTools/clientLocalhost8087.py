#!/usr/bin/env python

# Source - https://stackoverflow.com/a/18297623
# Posted by David, modified by community.
# See post 'Timeline' for change history
# Retrieved 2026-07-01, License - CC BY-SA 3.0

import socket

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the serverPod8087 inside the pyTools container in the
# podmanExample pod
clientsocket.connect(('localhost', 8087))

clientsocket.send(b'hello-localhost-8087')
