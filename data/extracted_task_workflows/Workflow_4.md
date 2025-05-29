---
Task: 5. Add a new ticket by filling out the form on the tickets/add page and submitting it via the 'Submit Ticket' button
Workflow:
Step 1: Navigate to http://127.0.0.1:5000/dashboard.
Step 2: Click on the link that navigates to http://127.0.0.1:5000/tickets.
Step 3: Click on the link that navigates to http://127.0.0.1:5000/tickets/add.
Step 4: Fill out the form with the action URL '/tickets/add' and method 'POST'. The form has two inputs: 
    - a select input for 'contact_id' and 
    - a textarea input for 'issue'. 
    Fill in the required information for 'contact_id' and 'issue'.
Step 5: Press the 'Submit Ticket' button which is a submit button with the text 'Submit Ticket' to submit the form.
Step 6: The form will be submitted to the URL http://127.0.0.1:5000/tickets/add via a POST request, and the automation agent can verify that the ticket has been added successfully.