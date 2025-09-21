#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCPサーバー for stock data from data_j.xls
銘柄コード、銘柄名、業種、規模の情報を提供するMCPサーバー
"""

import json
import os
import sys
import asyncio
import logging
from typing import Dict, List, Any, Optional

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockDataMcpServer:
    """株式データを提供するMCPサーバー"""
    
    def __init__(self):
        self.stocks_data = self._load_stock_data()
        logger.info(f"読み込まれた銘柄数: {len(self.stocks_data)}")
    
    def _load_stock_data(self) -> List[Dict[str, Any]]:
        """Excelデータ分析結果から銘柄データを読み込む"""
        try:
            analysis_path = '../excel_data_analysis.json'
            if os.path.exists(analysis_path):
                with open(analysis_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('stocks_data', [])
            
            # 分析ファイルがない場合はanalyze_excel_data.pyを実行
            logger.info("分析ファイルが見つかりません。analyze_excel_data.pyを実行します...")
            import subprocess
            subprocess.run(['python', 'analyze_excel_data.py'], check=True)
            
            if os.path.exists(analysis_path):
                with open(analysis_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('stocks_data', [])
            
            return []
            
        except Exception as e:
            logger.error(f"データ読み込みエラー: {e}")
            return []
    
    def get_stock_by_code(self, code: str) -> Dict[str, Any]:
        """銘柄コードで銘柄情報を検索"""
        if not self.stocks_data:
            return {"error": "データが読み込まれていません"}
        
        # コードを文字列に変換して比較
        search_code = str(code).strip()
        for stock in self.stocks_data:
            stock_code = str(stock.get('コード', '')).strip()
            if stock_code == search_code:
                return stock
        
        return {"error": f"銘柄コード {code} が見つかりません"}
    
    def search_stocks_by_name(self, name: str) -> List[Dict[str, Any]]:
        """銘柄名で銘柄を検索"""
        if not self.stocks_data:
            return [{"error": "データが読み込まれていません"}]
        
        search_name = name.lower()
        results = []
        for stock in self.stocks_data:
            stock_name = str(stock.get('銘柄名', '')).lower()
            if search_name in stock_name:
                results.append(stock)
        
        return results if results else [{"error": f"'{name}' を含む銘柄が見つかりません"}]
    
    def get_stocks_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """業種で銘柄をフィルタリング"""
        if not self.stocks_data:
            return [{"error": "データが読み込まれていません"}]
        
        target_industry = industry.lower()
        results = []
        for stock in self.stocks_data:
            stock_industry = str(stock.get('33業種区分', '')).lower()
            if target_industry in stock_industry:
                results.append(stock)
        
        return results if results else [{"error": f"業種 '{industry}' の銘柄が見つかりません"}]
    
    def get_stocks_by_size(self, size_code: int) -> List[Dict[str, Any]]:
        """規模コードで銘柄をフィルタリング"""
        if not self.stocks_data:
            return [{"error": "データが読み込まれていません"}]
        
        results = []
        for stock in self.stocks_data:
            stock_size = stock.get('規模コード')
            if stock_size == size_code:
                results.append(stock)
        
        return results if results else [{"error": f"規模コード {size_code} の銘柄が見つかりません"}]
    
    def get_all_stocks(self) -> List[Dict[str, Any]]:
        """全銘柄のリストを取得"""
        if not self.stocks_data:
            return [{"error": "データが読み込まれていません"}]
        
        return self.stocks_data
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """MCPリクエストを処理"""
        try:
            method = request.get("method", "")
            params = request.get("params", {})
            id = request.get("id")
            
            logger.info(f"処理中のリクエスト: {method}")
            
            if method == "get_stock_by_code":
                code = params.get("code")
                if code is None:
                    return self._error_response(id, "code parameter is required")
                result = self.get_stock_by_code(code)
                return self._success_response(id, result)
            
            elif method == "search_stocks_by_name":
                name = params.get("name")
                if name is None:
                    return self._error_response(id, "name parameter is required")
                result = self.search_stocks_by_name(name)
                return self._success_response(id, result)
            
            elif method == "get_stocks_by_industry":
                industry = params.get("industry")
                if industry is None:
                    return self._error_response(id, "industry parameter is required")
                result = self.get_stocks_by_industry(industry)
                return self._success_response(id, result)
            
            elif method == "get_stocks_by_size":
                size_code = params.get("size_code")
                if size_code is None:
                    return self._error_response(id, "size_code parameter is required")
                result = self.get_stocks_by_size(size_code)
                return self._success_response(id, result)
            
            elif method == "get_all_stocks":
                result = self.get_all_stocks()
                return self._success_response(id, result)
            
            else:
                return self._error_response(id, f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"リクエスト処理エラー: {e}")
            return self._error_response(request.get("id"), f"Internal error: {str(e)}")
    
    def _success_response(self, id: Any, result: Any) -> Dict[str, Any]:
        """成功レスポンスを作成"""
        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        }
    
    def _error_response(self, id: Any, message: str) -> Dict[str, Any]:
        """エラーレスポンスを作成"""
        return {
            "jsonrpc": "2.0",
            "id": id,
            "error": {
                "code": -32601,
                "message": message
            }
        }
    
    async def run(self):
        """MCPサーバーを実行"""
        logger.info("株式データMCPサーバーを開始します...")
        
        # 標準入出力でMCPプロトコルを処理
        while True:
            try:
                # リクエストを読み取る
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line.strip())
                logger.debug(f"受信リクエスト: {request}")
                
                # リクエストを処理
                response = self.handle_request(request)
                
                # レスポンスを送信
                response_json = json.dumps(response, ensure_ascii=False)
                sys.stdout.write(response_json + "\n")
                sys.stdout.flush()
                logger.debug(f"送信レスポンス: {response_json}")
                
            except json.JSONDecodeError:
                logger.error("無効なJSONリクエスト")
                error_response = self._error_response(None, "Invalid JSON")
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
                
            except Exception as e:
                logger.error(f"予期せぬエラー: {e}")
                error_response = self._error_response(None, f"Unexpected error: {str(e)}")
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()

def main():
    """メイン関数"""
    server = StockDataMcpServer()
    
    # 非同期実行
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("サーバーを終了します")
    except Exception as e:
        logger.error(f"サーバーエラー: {e}")

if __name__ == "__main__":
    main()
