# Project Structure

This project follows a modular Flask architecture to keep the code organized, scalable, and easy to maintain as new features are added.

```text
plumbing-company-template/
│
├── app/
│   ├── __init__.py          # Initializes the Flask application
│   ├── routes.py            # Website routes and page navigation
│   │
│   ├── templates/           # HTML templates
│   │   ├── base.html        # Shared layout
│   │   ├── index.html       # Home page
│   │   ├── about.html       # About page
│   │   ├── services.html    # Services page
│   │   ├── contact.html     # Contact page
│   │   └── 404.html         # Custom error page
│   │
│   ├── static/              # Static website assets
│   │   ├── css/             # Stylesheets
│   │   ├── js/              # JavaScript files
│   │   └── images/          # Images and logos
│   │
│   ├── models/              # Database models
│   ├── forms/               # Flask form definitions
│   └── utils/               # Helper functions and utilities
│
├── instance/                # Local instance files (database, configs)
├── migrations/              # Database migration history
├── tests/                   # Unit and integration tests
│
├── config.py                # Application configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not committed)
├── .gitignore               # Git ignored files
└── README.md                # Project documentation
```

## Development Workflow

The project is developed using Git with the following branch strategy:

* **main** – Stable, production-ready code.
* **develop** – Active development branch where new features are built and tested.

As the project grows, additional feature branches may be created from `develop` for larger features such as authentication, dashboards, or scheduling.

## Planned Modules

* Public marketing website
* Service request system
* Customer contact forms
* Administrative dashboard
* Authentication and authorization
* Appointment management
* Customer database
* Email notifications
* Image uploads
* Responsive mobile design

```
```

