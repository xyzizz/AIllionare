from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.llm import LLM
from src.macd_trader.tools.notification_tools import WechatNotificationTool
from src.macd_trader.tools.yfinance_tools import YFinanceMACDTool
from src.macd_trader.tools.longbridge_tools import LongBridgeMACDTool

notification_tool = WechatNotificationTool()
yf_fetcher_tool = YFinanceMACDTool()
lb_fetcher_tool = LongBridgeMACDTool()
llm = LLM.deepseek()


@CrewBase
class TradingCrew:
    """TradingCrew defines the agents and tasks for the automated trading system."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def data_fetcher(self) -> Agent:
        return Agent(
            config=self.agents_config["data_fetcher"],
            tools=[lb_fetcher_tool],
            llm=llm,
            verbose=True,
        )

    @agent
    def trading_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["trading_strategist"],
            llm=llm,
            verbose=True,
        )

    @agent
    def investment_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config["investment_advisor"],
            llm=llm,
            tools=[notification_tool],
            verbose=True,
        )

    # @agent
    # def trader(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config["trader"],
    #         tools=[trading_tool.execute_buy_order, trading_tool.execute_sell_order],
    #         # llm=self.llm,
    #         verbose=True,
    #     )

    # --- Tasks --- #

    @task
    def fetch_data_task(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_data_task"],
            agent=self.data_fetcher(),
        )

    @task
    def analyze_macd_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_macd_task"],
            agent=self.trading_strategist(),
            context=[self.fetch_data_task()],
        )

    @task
    def generate_advice_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_advice_task"],
            agent=self.investment_advisor(),
            context=[self.analyze_macd_task()],
        )

    # @task
    # def execute_trade_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["execute_trade_task"],
    #         agent=self.trader(),
    #         context=[self.analyze_macd_task()],
    #     )

    @crew
    def crew(self) -> Crew:
        """Creates the Trading Crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )
