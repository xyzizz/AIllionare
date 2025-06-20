"""
数据模型定义
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
import pandas as pd


class SignalType(Enum):
    """交易信号类型"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Trade:
    """单笔交易记录"""

    timestamp: datetime
    signal: SignalType
    price: float
    quantity: int
    commission: float = 0.0

    @property
    def total_value(self) -> float:
        """交易总价值（含手续费）"""
        if self.signal == SignalType.BUY:
            return self.price * self.quantity + self.commission
        else:
            return self.price * self.quantity - self.commission


@dataclass
class Position:
    """持仓状态"""

    quantity: int = 0
    avg_cost: float = 0.0
    current_price: float = 0.0

    @property
    def market_value(self) -> float:
        """当前市值"""
        return self.quantity * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        """未实现损益"""
        if self.quantity == 0:
            return 0.0
        return (self.current_price - self.avg_cost) * self.quantity


@dataclass
class BacktestResult:
    """回测结果"""

    # 基本信息
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float

    # 交易记录
    trades: List[Trade]

    # 性能指标
    total_return: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    profit_factor: float

    # 详细数据
    equity_curve: pd.DataFrame
    daily_returns: pd.Series

    # 统计信息
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float

    def __post_init__(self):
        """计算衍生指标"""
        if self.trades:
            self.total_trades = len(
                [t for t in self.trades if t.signal != SignalType.HOLD]
            )
            self._calculate_trade_stats()

    def _calculate_trade_stats(self):
        """计算交易统计"""
        profits = []
        for i in range(0, len(self.trades) - 1, 2):  # 买入卖出成对计算
            if (i + 1) < len(self.trades):
                buy_trade = self.trades[i]
                sell_trade = self.trades[i + 1]
                if (
                    buy_trade.signal == SignalType.BUY
                    and sell_trade.signal == SignalType.SELL
                ):
                    profit = (
                        (sell_trade.price - buy_trade.price) * buy_trade.quantity
                        - buy_trade.commission
                        - sell_trade.commission
                    )
                    profits.append(profit)

        if profits:
            winning_profits = [p for p in profits if p > 0]
            losing_profits = [p for p in profits if p < 0]

            self.winning_trades = len(winning_profits)
            self.losing_trades = len(losing_profits)
            self.win_rate = self.winning_trades / len(profits) if profits else 0
            self.avg_win = (
                sum(winning_profits) / len(winning_profits) if winning_profits else 0
            )
            self.avg_loss = (
                sum(losing_profits) / len(losing_profits) if losing_profits else 0
            )
            self.profit_factor = (
                abs(sum(winning_profits) / sum(losing_profits))
                if losing_profits
                else float("inf")
            )


@dataclass
class BacktestConfig:
    """回测配置"""

    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 100000.0
    commission_rate: float = 0.001

    # MACD 参数
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9

    # 交易规则
    trade_quantity: int = 100  # 每次交易股数
    max_position_size: float = 1.0  # 最大仓位比例

    # 风险控制
    stop_loss: Optional[float] = None  # 止损比例
    take_profit: Optional[float] = None  # 止盈比例
