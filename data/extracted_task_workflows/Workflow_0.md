---
Task: Navigate between all major pages like dashboard, contacts, tickets, admin, etc.
Workflow:
Step 1: Navigate to the dashboard page at http://127.0.0.1:5000/dashboard.
Step 2: From the dashboard page, click on the link to navigate to the contacts page at http://127.0.0.1:5000/contacts.
Step 3: On the contacts page, locate the form with action '/contacts/search' and method 'GET', and fill in the 'query' input field with a search term, then press the 'Search' button (type='submit', text='Search') to submit the form.
Step 4: From the contacts page, click on the link to navigate to the tickets page at http://127.0.0.1:5000/tickets.
Step 5: From the contacts page, click on the link to navigate to the admin page at http://127.0.0.1:5000/admin.
Step 6: From the contacts page, click on the link to navigate to the add contact page at http://127.0.0.1:5000/contacts/add, fill in the form with action '/contacts/add' and method 'POST', including inputs 'name', 'email', and 'notes', then press the 'Save Contact' button (type='submit', text='Save Contact') to submit the form.
Step 7: From the tickets page, click on the link to navigate to the dashboard page at http://127.0.0.1:5000/dashboard.
Step 8: From the tickets page, click on the link to navigate to the contacts page at http://127.0.0.1:5000/contacts.
Step 9: From the tickets page, click on the link to navigate to the admin page at http://127.0.0.1:5000/admin.
Step 10: From the tickets page, click on the link to navigate to the add ticket page at http://127.0.0.1:5000/tickets/add, fill in the form with action '/tickets/add' and method 'POST', including inputs 'contact_id' and 'issue', then press the 'Submit Ticket' button (type='submit', text='Submit Ticket') to submit the form.
Step 11: From the admin page, click on the link to navigate to the dashboard page at http://127.0.0.1:5000/dashboard.
Step 12: From the admin page, click on the link to navigate to the contacts page at http://127.0.0.1:5000/contacts.
Step 13: From the admin page, click on the link to navigate to the tickets page at http://127.0.0.1:5000/tickets.
Step 14: On the admin page, locate the form with action '/admin/settings' and method 'POST', fill in the inputs 'site_name' and 'support_email', then press the 'Save Settings' button (type='submit', text='Save Settings') to submit the form.
Step 15: From the add contact page, click on the links to navigate to the dashboard, contacts, tickets, and admin pages.
Step 16: From the add ticket page, click on the links to navigate to the dashboard, contacts, tickets, and admin pages.