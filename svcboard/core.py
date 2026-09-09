"""svcboard core: scan listening TCP ports and their owning processes."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

import psutil

# Well-known port hints (IANA + common dev services).
PORT_HINTS: dict[int, str] = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
    53: "dns", 80: "http", 110: "pop3", 143: "imap",
    443: "https", 465: "smtps", 587: "submission",
    3306: "mysql", 5432: "postgres", 6379: "redis",
    8080: "http-alt", 8443: "https-alt", 9000: "dev",
    11211: "memcached", 27017: "mongodb",
}


@dataclass
class Service:
    port: int
    host: str
    proto: str
    pid: Optional[int]
    name: Optional[str]
    cmdline: Optional[str]
    hint: Optional[str]

    def to_dict(self) -> dict:
        return asdict(self)


def scan(listen_only: bool = True, with_process: bool = True) -> list[Service]:
    """Return a sorted list of listening services on this machine."""
    services: list[Service] = []
    seen = set()
    for conn in psutil.net_connections(kind="tcp"):
        if listen_only and conn.status != psutil.CONN_LISTEN:
            continue
        if not conn.laddr:
            continue
        key = (conn.laddr.ip, conn.laddr.port)
        if key in seen:
            continue
        seen.add(key)
        pid = conn.pid
        name = cmdline = None
        if with_process and pid:
            try:
                proc = psutil.Process(pid)
                name = proc.name()
                cmdline = " ".join(proc.cmdline()) or None
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        services.append(Service(
            port=conn.laddr.port,
            host=conn.laddr.ip,
            proto="tcp",
            pid=pid,
            name=name,
            cmdline=cmdline,
            hint=PORT_HINTS.get(conn.laddr.port),
        ))
    services.sort(key=lambda s: (s.port, s.host))
    return services
