import psutil

def get_network_processes():
    processes = set()
    for conn in psutil.net_connections(kind='inet'):
        try:
            if conn.pid:
                proc = psutil.Process(conn.pid)
                processes.add(proc.name())
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(list(processes))

def get_ports_by_process(process_name):
    ports = set()
    for conn in psutil.net_connections(kind='inet'):
        try:
            proc = psutil.Process(conn.pid)
            if proc.name().lower() == process_name.lower():
                if conn.laddr: ports.add(conn.laddr.port)
                if conn.raddr: ports.add(conn.raddr.port)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return ports