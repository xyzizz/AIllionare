"""
MACD交易策略实现
"""
import pandas as pd
from ta.trend import MACD
from .models import SignalType, BacktestConfig


class MACDStrategy:
    """MACD交易策略"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.fast_period = config.macd_fast
        self.slow_period = config.macd_slow
        self.signal_period = config.macd_signal

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算MACD指标"""
        df = data.copy()

        # 计算MACD
        macd = MACD(
            close=df["Close"],
            window_fast=self.fast_period,
            window_slow=self.slow_period,
            window_sign=self.signal_period,
        )

        df["MACD"] = macd.macd()
        df["MACD_Signal"] = macd.macd_signal()
        df["MACD_Hist"] = macd.macd_diff()

        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        df = self.calculate_indicators(data)

        # 初始化信号列
        df["Signal"] = SignalType.HOLD.value
        df["Signal_Strength"] = 0.0  # 信号强度

        # 计算MACD交叉信号
        df["MACD_Cross"] = 0
        df["Signal_Cross"] = 0

        # MACD线穿越零轴
        for i in range(1, len(df)):
            # MACD金叉死叉判断
            if (
                df.iloc[i]["MACD"] > df.iloc[i]["MACD_Signal"]
                and df.iloc[i - 1]["MACD"] <= df.iloc[i - 1]["MACD_Signal"]
            ):
                df.iloc[i, df.columns.get_loc("MACD_Cross")] = 1  # 金叉
            elif (
                df.iloc[i]["MACD"] < df.iloc[i]["MACD_Signal"]
                and df.iloc[i - 1]["MACD"] >= df.iloc[i - 1]["MACD_Signal"]
            ):
                df.iloc[i, df.columns.get_loc("MACD_Cross")] = -1  # 死叉

        # 生成交易信号
        for i in range(len(df)):
            # 买入信号：MACD金叉且MACD在零轴上方
            if (
                df.iloc[i]["MACD_Cross"] == 1
                and df.iloc[i]["MACD"] > 0
                and df.iloc[i]["MACD_Hist"] > 0
            ):
                df.iloc[i, df.columns.get_loc("Signal")] = SignalType.BUY.value
                df.iloc[i, df.columns.get_loc("Signal_Strength")] = abs(
                    df.iloc[i]["MACD_Hist"]
                )

            # 卖出信号：MACD死叉或MACD转为负值
            elif df.iloc[i]["MACD_Cross"] == -1 or (
                df.iloc[i]["MACD"] < 0 and df.iloc[i]["MACD_Hist"] < 0
            ):
                df.iloc[i, df.columns.get_loc("Signal")] = SignalType.SELL.value
                df.iloc[i, df.columns.get_loc("Signal_Strength")] = abs(
                    df.iloc[i]["MACD_Hist"]
                )

        return df

    def apply_risk_management(
        self, data: pd.DataFrame, current_position: int
    ) -> pd.DataFrame:
        """应用风险管理规则"""
        df = data.copy()

        if self.config.stop_loss or self.config.take_profit:
            # 这里可以添加止损止盈逻辑
            pass

        return df

    def get_signal_explanation(self, row: pd.Series) -> str:
        """获取信号解释"""
        signal = row["Signal"]
        macd = row["MACD"]
        signal_line = row["MACD_Signal"]
        histogram = row["MACD_Hist"]

        if signal == SignalType.BUY.value:
            return (
                f"买入信号: MACD({macd:.4f}) > 信号线({signal_line:.4f}), "
                f"柱状图({histogram:.4f}) > 0, 趋势向上"
            )
        elif signal == SignalType.SELL.value:
            return (
                f"卖出信号: MACD({macd:.4f}) < 信号线({signal_line:.4f}), "
                f"柱状图({histogram:.4f}) < 0, 趋势向下"
            )
        else:
            return f"持有: MACD({macd:.4f}), 信号线({signal_line:.4f}), 无明确信号"
