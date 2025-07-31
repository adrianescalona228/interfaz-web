# 🧠 Micro CRM Management system

This is a lightweight prototype of a CRM (Customer Relations Management). This is
designed as a test project, it doesn't have a production use case.

---

## 🚀 Features
- **Contact management:** Full CRUD operations for contacts create, read, update and delete.
- **Sales relations management:** Associate sales records with contacts to track customer interactions and deal history..
- **Product inventory management:** Manage a list of products, link them to providers and track their status/availability.

---

## ⚙️ Development Setup

To clone this project use git or any git compatible tool.

```bash
git clone "https://github.com/adrianescalona228/interfaz-web.git"
```


This project's stack is [`flask`][flask] + `html` + `css` + `js`, to setup you must create
a virtual environment of your own, this is tested and most compatible with
the classic [`venv`][venv].

To setup this project with [`venv`][venv] run the following commands

```bash
# Create your virtual environment
python3 -m venv venv

# Get inside your virtual environment
source venv/bin/activate
```

When you set-up your environment you may install the packages. In this project
[`GNU make`][make] is used to ease some tasks. The following recipes are available

- **make test:** Test your current environment.
- **make run**: Run the project.
- **make install pkg=:** Install the specified package and add it to `requirements.txt`.
- **make install:** Update the project packages or install them.
- **make uninstall pkg=:** Uninstall the specified package and remove it from `requirements.txt`.
- **make docker-compose-up:** Trigger docker compose to deploy the application in the local environment.
- **make docker-compose-up build=1:** Trigger docker compose to deploy and build the application in the local environment.
- **make docker-compose-down:** Trigger docker compose to stop all the services related to this project.

You must also setup your environment file with the contents from the `.env.test` file
for the project to be able to find a database connection.

---

## 🔨 Building

You can build a deployable version using [`docker`][docker], [`docker compose`][docker-compose] is setup
in this repository so you can simply deploy your project to your machine.

There is the [`make`][make] helper which has the `docker-compose-up` and `docker-compose-down`
recipes for this purpose.

This will deploy your project in `http://localhost:5000` for you to use.

---

Happy hacking :)

[flask]: https://flask.palletsprojects.com/en/stable/
[make]: https://www.gnu.org/software/make/
[venv]: https://docs.python.org/3/library/venv.html
[docker]: https://docs.docker.com/
[docker-compose]: https://docs.docker.com/compose/
