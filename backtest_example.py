"""
回测系统使用示例
"""
import logging
from datetime import datetime

from src.backtesting.models import BacktestConfig
from src.backtesting.engine import BacktestEngine
from src.backtesting.visualization import BacktestVisualizer

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_simple_backtest():
    """运行简单回测示例"""
    print("=" * 60)
    print("🚀 开始运行MACD策略回测")
    print("=" * 60)

    # 配置回测参数
    config = BacktestConfig(
        symbol="NVDA",  # 可以改为其他股票代码，如 "AAPL", "TSLA" 等
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2024, 1, 1),
        initial_capital=100000.0,  # 初始资金10万美元
        commission_rate=0.001,  # 手续费率0.1%
        trade_quantity=10,  # 每次交易10股
        macd_fast=12,  # MACD快线参数
        macd_slow=26,  # MACD慢线参数
        macd_signal=9,  # MACD信号线参数
    )

    # 创建回测引擎
    engine = BacktestEngine(config)

    try:
        # 运行回测
        result = engine.run_backtest()

        # 显示结果摘要
        print("\n📊 回测结果摘要:")
        print(f"   股票代码: {result.symbol}")
        print(
            f"   回测期间: {result.start_date.strftime('%Y-%m-%d')} - {result.end_date.strftime('%Y-%m-%d')}"
        )
        print(f"   初始资金: ${result.initial_capital:,.2f}")
        print(f"   最终价值: ${result.equity_curve['portfolio_value'].iloc[-1]:,.2f}")
        print(f"   总收益率: {result.total_return:.2%}")
        print(f"   年化收益率: {result.annualized_return:.2%}")
        print(f"   最大回撤: {result.max_drawdown:.2%}")
        print(f"   夏普比率: {result.sharpe_ratio:.2f}")
        print(f"   交易次数: {result.total_trades}")
        print(f"   胜率: {result.win_rate:.2%}")

        # 创建可视化器
        visualizer = BacktestVisualizer(result)

        # 生成图表
        print("\n📈 生成回测图表...")
        visualizer.plot_equity_curve()
        visualizer.plot_returns_distribution()
        visualizer.plot_trade_analysis()
        visualizer.plot_comprehensive_analysis()

        # 生成报告
        print("\n📝 生成性能报告...")
        report = visualizer.create_performance_report(
            f"backtest_report_{config.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        print(report)

        return result

    except Exception as e:
        logger.error(f"回测过程中发生错误: {e}")
        raise


def run_parameter_optimization():
    """参数优化示例"""
    print("=" * 60)
    print("🔧 开始参数优化")
    print("=" * 60)

    base_config = BacktestConfig(
        symbol="AAPL",
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2024, 1, 1),
        initial_capital=100000.0,
        commission_rate=0.001,
        trade_quantity=10,
    )

    # 测试不同的MACD参数组合
    parameter_combinations = [
        (12, 26, 9),  # 标准参数
        (5, 35, 5),  # 快速参数
        (8, 21, 5),  # 中等参数
        (19, 39, 9),  # 慢速参数
    ]

    results = []

    for fast, slow, signal in parameter_combinations:
        config = BacktestConfig(
            symbol=base_config.symbol,
            start_date=base_config.start_date,
            end_date=base_config.end_date,
            initial_capital=base_config.initial_capital,
            commission_rate=base_config.commission_rate,
            trade_quantity=base_config.trade_quantity,
            macd_fast=fast,
            macd_slow=slow,
            macd_signal=signal,
        )

        engine = BacktestEngine(config)
        result = engine.run_backtest()

        results.append(
            {
                "parameters": f"({fast},{slow},{signal})",
                "total_return": result.total_return,
                "sharpe_ratio": result.sharpe_ratio,
                "max_drawdown": result.max_drawdown,
                "trades": result.total_trades,
            }
        )

        print(
            f"   参数 ({fast},{slow},{signal}): 收益率 {result.total_return:.2%}, "
            f"夏普 {result.sharpe_ratio:.2f}, 回撤 {result.max_drawdown:.2%}"
        )

    # 找到最佳参数
    best_result = max(results, key=lambda x: x["sharpe_ratio"])
    print(f"\n🏆 最佳参数组合: {best_result['parameters']}")
    print(f"   最高夏普比率: {best_result['sharpe_ratio']:.2f}")
    print(f"   对应收益率: {best_result['total_return']:.2%}")

    return results


def run_multi_symbol_backtest():
    """多股票回测对比"""
    print("=" * 60)
    print("📊 多股票回测对比")
    print("=" * 60)

    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
    results = {}

    for symbol in symbols:
        try:
            config = BacktestConfig(
                symbol=symbol,
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2024, 1, 1),
                initial_capital=100000.0,
                commission_rate=0.001,
                trade_quantity=10,
            )

            engine = BacktestEngine(config)
            result = engine.run_backtest()
            results[symbol] = result

            print(
                f"   {symbol}: 收益率 {result.total_return:.2%}, "
                f"夏普 {result.sharpe_ratio:.2f}, 回撤 {result.max_drawdown:.2%}"
            )

        except Exception as e:
            print(f"   {symbol}: 回测失败 - {e}")

    # 排序显示结果
    sorted_results = sorted(
        results.items(), key=lambda x: x[1].sharpe_ratio, reverse=True
    )

    print("\n🏆 按夏普比率排序:")
    for i, (symbol, result) in enumerate(sorted_results, 1):
        print(
            f"   {i}. {symbol}: 夏普比率 {result.sharpe_ratio:.2f}, 收益率 {result.total_return:.2%}"
        )

    return results


def main():
    """主函数"""
    print("🤖 MACD策略回测系统")
    print("选择运行模式:")
    print("1. 简单回测")
    print("2. 参数优化")
    print("3. 多股票对比")

    choice = input("请输入选择 (1-3): ").strip()

    if choice == "1":
        run_simple_backtest()
    elif choice == "2":
        run_parameter_optimization()
    elif choice == "3":
        run_multi_symbol_backtest()
    else:
        print("无效选择，运行默认简单回测...")
        run_simple_backtest()


if __name__ == "__main__":
    main()
