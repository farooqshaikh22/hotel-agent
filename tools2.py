from agno.tools import tool
from schema import Hotel, HotelsInput, HotelsOutput
from agno.agent import Agent
from agno.models.google import Gemini
from serpapi import GoogleSearch
import os
from dotenv import load_dotenv

load_dotenv()
model   = Gemini(api_key=os.getenv("GOOGLE_API_KEY"), id="gemini-2.0-flash")
api_key = os.getenv("SERPAPI_API_KEY")

@tool(name="search_hotels",
      description="Search hotels via SerpApi Google Hotels API.")
def search_hotels(params: HotelsInput) -> HotelsOutput:
    search_params = {
        "engine": "google_hotels",
        "api_key": api_key,
        "q": f"hotels in {params.location}",
        "check_in_date": params.check_in_date,
        "check_out_date":params.check_out_date,
        "adults": params.adults,
        "children": params.children,
        "rooms": params.rooms,
        **({"children_ages": ",".join(map(str, params.children_ages))}
           if params.children and params.children_ages else {})
    }

    resp = GoogleSearch(search_params).get_dict()
    results = []
    for h in resp.get("properties", [])[:5]:
        
        name   = h.get("name","").strip()
        total  = h.get("total_rate",{})
        price  = total.get("lowest") or (h.get("prices") or [{}])[0].get("rate_per_night",{}).get("lowest")
        rating = None
        if h.get("overall_rating") is not None:
            try: rating = float(h["overall_rating"])
            except: rating = None
        link = h.get("link") or h.get("serpapi_property_details_link")

        # 2) SECOND API CALL for address/details
        details_params = {
            **search_params,
            "property_token": h["property_token"],   # inject the token
        }
        detail_json = GoogleSearch(details_params).get_dict()
        address = detail_json.get("address") or detail_json.get("formatted_address")

        results.append(
            Hotel(
                name=name,
                address=address,
                price=price,
                rating=rating,
                link=link
            )
        )

    return HotelsOutput(hotels=results)

# # quick direct test
# if __name__ == "__main__":
#     inp = HotelsInput(
#         location="London",
#         check_in_date="2025-08-10",
#         check_out_date="2025-08-15",
#         adults=2,
#         children=0,
#         children_ages=[],
#         rooms=1
#     )
#     out = search_hotels.entrypoint(inp)
#     print(out.model_dump_json(indent=2))
