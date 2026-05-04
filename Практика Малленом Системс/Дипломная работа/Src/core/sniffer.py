from PyQt6.QtCore import QThread, pyqtSignal
from scapy.all import conf, sniff
from core.parser import PacketParser

class SnifferThread(QThread):
    packet_received = pyqtSignal(object, dict)
    stats_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.interface = None
        self.target_ports = set()
        self.is_running = False
        self.stats = {"TCP": 0, "UDP": 0, "ICMP": 0, "Total": 0}
        
        self.offline_file = None

    def run(self):
        self.stats = {"TCP": 0, "UDP": 0, "ICMP": 0, "Total": 0}
        self.stats_updated.emit(self.stats)

        if self.offline_file:
            try:

                sniff(offline=self.offline_file, prn=self.handle_packet, store=False)
            except Exception as e:
                print(f"Ошибка чтения PCAP: {e}")
            
            self.offline_file = None
            self.is_running = False

        else:
            try:
                socket = conf.L2listen(iface=self.interface)
            except Exception as e:
                print(f"Ошибка открытия сокета: {e}")
                return

            while self.is_running:
                sniff(
                    iface=self.interface, count=1, timeout=0.1, 
                    prn=self.handle_packet, stop_filter=lambda x: not self.is_running
                )

    def handle_packet(self, packet):
        if not self.is_running:
            return

        info = PacketParser.get_info(packet)

        if self.target_ports:
            sport = info.get("src_port")
            dport = info.get("dst_port")
            
            if sport == "-" or dport == "-":
                return
                
            try:
                if int(sport) not in self.target_ports and int(dport) not in self.target_ports:
                    return
            except ValueError:
                return

        proto = info["proto"]
        if proto in self.stats:
            self.stats[proto] += 1
        self.stats["Total"] += 1
        
        if "ips" not in self.stats:
            self.stats["ips"] = {} 
            
        src_ip = info.get("src", "-")
        dst_ip = info.get("dst", "-")
        
        ignore_ips = {"-", "0.0.0.0", "255.255.255.255", "127.0.0.1"}
        
        if src_ip not in ignore_ips:
            self.stats["ips"][src_ip] = self.stats["ips"].get(src_ip, 0) + 1
            
        if dst_ip not in ignore_ips:
            self.stats["ips"][dst_ip] = self.stats["ips"].get(dst_ip, 0) + 1
            
        if "flags" not in self.stats:
            self.stats["flags"] = {} 
            
        if proto == "TCP":
            flags = info.get("flags", "-")
            if flags != "-":
                self.stats["flags"][flags] = self.stats["flags"].get(flags, 0) + 1
        
        self.stats_updated.emit(self.stats)
        self.packet_received.emit(packet, info)