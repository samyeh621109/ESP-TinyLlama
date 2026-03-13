# TinyBit 第一天：環境建置指南

## 步驟一：確認你的板子規格（先接上 USB，1 分鐘）

```bash
# 安裝 esptool（用現有 python3）
pip3 install esptool

# 接上板子，然後確認裝置路徑
ls /dev/cu.*
# 通常是 /dev/cu.usbserial-XXXX 或 /dev/cu.wchusbserialXXXX

# 讀取晶片資訊（把 /dev/cu.XXXX 換成你的實際路徑）
esptool.py --port /dev/cu.XXXX flash_id
```

**記下輸出中的：**
- `Detected flash size:` → 你的 Flash 大小（8MB or 16MB）
- `Detected PSRAM:` → 你的 PSRAM（4MB / 8MB）

---

## 步驟二：安裝 ESP-IDF v5.3

```bash
# 建立工作目錄
mkdir -p ~/esp && cd ~/esp

# clone（只需 v5.3 tag，不需要全部 history，更快）
git clone --branch v5.3.1 --depth 1 --recurse-submodules \
  https://github.com/espressif/esp-idf.git

# 安裝工具鍊（會下載約 1GB，跑個 5-10 分鐘）
cd esp-idf
./install.sh esp32s3

# 設定環境變數（每次開新 terminal 都要跑）
. ./export.sh
```

> **提示：** 把 `. ~/esp/esp-idf/export.sh` 加進你的 `~/.zshrc`，就不用每次手動 source

---

## 步驟三：第一個 hello_world 測試

```bash
# 複製範例
cp -r $IDF_PATH/examples/get-started/hello_world ~/esp/hello_world
cd ~/esp/hello_world

# 設定目標晶片
idf.py set-target esp32s3

# 編譯
idf.py build

# 燒錄並監看（把 PORT 換成你的裝置路徑）
idf.py -p /dev/cu.XXXX flash monitor
```

看到 `Hello world!` 輸出就成功了。

---

## 步驟四：確認 PSRAM 是否啟用

```bash
# 修改 sdkconfig 啟用 PSRAM
idf.py menuconfig
# 進入：Component config → ESP PSRAM → Support for external, SPI-connected RAM
# 確認 Enable 打勾，設定 PSRAM mode = Octal

# 重新編譯
idf.py build flash monitor
```

輸出中應該看到：
```
I (xxx) spiram: Found 8MB SPI RAM device
I (xxx) spiram: SPI RAM mode: sram 80m
```

---

## 步驟五：clone 研究起點（llama2.c）

```bash
cd ~/esp
git clone https://github.com/karpathy/llama.c
# 這是你的 Xtensa porting 的起點
```

---

## ✅ 今天完成後的驗證清單

- [ ] `esptool.py --port /dev/cu.XXXX flash_id` 看到 Flash/PSRAM 規格
- [ ] ESP-IDF 安裝完成，`idf.py --version` 有輸出
- [ ] hello_world 在 ESP32-S3 上跑通
- [ ] PSRAM 已確認啟用（看到 `spiram: Found XMB`）
- [ ] llama.c 已 clone

---

*文件：`docs/day1_setup.md`*
