---
Task: 7. Move to the add contact page from various other pages to create a new contact
Workflow:
Step 1: Navigate to http://127.0.0.1:5000/dashboard, http://127.0.0.1:5000/contacts, http://127.0.0.1:5000/tickets, or http://127.0.0.1:5000/admin/settings as the starting point.
Step 2: Identify the link to http://127.0.0.1:5000/contacts from the current page and click on it to navigate to the contacts page.
Step 3: On the http://127.0.0.1:5000/contacts page, locate the link to http://127.0.0.1:5000/contacts/add and click on it to navigate to the add contact page.
Step 4: Alternatively, if the current page has a direct link to http://127.0.0.1:5000/contacts/add, click on it to navigate to the add contact page.
Step 5: Once on the http://127.0.0.1:5000/contacts/add page, fill out the form with the required information: 
    - Fill the 'text:name' input with the contact's name.
    - Fill the 'email:email' input with the contact's email.
    - Fill the 'textarea:notes' input with any additional notes about the contact.
Step 6: After filling out the form, locate the Button with type='submit' and text='Save Contact', and press it to submit the form.
Step 7: The form will be submitted to the URL http://127.0.0.1:5000/contacts/add using the POST method.
Step 8: Upon successful submission, the new contact will be created, and the page will redirect to one of the linked pages (http://127.0.0.1:5000/dashboard, http://127.0.0.1:5000/contacts, http://127.0.0.1:5000/tickets, or http://127.0.0.1:5000/admin).