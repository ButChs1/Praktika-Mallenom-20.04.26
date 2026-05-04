from scapy.all import get_working_ifaces

def get_available_interfaces():
    interfaces = []
    try:
        for iface in get_working_ifaces():
            interfaces.append((iface.description, iface.name))
    except Exception as e:
        print(f"Ошибка получения интерфейсов: {e}")
    
    return interfaces