from flask import Flask, render_template, request, redirect, url_for, flash
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Simulated in-memory databases
contacts_db = {}
tickets_db = {}
admin_settings = {"theme": "light", "notifications": True}

# ---------------------- ROUTES ----------------------

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# -------------------- CONTACTS ----------------------

@app.route('/contacts')
def contacts():
    return render_template('contacts.html', contacts=contacts_db)

@app.route('/contacts/add', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        contact_id = str(uuid.uuid4())
        contacts_db[contact_id] = {
            'id': contact_id,
            'name': request.form['name'],
            'email': request.form['email'],
            'notes': request.form['notes'],  # 🧨 Stored XSS test point
        }
        flash('Contact added successfully!', 'success')
        return redirect(url_for('contacts'))
    return render_template('add_contact.html')

@app.route('/contacts/edit/<id>', methods=['GET', 'POST'])
def edit_contact(id):
    contact = contacts_db.get(id)
    if not contact:
        return "Contact not found", 404
    if request.method == 'POST':
        contact['name'] = request.form['name']
        contact['email'] = request.form['email']
        contact['notes'] = request.form['notes']
        flash('Contact updated!', 'info')
        return redirect(url_for('contacts'))
    return render_template('edit_contact.html', contact=contact)

@app.route('/contacts/delete/<id>', methods=['GET', 'POST'])
def delete_contact(id):
    contact = contacts_db.get(id)
    if not contact:
        return "Contact not found", 404
    if request.method == 'POST':
        del contacts_db[id]
        flash('Contact deleted.', 'danger')
        return redirect(url_for('contacts'))
    return render_template('delete_contact.html', contact=contact)

@app.route('/contacts/search')
def search_contacts():
    query = request.args.get('query', '')
    
    print(query)
    results = {k: v for k, v in contacts_db.items() if query.lower() in v['name'].lower()}
    return render_template('search.html', contacts=results, query=query)

# ---------------------- TICKETS ----------------------

@app.route('/tickets')
def tickets():
    return render_template('tickets.html', tickets=tickets_db)

@app.route('/tickets/add', methods=['GET', 'POST'])
def add_ticket():
    if request.method == 'POST':
        ticket_id = str(uuid.uuid4())
        tickets_db[ticket_id] = {
            'id': ticket_id,
            'contact_id': request.form['contact_id'],
            'issue': request.form['issue'],  # 🧨 Stored XSS test point
        }
        flash('Ticket submitted!', 'success')
        return redirect(url_for('tickets'))
    return render_template('add_ticket.html', contacts=contacts_db)

@app.route('/tickets/view/<id>')
def ticket_detail(id):
    ticket = tickets_db.get(id)
    if not ticket:
        return "Ticket not found", 404
    contact = contacts_db.get(ticket['contact_id'], {})
    return render_template('ticket_detail.html', ticket=ticket, contact=contact)

# --------------------- ADMIN -------------------------

@app.route('/admin')
def admin():
    return redirect(url_for('admin_settings_view'))


# admin_settings_view


@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings_view():
    global admin_settings
    if request.method == 'POST':
        admin_settings['theme'] = request.form.get('theme')
        admin_settings['notifications'] = 'notifications' in request.form
        flash('Settings updated!', 'info')
    return render_template('settings.html', settings=admin_settings)

# --------------------- MAIN --------------------------

if __name__ == '__main__':
    app.run(debug=True)
