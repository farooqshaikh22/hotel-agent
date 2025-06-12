from tools1 import search_hotels
from schema import HotelsInput

# build the input
inp = HotelsInput(
    location="London",
    check_in_date="2025-06-12",
    check_out_date="2025-06-13",
    adults=2,
    children=0,
    children_ages=[],
    rooms=1
)

# call the pure function entrypoint
output = search_hotels.entrypoint(inp)
print(output.model_dump_json(indent=2))

