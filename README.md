# WeDaka MCP Server

WeDaka MCP Server 是一個員工打卡系統的 Model Context Protocol (MCP) 伺服器，讓員工能夠透過 MCP 客戶端進行打卡和查詢工時記錄。

## 功能特色

- **免登入設計**: 使用環境變數直接認證，無需登入流程
- **上班打卡**: 記錄員工上班時間，支援備註功能和指定日期時間
- **下班打卡**: 記錄員工下班時間，支援備註功能和指定日期時間  
- **工時查詢**: 查詢指定月份的所有打卡記錄
- **補打卡功能**: 支援往回補打過去日期的打卡記錄
- **工作日檢查**: 自動檢查日期是否為工作日，防止在假日或非工作日打卡
- **未來日期保護**: 禁止為未來日期打卡，只能為今天或過去的日期打卡

## 安裝方式

### 使用 uvx (推薦)

無需預先安裝，MCP 客戶端會自動處理：

```bash
# 從本地專案路徑安裝
uvx --from /path/to/WeDaka-MCP wedaka-server

# 從 GitHub 遠端倉庫安裝
uvx --from git+https://github.com/keith-hung/WeDaka-MCP.git wedaka-server

# 從特定 branch 或 tag 安裝
uvx --from git+https://github.com/keith-hung/WeDaka-MCP.git@main wedaka-server

# 安裝包含開發依賴的版本
uvx --from "git+https://github.com/keith-hung/WeDaka-MCP.git[dev]" wedaka-server
```

### 傳統 pip 安裝

```bash
pip install -r requirements.txt
pip install -e .
```

**需求：** Python 3.10+

## 環境變數設定

使用前需要設定以下環境變數：
- `WEDAKA_API_URL`：WeDaka API 伺服器位址
- `WEDAKA_USERNAME`：員工 AD 帳號（用於工時查詢）
- `WEDAKA_DEVICE_ID`：裝置 UUID（用於認證）
- `WEDAKA_EMP_NO`：員工編號（用於打卡）

**注意**: 本系統採用直接認證方式，無需密碼或登入流程。

## MCP 客戶端設定

### Claude Desktop

在 `claude_desktop_config.json` 中加入：

```json
{
  "mcpServers": {
    "wedaka": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/keith-hung/WeDaka-MCP.git", "wedaka-server"],
      "env": {
        "WEDAKA_API_URL": "https://your-wedaka-server.com",
        "WEDAKA_USERNAME": "your-ad-account",
        "WEDAKA_DEVICE_ID": "your-device-uuid",
        "WEDAKA_EMP_NO": "your-employee-number"
      }
    }
  }
}
```

### VSCode

在 `.vscode/settings.json` 中加入：

```json
{
  "mcp.servers": {
    "wedaka": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/keith-hung/WeDaka-MCP.git", "wedaka-server"],
      "env": {
        "WEDAKA_API_URL": "https://your-wedaka-server.com",
        "WEDAKA_USERNAME": "your-ad-account",
        "WEDAKA_DEVICE_ID": "your-device-uuid",
        "WEDAKA_EMP_NO": "your-employee-number"
      }
    }
  }
}
```

### 使用說明

1. 將上述設定中的 `your-ad-account`、`your-device-uuid`、`your-employee-number` 等替換為實際值
2. 重新啟動 Claude Desktop 或 VSCode
3. 現在可以直接使用 MCP tools，無需每次輸入認證資訊

## 可用的 MCP Tools

本系統提供以下 MCP tools：

- **wedaka_clock_in** - 上班打卡
  - 支援即時打卡（使用當前日期時間）
  - 支援指定日期打卡（格式：YYYY-MM-DD）
  - 支援指定時間打卡（格式：HH:MM:SS）
  - 支援添加備註說明
  
- **wedaka_clock_out** - 下班打卡  
  - 支援即時打卡（使用當前日期時間）
  - 支援指定日期打卡（格式：YYYY-MM-DD）
  - 支援指定時間打卡（格式：HH:MM:SS）
  - 支援添加備註說明
  
- **wedaka_get_timelog** - 查詢工時記錄
  - 查詢指定月份和年份的所有打卡記錄
  - 顯示詳細的打卡時間、類型和備註

- **wedaka_check_work_day** - 檢查工作日
  - 檢查指定日期是否為工作日
  - 返回日期類型和工作日狀態
  - 可用於確認是否可以打卡

### 使用範例

```
# 當天上班打卡
使用 wedaka_clock_in 工具進行上班打卡

# 當天下班打卡並添加備註
使用 wedaka_clock_out 工具進行下班打卡，備註：加班完成專案

# 指定日期和時間的補打卡
使用 wedaka_clock_in 工具，日期：2025-07-10，時間：09:30:00，備註：補打卡

# 查詢本月工時記錄
使用 wedaka_get_timelog 工具查詢 2025 年 7 月的工時記錄

# 檢查指定日期是否為工作日
使用 wedaka_check_work_day 工具檢查 2025-07-15 是否為工作日
```

### 工作日檢查機制

系統會自動檢查每次打卡的日期是否為工作日：
- **DateType "1"**: 工作日（可以打卡）
- **DateType "2"**: 假日類型1（週末或國定假日）
- **DateType "3"**: 假日類型2
- **DateType "4"**: 假日類型3

如果嘗試在非工作日打卡，系統會自動拒絕並提供相應的錯誤訊息。

### 未來日期保護機制

系統會檢查打卡日期，禁止為未來日期打卡：
- **今天**: 允許打卡（需通過工作日檢查）
- **過去日期**: 允許補打卡（需通過工作日檢查）
- **未來日期**: 一律拒絕打卡，提示錯誤訊息

這確保了打卡記錄的時間邏輯正確性，防止意外的未來日期打卡。

## 專案結構

```
WeDaka-MCP/
├── src/wedaka/
│   ├── __init__.py          # 專案初始化
│   ├── server.py            # MCP Server 主程式
│   ├── api_client.py        # WeDaka API 客戶端
│   └── models.py            # 資料模型定義
├── tests/                   # 測試目錄
│   ├── __init__.py
│   ├── conftest.py          # pytest 設定
│   └── test_api_integration.py  # API 整合測試
├── .env.test.example        # 測試環境變數範例
├── run_tests.py             # 測試執行腳本
├── pyproject.toml           # 專案設定和依賴
├── requirements.txt         # 相依套件清單
└── README.md               # 專案說明文件
```

## 開發和測試

### 安裝開發環境

建議使用 `uv` 來管理虛擬環境：

```bash
# 建立虛擬環境
uv venv

# 啟動虛擬環境
source .venv/bin/activate

# 安裝開發依賴
uv pip install -e ".[dev]"
```

這會安裝額外的開發工具包括：
- pytest (測試框架)
- pytest-asyncio (異步測試支援)
- black (程式碼格式化)
- isort (匯入排序)
- mypy (型別檢查)

### 執行測試

1. **設定測試環境變數**：
   ```bash
   cp .env.test.example .env.test
   # 編輯 .env.test 填入實際的認證資訊
   ```

2. **執行 API 整合測試**：
   ```bash
   # 使用測試腳本
   python run_tests.py
   
   # 或使用 pytest
   pytest tests/ -v
   ```

3. **程式碼品質檢查**：
   ```bash
   # 格式化程式碼
   black src/ tests/
   
   # 排序 imports
   isort src/ tests/
   
   # 型別檢查
   mypy src/
   ```

## 授權

MIT License

