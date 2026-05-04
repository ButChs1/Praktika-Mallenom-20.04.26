from PyQt6.QtCore import QThread, pyqtSignal
from scapy.all import IP, TCP, UDP, ICMP, send
import time
import random

class GeneratorThread(QThread):
    log_ready = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.dst_ip = "127.0.0.1"
        self.dst_port = 80
        
        self.src_ip = "192.168.1.100"
        self.src_port = 12345
        self.rand_src_ip = False
        self.rand_src_port = False
        
        self.proto = "TCP"
        self.tcp_flags = ""
        self.payload = "Test Packet"
        self.count = 1
        self.delay = 1.0
        self.is_running = False

    def _generate_random_ip(self):
        return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

    def run(self):
        self.is_running = True
        sent_count = 0

        for i in range(self.count):
            if not self.is_running:
                self.log_ready.emit("Генерация прервана пользователем.")
                break

            current_src_ip = self._generate_random_ip() if self.rand_src_ip else self.src_ip
            current_src_port = random.randint(1024, 65535) if self.rand_src_port else self.src_port

            if self.proto == "TCP":
                tcp_layer = TCP(sport=current_src_port, dport=int(self.dst_port))
                if self.tcp_flags:
                    tcp_layer.flags = self.tcp_flags
                packet = IP(src=current_src_ip, dst=self.dst_ip) / tcp_layer / self.payload
                log_proto = f"TCP {current_src_ip}:{current_src_port} -> {self.dst_ip}:{self.dst_port}"
                
            elif self.proto == "UDP":
                packet = IP(src=current_src_ip, dst=self.dst_ip) / UDP(sport=current_src_port, dport=int(self.dst_port)) / self.payload
                log_proto = f"UDP {current_src_ip}:{current_src_port} -> {self.dst_ip}:{self.dst_port}"
                
            elif self.proto == "ICMP":
                packet = IP(src=current_src_ip, dst=self.dst_ip) / ICMP() / self.payload
                log_proto = f"ICMP {current_src_ip} -> {self.dst_ip}"
            
            size = len(packet)
            send(packet, verbose=False)
            sent_count += 1
            
            log_msg = f"[{i+1}/{self.count}] {log_proto} | Size: {size}B"
            self.log_ready.emit(log_msg)
            
            if i < self.count - 1 and self.delay > 0:
                time.sleep(self.delay)

        self.status_message.emit(f"Отправка {sent_count} пакетов завершена")
        self.is_running = False

    def stop(self):
        self.is_running = False