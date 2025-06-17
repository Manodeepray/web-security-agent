---
Task: 2. Search for a contact using the form on the contacts page with a query
Workflow:
Step 1: Navigate to http://127.0.0.1:5000/contacts from any of the linked pages (e.g., http://127.0.0.1:5000/dashboard, http://127.0.0.1:5000/tickets, http://127.0.0.1:5000/admin).
Step 2: Locate the form on the contacts page with the action URL '/contacts/search' and method 'GET'. This form has one input field of type 'text' named 'query'.
Step 3: Fill in the form with the desired query in the 'query' input field.
Step 4: Locate the button of type 'submit' with the text 'Search' and press it to submit the form.
Step 5: The form submission will send a GET request to http://127.0.0.1:5000/contacts/search with the query parameter. The resulting page should display the search results for the given query.