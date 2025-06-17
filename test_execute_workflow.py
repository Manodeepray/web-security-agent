#################### imports

from pyppeteer import launch
import asyncio
import langgraph
from langchain.tools import tool


from bs4 import BeautifulSoup


from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
import json

# 1. Define your LLM
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os


import llm_bridge
import re


##################### variables

#### dicts
state = {
    "page" : None,  # Puppeteer page instance
    "home_url": None,
    "curr_url": None,
    "last_action": None,
    "page_html": None,
    "current_step": 0,
    "history": [],
}


page = {}




### other

home_url = "http://127.0.0.1:5000/"
test_url = "http://127.0.0.1:5000/contacts/add"




####################### functions




def get_workflow_dict(workflow_path):

    wf={ 
    "task":None,
    "workflow_steps":None
     }

    
    
    with open( workflow_path,"r") as f:
        workflow = f.read()

   
    wf["task"] = workflow.split("Workflow")[0]
    wf["workflow_steps"] = workflow.split("Workflow")[1].split("\n")
    return wf




###### tools 









@tool
async def navigate_to_link(state: dict, relative_url: str):
    """
    Navigate to a selected link (relative path like '/dashboard')
    Args:
        state (dict): Must contain a Puppeteer page object in `state["page"]`
        relative_url (str): e.g. '/dashboard'
    Returns:
        dict: Updated state with last action
    """
    page = state["page"]
    home_url = state["home_url"]

    # Construct absolute URL
    full_url = home_url.rstrip("/") + relative_url

    try:
        await page.goto(full_url, {'waitUntil': 'networkidle2'})
        state["curr_url"] = full_url
        state["last_action"] = f"✅ Navigated to {full_url}"
        print(f"✅ Navigated to {full_url}")
        return state
    except Exception as e:
        state["last_action"] = f"❌ Failed to navigate to {full_url}: {e}"
        return state









@tool
async def click_button_by_html(state: dict, html_string: str) -> dict:
    """
    Extract button text from HTML and click it on the current page.
    Args:
        state (dict): Must contain a Puppeteer page object in `state["page"]`
        html_string (str): e.g. '<button type="submit">Save Contact</button>'
    Returns:
        dict: Updated state with last action
    """
    page = state["page"]

    # Extract visible text from the button HTML
    try:
        soup = BeautifulSoup(html_string, 'html.parser')
        target_text = soup.get_text(strip=True)
    except Exception as e:
        state["last_action"] = f"❌ Failed to parse HTML: {e}"
        return state

    # Search all clickable elements
    try:
        buttons = await page.querySelectorAll('button, input[type="button"], input[type="submit"], [onclick]')
        
        for button in buttons:
            text = await page.evaluate('(el) => el.innerText || el.value || el.getAttribute("onclick") || ""', button)
            if text and target_text.lower() in text.strip().lower():
                await button.click()
                state["last_action"] = f"✅ Clicked button with text: {text.strip()}"
                return state
        
        state["last_action"] = f"❌ No button found with text: {target_text}"
        return state
    except Exception as e:
        state["last_action"] = f"❌ Error while clicking button: {e}"
        return state

# await click_button_by_html(state , buttons)



# form filling tool 

def parse_form_fields(html):
    soup = BeautifulSoup(html, "html.parser")
    inputs = soup.find_all(['input', 'textarea'])
    field_names = [tag.get("name") for tag in inputs if tag.get("name")]
    return field_names
    

# use this to the the field values for prompt



async def fill_form_fields(page, values: dict):
    """
    Fill out and submit a form using the parsed input names and user-provided values.
    
    Args:
        state: LangGraph agent state with a Puppeteer page
        form_html: HTML string of the <form>
        values: Dict of field names and their values (e.g., {"name": "John", "email": "john@example.com"})
    """
    for field_name, field_value in values.items():
        selector = f'input[name="{field_name}"], textarea[name="{field_name}"]'
        print(selector , field_value)
        try:
            await page.waitForSelector(selector, timeout=2000)
            await page.type(selector, field_value)
            print(f"✅ Filled successfully {field_name}:")
            print(f"✅ page = {page.url}")
            
        
            
        except Exception as e:
            print(f"⚠️ Failed to fill {field_name}: {e}")
            print(f"⚠️ page = {page.url}")

    await page.click('button[type="submit"], input[type="submit"]')
    await page.waitForNavigation(timeout=5000)
    print("✅ Form submitted.")
    return "✅ Form submitted."
    # # Try to click the submit button after filling the form
    # try:
    #     await page.click('button[type="submit"], input[type="submit"]')
    #     await page.waitForNavigation(timeout=5000)
    #     print("✅ Form submitted.")
        
    # except Exception as e:
    #     return f"⚠️ Failed to submit form: {e}"






@tool
async def form_filling_tool(state: dict, form_html: str, values: dict):
    """
    Fill out and submit a form using the parsed input names and user-provided values.
    
    Args:
        state: LangGraph agent state with a Puppeteer page
        form_html: HTML string of the <form>
        values: Dict of field names and their values (e.g., {"name": "John", "email": "john@example.com"})
    """
    fields = parse_form_fields(form_html)
    filtered_values = {k: v for k, v in values.items() if k in fields}
    
    result = await fill_form_fields(state["page"], filtered_values)
    state["last_action"] = result
    return state








##### tool flow + plan

def create_tools_workflow(state , wf , llm):

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

    response = llm.get_response(prompt)
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
        
########## agent        

def get_json_from_output(text):
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)

    if match:
        json_str = match.group(1)
        json_data = json.loads(json_str)
        # print(json_data)
    else:
        print("No JSON found.")
    
    return json_data






def get_llm():
    load_dotenv(dotenv_path="./.env")


    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

    # Groq model setup (e.g., Mixtral)
    llm = ChatGroq(
        temperature=0,
        model_name="llama-3.3-70b-versatile",  # or gemma-7b-it, llama3-8b-8192
        groq_api_key=GROQ_API_KEY # or set via env variable
    )


    return llm

def get_agent_prompt():
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

async def run_plan(state ,agent , parsed_plan, initial_page_html , tool_registry , page):
    # state = {
    #     "home_url":"http://127.0.0.1:5000/",
    #     "page":page,
    #     "page_html": initial_page_html,
    #     "current_step": 0,
    #     "history": []
    # }
    
    state["page"] = page
    state["page_html"]= initial_page_html
    state["current_step"] = 0
    state["history"] = []

    for idx, step_info in enumerate(parsed_plan):
        print(f"\n➡️ Step {idx+1}: {step_info['step']}")

        page_html = state["page_html"]
        step_description = step_info["step"]
        step_action =  step_info["action"]
        # 5. LLM agent input
        agent_input = {
            "page_html": page_html,
            "step_description": step_description,
            "step_action": step_action
            
        }

        # 6. Use LLM agent to choose tool and args
        # decision_raw = await agent.ainvoke(agent_input)
        # print(decision_raw)
        # decision = json.loads(decision_raw["text"]) 

        try:
            decision_raw = await agent.ainvoke(agent_input)
            # print(f"AGENT OUTPUT : {decision_raw} \n\n")
             # assumes LLMChain returns text field
            
        except Exception as e:
            print(f"❌ Failed to get response from agent: {e}")
            break


        try:
            decision = get_json_from_output(decision_raw["text"]) 
            print(f" EXTRACTED JSON : {decision}")
        except Exception as e:
            print(f"❌ Failed to parse agent output: {e}")
        
        

        tool_name = decision.get("tool")
        tool_args = decision.get("tool_args", {})
        tool_args['state'] = state
        tool_func = tool_registry.get(tool_name)


        # print(f"TOOL DETAILS : TOOL_NAME -> {tool_name} | TOOL_ARGS  -> {tool_args} | REGISTRY FUNC -> {tool_func} ")

        if tool_func is None:
            print(f"❌ Tool '{tool_name}' not found")
            break

        
        
        try:
            print(f"🔧 Running tool: {tool_name}")
            
            result = await tool_func.ainvoke(tool_args)
            new_page_html = result.get("new_page_html", page_html)

        except Exception as e:
            print(f"❌ Error running tool: {e}")
            break

        # 7. Update state
        state["history"].append({
            "step": step_info["step"],
            "tool": tool_name,
            "args": tool_args,
            "result": result
        })
        state["page_html"] =  await page.content() 
        state["current_step"] += 1
        
        
        

    print("✅ All steps executed.")
    return state










async def agent(state , wf , llm):
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

    page = await browser.newPage()
    await page.goto(test_url, {'waitUntil': 'networkidle2'})

    state['page'] = page
    state["home_url"] = home_url
    state["curr_url"] = page.url
    
    
    tools = [
            navigate_to_link,
            click_button_by_html,
            form_filling_tool,
            ]


    
    state['tools'] = tools
    
    
    
    tool_registry = {
                        "navigate_to_link": navigate_to_link,
                        "form_filling_tool": form_filling_tool,
                        "click_button_by_html": click_button_by_html
                    }


    import llm_bridge
    workflow_parser = llm_bridge.Bridge()


    tool_flow_list = create_tools_workflow(state , wf , workflow_parser)
    print(f"\n\n \033[91m TOOLFLOW LIST \033[0m {tool_flow_list}  \n\n")
    
    
    
    
    parsed_plan = get_parsed_plan(tool_flow_list= tool_flow_list)
    
    print(f"\n\n \033[91m PARSED PLAN \033[0m {parsed_plan}  \n\n")
    
    
    
    
    initial_page_html = await page.content() # initial page html
    
    prompt = get_agent_prompt()

    agent = LLMChain(llm=llm, prompt=prompt)

    state = await run_plan( state ,agent , parsed_plan, initial_page_html , tool_registry , page)

    await browser.close()

################### main ############################3
async def main():
    workflow_path = "data/extracted_task_workflows/Workflow_3.md"
    wf = get_workflow_dict(workflow_path)
    llm = get_llm()

    await agent(state=state, wf=wf, llm=llm)

if __name__ == "__main__":
    asyncio.run(main())