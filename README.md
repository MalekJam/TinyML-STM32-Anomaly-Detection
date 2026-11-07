# EdgeGuard AI — Embedded Motion Anomaly Detection on STM32

**STM32F103 Blue Pill · STM32CubeMX · STM32CubeIDE · Embedded C/HAL · MPU6050 · Python · TinyML**


## Overview

EdgeGuard AI is an embedded edge-inference project built around an STM32F103C8T6 and a 6-axis MPU6050. The intended processing pipeline is: **I²C motion sampling at 100 Hz → 32-sample windows → 12 statistical features → compact autoencoder (12–8–12) → anomaly score → PC13 LED/UART alert**. Training is performed with Python/NumPy; inference is implemented directly in portable Embedded C. Before training on real measurements the firmware uses an explicitly labeled *heuristic*, not a neural network.

This repository is organized for **STM32CubeMX and STM32CubeIDE**, with a saved `.ioc` hardware configuration and `Core/Src` / `Core/Inc` HAL application layout. It also contains a host-side test harness, synthetic data generator, serial capture utility and architectural documentation.

### Project progress

| Milestone | Current evidence |
|---|---|
| Blue Pill powered, STM32 firmware runs | UART boot messages observed in PuTTY |
| PC/laptop receives UART logs | **Verified** with USB-TTL on COM7 |
| ST-LINK flashing workflow | Firmware ran after programming; keep your own flash log for a documented pass |
| MPU6050 I²C device ID `0x68` | **Blocked**: I²C peripheral BUSY flag persists |
| Python/C driver and inference components | **Host tests pass** (not an STM32 target build) |
| Real-data training and physical anomaly detection | Not yet verified |
| Flash footprint and inference latency | Not yet measured |

## Technical references

- [STM32F103C8 product page](https://www.st.com/en/microcontrollers-microprocessors/stm32f103c8.html)
- [STM32CubeMX user manual](https://www.st.com/resource/en/user_manual/um1718-stm32cubemx-for-stm32-configuration-and-initialization-c-code-generation-stmicroelectronics.pdf)
- [STM32F103 medium-density errata (ES096)](https://www.st.com/resource/en/errata_sheet/es096-stm32f101x8b-stm32f102x8b-and-stm32f103x8b-mediumdensity-device-limitations-stmicroelectronics.pdf)
- [MPU6050 register map](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf)

MIT license. ST's firmware packages and proprietary toolchains are installed separately, not redistributed.
