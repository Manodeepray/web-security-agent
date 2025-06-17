---
Task: 3. Save settings by submitting the form on the admin settings page
Workflow:
Step 1: Navigate to the admin settings page by going to the URL: http://127.0.0.1:5000/admin/settings
Step 2: Fill out the form with the required information, the form details are as follows:
  - Form action: /admin/settings
  - Form method: POST
  - Form inputs:
    - text: site_name
    - email: support_email
Step 3: Locate the button to submit the form, the button details are as follows:
  - Button type: submit
  - Button text: Save Settings
Step 4: Press the Save Settings button to submit the form and save the settings.
Step 5: The form submission will send a POST request to the URL: http://127.0.0.1:5000/admin/settings with the provided form data.
Step 6: After submitting the form, the page may redirect to a different URL, in this case, it may stay on the same page or redirect to one of the following URLs: 
  - http://127.0.0.1:5000/dashboard
  - http://127.0.0.1:5000/contacts
  - http://127.0.0.1:5000/tickets
  - http://127.0.0.1:5000/admin 
  but for the purpose of this task, the specific redirect URL is not relevant as long as the settings are saved.