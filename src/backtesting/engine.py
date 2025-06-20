"""
回测引擎核心实现
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict
import logging
import yfinance as yf

from .models import BacktestConfig, BacktestResult, Trade, Position, SignalType
from .strategy import MACDStrategy
from .metrics import PerformanceMetrics

logger = logging.getLogger(__name__)


class BacktestEngine:
    """回测引擎"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.strategy = MACDStrategy(config)
        self.metrics = PerformanceMetrics()

        # 交易状态
        self.cash = config.initial_capital
        self.position = Position()
        self.trades: List[Trade] = []
        self.equity_curve: List[Dict] = []

    def fetch_data(self) -> pd.DataFrame:
        """获取历史数据"""
        try:
            ticker = yf.Ticker(self.config.symbol)
            data = ticker.history(
                start=self.config.start_date, end=self.config.end_date, interval="1d"
            )

            if data.empty:
                raise ValueError(f"无法获取 {self.config.symbol} 的历史数据")

            # 确保数据完整性
            data = data.dropna()
            logger.info(f"成功获取 {len(data)} 条 {self.config.symbol} 的历史数据")

            return data

        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            raise

    def execute_trade(self, timestamp: datetime, signal: SignalType, price: float):
        """执行交易"""
        if signal == SignalType.HOLD:
            return

        quantity = self.config.trade_quantity
        commission = price * quantity * self.config.commission_rate

        if signal == SignalType.BUY:
            # 检查资金是否足够
            total_cost = price * quantity + commission
            if self.cash >= total_cost:
                # 执行买入
                self.cash -= total_cost

                # 更新持仓
                if self.position.quantity == 0:
                    self.position.avg_cost = price
                else:
                    # 加仓情况下重新计算平均成本
                    total_cost_before = self.position.avg_cost * self.position.quantity
                    self.position.avg_cost = (total_cost_before + price * quantity) / (
                        self.position.quantity + quantity
                    )

                self.position.quantity += quantity
                self.position.current_price = price

                # 记录交易
                trade = Trade(
                    timestamp=timestamp,
                    signal=signal,
                    price=price,
                    quantity=quantity,
                    commission=commission,
                )
                self.trades.append(trade)

                logger.debug(
                    f"执行买入: {quantity}股 @ ${price:.2f}, 手续费: ${commission:.2f}"
                )

        elif signal == SignalType.SELL and self.position.quantity > 0:
            # 执行卖出
            sell_quantity = min(quantity, self.position.quantity)
            total_value = price * sell_quantity - commission
            self.cash += total_value

            # 更新持仓
            self.position.quantity -= sell_quantity
            if self.position.quantity == 0:
                self.position.avg_cost = 0.0
            self.position.current_price = price

            # 记录交易
            trade = Trade(
                timestamp=timestamp,
                signal=signal,
                price=price,
                quantity=sell_quantity,
                commission=commission,
            )
            self.trades.append(trade)

            logger.debug(
                f"执行卖出: {sell_quantity}股 @ ${price:.2f}, 手续费: ${commission:.2f}"
            )

    def update_equity_curve(self, timestamp: datetime, price: float):
        """更新权益曲线"""
        self.position.current_price = price
        portfolio_value = self.cash + self.position.market_value

        equity_point = {
            "timestamp": timestamp,
            "price": price,
            "cash": self.cash,
            "position_value": self.position.market_value,
            "portfolio_value": portfolio_value,
            "position_quantity": self.position.quantity,
            "unrealized_pnl": self.position.unrealized_pnl,
        }

        self.equity_curve.append(equity_point)

    def run_backtest(self) -> BacktestResult:
        """运行回测"""
        logger.info(
            f"开始回测 {self.config.symbol} ({self.config.start_date} - {self.config.end_date})"
        )

        # 获取数据
        data = self.fetch_data()

        # 生成交易信号
        data_with_signals = self.strategy.generate_signals(data)

        # 执行回测
        for idx, row in data_with_signals.iterrows():
            timestamp = idx
            price = row["Close"]
            signal = SignalType(row["Signal"])

            # 执行交易
            self.execute_trade(timestamp, signal, price)

            # 更新权益曲线
            self.update_equity_curve(timestamp, price)

        # 计算回测结果
        result = self.calculate_results(data_with_signals)

        logger.info(
            f"回测完成: 总收益率 {result.total_return:.2%}, 夏普比率 {result.sharpe_ratio:.2f}"
        )

        return result

    def calculate_results(self, data: pd.DataFrame) -> BacktestResult:
        """计算回测结果"""
        # 转换权益曲线为DataFrame
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df.set_index("timestamp", inplace=True)

        # 计算日收益率
        daily_returns = equity_df["portfolio_value"].pct_change().dropna()

        # 计算性能指标
        final_value = equity_df["portfolio_value"].iloc[-1]
        total_return = (
            final_value - self.config.initial_capital
        ) / self.config.initial_capital

        # 年化收益率
        days = (self.config.end_date - self.config.start_date).days
        years = days / 365.25
        annualized_return = (
            (1 + total_return) ** (1 / years) - 1 if years > 0 else total_return
        )

        # 最大回撤
        max_drawdown = self.metrics.calculate_max_drawdown(equity_df["portfolio_value"])

        # 夏普比率
        sharpe_ratio = self.metrics.calculate_sharpe_ratio(daily_returns)

        return BacktestResult(
            symbol=self.config.symbol,
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            initial_capital=self.config.initial_capital,
            trades=self.trades,
            total_return=total_return,
            annualized_return=annualized_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=0.0,  # 将在BacktestResult中计算
            profit_factor=0.0,  # 将在BacktestResult中计算
            equity_curve=equity_df,
            daily_returns=daily_returns,
            total_trades=0,  # 将在BacktestResult中计算
            winning_trades=0,  # 将在BacktestResult中计算
            losing_trades=0,  # 将在BacktestResult中计算
            avg_win=0.0,  # 将在BacktestResult中计算
            avg_loss=0.0,  # 将在BacktestResult中计算
        )
