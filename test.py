raw_tasks = """
1. Navigate from dashboard to contacts, tickets, or admin page
#####
2. Navigate from contacts to dashboard, tickets, admin, or add contact page
#####
3. Search for a contact using the search form on the contacts page
#####
4. Navigate from tickets to dashboard, contacts, admin, or add ticket page
#####
5. Add a new contact by filling out the form on the add contact page and submitting it
#####
6. Submit a new ticket by filling out the form on the add ticket page and submitting it
#####
7. Navigate from admin settings to dashboard, contacts, tickets, or admin page
#####
8. Save admin settings by filling out the form on the admin settings page and submitting it
#####
9. Navigate from add contact page to dashboard, contacts, tickets, or admin page
#####
10. Navigate from add ticket page to dashboard, contacts, tickets, or admin page
"""

# Split by delimiter and clean up
task_list = [task.strip() for task in raw_tasks.split("#####") if task.strip()]


    
