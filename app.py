# Import necessary modules from Python and Flask
from flask import Flask, render_template, request, redirect, url_for
import csv          # For saving leads to a CSV file
import os           # To check if the CSV file exists
from datetime import datetime  # To timestamp each lead

# Create a Flask application instance
app = Flask(__name__)

# Name of the file where we’ll save leads
LEADS_FILE = "leads.csv"

# Function to save a lead to the CSV
def save_lead(data):
    # Check if the CSV file already exists
    file_exists = os.path.isfile(LEADS_FILE)
    
    # Open the file in append mode (creates file if it doesn't exist)
    with open(LEADS_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # If file is new, write the headers as the first row
        if not file_exists:
            writer.writerow(["timestamp", "name", "email", "phone", "buy_or_sell", "timeline", "message"])

        # Write the lead data
        writer.writerow([
            datetime.utcnow().isoformat(),  # Record the current UTC time
            data.get("name",""),            # Name from the form
            data.get("email",""),           # Email from the form
            data.get("phone",""),           # Phone from the form
            data.get("buy_or_sell",""),     # Buy/sell/both
            data.get("timeline",""),        # Timeline for buying/selling
            data.get("message","")          # Optional message
        ])

# Route for the homepage (GET request)
@app.route("/", methods=["GET"])
def index():
    # Render the lead capture form
    return render_template("index.html")

# Route to handle form submission (POST request)
@app.route("/submit", methods=["POST"])
def submit():
    # Grab form fields the browser sends in the POST request
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    buy_or_sell = (request.form.get("buy_or_sell") or "").strip()
    timeline = (request.form.get("timeline") or "").strip()
    message = (request.form.get("message") or "").strip()

    # --- Server-side validation (important: users can bypass browser validation) ---
    # We'll build an error message if anything important is missing/invalid.
    error = None

    if not name:
        error = "Please enter your name."
    elif not email or "@" not in email:
        # Simple email check for Week 1 (later we can improve this)
        error = "Please enter a valid email address."
    elif buy_or_sell not in {"buy", "sell", "both"}:
        error = "Please select whether you're buying, selling, or both."
    elif timeline not in {"0-3 months", "3-6 months", "6-12 months", "12+ months"}:
        error = "Please select a timeline."

    # If there's an error, re-render the same form page and display the message.
    # We also send back the user's previous inputs so they don't have to retype.
    if error:
        return render_template(
            "index.html",
            error=error,
            form_data={
                "name": name,
                "email": email,
                "phone": phone,
                "buy_or_sell": buy_or_sell,
                "timeline": timeline,
                "message": message,
            },
        )

    # If validation passed, save it
    lead = {
        "name": name,
        "email": email,
        "phone": phone,
        "buy_or_sell": buy_or_sell,
        "timeline": timeline,
        "message": message,
    }

    save_lead(lead)

    # Redirect after POST prevents "resubmit form" if user refreshes the page
    return redirect(url_for("thank_you"))


# Route for the thank you page (GET request)
@app.route("/thank-you")
def thank_you():
    # Render a simple confirmation page
    return render_template("thank_you.html")

# Only run the app if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)  # debug=True enables live reload & error messages
