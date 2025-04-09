from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.llm import LLM
from src.macd_trader.tools.notification_tools import WechatNotificationTool
from src.macd_trader.tools.stock_data_tools import StockDataTools

# Assuming you might use Deepseek directly or another OpenAI-compatible API
# You might need to adjust the base_url and api_key parameters
# Example for OpenAI compatible endpoint (like local LLM server or other providers)
# llm = ChatOpenAI(
#     model = "deepseek-coder", # Or your specific model
#     base_url = "YOUR_API_ENDPOINT", # e.g., http://localhost:11434/v1
#     api_key = os.getenv("DEEPSEEK_API_KEY", "dummy_key") # API key might not be needed for local models
# )

# If Deepseek has its own Langchain integration class:
# from langchain_community.chat_models import ChatDeepseek # Fictional example
# llm = ChatDeepseek(model="deepseek-coder", api_key=os.getenv("DEEPSEEK_API_KEY"))

# Fallback: Using a standard OpenAI compatible model for structure
# Replace this with your actual Deepseek LLM setup
# deepseek_llm = LLM.deepseek()


# Import your custom tools


# Instantiate tools
notification_tool = WechatNotificationTool()
data_fetcher_tool = StockDataTools()
# trading_tool = TradingTools()


@CrewBase
class TradingCrew:
    """TradingCrew defines the agents and tasks for the automated trading system."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self) -> None:
        # If using a non-OpenAI model compatible with Langchain ChatModel interface:
        self.llm = LLM.deepseek()  # Use the llm defined above
        # If the Deepseek model requires direct SDK use within agents/tools,
        # you might not define a global LLM here, or pass it differently.

    @agent
    def data_fetcher(self) -> Agent:
        return Agent(
            config=self.agents_config["data_fetcher"],
            tools=[data_fetcher_tool],
            llm=self.llm,  # Uncomment if you want to explicitly pass the LLM
            verbose=True,
        )

    @agent
    def trading_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["trading_strategist"],
            # No specific tools needed here as logic is in the task description
            llm=self.llm,
            verbose=True,
        )

    @agent
    def investment_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config["investment_advisor"],
            llm=self.llm,
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

    # @agent
    # def notifier(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config["notifier"],
    #         tools=[
    #             WechatNotificationTool()
    #         ],
    #         llm=self.llm,
    #         verbose=True,
    #     )

    # --- Tasks --- #

    @task
    def fetch_data_task(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_data_task"],
            agent=self.data_fetcher(),
            # You might pass expected output format details here if needed
        )

    @task
    def analyze_macd_task(self) -> Task:
        # This task requires a more complex implementation than just description
        # It needs to parse the MACD data and apply the crossover logic.
        # CrewAI tasks can execute code directly or rely on agent capabilities/tools.
        # Let's define it to depend on the fetch_data_task context.
        return Task(
            config=self.tasks_config["analyze_macd_task"],
            agent=self.trading_strategist(),
            context=[self.fetch_data_task()],  # Pass output from previous task
        )

    # @task
    # def execute_trade_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["execute_trade_task"],
    #         agent=self.trader(),
    #         context=[self.analyze_macd_task()],  # Pass decision from strategist
    #     )

    # @task
    # def send_notification_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["send_notification_task"],
    #         agent=self.notifier(),
    #         context=[self.analyze_macd_task()],  # Pass trade execution result
    #     )

    @task
    def generate_advice_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_advice_task"],
            agent=self.investment_advisor(),
            context=[self.analyze_macd_task()],  # 使用MACD分析结果
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Trading Crew."""
        return Crew(
            manager_llm=self.llm,
            function_calling_llm=self.llm,
            chat_llm=self.llm,
            agents=[
                self.data_fetcher(),
                self.trading_strategist(),
                # self.trader()
                # self.notifier(),
                self.investment_advisor(),
            ],
            tasks=[
                self.fetch_data_task(),
                self.analyze_macd_task(),
                # self.execute_trade_task(),
                # self.send_notification_task(),
                self.generate_advice_task(),
            ],
            process=Process.sequential,  # Tasks will run one after another
            verbose=False,  # Set verbosity level (0, 1, or 2)
            # memory=True # Enable memory for conversational context if needed
        )
