# Network Configuration Guide: V-Series Routers

## Overview
This document outlines the standard configuration for V-Series routers used in the core telecom network.

## Interface Setup
To configure the GigabitEthernet interfaces, use the following commands:
1. Enter global configuration mode: `configure terminal`
2. Select the interface: `interface GigabitEthernet0/0/1`
3. Set the IP address: `ip address 192.168.10.1 255.255.255.0`
4. Enable the interface: `no shutdown`

## OSPF Routing
Enable OSPF for dynamic routing within Area 0:
- `router ospf 1`
- `network 192.168.10.0 0.0.0.255 area 0`

## Security Protocols
All V-Series routers must have SSH enabled and Telnet disabled for management access.
