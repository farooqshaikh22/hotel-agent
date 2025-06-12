import os
from agno.models.groq import Groq
from agno.models.google import Gemini
from agno.agent import Agent
from tools2 import search_hotels
from schema import Hotel, HotelsInput, HotelsOutput
from dotenv import load_dotenv

load_dotenv()

def build_hotel_agent()->Agent:
    
    model = Gemini(api_key=os.getenv("GOOGLE_API_KEY"),id="gemini-2.0-flash")
    # model=Groq(id="llama-3.3-70b-versatile")
    
    agent = Agent(
        model=model,
        name="hotel search agent",
        instructions=(
            "You are a hotel-booking assistant. "
            "When given user criteria for location, dates, and party composition, "
            "use the `search_hotels` tool to find matching hotels. "
            "Always output only the structured JSON defined by the HotelsOutput schema."
        ),
        description=(
            "Handles user requests to search for hotels. "
            "Validates input against HotelsInput and returns a JSON listing of hotels "
            "including name, address, price, rating, and link."
        ),
        tools=[search_hotels],
        # response_model=HotelsOutput,
        markdown=True,
        show_tool_calls=True,
        debug_mode=True,
               
    )
    
    return agent

if __name__ == "__main__":
    agent = build_hotel_agent()

    agent.print_response("Find hotels in New York from 2025-07-10 to 2025-07-15 for 2 adults and 1 rooms", stream=True)