---
Task: 6. Save a new contact by clicking the "Save Contact" button on the contacts add page
Workflow:
Step 1: Navigate to http://127.0.0.1:5000/dashboard
Step 2: Click on the link that navigates to http://127.0.0.1:5000/contacts
Step 3: On the http://127.0.0.1:5000/contacts page, click on the link that navigates to http://127.0.0.1:5000/contacts/add
Step 4: On the http://127.0.0.1:5000/contacts/add page, fill out the form with the required information: 
    - Fill input type 'text' with name 'name' with the contact's name
    - Fill input type 'email' with name 'email' with the contact's email
    - Fill textarea type with name 'notes' with any additional notes about the contact
Step 5: On the http://127.0.0.1:5000/contacts/add page, locate the button with type 'submit' and text 'Save Contact' and click it, which will submit the form to http://127.0.0.1:5000/contacts/add via the POST method
Step 6: After submitting the form, the new contact should be saved and the page should redirect to one of the linked pages (http://127.0.0.1:5000/dashboard, http://127.0.0.1:5000/contacts, http://127.0.0.1:5000/tickets, http://127.0.0.1:5000/admin) as per the given context.