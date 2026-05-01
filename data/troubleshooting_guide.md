# Customer Troubleshooting Guide: Fixed Wireless Access (FWA)

## Issue: Low Throughput / Packet Loss
Possible causes include signal interference, weather conditions, or hardware misalignment.

## Troubleshooting Steps
1. **Signal Strength (RSRP)**: Check if RSRP is above -90 dBm. If below, consider relocating the CPE (Customer Premises Equipment).
2. **SINR Check**: Ensure Signal-to-Interference-plus-Noise Ratio (SINR) is > 10 dB.
3. **Firmware Update**: Verify the CPE is running firmware version 2.4.1 or higher.
4. **Frequency Scan**: Perform a spectral scan to identify interference on the 5GHz band from local Wi-Fi hotspots.

## Resolution
- If signal metrics are healthy but throughput is low, perform a factory reset of the POE injector.
- If symptoms persist, replace the CPE unit.
