# Validate Exercise

Use this guide to check exercise readiness.

## Steps

1. Open `Exercise Designer`.
2. Review validation status.
3. Check `Objectives complete`.
4. Check `Controllers assigned`.
5. Review `Timeline conflicts`.
6. Review `Missing relationships`.
7. Confirm `Publish readiness`.
8. Select planned items with warnings and correct missing objective links, controller assignments, or scheduled times.
9. Click `Validate` to record an audit-ready validation event.

## Alpha Behavior

Validation is calculated from the local Exercise Data Engine.

Atlas checks whether objectives include success criteria and linked assets, injects have objective links and assigned controllers, timeline events have scheduled times, products reference a source, and publish readiness is blocked when warnings or pending reviews remain.
