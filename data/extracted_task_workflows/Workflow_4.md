---
Task: Save settings by filling out the form on the admin settings page and clicking the "Save Settings" button
Workflow:
Step 1: Navigate to the admin settings page by going to http://127.0.0.1:5000/admin/settings.
Step 2: Fill out the form on the admin settings page with the required inputs: 
    - site_name (text input)
    - support_email (email input)
Step 3: Identify and press the "Save Settings" button (type='submit', text='Save Settings') to submit the form.
Step 4: The form submission will be sent to the URL specified in the form's action attribute (/admin/settings) using the POST method.
Step 5: The automation agent should verify that the form has been submitted successfully and the settings have been saved.