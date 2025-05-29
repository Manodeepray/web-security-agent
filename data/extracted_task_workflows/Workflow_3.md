---
Task: 4. Add a new contact by filling out the form on the contacts/add page and submitting it via the 'Save Contact' button
Workflow:
Step 1: Navigate to http://127.0.0.1:5000/contacts/add from any of the following pages: http://127.0.0.1:5000/dashboard, http://127.0.0.1:5000/contacts, http://127.0.0.1:5000/tickets, or http://127.0.0.1:5000/admin.
Step 2: Fill out the form with the following inputs on the http://127.0.0.1:5000/contacts/add page: 
    - name (text input)
    - email (email input)
    - notes (textarea input)
Step 3: Locate the 'Save Contact' button on the http://127.0.0.1:5000/contacts/add page with type='submit' and text='Save Contact', then press it to submit the form.
Step 4: The form will be submitted to the action URL '/contacts/add' using the POST method.
Step 5: After submitting the form, the agent can navigate to any of the following pages: http://127.0.0.1:5000/dashboard, http://127.0.0.1:5000/contacts, http://127.0.0.1:5000/tickets, or http://127.0.0.1:5000/admin.