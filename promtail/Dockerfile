FROM dhi.io/promtail:3-debian13 AS pattern


# allow promtail to read log files by adding group to the container's user (nonroot)
FROM dhi.io/debian-base:trixie AS builder

COPY --from=pattern /etc/group /etc/group
RUN echo "adm:x:4:nonroot" >> /etc/group


FROM dhi.io/promtail:3-debian13 AS promtail

COPY --from=builder /etc/group /etc/group

# # Override entrypoint to use custom config location
# ENTRYPOINT ["/usr/bin/promtail"]
# CMD ["-config.file=/etc/promtail/config.yml"]
