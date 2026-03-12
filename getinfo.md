python3 -m esptool --port /dev/cu.usbmodem1421301 flash_id
Warning: Deprecated: Command 'flash_id' is deprecated. Use 'flash-id' instead.
esptool v5.2.0
Connected to ESP32-S3 on /dev/cu.usbmodem1421301:
Chip type:          ESP32-S3 (QFN56) (revision v0.2)
Features:           Wi-Fi, BT 5 (LE), Dual Core + LP Core, 240MHz, Embedded PSRAM 8MB (AP_3v3)
Crystal frequency:  40MHz
USB mode:           USB-Serial/JTAG
MAC:                94:a9:90:27:35:1c

Stub flasher running.

Flash Memory Information:
=========================
Manufacturer: 46
Device: 4018
Detected flash size: 16MB
Flash type set in eFuse: quad (4 data lines)
Flash voltage set by eFuse: 3.3V
立創實戰派規格確認：16MB Flash + 8MB PSRAM。
無名nologo規格
python3 -m esptool --port /dev/cu.usbmodem142101 flash-id
esptool v5.2.0
Connected to ESP32-S3 on /dev/cu.usbmodem142101:
Chip type:          ESP32-S3 (QFN56) (revision v0.2)
Features:           Wi-Fi, BT 5 (LE), Dual Core + LP Core, 240MHz, Embedded PSRAM 8MB (AP_3v3)
Crystal frequency:  40MHz
USB mode:           USB-Serial/JTAG
MAC:                94:a9:90:1b:69:68

Stub flasher running.

Flash Memory Information:
=========================
Manufacturer: ef
Device: 4018
Detected flash size: 16MB
Flash type set in eFuse: quad (4 data lines)
Flash voltage set by eFuse: 3.3V

Hard resetting via RTS pin...


ESP-ROM:esp32s3-20210327
Build:Mar 27 2021
rst:0xc (RTC_SW_CPU_RST),boot:0x2b (SPI_FAST_FLASH_BOOT)
Saved PC:0x40378fdc
--- 0x40378fdc: esp_restart_noos at /Users/sam/esp/esp-idf/components/esp_system/port/soc/esp32s3/system_internal.c:164
SPIWP:0xee
mode:DIO, clock div:1
load:0x3fce2820,len:0x14f0
load:0x403c8700,len:0xd24
--- 0x403c8700: _stext at ??:?
load:0x403cb700,len:0x2ef0
entry 0x403c8924
--- 0x403c8924: call_start_cpu0 at /Users/sam/esp/esp-idf/components/bootloader/subproject/main/bootloader_start.c:27
I (24) boot: ESP-IDF v5.5.3 2nd stage bootloader
I (24) boot: compile time Mar 12 2026 15:35:13
I (24) boot: Multicore bootloader
I (25) boot: chip revision: v0.2
I (27) boot: efuse block revision: v1.3
I (31) boot.esp32s3: Boot SPI Speed : 80MHz
I (35) boot.esp32s3: SPI Mode       : DIO
I (38) boot.esp32s3: SPI Flash Size : 2MB
I (42) boot: Enabling RNG early entropy source...
I (47) boot: Partition Table:
I (49) boot: ## Label            Usage          Type ST Offset   Length
I (55) boot:  0 nvs              WiFi data        01 02 00009000 00006000
I (62) boot:  1 phy_init         RF data          01 01 0000f000 00001000
I (68) boot:  2 factory          factory app      00 00 00010000 00100000
I (75) boot: End of partition table
I (78) esp_image: segment 0: paddr=00010020 vaddr=3c010020 size=077dch ( 30684) map
I (91) esp_image: segment 1: paddr=00017804 vaddr=3fc91e00 size=02cc0h ( 11456) load
I (95) esp_image: segment 2: paddr=0001a4cc vaddr=40374000 size=05b4ch ( 23372) load
I (106) esp_image: segment 3: paddr=00020020 vaddr=42000020 size=0f4b0h ( 62640) map
I (119) esp_image: segment 4: paddr=0002f4d8 vaddr=40379b4c size=08254h ( 33364) load
I (127) esp_image: segment 5: paddr=00037734 vaddr=50000000 size=00020h (    32) load
I (133) boot: Loaded app from partition at offset 0x10000
I (133) boot: Disabling RNG early entropy source...
I (144) cpu_start: Multicore app
I (153) cpu_start: GPIO 44 and 43 are used as console UART I/O pins
I (154) cpu_start: Pro cpu start user code
I (154) cpu_start: cpu freq: 160000000 Hz
I (155) app_init: Application information:
I (159) app_init: Project name:     hello_world
I (164) app_init: App version:      1
I (167) app_init: Compile time:     Mar 12 2026 15:34:53
I (172) app_init: ELF file SHA256:  65dde598e...
I (176) app_init: ESP-IDF:          v5.5.3
I (180) efuse_init: Min chip rev:     v0.0
I (184) efuse_init: Max chip rev:     v0.99 
I (188) efuse_init: Chip rev:         v0.2
I (192) heap_init: Initializing. RAM available for dynamic allocation:
I (198) heap_init: At 3FC95308 len 00054408 (337 KiB): RAM
I (203) heap_init: At 3FCE9710 len 00005724 (21 KiB): RAM
I (208) heap_init: At 3FCF0000 len 00008000 (32 KiB): DRAM
I (214) heap_init: At 600FE000 len 00001FE8 (7 KiB): RTCRAM
I (219) spi_flash: detected chip: winbond
I (223) spi_flash: flash io: dio
W (226) spi_flash: Detected size(16384k) larger than the size in the binary image header(2048k). Using the size in the binary image header.
I (238) sleep_gpio: Configure to isolate all GPIO pins in sleep state
I (244) sleep_gpio: Enable automatic switching of GPIO sleep configuration
I (251) main_task: Started on CPU0
I (261) main_task: Calling app_main()
Hello world!
This is esp32s3 chip with 2 CPU core(s), WiFi/BLE, silicon revision v0.2, 2MB external flash
Minimum free heap size: 392240 bytes

Flash 被限制了：硬體有 16MB，但軟體只用了 2MB（Detected size(16384k) larger than the size in the binary image header(2048k)）。


我正在幫你進行「硬體解鎖」
我已經建立了一個 sdkconfig.defaults 檔案，並正在重新編譯專案。這個配置會：

啟用 8MB OPI PSRAM（Octal SPI，最高速模式）。
啟用 16MB Flash。
將 CPU 時脈拉到 240MHz（原本是 160MHz）。

修改後
ESP-ROM:esp32s3-20210327
Build:Mar 27 2021
rst:0xc (RTC_SW_CPU_RST),boot:0x2b (SPI_FAST_FLASH_BOOT)
Saved PC:0x40378b64
--- 0x40378b64: esp_restart_noos at /Users/sam/esp/esp-idf/components/esp_system/port/soc/esp32s3/system_internal.c:164
SPIWP:0xee
mode:DIO, clock div:1
load:0x3fce2820,len:0x14f0
load:0x403c8700,len:0xd24
--- 0x403c8700: _stext at ??:?
load:0x403cb700,len:0x2ef0
entry 0x403c8924
--- 0x403c8924: call_start_cpu0 at /Users/sam/esp/esp-idf/components/bootloader/subproject/main/bootloader_start.c:27
I (24) boot: ESP-IDF v5.5.3 2nd stage bootloader
I (24) boot: compile time Mar 12 2026 15:40:44
I (24) boot: Multicore bootloader
I (25) boot: chip revision: v0.2
I (27) boot: efuse block revision: v1.3
I (31) boot.esp32s3: Boot SPI Speed : 80MHz
I (35) boot.esp32s3: SPI Mode       : DIO
I (38) boot.esp32s3: SPI Flash Size : 16MB
I (42) boot: Enabling RNG early entropy source...
I (47) boot: Partition Table:
I (49) boot: ## Label            Usage          Type ST Offset   Length
I (56) boot:  0 nvs              WiFi data        01 02 00009000 00006000
I (62) boot:  1 phy_init         RF data          01 01 0000f000 00001000
I (69) boot:  2 factory          factory app      00 00 00010000 00100000
I (75) boot: End of partition table
I (78) esp_image: segment 0: paddr=00010020 vaddr=3c010020 size=074cch ( 29900) map
I (91) esp_image: segment 1: paddr=000174f4 vaddr=3fc90f00 size=02b94h ( 11156) load
I (95) esp_image: segment 2: paddr=0001a090 vaddr=40374000 size=05f88h ( 24456) load
I (106) esp_image: segment 3: paddr=00020020 vaddr=42000020 size=0e95ch ( 59740) map
I (119) esp_image: segment 4: paddr=0002e984 vaddr=40379f88 size=06ed8h ( 28376) load
I (125) esp_image: segment 5: paddr=00035864 vaddr=50000000 size=00020h (    32) load
I (131) boot: Loaded app from partition at offset 0x10000
I (131) boot: Disabling RNG early entropy source...
I (144) cpu_start: Multicore app
I (153) cpu_start: GPIO 44 and 43 are used as console UART I/O pins
I (154) cpu_start: Pro cpu start user code
I (154) cpu_start: cpu freq: 240000000 Hz
I (155) app_init: Application information:
I (159) app_init: Project name:     hello_world
I (164) app_init: App version:      1
I (167) app_init: Compile time:     Mar 12 2026 15:40:15
I (172) app_init: ELF file SHA256:  0852e6e2b...
I (176) app_init: ESP-IDF:          v5.5.3
I (180) efuse_init: Min chip rev:     v0.0
I (184) efuse_init: Max chip rev:     v0.99 
I (188) efuse_init: Chip rev:         v0.2
I (192) heap_init: Initializing. RAM available for dynamic allocation:
I (198) heap_init: At 3FC942D8 len 00055438 (341 KiB): RAM
I (203) heap_init: At 3FCE9710 len 00005724 (21 KiB): RAM
I (208) heap_init: At 3FCF0000 len 00008000 (32 KiB): DRAM
I (214) heap_init: At 600FE000 len 00001FE8 (7 KiB): RTCRAM
I (219) spi_flash: detected chip: winbond
I (223) spi_flash: flash io: dio
I (226) sleep_gpio: Configure to isolate all GPIO pins in sleep state
I (232) sleep_gpio: Enable automatic switching of GPIO sleep configuration
I (239) main_task: Started on CPU0
I (249) main_task: Calling app_main()
Hello world!
This is esp32s3 chip with 2 CPU core(s), WiFi/BLE, silicon revision v0.2, 16MB external flash
Minimum free heap size: 396400 bytes
Restarting in 10 seconds...
Restarting in 9 seconds...
Restarting in 8 seconds...
Restarting in 7 seconds...
Restarting in 6 seconds...
Restarting in 5 seconds...
Restarting in 4 seconds...
Restarting in 3 seconds...
Restarting in 2 seconds...
Restarting in 1 seconds...
Restarting in 0 seconds...
Restarting now.
ESP-ROM:esp32s3-20210327
Build:Mar 27 2021
rst:0xc (RTC_SW_CPU_RST),boot:0x2b (SPI_FAST_FLASH_BOOT)
Saved PC:0x40378b64
--- 0x40378b64: esp_restart_noos at /Users/sam/esp/esp-idf/components/esp_system/port/soc/esp32s3/system_internal.c:164
SPIWP:0xee
mode:DIO, clock div:1
load:0x3fce2820,len:0x14f0
load:0x403c8700,len:0xd24
--- 0x403c8700: _stext at ??:?
load:0x403cb700,len:0x2ef0
entry 0x403c8924
--- 0x403c8924: call_start_cpu0 at /Users/sam/esp/esp-idf/components/bootloader/subproject/main/bootloader_start.c:27
I (24) boot: ESP-IDF v5.5.3 2nd stage bootloader
I (24) boot: compile time Mar 12 2026 15:40:44
I (24) boot: Multicore bootloader
I (25) boot: chip revision: v0.2
I (27) boot: efuse block revision: v1.3
I (31) boot.esp32s3: Boot SPI Speed : 80MHz
I (35) boot.esp32s3: SPI Mode       : DIO
I (38) boot.esp32s3: SPI Flash Size : 16MB
I (42) boot: Enabling RNG early entropy source...
I (47) boot: Partition Table:
I (49) boot: ## Label            Usage          Type ST Offset   Length
I (56) boot:  0 nvs              WiFi data        01 02 00009000 00006000
I (62) boot:  1 phy_init         RF data          01 01 0000f000 00001000
I (69) boot:  2 factory          factory app      00 00 00010000 00100000
I (75) boot: End of partition table
I (78) esp_image: segment 0: paddr=00010020 vaddr=3c010020 size=074cch ( 29900) map
I (91) esp_image: segment 1: paddr=000174f4 vaddr=3fc90f00 size=02b94h ( 11156) load
I (95) esp_image: segment 2: paddr=0001a090 vaddr=40374000 size=05f88h ( 24456) load
I (106) esp_image: segment 3: paddr=00020020 vaddr=42000020 size=0e95ch ( 59740) map
I (119) esp_image: segment 4: paddr=0002e984 vaddr=40379f88 size=06ed8h ( 28376) load
I (125) esp_image: segment 5: paddr=00035864 vaddr=50000000 size=00020h (    32) load
I (131) boot: Loaded app from partition at offset 0x10000
I (131) boot: Disabling RNG early entropy source...
I (144) cpu_start: Multicore app
I (153) cpu_start: GPIO 44 and 43 are used as console UART I/O pins
I (154) cpu_start: Pro cpu start user code
I (154) cpu_start: cpu freq: 240000000 Hz
I (155) app_init: Application information:
I (159) app_init: Project name:     hello_world
I (164) app_init: App version:      1
I (167) app_init: Compile time:     Mar 12 2026 15:40:15
I (172) app_init: ELF file SHA256:  0852e6e2b...
I (176) app_init: ESP-IDF:          v5.5.3
I (180) efuse_init: Min chip rev:     v0.0
I (184) efuse_init: Max chip rev:     v0.99 
I (188) efuse_init: Chip rev:         v0.2
I (192) heap_init: Initializing. RAM available for dynamic allocation:
I (198) heap_init: At 3FC942D8 len 00055438 (341 KiB): RAM
I (203) heap_init: At 3FCE9710 len 00005724 (21 KiB): RAM
I (208) heap_init: At 3FCF0000 len 00008000 (32 KiB): DRAM
I (214) heap_init: At 600FE000 len 00001FE8 (7 KiB): RTCRAM
I (219) spi_flash: detected chip: winbond
I (223) spi_flash: flash io: dio
I (226) sleep_gpio: Configure to isolate all GPIO pins in sleep state
I (232) sleep_gpio: Enable automatic switching of GPIO sleep configuration
I (239) main_task: Started on CPU0
I (249) main_task: Calling app_main()
Hello world!
This is esp32s3 chip with 2 CPU core(s), WiFi/BLE, silicon revision v0.2, 16MB external flash
Minimum free heap size: 396400 bytes