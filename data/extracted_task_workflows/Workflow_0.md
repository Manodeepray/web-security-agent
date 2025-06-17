---
Task: Navigate between all major pages like dashboard, contacts, tickets, admin, etc.
Workflow:
Step 1: Start at the dashboard page by navigating to http://127.0.0.1:5000/dashboard.
Step 2: From the dashboard page, navigate to the contacts page by clicking on the link that leads to http://127.0.0.1:5000/contacts.
Step 3: On the contacts page, locate the form with action '/contacts/search' and method 'GET', and fill in the 'query' input field, then press the 'Search' button (type='submit', text='Search') to submit the form.
Step 4: From the contacts page, navigate to the tickets page by clicking on the link that leads to http://127.0.0.1:5000/tickets.
Step 5: On the tickets page, navigate to the admin page by clicking on the link that leads to http://127.0.0.1:5000/admin/settings.
Step 6: On the admin settings page, locate the form with action '/admin/settings' and method 'POST', fill in the 'site_name' and 'support_email' input fields, then press the 'Save Settings' button (type='submit', text='Save Settings') to submit the form.
Step 7: From the admin settings page, navigate back to the contacts page by clicking on the link that leads to http://127.0.0.1:5000/contacts.
Step 8: On the contacts page, navigate to the add contact page by clicking on the link that leads to http://127.0.0.1:5000/contacts/add.
Step 9: On the add contact page, locate the form with action '/contacts/add' and method 'POST', fill in the 'name', 'email', and 'notes' input fields, then press the 'Save Contact' button (type='submit', text='Save Contact') to submit the form.
Step 10: From the add contact page, navigate to the tickets page by clicking on the link that leads to http://127.0.0.1:5000/tickets.
Step 11: On the tickets page, navigate to the add ticket page by clicking on the link that leads to http://127.0.0.1:5000/tickets/add.
Step 12: On the add ticket page, locate the form with action '/tickets/add' and method 'POST', select a 'contact_id' and fill in the 'issue' input field, then press the 'Submit Ticket' button (type='submit', text='Submit Ticket') to submit the form.
Step 13: From the add ticket page, navigate back to the dashboard page by clicking on the link that leads to http://127.0.0.1:5000/dashboard, completing the navigation between all major pages.