import os
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.google import Gemini
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage

from tools2 import search_hotels
from schema import HotelsInput, HotelsOutput

load_dotenv()

def build_hotel_agent() -> Agent:
    # Initialize the LLM model
    model = Gemini(api_key=os.getenv("GOOGLE_API_KEY"), id="gemini-2.0-flash")

    # Set up persistent memories (user preferences, past slot values)
    memory_db = SqliteMemoryDb(table_name="user_memories", db_file="tmp/agent.db")
    memory = Memory(model=model, db=memory_db)

    # Set up chat history storage
    storage = SqliteStorage(table_name="agent_sessions", db_file="tmp/agent.db")

    # Build the Agent with memory and storage enabled
    agent = Agent(
        model=model,
        name="hotel search agent",
        instructions=(
            "You are a hotel-booking assistant. "
            "Collect location, check-in/out dates, number of adults, children (and their ages), and rooms. "
            "Children and children_ages are optional. "
            "Once all required fields are gathered, call `search_hotels` and return only the HotelsOutput JSON."
        ),
        description=(
            "Multi-turn hotel-booking assistant with slot-filling and memory persistence."
        ),
        tools=[search_hotels],
        # response_model=HotelsOutput,
        memory=memory,
        storage=storage,
        enable_agentic_memory=True,
        enable_user_memories=True,
        add_history_to_messages=True,
        num_history_runs=3,
        markdown=True,
        show_tool_calls=True,
        debug_mode=True,
    )

    return agent


def run_cli():
    agent = build_hotel_agent()
    print("Hi there! I’m here to help you book your perfect stay. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not user_input or user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        # Get agent's response
        response = agent.run(user_input).content
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    run_cli()
