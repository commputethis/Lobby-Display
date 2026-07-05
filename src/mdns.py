#!/usr/bin/env python3
"""mDNS broadcaster for Lobby Display"""

import socket
import threading
from zeroconf import Zeroconf, ServiceInfo

class MDNSBroadcaster:
    def __init__(self, device_name, port=5000):
        self.device_name = device_name
        self.port = port
        self.zeroconf = None
        self.service_info = None
        self.running = False
        
    def _sanitize_hostname(self, name):
        sanitized = ''.join(c if c.isalnum() else '-' for c in name.lower())
        sanitized = '-'.join(filter(None, sanitized.split('-')))
        return sanitized or 'lobby-display'
    
    def start(self):
        if self.running:
            return
            
        hostname = self._sanitize_hostname(self.device_name)
        full_hostname = f"{hostname}.local"
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        
        self.service_info = ServiceInfo(
            "_http._tcp.local.",
            f"{self.device_name}._http._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=self.port,
            properties={
                'path': '/',
                'version': '1.0.0',
                'device': self.device_name
            },
            server=f"{hostname}.local."
        )
        
        self.zeroconf = Zeroconf()
        self.zeroconf.register_service(self.service_info)
        self.running = True
        
        print(f"mDNS: Broadcasting as {full_hostname} ({ip}:{self.port})")
        
    def update_name(self, new_name):
        if not self.running:
            self.device_name = new_name
            return
            
        self.zeroconf.unregister_service(self.service_info)
        
        self.device_name = new_name
        hostname = self._sanitize_hostname(new_name)
        
        self.service_info.name = f"{new_name}._http._tcp.local."
        self.service_info.server = f"{hostname}.local."
        self.service_info.properties = {
            'path': '/',
            'version': '1.0.0',
            'device': new_name
        }
        
        self.zeroconf.register_service(self.service_info)
        print(f"mDNS: Updated to {hostname}.local")
        
    def stop(self):
        if self.zeroconf:
            self.zeroconf.unregister_all_services()
            self.zeroconf.close()
        self.running = False
        
    def get_hostname(self):
        return f"{self._sanitize_hostname(self.device_name)}.local"