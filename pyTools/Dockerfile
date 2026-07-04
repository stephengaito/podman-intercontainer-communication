FROM python:trixie

RUN DEBIAN_FRONTEND=noninteractive && \
  apt-get update && \
  apt-get install -y tini iproute2 net-tools \
    iputils-ping iputils-tracepath \
    netcat-openbsd tcptraceroute ndisc6

COPY *.py /

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD [ "/usr/bin/sleep", "infinity" ]
