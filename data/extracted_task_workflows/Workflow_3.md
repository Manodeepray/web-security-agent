---
Task: Submit a new ticket by filling out the form on the tickets add page and clicking the "Submit Ticket" button
Workflow:
Step 1: Navigate to http://127.0.0.1:5000/dashboard
Step 2: Click on the link that navigates to http://127.0.0.1:5000/tickets
Step 3: Click on the link that navigates to http://127.0.0.1:5000/tickets/add
Step 4: Fill out the form with action '/tickets/add' and method 'POST' by providing inputs for 'select:contact_id' and 'textarea:issue'
Step 5: Locate the button with type 'submit' and text 'Submit Ticket' and click on it to submit the form
Step 6: The form submission should navigate to the tickets page or display a confirmation message, confirming that the ticket has been submitted successfully.