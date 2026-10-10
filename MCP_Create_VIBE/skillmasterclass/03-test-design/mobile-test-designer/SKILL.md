---
name: mobile-test-designer
description: >-
  Design mobile application tests for iOS and Android: installation, permissions, gestures, orientation, interruptions, connectivity, device and OS coverage, and store requirements, with Appium or native tooling. Use when a tester says "mobile testing", "app test cases", "device matrix", or an app release is planned.
license: MIT
metadata:
  author: skillmasterclass-local
  stlc-phase: Test Design
  version: 1.0.0
---

# Mobile App Test Designer

## When to use
- A mobile app release needs a test design.
- A device and OS support matrix must be defined.
- Field issues point to interruptions or poor connectivity.

## Workflow
1. **Confirm platforms.** iOS/Android versions, app type (native, hybrid, PWA) and distribution channel.
2. **Build the device matrix** from usage analytics when available, covering screen sizes, OS versions and a low-end device.
3. **Design core cases.** Install/upgrade/uninstall, first launch, permissions grant/deny, gestures, orientation, deep links, push notifications.
4. **Design resilience cases.** Calls, SMS, backgrounding, low battery, airplane mode, slow or flapping network, storage full.
5. **Add store and platform checks,** then **HUMAN REVIEW GATE** on the matrix and priorities.

## Output shape
A device/OS matrix and test cases grouped by functionality and resilience, each with platform applicability and priority.

## Quality checks
- Permission cases include both grant and deny.
- At least one interruption and one connectivity case exist.
- The matrix cites its source or is marked an assumption.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
