---
Task: 4. Add a new contact by filling out and submitting the form on the contacts add page
Workflow:
Step 1: Navigate to http://127.0.0.1:5000/dashboard
Step 2: Click on the link that navigates to http://127.0.0.1:5000/contacts
Step 3: Click on the link that navigates to http://127.0.0.1:5000/contacts/add
Step 4: Fill out the form with the following details: 
    - action: /contacts/add
    - method: POST
    - inputs: 
        - name (text): the name of the new contact
        - email (email): the email of the new contact
        - notes (textarea): any notes about the new contact
Step 5: Press the button to submit the form: 
    - type: submit
    - text: Save Contact
Step 6: Verify that the new contact has been added successfully and the page has navigated to one of the following URLs: http://127.0.0.1:5000/dashboard, http://127.0.0.1:5000/contacts, http://127.0.0.1:5000/tickets, or http://127.0.0.1:5000/admin