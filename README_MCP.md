# 株式データ MCP サーバー

data_j.xlsファイルから銘柄コード、銘柄名、業種、規模の情報を提供するMCP（Model Context Protocol）サーバーです。

## 機能

このMCPサーバーは以下の機能を提供します：

### ツール
- **get_stock_by_code**: 銘柄コードで銘柄情報を検索
- **search_stocks_by_name**: 銘柄名で銘柄を検索（部分一致）
- **get_stocks_by_industry**: 業種で銘柄をフィルタリング
- **get_stocks_by_size**: 規模コードで銘柄をフィルタリング
- **get_all_stocks**: 全銘柄のリストを取得

### リソース
- **stocks://list**: 全銘柄の基本情報リスト

## データ内容

data_j.xlsファイルには以下の情報が含まれています：
- 銘柄コード（例: 1301, 7203）
- 銘柄名（例: 極洋, トヨタ自動車）
- 市場・商品区分（プライム、スタンダード、ETF・ETNなど）
- 33業種コード・区分（水産・農林業、自動車など）
- 17業種コード・区分
- 規模コード（1-7, 1が大型株）
- 規模区分（TOPIX Core30, Mid400, Small 1, Small 2など）

## インストールとセットアップ

### 前提条件
- Python 3.11以上
- UVパッケージマネージャー

### インストール
```bash
uv sync
```

### MCPサーバーの設定

ClineなどのMCPクライアントで使用するには、設定ファイルに以下を追加：

```json
{
  "mcpServers": {
    "stock-data": {
      "command": "python",
      "args": ["/path/to/stock-investment/mcp_stock_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/stock-investment"
      }
    }
  }
}
```

または、提供されている `mcp-stock-server.json` 設定ファイルを使用します。

## 使用方法

### 銘柄コードで検索
```json
{
  "method": "get_stock_by_code",
  "params": {"code": 7203}
}
```

### 銘柄名で検索
```json
{
  "method": "search_stocks_by_name", 
  "params": {"name": "トヨタ"}
}
```

### 業種でフィルタリング
```json
{
  "method": "get_stocks_by_industry",
  "params": {"industry": "自動車"}
}
```

### 規模でフィルタリング
```json
{
  "method": "get_stocks_by_size",
  "params": {"size_code": 1}
}
```

### 全銘柄取得
```json
{
  "method": "get_all_stocks",
  "params": {}
}
```

## 規模コードの意味

規模コードは以下のように分類されます：
- **1**: TOPIX Core30（超大型株）
- **2**: TOPIX Large70（大型株）
- **3**: TOPIX Large70（大型株）
- **4**: TOPIX Mid400（中型株）
- **5**: TOPIX Small 1（小型株）
- **6**: TOPIX Small 1（小型株）
- **7**: TOPIX Small 2（超小型株）

## データ更新

元データのdata_j.xlsファイルが更新された場合：
1. `analyze_excel_data.py` スクリプトを実行して分析データを更新
2. MCPサーバーを再起動

```bash
python analyze_excel_data.py
```

## トラブルシューティング

### データが読み込めない場合
- data/data_j.xlsファイルが存在するか確認
- 必要なパッケージがインストールされているか確認 (`xlrd`, `pandas`)

### サーバーが起動しない場合
- Pythonパスが正しく設定されているか確認
- 必要な依存関係がインストールされているか確認

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
