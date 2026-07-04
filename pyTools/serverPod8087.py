#!/usr/bin/env python

# Source - https://stackoverflow.com/a/18297623
# Posted by David, modified by community.
# See post 'Timeline' for change history
# Retrieved 2026-07-01, License - CC BY-SA 3.0

import socket

def fPrint(f, msg) :
  f.write(msg + '\n')
  f.flush()

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('0.0.0.0', 8087))
serversocket.listen()

with open('/tmp/podmanExample/serverPod8087.log','w') as f :

  fPrint(
    f, "pyTools server running inside a container in the podmanExample pod"
  )
  fPrint(f, "listening to port 8087 on all interfaces")
  fPrint(f, "")

  try :
    while True:
      connection, address = serversocket.accept()
      fPrint(f, "")
      fPrint(f, "--------------------------------------------")
      fPrint(f, "")
      localIP,  localPort  = connection.getsockname()
      remoteIP, remotePort = connection.getpeername()
      fPrint(f, f'local    ip: {localIP}')
      fPrint(f ,f'local  port: {localPort}')
      fPrint(f, f'remote   ip: {remoteIP}')
      fPrint(f, f'remote port: {remotePort}')
      buf = connection.recv(64)
      if len(buf) > 0:
        fPrint(f, buf.decode('utf-8'))
        # break
  except KeyboardInterrupt :
    fPrint(f, "  bye")
