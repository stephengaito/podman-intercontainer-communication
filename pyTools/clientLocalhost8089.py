#!/usr/bin/env python

# Source - https://stackoverflow.com/a/18297623
# Posted by David, modified by community.
# See post 'Timeline' for change history
# Retrieved 2026-07-01, License - CC BY-SA 3.0

import socket

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the serverPasta8089 inside the pasta based pyTools container
clientsocket.connect(('localhost', 8089))

clientsocket.send(b'hello-localhost-8089')
