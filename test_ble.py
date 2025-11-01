#!/usr/bin/env python3
"""
Test script for Xiaomi Car Air Purifier BLE communication.

This script demonstrates how to connect to and control the purifier
using the Bleak library directly, without Home Assistant.

Requirements:
    pip install bleak

Usage:
    python test_ble.py
"""

import asyncio
import sys
from bleak import BleakClient, BleakScanner

# UUIDs from reverse engineering
SERVICE_UUID = "0000FFD0-0000-1000-8000-00805F9B34FB"
POWER_CHAR_UUID = "0000FFD1-0000-1000-8000-00805F9B34FB"
MODE_CHAR_UUID = "0000FFD3-0000-1000-8000-00805F9B34FB"

# Mode constants
MODE_AUTO = bytes([0x00, 0x00, 0x0F, 0x18])
MODE_SILENT = bytes([0x01, 0x00, 0x0F, 0x18])
MODE_STANDARD = bytes([0x02, 0x00, 0x0F, 0x18])
MODE_STRONG = bytes([0x03, 0x00, 0x0F, 0x18])

MODE_NAMES = {
    0x00: "Auto",
    0x01: "Silent",
    0x02: "Standard",
    0x03: "Strong",
}


async def scan_for_device():
    """Scan for Xiaomi Car Air Purifier."""
    print("Scanning for Xiaomi Car Air Purifier...")
    devices = await BleakScanner.discover(timeout=10.0)

    for device in devices:
        if device.name and "MI-CAR" in device.name.upper():
            print(f"✓ Found device: {device.name} ({device.address})")
            return device

    print("✗ Device not found")
    return None


async def read_status(client: BleakClient):
    """Read current device status."""
    print("\n--- Reading Status ---")

    # Read power status
    power_data = await client.read_gatt_char(POWER_CHAR_UUID)
    power_on = bool(power_data[0])
    print(f"Power: {'ON' if power_on else 'OFF'} (0x{power_data[0]:02x})")

    # Read mode
    mode_data = await client.read_gatt_char(MODE_CHAR_UUID)
    mode_byte = mode_data[0]
    mode_name = MODE_NAMES.get(mode_byte, "Unknown")
    mode_hex = " ".join(f"0x{b:02x}" for b in mode_data)
    print(f"Mode: {mode_name} ({mode_hex})")


async def test_power_control(client: BleakClient):
    """Test power on/off."""
    print("\n--- Testing Power Control ---")

    print("Turning OFF...")
    await client.write_gatt_char(POWER_CHAR_UUID, bytes([0x00]))
    await asyncio.sleep(2)
    await read_status(client)

    print("\nTurning ON...")
    await client.write_gatt_char(POWER_CHAR_UUID, bytes([0x01]))
    await asyncio.sleep(2)
    await read_status(client)


async def test_mode_control(client: BleakClient):
    """Test all mode changes."""
    print("\n--- Testing Mode Control ---")

    modes = [
        ("Auto", MODE_AUTO),
        ("Silent", MODE_SILENT),
        ("Standard", MODE_STANDARD),
        ("Strong", MODE_STRONG),
    ]

    for mode_name, mode_data in modes:
        print(f"\nSetting mode to {mode_name}...")
        await client.write_gatt_char(MODE_CHAR_UUID, mode_data)
        await asyncio.sleep(2)
        await read_status(client)


async def main():
    """Main test function."""
    print("=" * 60)
    print("Xiaomi Car Air Purifier BLE Test")
    print("=" * 60)

    # Scan for device
    device = await scan_for_device()
    if not device:
        print("\nPlease make sure:")
        print("  1. The purifier is powered on")
        print("  2. Bluetooth is enabled on this computer")
        print("  3. The purifier is in range")
        sys.exit(1)

    # Connect to device
    print(f"\nConnecting to {device.address}...")
    async with BleakClient(device.address) as client:
        if not client.is_connected:
            print("✗ Failed to connect")
            sys.exit(1)

        print("✓ Connected successfully")

        # Discover services
        print("\n--- Discovering Services ---")
        for service in client.services:
            if "FFD0" in service.uuid.upper():
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"  Characteristic: {char.uuid}")
                    print(f"    Properties: {char.properties}")

        # Read initial status
        await read_status(client)

        # Interactive menu
        while True:
            print("\n" + "=" * 60)
            print("Options:")
            print("  1. Read status")
            print("  2. Test power control")
            print("  3. Test mode control")
            print("  4. Power ON")
            print("  5. Power OFF")
            print("  6. Set mode: Auto")
            print("  7. Set mode: Silent")
            print("  8. Set mode: Standard")
            print("  9. Set mode: Strong")
            print("  0. Exit")
            print("=" * 60)

            choice = input("Select option: ").strip()

            if choice == "1":
                await read_status(client)
            elif choice == "2":
                await test_power_control(client)
            elif choice == "3":
                await test_mode_control(client)
            elif choice == "4":
                print("Turning ON...")
                await client.write_gatt_char(POWER_CHAR_UUID, bytes([0x01]))
                await asyncio.sleep(1)
                await read_status(client)
            elif choice == "5":
                print("Turning OFF...")
                await client.write_gatt_char(POWER_CHAR_UUID, bytes([0x00]))
                await asyncio.sleep(1)
                await read_status(client)
            elif choice == "6":
                print("Setting mode to Auto...")
                await client.write_gatt_char(MODE_CHAR_UUID, MODE_AUTO)
                await asyncio.sleep(1)
                await read_status(client)
            elif choice == "7":
                print("Setting mode to Silent...")
                await client.write_gatt_char(MODE_CHAR_UUID, MODE_SILENT)
                await asyncio.sleep(1)
                await read_status(client)
            elif choice == "8":
                print("Setting mode to Standard...")
                await client.write_gatt_char(MODE_CHAR_UUID, MODE_STANDARD)
                await asyncio.sleep(1)
                await read_status(client)
            elif choice == "9":
                print("Setting mode to Strong...")
                await client.write_gatt_char(MODE_CHAR_UUID, MODE_STRONG)
                await asyncio.sleep(1)
                await read_status(client)
            elif choice == "0":
                print("Exiting...")
                break
            else:
                print("Invalid option")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
