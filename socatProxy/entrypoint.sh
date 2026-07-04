#!/bin/ash

# This ash script creates a number of socat based unix-socket to tpc-port
# proxies.

# See the socat documentation for details of the UNIX-LISTEN options which
# can be used to control the unix socket permissions as well as the proxy
# behaviour:
#
#  http://www.dest-unreach.org/socat/doc/socat.html#ADDRESS_UNIX_LISTEN
#
# Unix socket permissions:
#
#  http://www.dest-unreach.org/socat/doc/socat.html#OPTION_UMASK
#  http://www.dest-unreach.org/socat/doc/socat.html#OPTION_MODE
#  http://www.dest-unreach.org/socat/doc/socat.html#OPTION_USER
#  http://www.dest-unreach.org/socat/doc/socat.html#OPTION_GROUP
#
# Proxy behaviour:
#
#  http://www.dest-unreach.org/socat/doc/socat.html#OPTION_FORK
#  http://www.dest-unreach.org/socat/doc/socat.html#OPTION_UNLINK_EARLY

set -e

# server inside pyTools container in the podmanExample pod
socat -d -d -d -lh                                                \
  unix-listen:/tmp/podmanExample/tcp8087.socket,fork,unlink-early \
  tcp4:localhost:8087 &

# server inside the pasta based pyTools container
socat -d -d -d -lh                                                \
  unix-listen:/tmp/podmanExample/tcp8089.socket,fork,unlink-early \
  tcp4:host.containers.internal:8089 &

wait -n
