#################### imports

from pyppeteer import launch
import asyncio
import langgraph
from langchain.tools import tool


from bs4 import BeautifulSoup


import json

# 1. Define your LLM
from langchain.chains import LLMChain
import os


try:
    from pipelines.execution_pipeline.execution_tools import Brain , Actuators
except:
    from .execution_tools import Brain , Actuators
import re

from rich import print 
from rich.console import Group
from rich.panel import Panel
from rich.text import Text



##################### variables

state = {
"page" : None,  # Puppeteer page instance
"home_url": None,
"curr_url": None,
"last_action": None,
"page_html": None,
"current_step": 0,
"history": [],
}


failed = {}




### other

home_url = "http://127.0.0.1:5000/"


#### dicts

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










async def run_plan(state ,agent , parsed_plan, initial_page_html , tool_registry , page,workflow_path , failed):
    # state = {
    #     "home_url":"http://127.0.0.1:5000/",
    #     "page":page,
    #     "page_html": initial_page_html,
    #     "current_step": 0,
    #     "history": []
    # }
    
    failed[workflow_path] = {} 
    
    failed_steps = []
    
    
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
            failed_steps.append(f"❌ Failed to get response from agent: {e}")
            break


        try:
            decision = get_json_from_output(decision_raw["text"]) 
            print(f" EXTRACTED JSON : {decision}")
        except Exception as e:
            print(f"❌ Failed to parse agent output: {e}")
            failed_steps.append(f"❌ Failed to parse agent output: {e}")
        
        

        tool_name = decision.get("tool")
        tool_args = decision.get("tool_args", {})
        tool_args['state'] = state
        tool_func = tool_registry.get(tool_name)


        # print(f"TOOL DETAILS : TOOL_NAME -> {tool_name} | TOOL_ARGS  -> {tool_args} | REGISTRY FUNC -> {tool_func} ")

        if tool_func is None:
            print(f"❌ Tool '{tool_name}' not found")
            failed_steps.append(f"❌ Tool '{tool_name}' not found")
            break

        
        
        try:
            print(f"🔧 Running tool: {tool_name}")
            
            result = await tool_func.ainvoke(tool_args)
            new_page_html = result.get("new_page_html", page_html)

        except Exception as e:
            print(f"❌ Error running tool: {e}")
            failed_steps.append(f"❌ Error running tool: {e}")
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
        # state["page"] = page  
        
    failed[workflow_path]["failed_steps"] = failed_steps   
        

    print("✅ All steps executed.")
    return state  , failed










async def Execute(state, wf, Agent, llm, home_url, workflow_path, failed=failed):
    
    
    

    print(Panel(Text("🚀 Launching Headless Browser", style="bold green"), title="Step 1: Browser Launch", border_style="green"))
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

    print(Panel(Text(f"🌐 Navigating to: {home_url}", style="bold cyan"), title="Step 2: Navigation", border_style="cyan"))
    page = await browser.newPage()
    await page.goto(home_url, {'waitUntil': 'networkidle2'})

    state['page'] = page
    state["home_url"] = home_url
    state["curr_url"] = page.url

    print(Panel(Text("🛠️ Initializing tools for interaction", style="bold magenta"), title="Step 3: Tool Setup", border_style="magenta"))
    tools = [
        Actuators.navigate_to_link,
        Actuators.click_button_by_html,
        Actuators.form_filling_tool,
    ]
    state['tools'] = tools

    tool_registry = {
        "navigate_to_link": Actuators.navigate_to_link,
        "form_filling_tool": Actuators.form_filling_tool,
        "click_button_by_html": Actuators.click_button_by_html
    }

    print(Panel(Text("🧠 Extracting tool-based workflow from task plan", style="bold yellow"), title="Step 4: Workflow Extraction", border_style="yellow"))
    workflow_parser = Brain.WorkflowExtractor()
    tool_flow_list = workflow_parser.create_tools_workflow(state, wf)

    print(Panel(Text(f"{tool_flow_list}", style="bold white"), title="Tool Flow List", border_style="white"))

    print(Panel(Text("📋 Parsing tool flow into structured plan", style="bold blue"), title="Step 5: Parsed Plan Creation", border_style="blue"))
    parsed_plan = Brain.get_parsed_plan(tool_flow_list=tool_flow_list)

    print(Panel(Text(f"{parsed_plan}", style="bold white"), title="Parsed Plan", border_style="white"))

    print(Panel(Text("📄 Capturing initial page HTML", style="bold green"), title="Step 6: Initial Page Snapshot", border_style="green"))
    initial_page_html = await page.content()

    print(Panel(Text("🤖 Loading agent and prompt for execution", style="bold cyan"), title="Step 7: Agent Prompt", border_style="cyan"))
    prompt = Agent.get_agent_prompt()
    agent = LLMChain(llm=llm, prompt=prompt)

    print(Panel(Text("⚙️ Running plan with tools and agent", style="bold magenta"), title="Step 8: Executing Plan", border_style="magenta"))
    state, failed = await run_plan(state, agent, parsed_plan, initial_page_html, tool_registry, page, workflow_path, failed)

    print(Panel(Text("✅ Closing browser session", style="bold red"), title="Step 9: Browser Shutdown", border_style="red"))
    await browser.close()

    
    
    summary_steps = Group(
        Text("1. Launched headless browser", style="bold green"),
        Text("2. Navigated to home URL", style="bold cyan"),
        Text("3. Initialized tools for interaction", style="bold magenta"),
        Text("4. Extracted tool flow from workflow", style="bold yellow"),
        Text("5. Parsed tool flow into structured plan", style="bold blue"),
        Text("6. Captured initial page HTML", style="bold green"),
        Text("7. Loaded agent and prompt", style="bold cyan"),
        Text("8. Executed tool plan using agent", style="bold magenta"),
        Text("9. Closed browser session", style="bold red")
    )

    print(Panel(summary_steps, title="✅ Execution Summary", border_style="bold white"))
    
    
    return state, failed
















################### main ############################3
async def workflow_execution(state , workflow_path = "data/extracted_task_workflows/Workflow_3.md" , home_url = home_url , failed = failed , ):
      
    
    wf = get_workflow_dict(workflow_path)
    
    Agent = Brain.ExecuterAgent()
    llm = Agent.get_agent()

    state  , failed = await Execute(state=state, wf=wf, Agent= Agent , llm=llm , home_url = home_url , failed = failed , workflow_path = workflow_path)

    return  state , failed





def main(workflow_path, home_url , state = None , failed = None ):



  




    print(Panel(Text("EXECUTING STEPS", style="bold red"), title=f"FOR WORKFLOW from {workflow_path}", border_style="green"))

    state, failed = asyncio.run(workflow_execution(state=state, workflow_path=workflow_path, home_url=home_url, failed=failed))

    print(Panel(Text("EXECUTING ENDED", style="bold red"), title=f"END for WORKFLOW : {workflow_path}", border_style="green"))

    # Pretty-print the failed dict with indentation
    if failed:
        failed_str = json.dumps(failed, indent=4)
        print(Panel(Text(failed_str, style="red"), title="Failed Details", border_style="red"))
    else:
        print(Panel(Text("No failures reported.", style="green"), title="Failed Details", border_style="green"))

    return state, failed
    
    
    

def batch_execution(workflow_paths , url ):
    states = []
    state = {
    "page" : None,  # Puppeteer page instance
    "home_url": None,
    "curr_url": None,
    "last_action": None,
    "page_html": None,
    "current_step": 0,
    "history": [],
    }


    failed = {}
    
    
    for workflow_path in workflow_paths:
        state  , failed = main(state=state , workflow_path = workflow_path , home_url= url , failed = failed)
        states.append(state)
        
    return states  , failed
    
    
    
if __name__ == "__main__":
    
    workflow_path , home_url = "data/extracted_task_workflows/Workflow_3.md" ,  home_url
    states  , failed = batch_execution(workflow_paths=[workflow_path] , url= home_url)
    
    # state  , failed  = main( workflow_path , home_url ) 
    
    print(failed)
    
    
