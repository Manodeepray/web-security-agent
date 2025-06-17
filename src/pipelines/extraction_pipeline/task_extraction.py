
import asyncio
from urllib.parse import urljoin
from pyppeteer import launch
import re
import pprint
try:
    from pipelines.extraction_pipeline.extraction_tools import llm_bridge

except:
    from .extraction_tools import llm_bridge
import argparse
import shutil
import os


########################################## variables initialized here ############################################
visited_links = list()
pages : list[dict]= list()
queue_links = []

ignore_count: int = 3


ignore_links: dict[str] = {
    
    "http://127.0.0.1:5000/admin" : 0,
                
}




WORKFLOW_DIR = "./data/extracted_task_workflows"











############################################## Functions #######################################################

async def extract_page_name(page):
    # Try to get <title> tag first
    # title = await page.title()
    
    # If <title> is missing, fall back to first heading
    print(f"\033[93m extracting page title \033[0m")
    title = await page.evaluate('''() => 
                                    {
                                    const elements = Array.from(
                                        document.querySelectorAll(
                                            'h2'
                                            
                                        ));   
                                    return elements.map(el => el.outerHTML);   
                                        
                                        
                                    }
                                    ''')

    return title


async def extract_links(page):
    
    print(f"\033[93m extracting links from <a> \033[0m")
    # Extract all hrefs from <a> tags
    links = await page.evaluate('''() => 
                                       {
                                        const elements = Array.from(
                                            document.querySelectorAll(
                                                'a'
                                                
                                            ));   
                                        return elements.map(el => el.outerHTML);   
                                           
                                           
                                       }
                                       ''') 
    
    
    # print(links)
    extracted_links = []
    for link in links:
        match = re.search(r'href=[\'"]([^\'"]+)[\'"]', link)

        if match:
            href_value = match.group(1)
            print(href_value)
        
        extracted_links.append(href_value)
        
    # breakpoint()
    
    return extracted_links 

async def extract_page_context(page):
    print(f"\033[93m extracting page content \033[0m")
    page_context = await page.evaluate('''() => 
                                       {
                                        const elements = Array.from(
                                            document.querySelectorAll(
                                                'h1, h2, h3, h4, h5, h6, p, section, article, label, li'
                                                
                                            ));   
                                        return elements.map(el => el.outerHTML);   
                                           
                                           
                                       }
                                       ''') 
    
    return page_context


async def extract_buttons(page):
    print(f"\033[93m extracting buttons \033[0m")
    buttons = await page.evaluate('''() => 
                                       {
                                        const elements = Array.from(
                                            document.querySelectorAll(
                                             'button, input[type="button"], input[type="submit"], [onclick]'   
                                                
                                            )
                                            
                                        );   
                                        return elements.map(el => el.outerHTML);   
                                           
                                           
                                       }
                                       ''') 
    
    
    return buttons

async def extract_forms(page):
    print(f"\033[93m extracting forms \033[0m")
    forms = await page.evaluate('''() => 
                                       {
                                        const elements = Array.from(
                                            document.querySelectorAll(
                                                'form'
                                                
                                            )
                                            
                                        );   
                                        return elements.map(el => el.outerHTML);   
                                           
                                           
                                       }
                                       ''') 
    
    
    return forms




async def crawl(page, base_url: str, depth: int = 0, max_depth: int = 2):
    if depth > max_depth:
        return

    url = page.url
    if url in visited_links:
        return
    
    
    visited_links.append(url)

    print(f"{'  '*depth}\033[92mVisiting:\033[0m {url}")



    page_dict = dict()

    
    print(f"\n \033[91m Start extraction from {page.url} \033[0m")
    
    page_dict['title'] = await extract_page_name(page)
    page_dict['page_url'] = page.url
    page_dict['links'] = await extract_links(page)
    page_dict['buttons'] = await extract_buttons(page)
    page_dict['forms'] = await extract_forms(page)


    pprint.pprint(page_dict , indent = 4)

    pages.append(page_dict)

    # Extract and normalize links
    raw_links = await extract_links(page)
    full_links = list(
    urljoin(base_url, href) for href in raw_links
    if href and not href.startswith("javascript")
    )
    
    # print(f"\n\n current page links : {full_links}","\n\n")

    
    for link in full_links:
        
        if link not in visited_links:
            # print(f"\n adding {link} to queue")
            queue_links.append(link)
    
    # print(f"\n\nqueue_links : {queue_links}","\n\n")

    for link in full_links:
        if link in visited_links:
            # print(f"\nremoving {link} from queue")
            try:
                queue_links.remove(link) 
            except:
                print(f"\n{link} not in queue yet")
                
                
    for link in full_links:
        if link in ignore_links:
            
            if ignore_links[link] > ignore_count:
                
                print(f"\n removing {link} from queue")
                try:
                    queue_links.remove(link) 
                except:
                    print(f"{link} not in queue yet")
            else:
                ignore_links[link] += 1
                break
                
                
                
    print(f"\n\n\n visited_links : {visited_links}")

    for link in queue_links:
        if link not in visited_links:
        
            try:
                await page.goto(link, {'waitUntil': 'networkidle2'})
                await crawl(page, base_url, depth + 1, max_depth)
                await page.goBack({'waitUntil': 'networkidle2'})
            except Exception as e:
                print(f"{'  '*depth}Failed to visit {link}: {e}")

        
        else:
            pass
                
            
async def extract(home_url = 'http://127.0.0.1:5000' ):
      # Change to your home URL
    
    
    # home_url = 'https://github.com'  # Change to your home URL
    
    
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

    page = await browser.newPage()
    await page.goto(home_url, {'waitUntil': 'networkidle2'})

 






    await crawl(page, home_url)

    await browser.close()








def get_context() -> str:
    context = f"Total visited URLs: {len(visited_links)}\nVisited URLs:\n{sorted(visited_links, key=lambda url: url.split("5000")[-1]) }\n\nPage Details:\n"

    for entry in pages:
        context += f"\n---\nURL: {entry['page_url']}\nData: {entry}\n"


    print(f"\n\n  \033[92mcontext \033[03m : {context}  \n\n")
    
    return context









def parse_pages( llm ):
    
    parsed_pages = []
    
    for i , page  in enumerate(pages):

        
        print(f" \n \033[92m AGENT parsing page  {i} : {page['page_url']} \033[0m")
        
        
        
        parsed_prompt = llm.get_individual_page_parsing_prompt(page_url =  page['page_url'] ,
                                                           buttons = page['buttons'] ,
                                                           forms = page['forms'] ,
                                                           linked_urls = page['links'])
    
    
        parsed_response = llm.get_response(prompt= parsed_prompt)
        parsed_response = parsed_response.choices[0].message.content
        # print(f" \033[93m AGENT response  {parsed_response} \033[0m")

        parsed_page_dict = {}
        parsed_page_dict['page'] = page['page_url']
        parsed_page_dict['response'] = parsed_response
    
        parsed_pages.append(parsed_page_dict)
    
    
    
    return parsed_pages


def remove_redundant_combine(llm , parsed_pages):
    
    prompt = llm.combination_redundancy_prompt(parsed_pages = parsed_pages)
    
    combined_response = llm.get_response(prompt= prompt)
    combined_response = combined_response.choices[0].message.content
    # print(f" \033[93m AGENT response  {combined_response} \033[0m")

    
    
    
    return combined_response




def task_extraction(llm , combined_response):
    tasks_response = llm.get_response(prompt = llm.get_task_prompt(context = combined_response , parse_type = 'combined'))
    tasks_response = tasks_response.choices[0].message.content
    
    print(f" \033[93m AGENT response on tasks extraction : \033[0m   {tasks_response}")
    
    return tasks_response




def get_detailed_workflows(llm, tasks_response, combined_response):
    tasks_list = [task.strip() for task in tasks_response.split("#####") if task.strip()]
    detailed_workflows = []
    workflow_panels = []

    print("[yellow bold]⚙️ AGENT: Creating Detailed Workflows for Each Task...[/yellow bold]")

    for i, task in enumerate(tasks_list, 1):
        prompt = llm.get_detailed_workflow_prompt(task=task, combined_response=combined_response)
        workflow = llm.get_response(prompt=prompt).choices[0].message.content
        detailed_workflows.append(workflow)

        panel = Panel(
            workflow,
            title=f"🧩 Workflow {i}",
            subtitle=task[:50] + "..." if len(task) > 50 else task,
            border_style="green"
        )
        workflow_panels.append(panel)

    print()  # spacing
    print(Panel(Group(*workflow_panels), title="📦 All Extracted Workflows", border_style="blue"))

    return detailed_workflows





def save_workflows(detailed_workflows, directory=WORKFLOW_DIR):
    # ---- Panel 1: Cleanup/Directory Preparation ----
    dir_ops_logs = []

    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    dir_ops_logs.append(f"[green]Deleted file:[/green] {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    dir_ops_logs.append(f"[green]Deleted folder:[/green] {file_path}")
            except Exception as e:
                dir_ops_logs.append(f"[red]Failed to delete {file_path}. Reason: {e}[/red]")
    else:
        os.makedirs(directory)
        dir_ops_logs.append(f"[cyan]Created directory:[/cyan] {directory}")

    dir_panel = Panel("\n".join(dir_ops_logs) or "[yellow]No existing files to delete[/yellow]",
                      title="🗂️ Directory Cleanup", border_style="magenta")

    # ---- Panel 2: Workflow Saving ----
    workflow_paths = []
    save_logs = []

    for i, workflow in enumerate(detailed_workflows):
        file_name = f"Workflow_{i}.md"
        save_path = os.path.join(directory, file_name)
        workflow_paths.append(save_path)
        save_logs.append(f"[bold green]Saved workflow {i}:[/bold green] {save_path}")

        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(str(workflow))

    save_panel = Panel("\n".join(save_logs), title="📝 Workflow Saving", border_style="green")

    # ---- Final Group Display ----
    print(Group(dir_panel, save_panel))

    return workflow_paths




















######################################################## MAIN ##################################################################################


from rich import print
from rich.panel import Panel
from rich.console import Group



def main(URL) -> None:
    
    steps = []

    # Step 1: Extract site
    asyncio.get_event_loop().run_until_complete(extract(home_url=URL))
    steps.append(Panel("[yellow]Web extraction completed using crawler.[/yellow]", title="Step 1: Web-Crawler"))

    # Step 2: Get context
    context = get_context()
    steps.append(Panel("[cyan]Context successfully retrieved from pages.[/cyan]", title="Step 2: Context-Extraction"))

    # Step 3: Initialize bridge
    
    bridge = llm_bridge.Bridge()

    print(Panel("[bold red]STARTING AGENT LOOP[/bold red]", title="Startup"))

    # Step 4: Agent loop 1
    print(Panel("[green]AGENT loop 1: Parsing pages for inter-page relationships...[/green]", title="Loop 1"))
    parsed_pages = parse_pages(llm=bridge)
    print(Panel("[green]AGENT loop 1 complete: Parsed page relationships.[/green]", title="Loop 1"))

    steps.append(Panel("[red]Successfully parsed pages for inter-page relationships.[/red]", title="Step 3: Relation-Generator"))
    
    
    
    # Step 5: Agent loop 2
    print(Panel("[green]AGENT loop 2: Combining and deduplicating relations...[/green]", title="Loop 2"))
    combined_response = remove_redundant_combine(llm=bridge, parsed_pages=parsed_pages)
    print(Panel("[green]AGENT loop 2 complete: Relations deduplicated and combined.[/green]", title="Loop 2"))

    steps.append(Panel("[cyan]Combining and deduplicating page relationships.[/cyan]", title="Step 4: Removing-Redundancy&Combining"))




    # Step 6: Agent loop 3
    print(Panel("[green]AGENT loop 3: Extracting task-level descriptions...[/green]", title="Loop 3"))
    tasks_response = task_extraction(llm=bridge, combined_response=combined_response)
    print(Panel("[green]AGENT loop 3 complete: Tasks extracted.[/green]", title="Loop 3"))

    steps.append(Panel("[pink]Extracting task-level descriptions.[/pink]", title="Step 5: Tasks-Extraction"))






    # Step 7: Agent loop 4
    print(Panel("[green]AGENT loop 4: Generating detailed workflows for tasks...[/green]", title="Loop 4"))
    detailed_workflows = get_detailed_workflows(llm=bridge, tasks_response=tasks_response, combined_response=combined_response)
    print(Panel("[green]AGENT loop 4 complete: Workflows generated.[/green]", title="Loop 4"))

    steps.append(Panel("[green]Detailed Workflows generated.[/green]", title="Step 6: Detailed-Workflows"))



    # Step 8: Save
    workflow_paths = save_workflows(detailed_workflows)

    steps.append(Panel("[cyan]Old Workflows deleted - new workflows saved.[/cyan]", title="Step 7: Saving-Workflows"))



    # Summary panel
    print(Panel(Group(*steps), title="Task Extractor Agent Summary", border_style="blue"))

    return combined_response, tasks_response, detailed_workflows, WORKFLOW_DIR, workflow_paths



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Optional URL argument with default")

# Add URL argument with default value
    parser.add_argument(
        '--url',
        type=str,
        default='http://127.0.0.1:5000',
        help='Base URL of the server (default: http://127.0.0.1:5000)'
    )

    # Parse the arguments
    args = parser.parse_args()

    # Use the URL
    URL = args.url

    print(f"Using URL: {URL}")
        
    
    main(URL = URL)