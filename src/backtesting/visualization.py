"""
回测结果可视化
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Optional
import seaborn as sns

from .models import BacktestResult, SignalType

# 设置中文字体支持
plt.rcParams["font.sans-serif"] = ["SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


class BacktestVisualizer:
    """回测结果可视化器"""

    def __init__(self, result: BacktestResult):
        self.result = result
        self.figsize = (15, 10)

    def plot_equity_curve(
        self, save_path: Optional[str] = None, show_drawdown: bool = True
    ):
        """绘制权益曲线"""
        fig, axes = plt.subplots(
            2 if show_drawdown else 1, 1, figsize=self.figsize, sharex=True
        )
        if not show_drawdown:
            axes = [axes]

        # 权益曲线
        equity_curve = self.result.equity_curve["portfolio_value"]
        axes[0].plot(
            equity_curve.index,
            equity_curve.values,
            "b-",
            linewidth=2,
            label="投资组合价值",
        )
        axes[0].axhline(
            y=self.result.initial_capital,
            color="r",
            linestyle="--",
            alpha=0.7,
            label="初始资金",
        )

        # 标记买入卖出点
        for trade in self.result.trades:
            color = "green" if trade.signal == SignalType.BUY else "red"
            marker = "^" if trade.signal == SignalType.BUY else "v"
            axes[0].scatter(
                trade.timestamp,
                trade.price * trade.quantity,
                color=color,
                marker=marker,
                s=100,
                alpha=0.8,
            )

        axes[0].set_title(
            f'{self.result.symbol} 权益曲线 ({self.result.start_date.strftime("%Y-%m-%d")} - {self.result.end_date.strftime("%Y-%m-%d")})'
        )
        axes[0].set_ylabel("投资组合价值 ($)")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # 回撤图
        if show_drawdown:
            running_max = equity_curve.cummax()
            drawdown = (equity_curve - running_max) / running_max * 100

            axes[1].fill_between(
                drawdown.index, drawdown.values, 0, color="red", alpha=0.3
            )
            axes[1].plot(drawdown.index, drawdown.values, "r-", linewidth=1)
            axes[1].set_title("回撤分析")
            axes[1].set_ylabel("回撤 (%)")
            axes[1].set_xlabel("日期")
            axes[1].grid(True, alpha=0.3)

        # 格式化x轴
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()

    def plot_returns_distribution(self, save_path: Optional[str] = None):
        """绘制收益率分布"""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))

        returns = self.result.daily_returns * 100  # 转换为百分比

        # 收益率直方图
        axes[0].hist(returns, bins=50, alpha=0.7, color="skyblue", edgecolor="black")
        axes[0].axvline(
            returns.mean(),
            color="red",
            linestyle="--",
            label=f"均值: {returns.mean():.2f}%",
        )
        axes[0].axvline(
            returns.median(),
            color="green",
            linestyle="--",
            label=f"中位数: {returns.median():.2f}%",
        )
        axes[0].set_title("日收益率分布")
        axes[0].set_xlabel("日收益率 (%)")
        axes[0].set_ylabel("频次")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # Q-Q图
        from scipy import stats

        stats.probplot(returns, dist="norm", plot=axes[1])
        axes[1].set_title("收益率正态性检验 (Q-Q图)")
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()

    def plot_monthly_returns(self, save_path: Optional[str] = None):
        """绘制月度收益率热力图"""
        returns = self.result.daily_returns

        # 按月份分组计算收益率
        monthly_returns = returns.resample("M").apply(lambda x: (1 + x).prod() - 1)
        monthly_returns.index = monthly_returns.index.to_period("M")

        # 创建年月矩阵
        years = monthly_returns.index.year.unique()
        months = range(1, 13)

        data = []
        for year in years:
            year_data = []
            for month in months:
                try:
                    value = monthly_returns[f"{year}-{month:02d}"]
                    year_data.append(value * 100)  # 转换为百分比
                except KeyError:
                    year_data.append(np.nan)
            data.append(year_data)

        # 绘制热力图
        fig, ax = plt.subplots(figsize=(12, 8))

        sns.heatmap(
            data,
            xticklabels=[
                "1月",
                "2月",
                "3月",
                "4月",
                "5月",
                "6月",
                "7月",
                "8月",
                "9月",
                "10月",
                "11月",
                "12月",
            ],
            yticklabels=years,
            annot=True,
            fmt=".1f",
            cmap="RdYlGn",
            center=0,
            ax=ax,
        )

        ax.set_title("月度收益率热力图 (%)")
        ax.set_xlabel("月份")
        ax.set_ylabel("年份")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()

    def plot_trade_analysis(self, save_path: Optional[str] = None):
        """绘制交易分析"""
        if not self.result.trades:
            print("没有交易记录可以分析")
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # 计算每笔交易的盈亏
        profits = []
        for i in range(0, len(self.result.trades) - 1, 2):
            if (i + 1) < len(self.result.trades):
                buy_trade = self.result.trades[i]
                sell_trade = self.result.trades[i + 1]
                if (
                    buy_trade.signal == SignalType.BUY
                    and sell_trade.signal == SignalType.SELL
                ):
                    profit = (sell_trade.price - buy_trade.price) * buy_trade.quantity
                    profit -= buy_trade.commission + sell_trade.commission
                    profits.append(profit)

        if profits:
            # 盈亏分布
            axes[0, 0].hist(
                profits, bins=20, alpha=0.7, color="lightblue", edgecolor="black"
            )
            axes[0, 0].axvline(
                np.mean(profits),
                color="red",
                linestyle="--",
                label=f"平均: ${np.mean(profits):.2f}",
            )
            axes[0, 0].set_title("单笔交易盈亏分布")
            axes[0, 0].set_xlabel("盈亏 ($)")
            axes[0, 0].set_ylabel("频次")
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)

            # 累计盈亏
            cumulative_profits = np.cumsum(profits)
            axes[0, 1].plot(
                range(1, len(cumulative_profits) + 1),
                cumulative_profits,
                "b-",
                linewidth=2,
            )
            axes[0, 1].set_title("累计盈亏曲线")
            axes[0, 1].set_xlabel("交易次数")
            axes[0, 1].set_ylabel("累计盈亏 ($)")
            axes[0, 1].grid(True, alpha=0.3)

        # 交易频率统计
        trade_dates = [trade.timestamp for trade in self.result.trades]
        trade_counts = pd.Series(trade_dates).dt.date.value_counts()

        axes[1, 0].bar(
            range(len(trade_counts)), trade_counts.values, alpha=0.7, color="orange"
        )
        axes[1, 0].set_title("每日交易频率")
        axes[1, 0].set_xlabel("交易日")
        axes[1, 0].set_ylabel("交易次数")
        axes[1, 0].grid(True, alpha=0.3)

        # 胜率统计
        if profits:
            winning_trades = len([p for p in profits if p > 0])
            losing_trades = len([p for p in profits if p < 0])

            labels = ["盈利交易", "亏损交易"]
            sizes = [winning_trades, losing_trades]
            colors = ["green", "red"]

            axes[1, 1].pie(
                sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90
            )
            axes[1, 1].set_title(f"胜率统计 (总计 {len(profits)} 笔交易)")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()

    def create_performance_report(self, save_path: Optional[str] = None) -> str:
        """创建性能报告"""
        report = f"""
# {self.result.symbol} 回测性能报告

## 基本信息
- 股票代码: {self.result.symbol}
- 回测期间: {self.result.start_date.strftime('%Y-%m-%d')} - {self.result.end_date.strftime('%Y-%m-%d')}
- 初始资金: ${self.result.initial_capital:,.2f}

## 收益指标
- 总收益率: {self.result.total_return:.2%}
- 年化收益率: {self.result.annualized_return:.2%}
- 最大回撤: {self.result.max_drawdown:.2%}

## 风险指标
- 夏普比率: {self.result.sharpe_ratio:.2f}

## 交易统计
- 总交易次数: {self.result.total_trades}
- 盈利交易: {self.result.winning_trades}
- 亏损交易: {self.result.losing_trades}
- 胜率: {self.result.win_rate:.2%}
- 平均盈利: ${self.result.avg_win:.2f}
- 平均亏损: ${self.result.avg_loss:.2f}
- 盈亏比: {self.result.profit_factor:.2f}
"""

        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report)

        return report

    def plot_comprehensive_analysis(self, save_path: Optional[str] = None):
        """综合分析图表"""
        fig = plt.figure(figsize=(20, 15))

        # 创建子图布局
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 权益曲线
        ax1 = fig.add_subplot(gs[0, :2])
        equity_curve = self.result.equity_curve["portfolio_value"]
        ax1.plot(equity_curve.index, equity_curve.values, "b-", linewidth=2)
        ax1.set_title("权益曲线")
        ax1.set_ylabel("投资组合价值 ($)")
        ax1.grid(True, alpha=0.3)

        # 回撤
        ax2 = fig.add_subplot(gs[1, :2])
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max * 100
        ax2.fill_between(drawdown.index, drawdown.values, 0, color="red", alpha=0.3)
        ax2.set_title("回撤分析")
        ax2.set_ylabel("回撤 (%)")
        ax2.grid(True, alpha=0.3)

        # 收益率分布
        ax3 = fig.add_subplot(gs[0, 2])
        returns = self.result.daily_returns * 100
        ax3.hist(returns, bins=30, alpha=0.7, color="skyblue")
        ax3.set_title("收益率分布")
        ax3.set_xlabel("日收益率 (%)")

        # 性能指标表
        ax4 = fig.add_subplot(gs[1, 2])
        ax4.axis("off")
        metrics_text = f"""
性能指标:
总收益率: {self.result.total_return:.2%}
年化收益率: {self.result.annualized_return:.2%}
最大回撤: {self.result.max_drawdown:.2%}
夏普比率: {self.result.sharpe_ratio:.2f}
胜率: {self.result.win_rate:.2%}
总交易次数: {self.result.total_trades}
"""
        ax4.text(
            0.1,
            0.9,
            metrics_text,
            transform=ax4.transAxes,
            fontsize=12,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        # 月度收益率
        ax5 = fig.add_subplot(gs[2, :])
        monthly_returns = (
            self.result.daily_returns.resample("M").apply(lambda x: (1 + x).prod() - 1)
            * 100
        )
        ax5.bar(range(len(monthly_returns)), monthly_returns.values, alpha=0.7)
        ax5.set_title("月度收益率 (%)")
        ax5.set_xlabel("月份")
        ax5.set_ylabel("收益率 (%)")
        ax5.grid(True, alpha=0.3)

        plt.suptitle(
            f"{self.result.symbol} 综合回测分析报告", fontsize=16, fontweight="bold"
        )

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()
