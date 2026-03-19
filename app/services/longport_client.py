"""
LongPort客户端模块
用于获取美股和港股数据
"""

from typing import List, Dict, Any, Optional
from longport.openapi import Config, QuoteContext, AdjustType, Period
from app.config import get_longport_config
from app.db import save_stock_history_to_db
from datetime import datetime, timedelta


class LongPortClient:
    """LongPort客户端"""
    
    def __init__(self):
        self._config = None
        self._ctx = None
    
    def _get_config(self) -> Config:
        """获取LongPort配置"""
        if self._config is None:
            longport_config = get_longport_config()
            app_key = longport_config.get('app_key', '')
            app_secret = longport_config.get('app_secret', '')
            access_token = longport_config.get('access_token', '')
            
            if not app_key or not app_secret or not access_token:
                raise ValueError("LongPort配置不完整，请在系统配置页面配置")
            
            self._config = Config(
                app_key=app_key,
                app_secret=app_secret,
                access_token=access_token
            )
        return self._config
    
    def _get_context(self) -> QuoteContext:
        """获取行情上下文"""
        if self._ctx is None:
            self._ctx = QuoteContext(self._get_config())
        return self._ctx
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取股票报价"""
        try:
            ctx = self._get_context()
            resp = ctx.quote([symbol])
            if resp:
                quote = resp[0]
                return {
                    'symbol': quote.symbol,
                    'name': quote.name,
                    'last_price': float(quote.last_price) if quote.last_price else None,
                    'change': float(quote.change) if quote.change else None,
                    'change_percent': float(quote.change_percent) if quote.change_percent else None,
                    'volume': int(quote.volume) if quote.volume else None,
                    'amount': float(quote.amount) if quote.amount else None,
                    'open': float(quote.open) if quote.open else None,
                    'high': float(quote.high) if quote.high else None,
                    'low': float(quote.low) if quote.low else None,
                    'close': float(quote.close) if quote.close else None,
                    'prev_close': float(quote.prev_close) if quote.prev_close else None,
                }
            return None
        except Exception as e:
            print(f"获取股票报价失败: {str(e)}")
            return None
    
    def get_historical_data(self, symbol: str, start_date: str = None, end_date: str = None, 
                            adjust_type: AdjustType = AdjustType.NoAdjust) -> List[Dict[str, Any]]:
        """获取股票历史数据"""
        try:
            ctx = self._get_context()
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 解析日期
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # 使用位置参数调用 history_candlesticks_by_date
            resp = ctx.history_candlesticks_by_date(
                symbol,
                Period.Day,
                adjust_type,
                start_date_obj,
                end_date_obj
            )
            print(f"API response type: {type(resp)}")
            print(f"API response: {resp}")
            
            if not resp:
                return []
            
            # 检查 resp 是列表还是对象
            if isinstance(resp, list):
                # 如果是列表，直接使用
                candlesticks = resp
                print(f"Response is list, length: {len(candlesticks)}")
            else:
                # 如果是对象，尝试获取 candlesticks 属性（考虑大小写）
                candlesticks = getattr(resp, 'candlesticks', None)
                if not candlesticks:
                    candlesticks = getattr(resp, 'Candlestick', None)
                if not candlesticks:
                    candlesticks = getattr(resp, 'Candlesticks', None)
                print(f"Response is object, candlesticks: {candlesticks}")
            
            if not candlesticks:
                return []
            
            result = []
            for kline in candlesticks:
                # 检查 kline 是对象还是字典
                if hasattr(kline, 'timestamp'):
                    # 如果是对象，使用属性访问
                    timestamp = kline.timestamp
                    open_price = kline.open
                    high_price = kline.high
                    low_price = kline.low
                    close_price = kline.close
                    volume = kline.volume
                    turnover = getattr(kline, 'turnover', getattr(kline, 'amount', 0))
                else:
                    # 如果是字典，使用键访问
                    timestamp = kline.get('timestamp')
                    open_price = kline.get('open')
                    high_price = kline.get('high')
                    low_price = kline.get('low')
                    close_price = kline.get('close')
                    volume = kline.get('volume')
                    turnover = kline.get('turnover', kline.get('amount', 0))
                
                # 处理 timestamp
                if isinstance(timestamp, datetime):
                    # 如果 timestamp 已经是 datetime 对象
                    date_str = timestamp.strftime('%Y-%m-%d')
                elif isinstance(timestamp, str):
                    # 如果 timestamp 是字符串，尝试解析
                    try:
                        if 'T' in timestamp:
                            # ISO格式: 2025-12-18T05:00:00Z
                            date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            date_str = date_obj.strftime('%Y-%m-%d')
                        else:
                            # 其他格式
                            date_str = timestamp
                    except Exception as e:
                        print(f"解析时间戳失败: {e}")
                        date_str = start_date
                else:
                    # 如果 timestamp 是数字，转换为日期
                    try:
                        date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                    except Exception as e:
                        print(f"转换时间戳失败: {e}")
                        date_str = start_date
                
                result.append({
                    'date': date_str,
                    'code': symbol,
                    'open': float(open_price) if open_price else 0,
                    'high': float(high_price) if high_price else 0,
                    'low': float(low_price) if low_price else 0,
                    'close': float(close_price) if close_price else 0,
                    'volume': int(volume) if volume else 0,
                    'amount': float(turnover) if turnover else 0,
                })
            
            print(f"处理后的数据: {result[:2]}...")
            return result
        except Exception as e:
            print(f"获取股票历史数据失败: {str(e)}")
            return []
    
    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        try:
            quote = self.get_quote(symbol)
            if quote:
                return {
                    'code': symbol,
                    'name': quote.get('name', ''),
                }
            return None
        except Exception as e:
            print(f"获取股票信息失败: {str(e)}")
            return None
    
    def search_symbols(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索股票代码"""
        try:
            ctx = self._get_context()
            resp = ctx.search_symbol(keyword)
            
            return [
                {
                    'symbol': item.symbol,
                    'name': item.name,
                }
                for item in resp
            ]
        except Exception as e:
            print(f"搜索股票失败: {str(e)}")
            return []


longport_client = LongPortClient()

def sync_stock_data(code: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """同步股票历史数据"""
    try:
        history = longport_client.get_historical_data(code, start_date, end_date)
        if history:
            save_stock_history_to_db(history)
        
            return {
                'success': True,
                'message': f'成功同步 {len(history)} 条历史数据',
                'count': len(history)
            }
        else:
            return {
                'success': False,
                'message': '未能获取到历史数据'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'同步失败: {str(e)}'
        }
