"""Constants for the Xiaomi Car Air Purifier integration."""

DOMAIN = "xiaomi_car_air_purifier"

# BLE Service UUIDs - Confirmed through reverse engineering
SERVICE_UUID = "0000FFD0-0000-1000-8000-00805F9B34FB"
POWER_CHAR_UUID = "0000FFD1-0000-1000-8000-00805F9B34FB"  # Power control (Read/Write)
MODE_CHAR_UUID = "0000FFD3-0000-1000-8000-00805F9B34FB"   # Fan mode control (Read/Write)

# Power states
POWER_ON = bytes([0x01])
POWER_OFF = bytes([0x00])

# Device modes (4 bytes: [mode, 0x00, 0x0F, 0x18])
MODE_AUTO = bytes([0x00, 0x00, 0x0F, 0x18])      # Auto mode
MODE_SILENT = bytes([0x01, 0x00, 0x0F, 0x18])    # Silent mode
MODE_STANDARD = bytes([0x02, 0x00, 0x0F, 0x18])  # Standard mode
MODE_STRONG = bytes([0x03, 0x00, 0x0F, 0x18])    # Strong mode

# Mode mapping
MODE_NAMES = {
    0x00: "Auto",
    0x01: "Silent",
    0x02: "Standard",
    0x03: "Strong",
}

MODE_VALUES = {
    "Auto": MODE_AUTO,
    "Silent": MODE_SILENT,
    "Standard": MODE_STANDARD,
    "Strong": MODE_STRONG,
}

# Update interval
UPDATE_INTERVAL = 30  # seconds
DEFAULT_SCAN_INTERVAL = 30  # seconds

# Connection stability settings
MAX_RETRIES = 3  # Number of retries for operations
CONSECUTIVE_FAILURES_THRESHOLD = 5  # Number of consecutive failures before marking unavailable

# Configuration
CONF_MAC_ADDRESS = "mac_address"
CONF_SCAN_INTERVAL = "scan_interval"
