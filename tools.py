from agno.tools import tool
from schema import Hotel, HotelsInput, HotelsOutput
from agno.agent import Agent
from agno.tools.serperapi import SerperApiTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.models.google import Gemini
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()
model = Gemini(api_key=os.getenv("GOOGLE_API_KEY"),id="gemini-2.0-flash")
api_key = os.getenv("SERPAPI_API_KEY")

@tool(
    name="search_hotels",
    description=(
        "Search hotels via SerperApi. "
        "Inputs: HotelsInput. "
        "Returns: HotelsOutput."
    ),
    # args_schema=HotelsInput,
    # strict=True
)

def search_hotels(params:HotelsInput)->HotelsOutput:
    """
    Search for hotels using the Serper API based on provided criteria.

    Args:
        params (HotelsInput): Input model containing:
            - location: City or region for hotel search
            - check_in_date: Check-in date in YYYY-MM-DD format
            - check_out_date: Check-out date in YYYY-MM-DD format
            - adults: Number of adults
            - children: Number of children
            - children_ages: List of ages for each child
            - rooms: Number of rooms requested

    Returns:
        HotelsOutput: Pydantic model with a list of Hotel entries matching the query.
        
    """
    ##  Build base search parameters for SerpAPI
    search_params = {
        "engine": "google_hotels",
        "api_key": api_key,
        "q": f"hotels in {params.location}",
        "check_in_date": params.check_in_date,
        "check_out_date": params.check_out_date,
        "adults": params.adults,
        "children": params.children,
        "rooms": params.rooms
        
    }
    
    ## include children age if provided
    if params.children and params.children_ages:
        search_params["children_ages"] = ",".join(str(age) for age in params.children_ages)
        
    ## execute search 
    # serp = SerperApiTools(search_params)
    serp = GoogleSearch(search_params)
    data = serp.get_dict()
    # search = GoogleSearchTools(search_params)
    # data = serp.get_dict()
    
    hotels: list[Hotel] = []
    for h in data.get("properties", [])[:5]:
        hotels.append(
            Hotel(
                name=h.get("name", "").strip(),
                address=h.get("address", ""),
                price=h.get("price", ""),
                rating=h.get("rating"),
                link=h.get("link", "")
                   
            )
        )
        
    return HotelsOutput(hotels=hotels)

inp = HotelsInput(
    location="Paris",
    check_in_date="2025-08-10",
    check_out_date="2025-08-15",
    adults=1,
    children=1,
    children_ages=[4],   # must match children=1
    rooms=1
)

agent = Agent(model=model, tools=[search_hotels], show_tool_calls=True, markdown=True)
agent.print_response("Find hotels in Dubai from 2025-08-10 to 2025-08-15 for 2 adults and 1 rooms", stream=True)