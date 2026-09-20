from pydantic import BaseModel, Field
from typing import Optional, Dict

class PersonalInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="اسم المستخدم")
    
    current_role: Optional[str] = Field(
        default=None,
        description="The job title and company are combined into a single phrase—for example, ""AI Engineer at IBM,"" or ""Former AI Engineer at IBM"" if the person has left the company."
    )
    
    education: Optional[str] = Field(default=None, description="Educational Qualification")
    graduation_date: Optional[str] = Field(default=None, description="Graduation Date")
    birthday: Optional[str] = Field(default=None, description="date of birth")
    
    languages: Optional[Dict[str, str]] = Field(
        default=None,
        description="Languages ​​and the proficiency level of each, e.g., {'Arabic': 'native', 'English': 'B2'}"
    )
    
    military_service: Optional[Dict[str, str]] = Field(
        default=None,
        description="Military service period (if applicable, for men): {'start': '...', 'end': '...'}"
    )
    
    additional_notes: Dict[str, str] = Field(
        default_factory=dict,
        description="Any other personal information not covered by the fields above (hobbies, family, projects, etc.) — use a clear label for each piece of information."
    )
    summary: Optional[str] =Field(
        default=None,
        description=  """Write a general summary containing all relevant information about the person, like this: 
        ""My name is Ziad Elshaque. I am a software engineering graduate with a degree in Computer Science from Sadat University. I am 23 years old and currently completing my military service,
          which ends in March 2027. After that, I plan to launch my career as an AI engineer."" """)