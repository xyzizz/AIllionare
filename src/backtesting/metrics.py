"""
回测性能指标计算
"""
import pandas as pd
import numpy as np
from typing import Dict


class PerformanceMetrics:
    """性能指标计算器"""

    @staticmethod
    def calculate_returns(prices: pd.Series) -> pd.Series:
        """计算收益率"""
        return prices.pct_change().dropna()

    @staticmethod
    def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
        """计算累计收益率"""
        return (1 + returns).cumprod() - 1

    @staticmethod
    def calculate_total_return(start_value: float, end_value: float) -> float:
        """计算总收益率"""
        return (end_value - start_value) / start_value

    @staticmethod
    def calculate_annualized_return(total_return: float, days: int) -> float:
        """计算年化收益率"""
        years = days / 365.25
        if years > 0:
            return (1 + total_return) ** (1 / years) - 1
        return total_return

    @staticmethod
    def calculate_volatility(returns: pd.Series, annualized: bool = True) -> float:
        """计算波动率"""
        vol = returns.std()
        if annualized:
            vol *= np.sqrt(252)  # 年化
        return vol

    @staticmethod
    def calculate_sharpe_ratio(
        returns: pd.Series, risk_free_rate: float = 0.02
    ) -> float:
        """计算夏普比率"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        excess_returns = returns.mean() * 252 - risk_free_rate  # 年化
        volatility = returns.std() * np.sqrt(252)  # 年化波动率

        return excess_returns / volatility if volatility != 0 else 0.0

    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """计算最大回撤"""
        if len(equity_curve) == 0:
            return 0.0

        # 计算累计最高点
        running_max = equity_curve.cummax()

        # 计算回撤
        drawdown = (equity_curve - running_max) / running_max

        return abs(drawdown.min())

    @staticmethod
    def calculate_calmar_ratio(annualized_return: float, max_drawdown: float) -> float:
        """计算卡玛比率"""
        if max_drawdown == 0:
            return float("inf") if annualized_return > 0 else 0.0
        return annualized_return / max_drawdown

    @staticmethod
    def calculate_sortino_ratio(
        returns: pd.Series, risk_free_rate: float = 0.02
    ) -> float:
        """计算索提诺比率"""
        if len(returns) == 0:
            return 0.0

        excess_returns = returns.mean() * 252 - risk_free_rate
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0:
            return float("inf") if excess_returns > 0 else 0.0

        downside_deviation = downside_returns.std() * np.sqrt(252)

        return excess_returns / downside_deviation if downside_deviation != 0 else 0.0

    @staticmethod
    def calculate_var(returns: pd.Series, confidence: float = 0.05) -> float:
        """计算风险价值(VaR)"""
        if len(returns) == 0:
            return 0.0
        return returns.quantile(confidence)

    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence: float = 0.05) -> float:
        """计算条件风险价值(CVaR)"""
        if len(returns) == 0:
            return 0.0
        var = PerformanceMetrics.calculate_var(returns, confidence)
        return returns[returns <= var].mean()

    @staticmethod
    def calculate_beta(returns: pd.Series, market_returns: pd.Series) -> float:
        """计算贝塔系数"""
        if len(returns) == 0 or len(market_returns) == 0:
            return 0.0

        # 确保两个序列长度一致
        aligned_returns = returns.align(market_returns, join="inner")
        returns_aligned = aligned_returns[0].dropna()
        market_aligned = aligned_returns[1].dropna()

        if len(returns_aligned) == 0 or market_aligned.var() == 0:
            return 0.0

        return np.cov(returns_aligned, market_aligned)[0, 1] / market_aligned.var()

    @staticmethod
    def calculate_alpha(
        returns: pd.Series, market_returns: pd.Series, risk_free_rate: float = 0.02
    ) -> float:
        """计算阿尔法系数"""
        if len(returns) == 0 or len(market_returns) == 0:
            return 0.0

        beta = PerformanceMetrics.calculate_beta(returns, market_returns)
        portfolio_return = returns.mean() * 252
        market_return = market_returns.mean() * 252

        return portfolio_return - (
            risk_free_rate + beta * (market_return - risk_free_rate)
        )

    @staticmethod
    def calculate_information_ratio(
        returns: pd.Series, benchmark_returns: pd.Series
    ) -> float:
        """计算信息比率"""
        if len(returns) == 0 or len(benchmark_returns) == 0:
            return 0.0

        # 确保两个序列长度一致
        aligned_returns = returns.align(benchmark_returns, join="inner")
        returns_aligned = aligned_returns[0].dropna()
        benchmark_aligned = aligned_returns[1].dropna()

        if len(returns_aligned) == 0:
            return 0.0

        excess_returns = returns_aligned - benchmark_aligned
        tracking_error = excess_returns.std() * np.sqrt(252)

        if tracking_error == 0:
            return 0.0

        return (excess_returns.mean() * 252) / tracking_error

    @classmethod
    def calculate_all_metrics(
        cls,
        equity_curve: pd.Series,
        returns: pd.Series,
        market_returns: pd.Series = None,
        risk_free_rate: float = 0.02,
    ) -> Dict[str, float]:
        """计算所有性能指标"""
        if len(equity_curve) == 0 or len(returns) == 0:
            return {}

        start_value = equity_curve.iloc[0]
        end_value = equity_curve.iloc[-1]
        days = (equity_curve.index[-1] - equity_curve.index[0]).days

        total_return = cls.calculate_total_return(start_value, end_value)
        annualized_return = cls.calculate_annualized_return(total_return, days)

        metrics = {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "volatility": cls.calculate_volatility(returns),
            "sharpe_ratio": cls.calculate_sharpe_ratio(returns, risk_free_rate),
            "max_drawdown": cls.calculate_max_drawdown(equity_curve),
            "calmar_ratio": cls.calculate_calmar_ratio(
                annualized_return, cls.calculate_max_drawdown(equity_curve)
            ),
            "sortino_ratio": cls.calculate_sortino_ratio(returns, risk_free_rate),
            "var_95": cls.calculate_var(returns, 0.05),
            "cvar_95": cls.calculate_cvar(returns, 0.05),
        }

        # 如果提供了市场收益率，计算相对指标
        if market_returns is not None and len(market_returns) > 0:
            metrics.update(
                {
                    "beta": cls.calculate_beta(returns, market_returns),
                    "alpha": cls.calculate_alpha(
                        returns, market_returns, risk_free_rate
                    ),
                    "information_ratio": cls.calculate_information_ratio(
                        returns, market_returns
                    ),
                }
            )

        return metrics
