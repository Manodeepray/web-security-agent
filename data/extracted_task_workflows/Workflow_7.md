---
Task: 8. Move to the add ticket page from various other pages to create a new ticket
Workflow:
Step 1: Navigate to http://127.0.0.1:5000/dashboard and click on the link that navigates to http://127.0.0.1:5000/tickets.
Step 2: From http://127.0.0.1:5000/tickets, click on the link that navigates to http://127.0.0.1:5000/tickets/add to access the add ticket page.
Step 3: Alternatively, navigate to http://127.0.0.1:5000/contacts and click on the link that navigates to http://127.0.0.1:5000/tickets, then click on the link that navigates to http://127.0.0.1:5000/tickets/add.
Step 4: Another option is to navigate to http://127.0.0.1:5000/admin/settings, then click on the link that navigates to http://127.0.0.1:5000/tickets, and finally click on the link that navigates to http://127.0.0.1:5000/tickets/add.
Step 5: Once on the http://127.0.0.1:5000/tickets/add page, fill out the form with the required information, which includes selecting a contact ID from a select input and describing the issue in a textarea input.
Step 6: Submit the form by clicking the button with type='submit' and text='Submit Ticket' to create a new ticket.
Step 7: Verify that the new ticket has been created by checking the http://127.0.0.1:5000/tickets page for the newly added ticket.