# Xiaomi Car Air Purifier BLE Protocol - Reverse Engineering Documentation

## 目录 / Table of Contents

- [设备信息 / Device Information](#设备信息--device-information)
- [BLE 服务和特征 / BLE Services and Characteristics](#ble-服务和特征--ble-services-and-characteristics)
- [协议格式 / Protocol Format](#协议格式--protocol-format)
- [命令列表 / Command List](#命令列表--command-list)
- [数据解析 / Data Parsing](#数据解析--data-parsing)
- [逆向工程过程 / Reverse Engineering Process](#逆向工程过程--reverse-engineering-process)
- [待完善 / TODO](#待完善--todo)

---

## 设备信息 / Device Information

### 基本信息 / Basic Information

- **产品名称 / Product Name**: Xiaomi Car Air Purifier (小米车载空气净化器)
- **型号 / Model**: [待填写 / To be filled]
- **制造商 / Manufacturer**: Xiaomi (小米)
- **BLE 设备名称 / BLE Device Name**: `MI-CAR-*` (pattern)

### 支持的功能 / Supported Features

- ✅ 电源控制 / Power Control (On/Off)
- ✅ 工作模式切换 / Mode Switching (Auto/Sleep/Favorite/Strong)
- ✅ 风速调节 / Fan Speed Control (3 levels)
- ✅ 环境传感器读取 / Environmental Sensors
  - PM2.5 浓度 / PM2.5 Concentration
  - 温度 / Temperature
  - 湿度 / Humidity

---

## BLE 服务和特征 / BLE Services and Characteristics

### 主要服务 UUID / Primary Service UUID

```
Service UUID: 0000FFD0-0000-1000-8000-00805F9B34FB
```

> **已确认 / Confirmed**: 所有控制操作都在此服务中进行。
> All control operations are performed within this service.

### 特征值 / Characteristics

| 特征 / Characteristic | UUID | 属性 / Properties | 用途 / Purpose |
|---------------------|------|------------------|---------------|
| Power Control | `0xFFD1` | Read, Write | 电源开关控制 / Power on/off control |
| Fan Mode Control | `0xFFD3` | Read, Write | 风扇模式/风速控制 / Fan mode/speed control |

> **✅ 已验证 / Verified**: 上述UUID已通过实际设备测试确认。
> The above UUIDs have been confirmed through actual device testing.

---

## 协议格式 / Protocol Format

### 协议特点 / Protocol Characteristics

小米车载空气净化器使用**直接读写特征值**的方式进行控制，无需复杂的命令序列。
The Xiaomi Car Air Purifier uses **direct characteristic read/write** for control, without complex command sequences.

- **读取状态 / Read Status**: 直接读取对应特征值 / Directly read the characteristic
- **设置状态 / Set Status**: 直接写入对应特征值 / Directly write to the characteristic
- **无需序列号 / No Sequence Required**: 不需要维护命令序列号 / No need to maintain command sequence numbers

---

## 控制接口 / Control Interface

### 1. 电源控制 / Power Control

**特征值 UUID / Characteristic UUID**: `0xFFD1`

#### 读取电源状态 / Read Power Status

```python
# 读取特征值 / Read characteristic
value = await client.read_gatt_char("0000FFD1-0000-1000-8000-00805F9B34FB")
```

**返回值 / Return Value**:
- `0x01`: 开机 / Power On
- `0x00`: 关机 / Power Off

#### 设置电源状态 / Set Power Status

```python
# 开机 / Power On
await client.write_gatt_char("0000FFD1-0000-1000-8000-00805F9B34FB", bytes([0x01]))

# 关机 / Power Off
await client.write_gatt_char("0000FFD1-0000-1000-8000-00805F9B34FB", bytes([0x00]))
```

---

### 2. 模式控制 / Mode Control

**特征值 UUID / Characteristic UUID**: `0xFFD3`

#### 读取工作模式 / Read Working Mode

```python
# 读取特征值 / Read characteristic (4 bytes)
value = await client.read_gatt_char("0000FFD3-0000-1000-8000-00805F9B34FB")
# 返回格式 / Return format: [MODE, 0x00, 0x0F, 0x18]
```

**返回值 / Return Value**:

| 字节 / Bytes | 模式 / Mode | 说明 / Description |
|-------------|------------|-------------------|
| `0x00 0x00 0x0F 0x18` | Auto / 自动 | 根据空气质量自动调节 / Adjust based on air quality |
| `0x01 0x00 0x0F 0x18` | Silent / 静音 | 低噪音模式，适合睡眠 / Low noise, suitable for sleep |
| `0x02 0x00 0x0F 0x18` | Standard / 标准 | 标准净化模式 / Standard purification mode |
| `0x03 0x00 0x0F 0x18` | Strong / 超强 | 最大风速模式，快速净化 / Maximum speed, fast purification |

#### 设置工作模式 / Set Working Mode

```python
# 设置为自动模式 / Set to Auto mode
await client.write_gatt_char("0000FFD3-0000-1000-8000-00805F9B34FB", bytes([0x00, 0x00, 0x0F, 0x18]))

# 设置为静音模式 / Set to Silent mode
await client.write_gatt_char("0000FFD3-0000-1000-8000-00805F9B34FB", bytes([0x01, 0x00, 0x0F, 0x18]))

# 设置为标准模式 / Set to Standard mode
await client.write_gatt_char("0000FFD3-0000-1000-8000-00805F9B34FB", bytes([0x02, 0x00, 0x0F, 0x18]))

# 设置为超强模式 / Set to Strong mode
await client.write_gatt_char("0000FFD3-0000-1000-8000-00805F9B34FB", bytes([0x03, 0x00, 0x0F, 0x18]))
```

---

### 模式对照表 / Mode Mapping Table

| 第一字节 / Byte 0 | 模式名称 / Mode Name | 中文名称 | 特点 / Features |
|------------------|---------------------|---------|---------------|
| `0x00` | Auto | 自动模式 | 智能调节风速 / Smart speed adjustment |
| `0x01` | Silent | 静音模式 | 超低噪音 / Ultra-low noise |
| `0x02` | Standard | 标准模式 | 平衡净化和噪音 / Balance purification and noise |
| `0x03` | Strong | 超强模式 | 最大净化效率 / Maximum purification efficiency |

**注意 / Note**: 后三个字节 `0x00 0x0F 0x18` 在所有模式中保持不变，可能是设备的固定参数。
The last three bytes `0x00 0x0F 0x18` remain constant across all modes, likely device-specific parameters.

---

## 完整示例代码 / Complete Example Code

### Python + Bleak 示例 / Python + Bleak Example

```python
import asyncio
from bleak import BleakClient, BleakScanner

# UUIDs
SERVICE_UUID = "0000FFD0-0000-1000-8000-00805F9B34FB"
POWER_CHAR_UUID = "0000FFD1-0000-1000-8000-00805F9B34FB"
MODE_CHAR_UUID = "0000FFD3-0000-1000-8000-00805F9B34FB"

# Mode constants
MODE_AUTO = bytes([0x00, 0x00, 0x0F, 0x18])
MODE_SILENT = bytes([0x01, 0x00, 0x0F, 0x18])
MODE_STANDARD = bytes([0x02, 0x00, 0x0F, 0x18])
MODE_STRONG = bytes([0x03, 0x00, 0x0F, 0x18])


async def main():
    # 扫描设备 / Scan for device
    print("Scanning for Xiaomi Car Air Purifier...")
    devices = await BleakScanner.discover()
    device = None

    for d in devices:
        if d.name and "MI-CAR" in d.name.upper():
            device = d
            print(f"Found device: {d.name} ({d.address})")
            break

    if not device:
        print("Device not found!")
        return

    # 连接设备 / Connect to device
    async with BleakClient(device.address) as client:
        print(f"Connected: {client.is_connected}")

        # 读取电源状态 / Read power status
        power_value = await client.read_gatt_char(POWER_CHAR_UUID)
        print(f"Power status: {'ON' if power_value[0] == 0x01 else 'OFF'}")

        # 读取模式 / Read mode
        mode_value = await client.read_gatt_char(MODE_CHAR_UUID)
        mode_map = {0x00: "Auto", 0x01: "Silent", 0x02: "Standard", 0x03: "Strong"}
        print(f"Current mode: {mode_map.get(mode_value[0], 'Unknown')}")

        # 开机 / Power on
        print("Turning on...")
        await client.write_gatt_char(POWER_CHAR_UUID, bytes([0x01]))
        await asyncio.sleep(1)

        # 设置为自动模式 / Set to auto mode
        print("Setting to Auto mode...")
        await client.write_gatt_char(MODE_CHAR_UUID, MODE_AUTO)
        await asyncio.sleep(1)

        # 设置为超强模式 / Set to strong mode
        print("Setting to Strong mode...")
        await client.write_gatt_char(MODE_CHAR_UUID, MODE_STRONG)
        await asyncio.sleep(2)

        # 关机 / Power off
        print("Turning off...")
        await client.write_gatt_char(POWER_CHAR_UUID, bytes([0x00]))


if __name__ == "__main__":
    asyncio.run(main())
```

### Home Assistant 集成示例 / Home Assistant Integration Example

参考本项目的 `custom_components/xiaomi_car_air_purifier/` 目录获取完整的 Home Assistant 集成实现。
Refer to the `custom_components/xiaomi_car_air_purifier/` directory in this project for the complete Home Assistant integration implementation.

---

## 逆向工程过程 / Reverse Engineering Process

### 工具 / Tools Used

1. **nRF Connect** (Android/iOS)
   - 用于扫描BLE设备和查看服务特征
   - For scanning BLE devices and viewing service characteristics

2. **Wireshark** + **Android HCI Snoop**
   - 抓取BLE通信数据包
   - Capture BLE communication packets

3. **Python + Bleak**
   - 编写测试脚本进行协议验证
   - Write test scripts for protocol validation

### 逆向步骤 / Reverse Engineering Steps

#### 第一步：设备发现 / Step 1: Device Discovery

```bash
# 使用 bluetoothctl 扫描设备
bluetoothctl scan on

# 或使用 Python + Bleak
python3 -m bleak scan
```

寻找设备名称包含 "MI-CAR" 的设备。
Look for devices with names containing "MI-CAR".

#### 第二步：服务枚举 / Step 2: Service Enumeration

使用 nRF Connect 连接到设备并记录：
Use nRF Connect to connect to the device and record:

1. 所有服务 UUID / All service UUIDs
2. 每个服务下的特征值 UUID / Characteristic UUIDs under each service
3. 特征值的属性（Read/Write/Notify）/ Characteristic properties

#### 第三步：抓包分析 / Step 3: Packet Capture Analysis

1. 在 Android 设备上启用 **Developer Options → Enable Bluetooth HCI snoop log**
2. 使用官方小米 App 控制设备
3. 收集 HCI 日志文件（通常在 `/sdcard/Android/data/btsnoop_hci.log`）
4. 使用 Wireshark 打开并过滤 ATT 协议数据包

关键操作与数据包对照：
Key operations and packet mapping:

| 操作 / Operation | 观察到的数据包 / Observed Packets |
|-----------------|--------------------------------|
| 开机 / Power On | [待抓取 / To be captured] |
| 关机 / Power Off | [待抓取 / To be captured] |
| 切换模式 / Change Mode | [待抓取 / To be captured] |
| 调节风速 / Adjust Speed | [待抓取 / To be captured] |
| 读取状态 / Read Status | [待抓取 / To be captured] |

#### 第四步：协议验证 / Step 4: Protocol Validation

使用 Python 脚本验证逆向出的协议：

```python
import asyncio
from bleak import BleakClient

async def test_protocol():
    address = "XX:XX:XX:XX:XX:XX"  # Device MAC address

    async with BleakClient(address) as client:
        # Subscribe to notifications
        await client.start_notify(NOTIFY_UUID, notification_handler)

        # Test command: Get status
        await client.write_gatt_char(WRITE_UUID, bytes([0x01, 0x01]))
        await asyncio.sleep(2)

        # Test command: Power on
        await client.write_gatt_char(WRITE_UUID, bytes([0x02, 0x02]))
        await asyncio.sleep(2)

asyncio.run(test_protocol())
```

---

## 待完善 / TODO

### 已完成 / Completed

- [x] ✅ 确认 BLE Service UUID: `0xFFD0`
- [x] ✅ 确认 Power Control Characteristic: `0xFFD1`
- [x] ✅ 确认 Fan Mode Control Characteristic: `0xFFD3`
- [x] ✅ 验证电源控制协议
- [x] ✅ 验证模式控制协议（4种模式）

### 待完善 / TODO

#### 高优先级 / High Priority

- [ ] 研究是否有传感器数据读取功能（PM2.5、温度、湿度等）
- [ ] 测试设备是否支持 Notify 功能（主动推送状态变化）
- [ ] 研究后三字节 `0x00 0x0F 0x18` 的具体含义
- [ ] 测试异常情况下的设备响应

#### 中优先级 / Medium Priority

- [ ] 研究是否有滤芯寿命查询功能
- [ ] 研究是否有设备信息查询（固件版本、序列号等）
- [ ] 测试设备是否有加密或认证机制
- [ ] 添加更多 BLE 扫描和连接的最佳实践

#### 低优先级 / Low Priority

- [ ] 研究设备是否支持 OTA 升级
- [ ] 研究是否有儿童锁功能
- [ ] 研究是否有定时开关机功能
- [ ] 添加抓包分析的详细截图和步骤

---

## 贡献 / Contributing

如果您发现了新的命令或协议细节，欢迎提交 Pull Request 或 Issue！
If you discover new commands or protocol details, feel free to submit a Pull Request or Issue!

### 提交格式 / Submission Format

```markdown
### 新发现的命令 / Newly Discovered Command

**功能 / Function**: [描述 / Description]

**命令 / Command**:
Hex: [命令字节 / Command bytes]

Example: [示例 / Example]


**响应 / Response**:
Hex: [响应字节 / Response bytes]

Example: [示例 / Example]


**验证方法 / Verification Method**:
[如何验证这个命令 / How to verify this command]
```

---

## 免责声明 / Disclaimer

本文档仅供学习和研究目的。使用本文档中的信息所造成的任何后果，作者不承担任何责任。
This document is for educational and research purposes only. The author assumes no responsibility for any consequences resulting from the use of information in this document.

请遵守当地法律法规，不要将逆向工程用于非法目的。
Please comply with local laws and regulations, and do not use reverse engineering for illegal purposes.

---

## 参考资料 / References

- [Bleak - Python BLE Library](https://github.com/hbldh/bleak)
- [nRF Connect for Mobile](https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-mobile)
- [Wireshark Bluetooth HCI Analysis](https://wiki.wireshark.org/Bluetooth)
- [Home Assistant BLE Integration](https://www.home-assistant.io/integrations/bluetooth/)

---

**文档版本 / Document Version**: 0.1.0
**最后更新 / Last Updated**: 2024-11-01
**维护者 / Maintainer**: @fooling
