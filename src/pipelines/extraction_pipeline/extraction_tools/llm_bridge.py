from groq import Groq
import asyncio
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup



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
        
        self.response_limit : int = 100
        
        
        
    
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
                                
                                
        elif parse_type.lower() == "combined" or parse_type.lower() == "relations":
            task_prompt: str = f"""
        You are an intelligent agent analyzing a website's structure. The following are the navigation and interaction relations extracted from multiple web pages:

        {context}

        Based on these relationships (between pages, buttons, and forms), identify actionable tasks that a user can perform on this website.

        - Combine similar trivial tasks such as page navigations across multiple pages into one generalized task (e.g., "Navigate between all major pages like dashboard, contacts, tickets, admin, etc.") instead of listing each individually.
        - Treat interactions like button clicks or form submissions as distinct tasks.
        - Each task must be realistic and based on the link, button, or form relations observed.
        - Number each task.
        - Separate each task using exactly five hash characters (#####).
        - Each task should be concise but clear about what the user can do and how (e.g., "Navigate from X to Y", "Search for a contact using form Z", "Submit ticket via button Q").

        Only output the list of tasks. Do not include any extra commentary or explanation. 
        
        Begin.
        """

                
        
        return task_prompt
    
    
    
    def get_individual_page_parsing_prompt(self, page_url: str, linked_urls: list, buttons: list, forms: list):
        """
        Takes the current page's URL, all child URLs in <a> tags, buttons present, and forms present.
        Creates a prompt to figure out the relation between the current URL and its children elements.
        """

        prompt = f"You are analyzing the structure of a webpage.\n\n"
        prompt += f"Current page URL: {page_url}\n\n"

        # Normalize links to full URLs
        full_links = []
        for link in linked_urls:
            full_links.append(link)
            

        if full_links:
            prompt += "Linked URLs (via <a> tags):\n"
            for url in full_links:
                prompt += f"- {page_url} --> {url}\n"
            prompt += "\n"

        if buttons:
            prompt += "Buttons on the page:\n"
            for btn_html in buttons:
                soup = BeautifulSoup(btn_html, 'html.parser')
                btn = soup.find('button')
                btn_text = btn.get_text(strip=True)
                btn_type = btn.get('type', 'N/A')
                prompt += f"- {page_url} --press--> Button(type='{btn_type}', text='{btn_text}')\n"
            prompt += "\n"

        if forms:
            prompt += "Forms on the page:\n"
            for form_html in forms:
                soup = BeautifulSoup(form_html, 'html.parser')
                form = soup.find('form')
                if not form:
                    continue  # skip if no form found

                action = form.get('action', 'N/A')
                method = form.get('method', 'GET').upper()

                inputs = []
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    name = input_tag.get('name') or input_tag.get('id') or 'unnamed'
                    field_type = input_tag.get('type', 'text') if input_tag.name == 'input' else input_tag.name
                    inputs.append(f"{field_type}:{name}")

                prompt += f"- {page_url} --fill--> Form(action='{action}', method='{method}', inputs={inputs})\n"
            prompt += "\n"

        prompt += (
            "Only return the relationships in the above format:\n"
            "page_x (url) --> page_y (url)\n"
            "page_x (url) --press--> button (details)\n"
            "page_x (url) --fill--> form (details)\n"
            "add extra explanation for further agentinc task flow operations in steps."
        )

        return prompt



    def combination_redundancy_prompt(self, parsed_pages):
        """
        Taking the relations extracted from each page and combining them,
        while removing redundant or duplicate information.
        """
        
        combined_prompt = "You are an agent combining relationships extracted from multiple web pages.\n\n"
        combined_prompt += "Each page has been analyzed and returned the following relationships:\n\n"

        # Add all individual page relations
        for i, page_output in enumerate(parsed_pages, 1):
            combined_prompt += f"--- Page {i} , {page_output['page']}  ---\n"
            combined_prompt += page_output['response'] + "\n\n"

        combined_prompt += (
            "Now, combine all the above into a concise set of unique relationships.\n"
            "Remove any redundant or duplicate entries.\n"
            "Only return in one of the following formats:\n"
            "- page_x (url) --> page_y (url)\n"
            "- page_x (url) --press--> button (details)\n"
            "- page_x (url) --fill--> form (details)\n"
            "Avoid repeating the same relationship multiple times.\n"
            "Do not add any explanations or extra commentary.\n"
        )

        return combined_prompt

    
    
    
    def get_detailed_workflow_prompt(self, task, combined_response):
        """
        Using the individual task and the cleaned, combined relations between
        pages, forms, and buttons, this function creates a detailed workflow prompt.
        
        The output should include:
        - The URLs involved in completing the task
        - Buttons that need to be pressed (with how to identify them)
        - Forms that need to be filled (with their attributes and required inputs)
        - Clear step-by-step instructions for agentic actions
        """

        workflow_prompt = f"""
        You are an intelligent agent helping to automate user tasks on a web application.
        Below is a specific task followed by the full context of page-to-page relationships, buttons, and forms.

        Your goal is to:
        1. Identify all pages and URLs involved in the task.
        2. Identify buttons involved and how to locate them in the HTML (via type, text, etc.).
        3. Identify forms involved, their action URLs, method (GET/POST), and inputs.
        4. Provide a detailed, step-by-step workflow that an automation agent can follow to complete the task.

        Format the response as follows:
        ---
        Task: [repeat the task]
        Workflow:
        Step 1: ...
        Step 2: ...
        ...

        Make sure your steps include all relevant URLs, button text, form action/method/input details. The response should be actionable by an automated browser agent.

        Task:
        {task}

        Context of page relationships and element details:
        {combined_response}

        Only output the structured workflow as described.
        """

        return workflow_prompt

    
        
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
    
################################################## TEST ##########################################################





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