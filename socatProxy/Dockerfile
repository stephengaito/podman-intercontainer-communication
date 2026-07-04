FROM alpine:latest

RUN apk --upgrade --no-cache add \
  socat tini iproute2-ss netcat-openbsd \
  inetutils-telnet

COPY entrypoint.sh /

RUN chmod a+x /entrypoint.sh

ENTRYPOINT [ "/sbin/tini", "--" ]

CMD [ "/entrypoint.sh" ]
