
import asyncio
from urllib.parse import urljoin
from pyppeteer import launch
import re
import pprint

import llm_bridge
import argparse
 

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
    
    print(f"\n\n current page links : {full_links}","\n\n")

    
    for link in full_links:
        
        if link not in visited_links:
            print(f"\n adding {link} to queue")
            queue_links.append(link)
    
    print(f"\n\nqueue_links : {queue_links}","\n\n")

    for link in full_links:
        if link in visited_links:
            print(f"\nremoving {link} from queue")
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
        print(f" \033[93m AGENT response  {parsed_response} \033[0m")

        parsed_page_dict = {}
        parsed_page_dict['page'] = page['page_url']
        parsed_page_dict['response'] = parsed_response
    
        parsed_pages.append(parsed_page_dict)
    
    
    
    return parsed_pages


def remove_redundant_combine(llm , parsed_pages):
    
    prompt = llm.combination_redundancy_prompt(parsed_pages = parsed_pages)
    
    combined_response = llm.get_response(prompt= prompt)
    combined_response = combined_response.choices[0].message.content
    print(f" \033[93m AGENT response  {combined_response} \033[0m")

    
    
    
    return combined_response




def task_extraction(llm , combined_response):
    tasks_response = llm.get_response(prompt = llm.get_task_prompt(context = combined_response , parse_type = 'combined'))
    tasks_response = tasks_response.choices[0].message.content
    
    print(f" \033[93m AGENT response on tasks extraction : \033[0m   {tasks_response}")
    
    return tasks_response




def get_detailed_workflows(llm , tasks_response , combined_response ):
    
    tasks_list = [task.strip() for task in tasks_response.split("#####") if task.strip()]

    
    detailed_workflows = []
    

    for i, task in enumerate(tasks_list, 1):

        prompt = llm.get_detailed_workflow_prompt(task = task , combined_response= combined_response)

        workflow = llm.get_response(prompt = prompt)
        workflow = workflow.choices[0].message.content
        
        detailed_workflows.append(workflow)
    
    print(f" \033[93m AGENT response on workflow creation : \033[0m ")

    for i , workflow in enumerate(detailed_workflows):
        print(f" \n workflow {i} : {workflow}")
    
    return detailed_workflows


# def delete_previous_workflows(directory = WORKFLOW_DIR) -> None:

#     workflow_lists = os.listdir(path= WORKFLOW_DIR)
    
#     for path

#     return None



def save_workflows(detailed_workflows , directory = WORKFLOW_DIR):
    
    print("\n \033[93m Saving workflows \033[0m")
    
    for i ,  workflow in enumerate(detailed_workflows):
        
        file_name = f"Workflow_{i}.md"
        save_path = os.path.join(directory , file_name )
        
        
        print(f"\033[93m Saving workflow {i} as {save_path} \033[0m")
        
        with open(save_path , 'w' , encoding= 'utf-8') as f:
            f.write(str(workflow)) 


    return None




















######################################################## MAIN ##################################################################################

def main(URL) -> None:
    
    
    
    
    asyncio.get_event_loop().run_until_complete(extract( home_url = URL))
    
    # print(f"\n\n\n visited_links {visited_links}")
    # print(f"\n\n\n pages = {pages}")
    
    
    context = get_context()
    
    
    # context = "ehe"# dummy context 
    
    
    # breakpoint()
    
    
    
    print(f" \033[91m INITIALIZING AGENT  \033[0m")
    
    bridge = llm_bridge.Bridge()
    
    print(f" \033[91m STARTING AGENT LOOP  \033[0m")

    
    
    print(f"\n \033[92m AGENT loop 1 : Parsing pages through agent for finding relations btwn pages \033[0m")
    
    
    
    parsed_pages = parse_pages(llm = bridge)
    
    print(f" \033[92m AGENT loop 1 complete : Iterated through the pages for finding relations in btwn  \033[0m")






    
    print(f"\n \033[92m AGENT loop 2 : Taking the relations extracted from each parsed page and combining them, while removing redundant or duplicate information. \033[0m")

    
    combined_response = remove_redundant_combine(llm= bridge , parsed_pages= parsed_pages)
    
    
    print(f" \033[92m AGENT loop 2 complete : Combined extracted parsed_pages data and removed redundant data \033[0m")


    




    print(f"\n \033[92m AGENT loop 3 : Taking the combined data and creating the required task flows i.e extracting the tasks. \033[0m")

        
    tasks_response = task_extraction(llm = bridge , combined_response= combined_response)
    

    print(f"\n \033[92m AGENT loop 3 complete: Tasks response Extracted . \033[0m")




    print(f"\n \033[92m AGENT loop 4 : Taking the combined data and tasks list to create detailed workflow for each task. \033[0m")


    detailed_workflows = get_detailed_workflows(llm = bridge , tasks_response = tasks_response  , combined_response = combined_response)
    
    print(f"\n \033[92m AGENT loop 4 complete: Detailed Workflows Generated . \033[0m")


    
    save_workflows(detailed_workflows)

    print(f" \033[91m CLOSING AGENT LOOP  \033[0m")

    
    return None





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