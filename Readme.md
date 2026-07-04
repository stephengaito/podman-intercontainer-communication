# Example inter-container communication with Rootless Podman


## The problem

With rootless Podman, if you run everything *inside* a *single* pod,
inter-container communication is simplicity itself. Every TCP port is
located on the pod's `localhost` (`127.0.0.1`) and is isolated from the
host's network unless specific ports are published.

However, with Podman v 5.8.x, the traffic over any ports published to the
host, lose the originating IP addresses.

For most purposes, this is not a problem.

However for some services, such as, for example, NGinx, Postfix and
Dovecot, this does present some of the following problems:

1. With the loss of the originating IP address, Fail2Ban is unable to ban
   (or at least slow down) external hacking tools such as:
      - password crackers  (Dovecot, Postfix)
      - database vulnerability tools  (NGinx)
      - deep website analysis tools (NGinx)

   This means that weak login passwords to Dovecot IMAPS or Submission are
   potentially more vulnerable.

   Equally weak website frameworks are more easily probed and exploited.

   While passwords and website frameworks ***should*** be strong, they
   are often weaker then we might want.

2. With the loss of the originating IP address, Postfix and RSpamd are
   unable to distinguish incoming from outgoing email traffic, since every
   email "originates" on a local IP address.

   In particular this means that SPF, RBL blocks, DKIM and DMARC checking
   are severely impaired, if not stopped all together.

   For current SMTP, this means obviously SPAMED email is harder to
   detect.

One solution to this problem is to take the containers which need the
originating IP address and run them with either the host or pasta
network stacks.

While running these containers on the host network stack works, it defeats
the purposes of running them rootless. The problem here is that when run
on the host network stack, *every* port on the host is accessible from
inside these containers. For details, see the [discussion
here](https://github.com/eriksjolund/podman-networking-docs#host).

However, while, the pasta network stack, with Podman v5.8.x, keeps the
originating IP addresses intact, containers on the pasta network stack are
unable to communicate with any other Podman container on the same
underlying host. This is true of other containers on pasta network stacks,
or other containers inside any pod or bridge networks.

For example, this means that Postfix is unable to access RSpamd's milter
interface to enable RSpamd to check any incoming email.

Note that applications *inside* a pod or bridge network *can* access
applications inside containers on a pasta network stack (but *not* visa
versa).

## A solution

The solution we exhibit in this repository, would place the containers
which *need* the originating IP address in individual containers located
on *pasta network stacks*, and places everything else inside one or more
Podman pods using one or more bridge based networks.

We then add one or more inter-process communication containers inside the
various pods.

These inter-process communication containers, use `socat` to proxy traffic
on various dedicated unix sockets to corresponding TCP ports *inside* the
pod's networks.

These dedicated unix sockets are then mounted by the required (pasta
based) containers to enable them to communicate to the required TCP ports.

Note that NGinx, Postfix, and Dovecot (for our purposes) *can* make use of
unix sockets.

Equally importantly, note that since the socat proxies are located
*inside* a pod's network, they *do not* preserve the IP address of any
external connection (nor of course do the unix sockets have an associated
IP address or port). These proxies can only be used for traffic for which
the original IP address is no longer used.

## Exploring this solution

This repository includes a very simple Python based client/server
application together with a "pyTools" and a "socatProxy" Containerfile
which can be used to create the required container images.

This repository also has a number of bash scripts which can be used to
create the required images, networks, pods and containers used in this
example setup.

The pyTools containers include the python client/server scripts for you to
run. However, by default, the pyTools image simply runs `sleep infinity`.
The corresponding createPod and runPasta scripts start the appropriate
servers in appropriate containers.

We provide the following scripts to be run on the host:

  - **buildPyTools** builds the pyTools image.
  
  - **deletePyTools** removes the pyTools image
  
  - **buildSocatProxy** builds the socatProxy image.

  - **deleteSocateProxy** removes the socatProxy image.

  - **createPod** creates the podmanExample pod together with all of the
    associated bridge networks, and containers.

    In particular, the example_pytools_pod container is created in the
    podmanExample pod, publishes the 8087 port to the host and mounts the
    `/tmp/podmanExample` directory to access the unix sockets.

  - **startPod** starts the podmanExample pod and its associated containers.

  - **stopPod** starts the podmanExample pod and its associated containers.

  - **deletePod** removes the podmanExample pod together with all of the
    associated bridge networks and containers.

  - **runPasta** runs the pyTools image in a container in its own pasta
    network stack. This container publishes the 8089 port to the host and
    mounts the `/tmp/podmanExample` directory to access the unix sockets.

  - **enterPasta** runs `podman exec` on the pyTools container run by the
    *runPasta* tool.

  - **enterPodPyTools** runs `podman exec` on the pyTools container in the
    podmanExample pod.

  - **enterSocatProxy** runs `podman exec` on the socatProxy container in the
    podmanExample pod.

  - **watchPasta** tails the output from the serverPasta8089 server.

  - **watchPodPyTools** tails the output from the serverPod8087 server.

  - **watchSocat** follows the podman logs output for the
    example_socatproxy_pod container in the podmanExample pod.

Once both images have been built, the pod created and started, you can
enter these running containers multiple times to run the clients or simply
investigate the view of the network each container has (or does not have).

Any of the client scripts can be run in either the pasta or podPyTools
containers or on the host itself to see the results.

The two servers, serverPod8087 and serverPasta8089, report the local and
remote IP addresses and ports from each client connection.

To close down this example, type `^C` in the running pasta container, and
run stopPod.

To remove all images simply run the `deletePod`, `deletePyTools` and
`deleteSocateProxy` scripts.

## Using socat to control access to unix sockets.

Since this approach exposes extra inter-container communication channels to
the host, it is *critical* that these unix socket based channels have
additional permissions set to control who has read/write access to these
channels.

The socat [UNIX-LISTEN address
type](http://www.dest-unreach.org/socat/doc/socat.html#ADDRESS_UNIX_LISTEN)
has options which can be used to manipulate the
[umask](http://www.dest-unreach.org/socat/doc/socat.html#OPTION_UMASK),
[mode](http://www.dest-unreach.org/socat/doc/socat.html#OPTION_MODE),
[user](http://www.dest-unreach.org/socat/doc/socat.html#OPTION_USER), and
[group](http://www.dest-unreach.org/socat/doc/socat.html#OPTION_GROUP)
attributes of the associated unix socket.

It is also *critical* that the [UNIX-LISTEN address
type](http://www.dest-unreach.org/socat/doc/socat.html#ADDRESS_UNIX_LISTEN)
uses the
[fork](http://www.dest-unreach.org/socat/doc/socat.html#OPTION_FORK)
option. Without this fork option, the socat proxy would exit after the
*first* connection.

## Why use a pod instead of simple bridge network?

For this example, it is *critical* that the socatProxy runs in the same
*pod* as the serverPod8087 server. This is so that the socatProxy can
simply use the pod's localhost to access the 8087 port on which the
serverPod8087 server listens.

While it *might* be possible to use multiple containers on the same bridge
network (but not in the same pod), this is a much more complex setup,
which *is not* explored in this example.

## What about `--map-gw` or `--map-host-loopback`?

In Erik Sjölund's excellent "[rootless Podman networking documentation
with
examples](https://github.com/eriksjolund/podman-networking-docs#outbound-tcpudp-connections-to-the-hosts-localhost)",
it is suggested to use `--map-gw` or `--map-host-loopback` to place the
Pasta network stack *on* the host's loopback interface. As pointed out in
that discussion, this is similar to using the host network stack, with all
of its attendant
[problems](https://github.com/eriksjolund/podman-networking-docs#host).

Using socat to provide unix sockets, while we do expose additional
communication channels which a pod only solution (such as Podman v6.0.0
below) does not expose, using unix sockets we do have more control over
which users on the host have access to to which channels (unix sockets).

Using the `--map-gw` or `--map-host-loopback` options, all of these
channels would still have to be exposed to the host, but with out any
attendant additional restrictions. Equally, *all* of the host's tcp-ports
would also be exposed directly to the inside of the various containers run
on the pasta network stack.

## What about Podman v6.0.0?

Podman v6.0.0 *was* released two weeks ago, and it does *now* provide the
ability *keep* the originating IP addresses on published ports.

This means that with Podman v6.0.0, we could place every container inside
a podman pod using a bridge network *and* keep the originating IP
addresses.

However, the [v6.0.0 release
notes](https://github.com/podman-container-tools/podman/releases/tag/v6.0.0)
strongly suggest that this is an "experimental" feature, which *should*
work but is not (yet) ready for production servers.

    A new experimental option for the rootless_port_forwarder field in
    containers.conf has been added, rootless_port_forwarder="pasta". When
    set, rootless bridge networks will use Pasta's kernel-level port
    forwarding via Pesto instead of rootlessport, preserving the original
    client source IP in network traffic in rootless containers. The
    default remains rootlessport (the default for Podman 5.x), but we will
    investigate switching at a later date when stability is more certain.

Equally importantly, Podman v6.0.0 *is not* yet included in any major
Linux OS packaging system. So again, it is not (yet) really ready for a
production server.
    
