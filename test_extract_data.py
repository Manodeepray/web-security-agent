
import asyncio
from urllib.parse import urljoin
from pyppeteer import launch
import re
import pprint

import llm_bridge

visited_links = list()
pages : list[dict]= list()
queue_links = []

ignore_count: int = 3


ignore_links: dict[str] = {
    
    "http://127.0.0.1:5000/admin" : 0,
                
}



async def extract_page_name(page):
    # Try to get <title> tag first
    # title = await page.title()
    
    # If <title> is missing, fall back to first heading
    
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







def main(URL) -> None:
    
    
    
    
    asyncio.get_event_loop().run_until_complete(extract( home_url = URL))
    
    # print(f"\n\n\n visited_links {visited_links}")
    # print(f"\n\n\n pages = {pages}")
    
    
    context = get_context()
    
    
    # context = "ehe"# dummy context 
    
    # breakpoint()
    bridge = llm_bridge.Bridge()
    
    tasks = bridge.get_response(prompt = bridge.get_task_prompt(context = context , parse_type = 'pages'))
    
    print(f" \033[91m response on tasks : \033[0m   {tasks.choices[0].message.content}")
    
    response : str = f"response on tasks extraction : \033[0m :  {tasks.choices[0].message.content}"
    
    
    return None





if __name__ == '__main__':
    
    
    URL = 'http://127.0.0.1:5000'
    
    main(URL = URL)