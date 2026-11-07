#ifndef EDGEGUARD_APP_H
#define EDGEGUARD_APP_H
#include "stm32f1xx_hal.h"

/* High-level application entry points called from CubeMX USER CODE blocks.
 * Leave pin setup and peripheral initialization to CubeMX-generated code. */
void EdgeGuard_AppInit(I2C_HandleTypeDef *i2c, UART_HandleTypeDef *uart);
void EdgeGuard_AppTick(void);
#endif
