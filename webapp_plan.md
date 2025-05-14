Perfect — we'll build a **Flask web app with *multiple workflows*** that YURASCANNER can explore. Below is a refined and expanded version of the **MiniCRM** example to include **multiple task flows**, deeply nested forms, and interactive UI elements.

---

## 💼 Final App Use Case: `MiniCRM` — A Flask-Based CRM with Multiple Workflows

---

### ✅ Workflows / Task Flows Overview (that YURASCANNER will explore):

| Workflow ID | Task Description                                           | Route Chain                                                                 |
|-------------|------------------------------------------------------------|------------------------------------------------------------------------------|
| **WF1**     | **Add a new Contact**                                      | `/dashboard` → `/contacts` → `/contacts/add`                                |
| **WF2**     | **Edit existing Contact**                                  | `/dashboard` → `/contacts` → `/contacts/edit/<id>`                          |
| **WF3**     | **Add a Support Ticket for a Contact**                     | `/dashboard` → `/tickets` → `/tickets/add` (select contact)                 |
| **WF4**     | **View All Tickets & Ticket Details**                      | `/dashboard` → `/tickets` → `/tickets/view/<id>`                            |
| **WF5**     | **Admin Settings Configuration (Deep State)**              | `/dashboard` → `/admin` → `/admin/settings`                                 |
| **WF6**     | **Delete a Contact (confirmation screen)**                 | `/dashboard` → `/contacts` → `/contacts/delete/<id>`                        |
| **WF7**     | **Search for a Contact (Form Input with GET parameter)**   | `/dashboard` → `/contacts/search?query=...`                                 |

---

## 📁 Flask App Folder Structure

```plaintext
minicrm/
├── app.py
├── templates/
│   ├── layout.html
│   ├── dashboard.html
│   ├── contacts.html
│   ├── add_contact.html
│   ├── edit_contact.html
│   ├── delete_contact.html
│   ├── tickets.html
│   ├── add_ticket.html
│   ├── ticket_detail.html
│   ├── settings.html
│   ├── search.html
└── static/
    └── style.css (optional)
```

---

## 🔧 Features That Support YURASCANNER Testing

| Feature Type               | Examples in App                                                            |
|---------------------------|-----------------------------------------------------------------------------|
| Multi-step workflows      | Nested flows like `Add Ticket` → `Select Contact` → `Submit Ticket`        |
| CRUD for multiple entities| Contacts, Tickets                                                           |
| Deep States               | `/admin/settings` only reachable after 2–3 clicks                           |
| Input forms               | Contact creation, ticket notes, settings change                            |
| Stored XSS vector         | Ticket description or contact notes shown with `| safe`                    |
| Interactive UI elements   | Links, buttons, forms, dropdowns                                           |

---

## 🛠️ Next Step: Get All Code

I will now send you **all the code files** one by one. Each will be clearly marked (e.g., `app.py`, `add_contact.html`, etc.).

Shall I start with:
1. `app.py`
2. Then all HTML templates one by one?

Let me know if you want a zip or copy-paste format for each.