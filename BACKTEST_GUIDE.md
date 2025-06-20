# 🚀 AIllionare 回测系统使用指南

## 📖 系统概述

回测系统是 AIllionare 项目的重要扩展，它允许您在历史数据上测试 MACD 交易策略的性能，帮助您：
- 验证策略的有效性
- 优化交易参数
- 评估风险收益特征
- 对比不同股票的表现

## 🏗️ 系统架构

```
src/backtesting/
├── __init__.py          # 模块初始化
├── models.py            # 数据模型定义
├── strategy.py          # MACD交易策略
├── engine.py            # 回测引擎核心
├── metrics.py           # 性能指标计算
└── visualization.py     # 结果可视化
```

## 🔧 安装依赖

```bash
pip install -r requirements.txt
```

## 💡 快速开始

### 1. 简单回测示例

```python
from datetime import datetime
from src.backtesting.models import BacktestConfig
from src.backtesting.engine import BacktestEngine
from src.backtesting.visualization import BacktestVisualizer

# 配置回测参数
config = BacktestConfig(
    symbol="NVDA",                    # 股票代码
    start_date=datetime(2023, 1, 1),  # 回测开始日期
    end_date=datetime(2024, 1, 1),    # 回测结束日期
    initial_capital=100000.0,         # 初始资金
    commission_rate=0.001,            # 手续费率
    trade_quantity=10                 # 每次交易股数
)

# 运行回测
engine = BacktestEngine(config)
result = engine.run_backtest()

# 查看结果
print(f"总收益率: {result.total_return:.2%}")
print(f"夏普比率: {result.sharpe_ratio:.2f}")
print(f"最大回撤: {result.max_drawdown:.2%}")

# 生成图表
visualizer = BacktestVisualizer(result)
visualizer.plot_equity_curve()
```

### 2. 运行示例脚本

```bash
python backtest_example.py
```

选择运行模式：
- **1. 简单回测**: 对单个股票进行回测
- **2. 参数优化**: 测试不同MACD参数组合
- **3. 多股票对比**: 对比多个股票的策略表现

## 📊 核心功能

### 🎯 回测配置

`BacktestConfig` 类包含所有回测参数：

```python
config = BacktestConfig(
    symbol="AAPL",              # 必须：股票代码
    start_date=datetime(...),   # 必须：开始日期
    end_date=datetime(...),     # 必须：结束日期
    initial_capital=100000.0,   # 初始资金
    commission_rate=0.001,      # 手续费率（0.1%）
    
    # MACD参数
    macd_fast=12,              # 快线周期
    macd_slow=26,              # 慢线周期
    macd_signal=9,             # 信号线周期
    
    # 交易规则
    trade_quantity=100,        # 每次交易股数
    max_position_size=1.0,     # 最大仓位比例
    
    # 风险控制（可选）
    stop_loss=0.05,           # 止损比例（5%）
    take_profit=0.15          # 止盈比例（15%）
)
```

### 📈 MACD策略逻辑

系统实现的MACD交易策略：

**买入信号条件**：
- MACD线上穿信号线（金叉）
- MACD线在零轴上方
- MACD柱状图为正值

**卖出信号条件**：
- MACD线下穿信号线（死叉）
- 或MACD线转为负值且柱状图为负值

### 📊 性能指标

系统计算以下关键指标：

**收益指标**：
- 总收益率
- 年化收益率
- 累计收益曲线

**风险指标**：
- 最大回撤
- 波动率（年化）
- 夏普比率
- 索提诺比率
- VaR (95%)

**交易统计**：
- 总交易次数
- 胜率
- 平均盈利/亏损
- 盈亏比

### 📉 可视化图表

1. **权益曲线图**: 显示投资组合价值变化
2. **回撤分析图**: 显示历史回撤情况
3. **收益率分布图**: 显示日收益率统计特征
4. **月度收益热力图**: 按月份显示收益表现
5. **交易分析图**: 分析单笔交易盈亏
6. **综合分析报告**: 一页式全面分析

## 🛠️ 高级用法

### 参数优化

```python
def optimize_parameters():
    base_config = BacktestConfig(...)
    
    # 定义参数范围
    fast_periods = [5, 8, 12, 15]
    slow_periods = [21, 26, 30, 35]
    signal_periods = [5, 9, 14]
    
    best_sharpe = -999
    best_params = None
    
    for fast in fast_periods:
        for slow in slow_periods:
            for signal in signal_periods:
                if fast >= slow:  # 跳过无效组合
                    continue
                    
                config = BacktestConfig(
                    **base_config.__dict__,
                    macd_fast=fast,
                    macd_slow=slow,
                    macd_signal=signal
                )
                
                result = BacktestEngine(config).run_backtest()
                
                if result.sharpe_ratio > best_sharpe:
                    best_sharpe = result.sharpe_ratio
                    best_params = (fast, slow, signal)
    
    return best_params, best_sharpe
```

### 多股票回测

```python
def compare_stocks():
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
    results = {}
    
    for symbol in symbols:
        config = BacktestConfig(symbol=symbol, ...)
        result = BacktestEngine(config).run_backtest()
        results[symbol] = result
    
    # 按夏普比率排序
    sorted_results = sorted(
        results.items(), 
        key=lambda x: x[1].sharpe_ratio, 
        reverse=True
    )
    
    return sorted_results
```

## 📝 结果分析

### 生成报告

```python
# 生成Markdown报告
visualizer = BacktestVisualizer(result)
report = visualizer.create_performance_report("report.md")

# 保存图表
visualizer.plot_equity_curve(save_path="equity_curve.png")
visualizer.plot_comprehensive_analysis(save_path="analysis.png")
```

### 解读指标

**夏普比率**：
- \> 1.0: 优秀
- 0.5-1.0: 良好  
- < 0.5: 需要改进

**最大回撤**：
- < 10%: 低风险
- 10-20%: 中等风险
- \> 20%: 高风险

**胜率**：
- \> 60%: 高胜率策略
- 40-60%: 中等胜率
- < 40%: 低胜率策略

## ⚠️ 注意事项

1. **历史表现不代表未来收益**
2. **数据质量影响回测结果**
3. **考虑交易成本和滑点**
4. **避免过度优化（过拟合）**
5. **样本外测试的重要性**

## 🔍 故障排除

### 常见问题

**Q: 获取数据失败？**
A: 检查网络连接和股票代码是否正确

**Q: 回测结果异常？**
A: 检查日期范围和参数设置

**Q: 图表显示问题？**
A: 确保安装了 matplotlib 和相关依赖

**Q: 内存不足？**
A: 缩短回测时间范围或减少数据量

## 🚀 扩展建议

1. **添加更多技术指标** (RSI, KDJ, 布林带)
2. **实现多时间框架分析**
3. **添加基准对比功能**
4. **集成风险管理模块**
5. **支持更多数据源**

## 📞 技术支持

如有问题，请检查：
1. 日志输出信息
2. 参数配置是否正确
3. 数据可用性
4. 依赖库版本

---

*Happy Backtesting! 📊📈* 