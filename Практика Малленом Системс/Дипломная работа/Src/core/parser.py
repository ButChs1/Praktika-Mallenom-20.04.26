from scapy.all import IP, TCP, UDP, ICMP
class PacketParser:
    @staticmethod
    def get_info(packet):
        info = {
            "proto": packet.summary().split()[0] if packet.summary() else "Unknown",
            "src": "-", "dst": "-", "src_port": "-", "dst_port": "-",
            "length": len(packet),
            "ttl": "-",
            "flags": "-"
        }

        if packet.haslayer('IP'):
            info["src"] = packet['IP'].src
            info["dst"] = packet['IP'].dst
            info["ttl"] = packet['IP'].ttl

        if packet.haslayer('TCP'):
            info["proto"] = "TCP"
            info["src_port"] = packet['TCP'].sport
            info["dst_port"] = packet['TCP'].dport
            info["flags"] = str(packet['TCP'].flags)
        
        elif packet.haslayer('UDP'):
            info["proto"] = "UDP"
            info["src_port"] = packet['UDP'].sport
            info["dst_port"] = packet['UDP'].dport
            
        elif packet.haslayer('ICMP'):
            info["proto"] = "ICMP"
        else:
            info["proto"] = packet.lastlayer().name

        return info