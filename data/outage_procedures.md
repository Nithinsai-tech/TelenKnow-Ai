# Standard Operating Procedure: Fiber Cut Outage (SOP-042)

## Description
This procedure must be followed in the event of a suspected fiber optic cable cut affecting the regional backhaul.

## Immediate Actions
1. **Detection**: Monitor the Network Management System (NMS) for 'Loss of Signal' (LOS) alarms on trunk ports.
2. **Verification**: Contact the NOC (Network Operations Center) to confirm if maintenance work is scheduled in the area.
3. **Dispatch**: Immediately dispatch the field repair team to the last known healthy splice point.

## Traffic Rerouting
- Initiate BGP path prepending to shift traffic to the secondary microwave link.
- Notify high-priority enterprise customers of potential latency increases (up to 50ms).

## Escalation
If the fiber repair exceeds 4 hours, escalate to the Regional Director of Operations.
