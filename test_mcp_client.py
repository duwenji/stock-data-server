#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCPサーバーのテストクライアント
"""

import json
import subprocess
import sys
import time
from typing import Dict, Any

def test_mcp_server():
    """MCPサーバーをテスト"""
    print("MCPサーバーのテストを開始します...")
    
    # MCPサーバーを起動
    try:
        # サーバープロセスを起動
        server_process = subprocess.Popen(
            [sys.executable, "mcp_stock_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # サーバー起動待機
        time.sleep(2)
        
        # テストリクエストを送信
        test_requests = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "get_all_stocks",
                "params": {}
            },
            {
                "jsonrpc": "2.0", 
                "id": 2,
                "method": "get_stock_by_code",
                "params": {"code": "1301_T"}
            },
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "search_stocks_by_name",
                "params": {"name": "トヨタ"}
            }
        ]
        
        for request in test_requests:
            print(f"\n送信リクエスト: {json.dumps(request, ensure_ascii=False)}")
            
            # リクエストを送信
            server_process.stdin.write(json.dumps(request) + "\n")
            server_process.stdin.flush()
            
            # レスポンスを受信
            response_line = server_process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"受信レスポンス: {json.dumps(response, ensure_ascii=False, indent=2)}")
            else:
                print("レスポンスがありません")
        
        # サーバーを終了
        server_process.terminate()
        server_process.wait()
        
        print("\nテストが完了しました")
        
    except Exception as e:
        print(f"テストエラー: {e}")
        if 'server_process' in locals():
            server_process.terminate()

def manual_test():
    """手動テスト用の関数"""
    from mcp_stock_server import StockDataMcpServer
    
    server = StockDataMcpServer()
    
    print("手動テストを開始します...")
    print(f"読み込まれた銘柄数: {len(server.stocks_data)}")
    
    # テストケース
    test_cases = [
        ("get_stock_by_code", {"code": "1301_T"}),
        ("get_stock_by_code", {"code": "9999_T"}),  # 存在しないコード
        ("search_stocks_by_name", {"name": "トヨタ"}),
        ("search_stocks_by_name", {"name": "存在しない銘柄"}),
        ("get_stocks_by_industry", {"industry": "自動車"}),
        ("get_stocks_by_size", {"size_code": 1}),
        ("get_all_stocks", {})
    ]
    
    for method, params in test_cases:
        print(f"\n--- {method} ---")
        print(f"パラメータ: {params}")
        
        # リクエストを作成
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        # リクエストを処理
        response = server.handle_request(request)
        print(f"レスポンス: {json.dumps(response, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    print("MCPサーバーテスト")
    print("1. 自動テスト (サーバープロセス起動)")
    print("2. 手動テスト (直接関数呼び出し)")
    
    choice = input("選択してください (1 or 2): ").strip()
    
    if choice == "1":
        test_mcp_server()
    elif choice == "2":
        manual_test()
    else:
        print("無効な選択です")
