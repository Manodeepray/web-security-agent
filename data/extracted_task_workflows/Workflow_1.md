---
Task: 2. Search for a contact using the form on the contacts page
Workflow:
Step 1: Navigate to the contacts page at http://127.0.0.1:5000/contacts from any of the following pages: http://127.0.0.1:5000/dashboard, http://127.0.0.1:5000/tickets, http://127.0.0.1:5000/admin.
Step 2: Locate the search form on the contacts page with the action URL '/contacts/search' and method 'GET'.
Step 3: Fill in the search form with the desired query in the 'query' input field of type 'text'.
Step 4: Locate the 'Search' button of type 'submit' and press it to submit the form.
Step 5: The browser will navigate to the URL http://127.0.0.1:5000/contacts/search?query=<user_input> where <user_input> is the value entered in the 'query' field.
Step 6: The contacts page will display the search results based on the query submitted.