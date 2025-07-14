# WeDaka MCP Server

WeDaka MCP Server 是一個員工打卡系統的 Model Context Protocol (MCP) 伺服器，讓員工能夠透過 MCP 客戶端進行打卡和查詢工時記錄。

## 功能特色

- **員工認證**: 使用員工 AD 帳號和裝置代碼進行認證（無需密碼）
- **上班打卡**: 記錄員工上班時間
- **下班打卡**: 記錄員工下班時間  
- **工時查詢**: 查詢指定月份的所有打卡記錄

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

**需求：** Python 3.8+

## 環境變數設定

使用前需要設定以下環境變數：
- `WEDAKA_API_URL`：WeDaka API 伺服器位址（如：https://your-server.com）
- `WEDAKA_USERNAME`：員工 AD 帳號
- `WEDAKA_DEVICE_ID`：裝置代碼
- `WEDAKA_EMP_NO`：員工編號

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
        "WEDAKA_API_URL": "https://your-server.com",
        "WEDAKA_USERNAME": "your-ad-account",
        "WEDAKA_DEVICE_ID": "your-device-id",
        "WEDAKA_EMP_NO": "your-employee-id"
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
        "WEDAKA_API_URL": "https://your-server.com",
        "WEDAKA_USERNAME": "your-ad-account",
        "WEDAKA_DEVICE_ID": "your-device-id",
        "WEDAKA_EMP_NO": "your-employee-id"
      }
    }
  }
}
```

### 使用說明

1. 將上述設定中的 `your-server.com`、`your-ad-account` 等替換為實際值
2. 重新啟動 Claude Desktop 或 VSCode
3. 現在可以直接使用 MCP tools，無需每次輸入認證資訊

## 可用的 MCP Tools

- **wedaka_login** - 員工登入認證
- **wedaka_clock_in** - 上班打卡
- **wedaka_clock_out** - 下班打卡  
- **wedaka_get_timelog** - 查詢工時記錄


## 專案結構

```
WeDaka-MCP/
├── src/
│   ├── __init__.py          # 專案初始化
│   ├── server.py            # MCP Server 主程式
│   ├── api_client.py        # API 客戶端封裝
│   └── models.py            # 資料模型定義
├── pyproject.toml           # 專案設定
├── requirements.txt         # 相依套件清單
└── README.md               # 專案說明文件
```

## 開發

如果要進行開發，可以安裝開發相依套件：

```bash
pip install -e .[dev]
```

這會安裝額外的開發工具包括：
- pytest (測試)
- black (程式碼格式化)
- isort (匯入排序)
- mypy (型別檢查)

## 授權

MIT License

