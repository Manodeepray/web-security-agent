---
Task: 3. Add a new contact by filling out the form on the contacts add page and submitting it
Workflow:
Step 1: Navigate to http://127.0.0.1:5000/dashboard
Step 2: Click on the link that navigates to http://127.0.0.1:5000/contacts
Step 3: Click on the link that navigates to http://127.0.0.1:5000/contacts/add
Step 4: Fill out the form with the following details:
    - action URL: /contacts/add
    - method: POST
    - inputs: 
        - name (text input)
        - email (email input)
        - notes (textarea input)
Step 5: Fill in the required input fields with the new contact's information:
    - text input for 'name'
    - email input for 'email'
    - textarea input for 'notes'
Step 6: Press the button with type='submit' and text='Save Contact' to submit the form
Step 7: The automation agent should now be on the page that handles the form submission, which could be http://127.0.0.1:5000/contacts/add or http://127.0.0.1:5000/contacts, depending on the application's implementation. The agent can verify the contact was added by checking for the presence of the new contact's information on this page.