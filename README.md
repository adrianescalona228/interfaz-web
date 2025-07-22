# Management System with Flask

This is a modular management system developed using Python and Flask. The application includes modules to manage **sales**, **purchases**, **clients**, and **inventory**. It is structured with Flask Blueprints for better code organization and scalability.

## 🚀 Technologies Used

- **Python 3**
- **Flask**
- **Blueprints** for modular routing
- **Jinja2** templates
- **SQLite** or other database connected via `get_db()`
- **Advanced logging** with daily rotation
- **HTML templates** with `render_template`
- Route separation by module (e.g., `routes/ventas`, `routes/compras`, etc.)

> ⚠️ Note: Some functions, variables, and folder names are in Spanish due to the project's original development context.


## ⚙️ How to Run the Project

1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/repo_name.git
   cd repo_name
Install the dependencies (recommended: use a virtual environment):


pip install flask
Create a query.txt file to store your secret key (used by Flask):


echo "your_secret_key_here" > query.txt
Run the application:


python app.py
Open your browser and go to: http://localhost:5000

✅ Project Status
This project is under active development. Some modules may still be incomplete or in progress (e.g., graph visualizations).

📌 Notes
Logs are stored in the logs/ folder and are rotated daily. Up to 30 days of logs are kept.

The database connection is handled in routes/database2.py and injected into each request.
