# Xiaomi Car Air Purifier - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License](https://img.shields.io/github/license/fooling/xiaomi-car-air-purifier)](LICENSE)

[English](#english) | [中文](#中文)

---

## English

Home Assistant custom component for Xiaomi Car Air Purifier via Bluetooth Low Energy (BLE).

### Features

- ✅ **Power Control**: Turn the purifier on/off
- ✅ **Mode Selection**: Auto, Silent, Standard, Strong modes
- ✅ **Real-time Status**: Monitor current power state and operating mode
- ✅ **Native BLE**: Uses Home Assistant's built-in Bluetooth integration
- ✅ **Easy Setup**: Automatic device discovery via config flow

### Requirements

- Home Assistant 2023.1 or newer
- Bluetooth adapter with BLE support
- Python 3.10+
- `bleak>=0.19.0` (installed automatically)

### Installation

#### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/fooling/xiaomi-car-air-purifier`
6. Select category: "Integration"
7. Click "Add"
8. Search for "Xiaomi Car Air Purifier"
9. Click "Install"
10. Restart Home Assistant

#### Manual Installation

1. Copy the `custom_components/xiaomi_car_air_purifier` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add the integration via the UI

### Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Xiaomi Car Air Purifier"
4. Select your device from the discovered list
5. Click **Submit**

The integration will automatically create:
- **Fan entity**: Control power and modes
- **Switch entity**: Simple on/off control
- **Sensor entity**: Display current mode

### Usage

#### Via Home Assistant UI

Control your purifier from the Devices page or add it to your dashboard:

```yaml
type: entities
entities:
  - entity: fan.xiaomi_car_air_purifier
  - entity: switch.xiaomi_car_air_purifier_power
  - entity: sensor.xiaomi_car_air_purifier_mode
```

#### Via Automations

```yaml
automation:
  - alias: "Turn on purifier when car door opens"
    trigger:
      - platform: state
        entity_id: binary_sensor.car_door
        to: "on"
    action:
      - service: fan.turn_on
        target:
          entity_id: fan.xiaomi_car_air_purifier
        data:
          preset_mode: "Auto"
```

### Available Modes

| Mode | Description |
|------|-------------|
| **Auto** | Automatically adjusts based on air quality |
| **Silent** | Ultra-low noise, ideal for sleeping |
| **Standard** | Balanced purification and noise level |
| **Strong** | Maximum purification efficiency |

### Troubleshooting

**Device not found**
- Ensure Bluetooth is enabled on your Home Assistant host
- Make sure the purifier is powered on and in range
- Try restarting the purifier

**Connection fails**
- Check if another device is connected to the purifier
- Restart Home Assistant's Bluetooth service
- Check logs: Settings → System → Logs

**Intermittent disconnections**
- Improve Bluetooth signal strength
- Reduce distance between Home Assistant and purifier
- Check for BLE interference from other devices

### Protocol Documentation

For developers interested in the BLE protocol, see [docs/protocol_reverse_engineering.md](docs/protocol_reverse_engineering.md).

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments

- Inspired by [em1003](https://github.com/fooling/em1003) integration
- Thanks to the Home Assistant community

### Related Projects

- [em1003](https://github.com/fooling/em1003) - Bluetooth EM1003 sensor integration

---

## 中文

小米车载空气净化器的 Home Assistant 自定义组件，通过低功耗蓝牙 (BLE) 连接。

### 功能特性

- ✅ **电源控制**：开关净化器
- ✅ **模式选择**：自动、静音、标准、超强模式
- ✅ **实时状态**：监控当前电源状态和工作模式
- ✅ **原生 BLE**：使用 Home Assistant 内置蓝牙集成
- ✅ **简单设置**：通过配置流程自动发现设备

### 系统要求

- Home Assistant 2023.1 或更新版本
- 支持 BLE 的蓝牙适配器
- Python 3.10+
- `bleak>=0.19.0`（自动安装）

### 安装方法

#### 通过 HACS 安装（推荐）

1. 在 Home Assistant 中打开 HACS
2. 点击"集成"
3. 点击右上角的三个点
4. 选择"自定义存储库"
5. 添加此仓库 URL：`https://github.com/fooling/xiaomi-car-air-purifier`
6. 选择类别："Integration"
7. 点击"添加"
8. 搜索"Xiaomi Car Air Purifier"
9. 点击"安装"
10. 重启 Home Assistant

#### 手动安装

1. 将 `custom_components/xiaomi_car_air_purifier` 目录复制到 Home Assistant 的 `custom_components` 目录
2. 重启 Home Assistant
3. 通过 UI 添加集成

### 配置

1. 进入 **设置** → **设备与服务**
2. 点击 **+ 添加集成**
3. 搜索"Xiaomi Car Air Purifier"
4. 从发现列表中选择您的设备
5. 点击 **提交**

集成将自动创建：
- **风扇实体**：控制电源和模式
- **开关实体**：简单的开关控制
- **传感器实体**：显示当前模式

### 使用方法

#### 通过 Home Assistant UI

从设备页面控制净化器，或将其添加到仪表板：

```yaml
type: entities
entities:
  - entity: fan.xiaomi_car_air_purifier
  - entity: switch.xiaomi_car_air_purifier_power
  - entity: sensor.xiaomi_car_air_purifier_mode
```

#### 通过自动化

```yaml
automation:
  - alias: "车门打开时启动净化器"
    trigger:
      - platform: state
        entity_id: binary_sensor.car_door
        to: "on"
    action:
      - service: fan.turn_on
        target:
          entity_id: fan.xiaomi_car_air_purifier
        data:
          preset_mode: "Auto"
```

### 可用模式

| 模式 | 说明 |
|------|------|
| **Auto（自动）** | 根据空气质量自动调节 |
| **Silent（静音）** | 超低噪音，适合睡眠 |
| **Standard（标准）** | 平衡净化效果和噪音 |
| **Strong（超强）** | 最大净化效率 |

### 故障排除

**找不到设备**
- 确保 Home Assistant 主机已启用蓝牙
- 确保净化器已开机且在范围内
- 尝试重启净化器

**连接失败**
- 检查是否有其他设备连接到净化器
- 重启 Home Assistant 的蓝牙服务
- 查看日志：设置 → 系统 → 日志

**间歇性断开连接**
- 改善蓝牙信号强度
- 减少 Home Assistant 与净化器之间的距离
- 检查其他设备的 BLE 干扰

### 协议文档

对于对 BLE 协议感兴趣的开发者，请参阅 [docs/protocol_reverse_engineering.md](docs/protocol_reverse_engineering.md)。

### 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

### 许可证

本项目采用 GPL-3.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

### 致谢

- 受 [em1003](https://github.com/fooling/em1003) 集成启发
- 感谢 Home Assistant 社区

### 相关项目

- [em1003](https://github.com/fooling/em1003) - 蓝牙 EM1003 传感器集成
