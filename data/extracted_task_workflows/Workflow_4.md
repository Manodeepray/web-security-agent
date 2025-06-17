---
Task: Submit a new ticket by filling out and submitting the form on the tickets add page
Workflow:
Step 1: Navigate to http://127.0.0.1:5000/dashboard
Step 2: Click on the link that navigates to http://127.0.0.1:5000/tickets
Step 3: Click on the link that navigates to http://127.0.0.1:5000/tickets/add
Step 4: Fill out the form with action '/tickets/add' and method 'POST' by providing the required inputs: 
    - select: contact_id 
    - textarea: issue
Step 5: Press the Button with type='submit' and text='Submit Ticket' to submit the form
Step 6: The automation agent should now be on the page http://127.0.0.1:5000/tickets or a page that indicates a successful ticket submission, depending on the application's implementation.