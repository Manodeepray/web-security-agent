from groq import Groq
import asyncio
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="./.env")


GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

class Bridge:
    """ the LLM bridge that acts as the controlling agent throughout the project
    """
    def __init__(self) -> None:
        
        self.llm  = Groq(
                    api_key=GROQ_API_KEY,
                    )   
        self.response_count : int = 0
        
        self.response_limit : int = 10
        
        
        
    
    def get_task_prompt(self, context : str  | list | dict | set , parse_type : str  ) -> str:
        
        
        # parse_type : urls , urls + buttons , urls + buttons + forms to fill 
        
        if parse_type.lower() == "urls" or parse_type.lower() == "url" : 
            task_prompt : str = f"""
                                You are an intelligent agent analyzing a web application's structure.

                                From the given list of URLs, generate:
                                1. A list of high-level tasks or features represented by each URL.
                                2. A logical workflow or user journey connecting these tasks (if applicable).

                                Provide your response in two parts:
                                - "Tasks": A bullet list of features/actions (e.g., "View Dashboard", "Manage Contacts").
                                - "Workflow": An ordered list showing how a typical user might navigate through the app.

                                URLs to analyze:
                                {context}
                                """

        elif parse_type.lower() == "pages" or parse_type.lower() == "page" : 
            task_prompt : str = f"""
                                You are an intelligent agent analyzing a web application's structure.

                                From the given list of URLs and the associated HTML content and metadata, generate:
                                1. A list of high-level tasks or features represented by each URL.
                                2. A logical workflow or user journey connecting these tasks (if applicable).

                                For each URL, consider the buttons, forms, links, page description elements, and title to infer functionality.

                                Provide your response in two parts:
                                - "Tasks": A bullet list of features/actions (e.g., "View Dashboard", "Manage Contacts").
                                - "Workflow": An ordered list showing how a typical user might navigate through the app using links and urls. 

                                context : 
                                
                                {context}
                                """
        

        
        
        
        return task_prompt
    
    def get_response(self  , prompt : str , ) -> str:
        
        if self.response_count <= self.response_limit:
            
            response  = self.llm.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": f"{prompt}",
                            }
                        ],
                        model="llama-3.3-70b-versatile",
                    )
            
            self.response_count += 1
        
        else : response = "rate limit exceedee"
        
        
        return response