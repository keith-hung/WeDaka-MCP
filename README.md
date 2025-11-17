# WeDaka MCP Server - TypeScript Implementation

WeDaka MCP Server 的 TypeScript 實作版本，提供員工打卡系統的 Model Context Protocol (MCP) 伺服器功能。

## 功能特色

- **免登入設計**: 使用環境變數直接認證，無需登入流程
- **上班打卡**: 記錄員工上班時間，支援備註功能和指定日期時間
- **下班打卡**: 記錄員工下班時間，支援備註功能和指定日期時間  
- **工時查詢**: 查詢指定月份的所有打卡記錄
- **補打卡功能**: 支援往回補打過去日期的打卡記錄
- **工作日檢查**: 自動檢查日期是否為工作日，防止在假日或非工作日打卡（DateType "1": 工作日、"2": 休假日、"3": 例假日）
- **未來日期保護**: 禁止為未來日期打卡，只能為今天或過去的日期打卡

## 安裝方式

### 方式一：從 GitHub 直接安裝（推薦）

```bash
# 複製專案並安裝依賴
git clone git@github.com:keith-hung/WeDaka-MCP.git
cd WeDaka-MCP
npm install
npm run build
```

### 方式二：本地開發安裝

如果您已經有專案檔案：

```bash
# 安裝依賴
npm install

# 編譯 TypeScript
npm run build
```

### 前置需求

- Node.js 20.0.0+
- Git（用於從 GitHub 安裝）
- npm 或 yarn

## 環境變數設定

使用前需要設定以下環境變數：

```bash
export WEDAKA_API_URL="https://your-wedaka-server.com"
export WEDAKA_USERNAME="your-ad-account"
export WEDAKA_DEVICE_ID="your-device-uuid"
export WEDAKA_EMP_NO="your-employee-number"
```

## 開發腳本

```bash
# 編譯 TypeScript
npx tsc

# 開發模式運行
npx tsx src/server.ts

# 運行編譯後的程式
node dist/server.js

# 執行測試
npx jest

# 程式碼檢查
npx eslint src/**/*.ts

# 程式碼格式化
npx prettier --write src/**/*.ts
```

## MCP 客戶端設定

### Claude Desktop

在 `claude_desktop_config.json` 中加入：

```json
{
  "mcpServers": {
    "wedaka": {
      "command": "npx",
      "args": ["-y", "git+https://github.com/keith-hung/WeDaka-MCP.git"],
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
      "command": "npx",
      "args": ["-y", "git+https://github.com/keith-hung/WeDaka-MCP.git"],
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

**注意事項：**
1. 將上述設定中的環境變數替換為實際值
2. 重新啟動 Claude Desktop 或 VSCode 以載入設定
3. 首次執行時 npx 會自動從 GitHub 下載並安裝專案
4. 確保使用 Node.js 20.0.0 或更高版本


## 可用的 MCP Tools

本系統提供以下 MCP tools：

- **wedaka_clock_in** - 上班打卡
- **wedaka_clock_out** - 下班打卡
- **wedaka_get_timelog** - 查詢工時記錄
- **wedaka_check_work_day** - 檢查工作日

### Time Log 資料結構

`wedaka_get_timelog` 回傳的每筆記錄包含以下重要欄位：

#### WorkItem (記錄類型)
| 數值 | 意義 | 說明 |
|------|------|------|
| `'1'` | 上班打卡 | 員工開始工作的時間記錄 |
| `'2'` | 請假 | 員工全天請假 |
| `'4'` | 下班打卡 | 員工結束工作的時間記錄 |

**重要**：當 `WorkItem = '2'` 時，表示員工當天全天請假（不會有打卡時間記錄）。

#### DateType (日期類型)
| 數值 | 意義 |
|------|------|
| `'1'` | 工作日 |
| `'2'` | 休假日 |
| `'3'` | 例假日 |

#### 其他欄位
- **WorkTime**: 打卡時間 (格式: YYYY/MM/DD HH:MM:SS，請假記錄時為 null)
- **WorkDate**: 打卡日期
- **Memo**: 備註
- **LeaveHours**: 請假時數 (此欄位可能為 0 或 null，不代表實際請假時數)

更多詳細資料結構說明請參考 [DEVELOPMENT.md](DEVELOPMENT.md#api-資料結構說明)。

## 專案結構

```
typescript/
├── src/
│   ├── types/           # TypeScript 類型定義
│   ├── models/          # Zod 驗證模型
│   ├── client/          # API 客戶端
│   ├── server/          # MCP 伺服器實作
│   ├── __tests__/       # 測試檔案
│   └── server.ts        # 主要入口點
├── dist/                # 編譯輸出目錄
├── jest.config.js       # Jest 測試設定
├── tsconfig.json        # TypeScript 設定
├── .eslintrc.js         # ESLint 設定
├── .prettierrc          # Prettier 設定
└── package.json         # 專案設定
```

## 技術棧

- **TypeScript**: 型別安全的 JavaScript
- **Zod**: 執行時型別驗證
- **Axios**: HTTP 客戶端
- **@modelcontextprotocol/sdk**: MCP SDK
- **Jest**: 測試框架
- **ESLint**: 程式碼檢查
- **Prettier**: 程式碼格式化

## 開發指南

### 程式碼風格

- 使用 TypeScript 嚴格模式
- 遵循 ESLint 和 Prettier 規則
- 使用 Zod 進行資料驗證
- 採用 async/await 處理異步操作

### 測試

```bash
# 執行所有測試
npx jest

# 執行特定測試檔案
npx jest src/__tests__/WedakaApiClient.test.ts

# 執行測試並生成覆蓋率報告
npx jest --coverage
```

### 程式碼品質

```bash
# 檢查程式碼風格
npx eslint src/**/*.ts

# 自動修復可修復的問題
npx eslint src/**/*.ts --fix

# 格式化程式碼
npx prettier --write src/**/*.ts
```

## 授權

MIT License