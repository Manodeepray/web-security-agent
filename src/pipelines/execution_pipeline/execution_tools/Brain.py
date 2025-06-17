from groq import Groq
import asyncio
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

import re

from langchain_groq import ChatGroq

from langchain_core.prompts import PromptTemplate







load_dotenv(dotenv_path="./.env")


GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

class WorkflowExtractor:
    """ the LLM bridge that acts as the controlling agent throughout the project
    """
    def __init__(self) -> None:
        
        self.llm  = Groq(
                    api_key=GROQ_API_KEY,
                    )   
        self.response_count : int = 0
        
        self.response_limit : int = 100
        
        
        
   
        
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
    
    
    def create_tools_workflow(self , state , wf ):

        prompt = f"""
        You are a workflow planner agent.

        ## Objective:
        You are given:
        1. A task to complete.
        2. A list of natural language steps that must be followed in sequence.
        3. A list of available tools (functions) in JSON format — each tool has a name and a description.

        Your job:
        - Match each step with the most appropriate tool.
        - Describe the specific action and **arguments/parameters** the tool should use.
        - Include details like which values are passed in (if relevant).
        - if there is a form to fill do not have a step to click button to subimt form as filling it would submit it automaticaly
        - DO NOT REPEAT SAME STEPS
        ---

        ## Task:
        {wf["task"]}

        ## Steps:
        {wf["workflow_steps"]}

        ## Input Values (e.g. for forms):
        {wf.get("values", {})}

        ## Available Tools (in JSON):
        {state["tools"]}

        ---

        ## Output format:
        Produce a **single-line string**, no newlines. For each step, use this format:

        `StepDescription -> ToolName -> DetailedAction`

        Where:
        - `StepDescription` is a natural language summary of the step.
        - `ToolName` is the name of the tool to use.
        - `DetailedAction` explains exactly what the tool should do, including what arguments or values are used (if applicable).

        Separate each step with ` || ` (double pipe). Do not add newlines or extra commentary.

        ---

        ## Example Output:
        Navigate to the contact creation page -> navigate_to_link -> Go to relative URL '/contacts/add' from base URL || Fill out the form with name, email, and notes -> form_filling_tool -> Fill 'name' with 'John Doe', 'email' with 'john@example.com', and 'notes' with 'New lead from campaign' || Click the submit button -> click_button_by_html -> Find and click button with text 'Save Contact' and type='submit'

        Only return the result in the required format.
        """



        # response = llm.invoke(prompt)
        # toolflow = response.content

        response = self.get_response(prompt)
        toolflow = response.choices[0].message.content

        tool_flow_list = toolflow.split("||")

        return tool_flow_list
        
        
def get_parsed_plan(tool_flow_list):
    print(tool_flow_list)
    parsed_plan = []
    for s in tool_flow_list:
        parsed = {}

        match = re.match(r"^(.*?)\s*->", s)
        if match:
            step_description = match.group(1).strip()
            print(step_description)

        match = re.match(r"^[^>]*->\s*([^>]+?)\s*->", s)
        if match:
            tool_name = match.group(1).strip()
            print(tool_name)

        match = re.match(r"^[^>]*->[^>]*->\s*(.*)$", s)
        if match:
            action = match.group(1).strip()
            print(action)
            
        parsed['step'] = step_description
        parsed['tool'] = tool_name
        parsed['action'] = action
        print(parsed)
        parsed_plan.append(parsed)
    
    return parsed_plan
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
class ExecuterAgent():
    
    def __init__(self):
        GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

        # Groq model setup (e.g., Mixtral)
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile",  # or gemma-7b-it, llama3-8b-8192
            groq_api_key=GROQ_API_KEY # or set via env variable
        )


        
    def get_agent(self):
        return self.llm
        



    def get_agent_prompt(self):
        prompt = PromptTemplate.from_template("""
                You are an automation agent. Your job is to decide which tool to use and what values to fill in, based on the page's HTML and the current step.

                Available tools:
                - navigate_to_link
                - form_filling_tool
                - click_button_by_html

                Each tool has its own input format:
                - navigate_to_link: {{ "relative_url": "..." }}
                - form_filling_tool: {{ "form_html": "...", "values": {{ "name": "...", "email": "...", "notes": "..." }} }}
                - click_button_by_html: {{ "button_html": "..." }}

                Reply with a JSON object:
                {{ "tool": "...", "tool_args": {{ ... }} }}


                only when filling form fill the empty values with some examples 


                Step: {step_description}

                Action for the agent to do : {step_action}
                Current Page HTML:
                {page_html}


                - Choose the correct tool and provide only the **required minimal arguments**.
                - Wrap the final output in **markdown-style fenced code block** with `json`, like this:
                - fill the form values with dummy names

                ```json
                ```




                """)
        return prompt























######################################################### MAIN #########################################################################

if __name__ == "__main__":
    
    llm = Bridge()
    
    
    page = {'title': ['<h2>➕ Add New Contact</h2>'], 'page_url': 'http://127.0.0.1:5000/contacts/add', 
            'links': ['/dashboard', '/contacts', '/tickets', '/admin', '/contacts'], 
            'buttons': ['<button type="submit">Save Contact</button>'], 
            'forms': ['<form action="/contacts/add" method="post">\n    <label for="name">Name:</label><br>\n    <input type="text" name="name" required=""><br><br>\n\n    <label for="email">Email:</label><br>\n    <input type="email" name="email" required=""><br><br>\n\n    <label for="notes">Notes:</label><br>\n    <textarea name="notes" rows="4" cols="50"></textarea><br><br>\n\n    <button type="submit">Save Contact</button>\n</form>']
            }
    
    
    
    prompt = llm.get_individual_page_parsing_prompt(page_url =  page['page_url'] ,
                                                           buttons = page['buttons'] ,
                                                           forms = page['forms'] ,
                                                           linked_urls = page['links'])
    response = llm.get_response(prompt=prompt)
    
    
    print(response.choices[0].message.content)