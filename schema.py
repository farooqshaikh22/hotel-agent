from agno.agent import Agent
from agno.tools.serperapi import SerperApiTools
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Annotated


# define an Annotated alias for readability
ChildrenAges = Annotated[
    List[int], 
    Field(
        default_factory=list,
        description="A list of children ages; length must equal 'children'.",
        min_length=0,
        max_length=8
          )
    ]


class HotelsInput(BaseModel):
    
    location:str = Field(...,description="Location of the hotel")
    check_in_date:str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Check-in date. The format is YYYY-MM-DD. e.g. 2024-06-22")
    check_out_date:str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Check-out date. The format is YYYY-MM-DD. e.g. 2024-06-28")
    adults:Optional[int] = Field(default=1, ge=1, description="Number of adults. Default to 1.")
    children:Optional[int] = Field(default=0, ge=0, description="Number of children. Default to 0.")
    children_ages: ChildrenAges
    rooms:Optional[int] = Field(default=1, ge=1, description="Number of rooms. Default to 1.")
    
    @model_validator(mode="after")
    def check_children_ages(self)->"HotelsInput":
        """
        Make sure that children_ages list length equals children count.
        This runs *after* all field-level parsing/validation.
        
        """
        # children = values.get("children",0)  ## children count
        # ages = values.get("children_ages",[])  ## list of children's ages
        
        if len(self.children_ages) != (self.children or 0):
            raise ValueError(f"'children_ages' must have exactly {self.children} entries; got {len(self.children_ages)}")
        
        return self
    
        
        
class Hotel(BaseModel):
    name:str
    address:str | None
    price:str | None
    rating:float | None
    link:str | None  
    

class HotelsOutput(BaseModel):
    hotels: List[Hotel] = Field(..., description="List of matched hotels")
    

