🧠 Management System with Flask
A modular management system built with Python and Flask, designed to handle sales, purchases, clients, and inventory. It uses Flask Blueprints to separate logic by domain and is structured for scalability and maintainability.

🚀 Technologies Used
🐍 Python 3

🌐 Flask

🧱 Flask Blueprints (modular routing)

🎨 Jinja2 templates

🗃️ SQLite (or another DB via get_db())

📝 Advanced logging with daily rotation

🖥️ HTML/CSS (with minimal styling)

📁 Modular routes (e.g., routes/ventas, routes/compras)

⚠️ Note: Some variables, functions, and folder names are in Spanish, as the project was originally developed in a Spanish-speaking environment.

⚙️ How to Run the Project
Clone the repository:

bash
Copy code
git clone https://github.com/adrianescalona228/interfaz-web.git
cd interfaz-web
(Optional but recommended) Create a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Set up your secret key:

Create a file named query.txt and add your Flask secret key there:

bash
Copy code
echo "your_secret_key_here" > query.txt
Run the application:

bash
Copy code
python app.py
Open your browser:

Go to http://localhost:5000

✅ Project Status
This project is under active development.

Core modules for sales, purchases, clients, and inventory are functional.

Some features like graph visualizations and authentication are planned or in progress.

📦 Folder Structure (Simplified)
cpp
Copy code
interfaz-web/
├── app.py
├── routes/
│   ├── ventas/
│   ├── compras/
│   ├── clients/
│   ├── inventory/
│   └── database2.py
├── static/
├── templates/
├── logs/
├── query.txt
└── requirements.txt
📌 Notes
Logs are stored in the logs/ folder and rotated daily, keeping up to 30 days of logs.

The database connection is abstracted in routes/database2.py and injected per request.

Code is modular and easily extendable.

🐳 Upcoming Features
 Docker support

 User authentication

 REST API endpoints

 Role-based access

 Graphs for analytics

🤝 Contributions
Pull requests and suggestions are welcome! This project is open for collaboration.

