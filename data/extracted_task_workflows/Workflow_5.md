---
Task: 6. Save settings by filling out the form on the admin/settings page and submitting it via the 'Save Settings' button
Workflow:
Step 1: Navigate to the admin/settings page by going to http://127.0.0.1:5000/admin/settings.
Step 2: Locate the form on the page with action="/admin/settings" and method="POST".
Step 3: Fill out the form with the required inputs: 
    - site_name (text input)
    - support_email (email input)
Step 4: Locate the button with type="submit" and text="Save Settings".
Step 5: Press the "Save Settings" button to submit the form with the POST method to /admin/settings.
Step 6: Verify that the settings have been saved successfully.