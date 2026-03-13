/*
 * SPDX-FileCopyrightText: 2010-2022 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: CC0-1.0
 */

#include <stdio.h>
#include <inttypes.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_chip_info.h"
#include "esp_flash.h"
#include "esp_system.h"
#include "esp_psram.h"
#include "esp_heap_caps.h"

void app_main(void)
{
    printf("\n--- TinyBit Hardware Diagnostic ---\n");

    /* 1. Chip Info */
    esp_chip_info_t chip_info;
    esp_chip_info(&chip_info);
    printf("Chip: %s (rev %d.%d), Cores: %d\n", 
           CONFIG_IDF_TARGET, chip_info.revision / 100, chip_info.revision % 100, chip_info.cores);

    /* 2. Flash Info */
    uint32_t flash_size;
    if(esp_flash_get_size(NULL, &flash_size) == ESP_OK) {
        printf("Flash size: %" PRIu32 " MB (%s)\n", flash_size / (1024 * 1024),
               (chip_info.features & CHIP_FEATURE_EMB_FLASH) ? "embedded" : "external");
    }

    /* 3. PSRAM Info */
    size_t psram_size = esp_psram_get_size();
    if (psram_size > 0) {
        printf("PSRAM size: %d MB (Detected! ✅)\n", (int)(psram_size / (1024 * 1024)));
    } else {
        printf("PSRAM size: 0 MB (Not Detected ❌)\n");
    }

    /* 4. Memory/Heap Info */
    printf("\n--- Memory Status ---\n");
    printf("Internal RAM free: %u bytes\n", (unsigned int)heap_caps_get_free_size(MALLOC_CAP_INTERNAL));
    if (psram_size > 0) {
        printf("External PSRAM free: %u bytes\n", (unsigned int)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
    }
    printf("Min free heap: %" PRIu32 " bytes\n", esp_get_minimum_free_heap_size());

    printf("\nStarting TinyBit experiments in 5s...\n");
    for (int i = 5; i >= 0; i--) {
        printf("%d...", i);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
    printf("\nRestarting...\n");
    fflush(stdout);
    esp_restart();
}
