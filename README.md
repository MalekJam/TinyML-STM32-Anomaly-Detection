# EdgeGuard AI — Embedded Motion Anomaly Detection on STM32

**STM32F103 Blue Pill · STM32CubeMX · STM32CubeIDE · Embedded C/HAL · MPU6050 · Python · TinyML**


## Project status — Archived / discontinued

**Status:** Incomplete prototype · Hardware validation blocked · Development discontinued (November 2026)

This repository documents my attempt to build an STM32-based TinyML motion anomaly detector. I implemented the firmware structure, MPU6050 driver, streaming feature extraction, C inference logic, and Python training utilities. **I did not complete or validate the end-to-end system on physical hardware.**

I confirmed basic firmware execution and UART diagnostic output on my STM32F103 Blue Pill. However, communication with the MPU6050 remained blocked by a persistent I²C `BUSY` condition. I investigated the issue using STM32 HAL return codes, peripheral status flags, GPIO signal checks, and recovery attempts, but did not resolve it.

**What remains unverified:** reliable sensor acquisition; the complete firmware build from this repository snapshot; a neural-network model trained on real MPU6050 measurements; on-device TinyML inference; accuracy, latency, and memory measurements. The checked-in `model_generated.h` is a placeholder (`EDGEGUARD_MODEL_READY=0`), so the C code defaults to a **rule-based heuristic**, not a trained model. The `.ioc` file and CubeIDE-style sources are included, but STM32CubeMX code generation and installed STM32 HAL dependencies are required to produce a full buildable IDE project.

I have **stopped development** and am retaining the source and documentation as a learning record rather than a finished product. The project gave me hands-on experience with STM32CubeMX/CubeIDE, Embedded C, HAL, I²C, UART, sensor interfacing, on-device inference design, and hardware debugging. It is **not production-ready or hardware-validated**.

## Overview

EdgeGuard AI is an embedded edge-inference project built around an STM32F103C8T6 and a 6-axis MPU6050. The intended processing pipeline is: **I²C motion sampling at 100 Hz → 32-sample windows → 12 statistical features → compact autoencoder (12–8–12) → anomaly score → PC13 LED/UART alert**. Training is performed with Python/NumPy; inference is implemented directly in portable Embedded C. Before training on real measurements the firmware uses an explicitly labeled *heuristic*, not a neural network.

This repository is organized for **STM32CubeMX and STM32CubeIDE**, with a saved `.ioc` hardware configuration and `Core/Src` / `Core/Inc` HAL application layout. It also contains offline feature-processing and model-training code, a synthetic data generator, a serial capture utility, and architecture documentation. This repository snapshot does not include an automated test suite.

### Project progress

| Milestone | Current evidence |
|---|---|
| Blue Pill powered, STM32 firmware runs | UART boot messages observed in PuTTY |
| PC/laptop receives UART logs | **Verified** with USB-TTL on COM7 |
| ST-LINK flashing workflow | Firmware execution was observed; a reproducible build/flash log is not included |
| MPU6050 I²C device ID `0x68` | **Blocked**: I²C peripheral BUSY flag persists |
| Python/C driver and inference components | Source included; no automated tests included in this ZIP snapshot |
| Real-data training and physical anomaly detection | Not completed; development discontinued |
| Flash footprint and inference latency | Not measured |

## Technical references

- [STM32F103C8 product page](https://www.st.com/en/microcontrollers-microprocessors/stm32f103c8.html)
- [STM32CubeMX user manual](https://www.st.com/resource/en/user_manual/um1718-stm32cubemx-for-stm32-configuration-and-initialization-c-code-generation-stmicroelectronics.pdf)
- [STM32F103 medium-density errata (ES096)](https://www.st.com/resource/en/errata_sheet/es096-stm32f101x8b-stm32f102x8b-and-stm32f103x8b-mediumdensity-device-limitations-stmicroelectronics.pdf)
- [MPU6050 register map](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf)

MIT license. ST's firmware packages and proprietary toolchains are installed separately, not redistributed.
