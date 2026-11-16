FROM debian:13-slim

# tftpd-hpa: el servidor tftp clásico de linux
RUN apt-get update \
    && apt-get install -y --no-install-recommends tftpd-hpa \
    && rm -rf /var/lib/apt/lists/*

COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

EXPOSE 69/udp
CMD ["/usr/local/bin/start.sh"]
