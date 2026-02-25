# CommunitySacco

A Django-based web application for managing community savings and loan services. CommunitySacco provides a platform for members to contribute savings, apply for loans, track transactions, and manage their financial activities within a community-based organization.

## Features

### Authentication & Membership
- User registration and authentication
- Member profile management with membership numbers
- Phone number and address tracking
- Membership tracking with join dates

### Savings Management
- Members can contribute to savings
- View savings history and records
- Track savings over time with timestamps

### Loan Management
- Members can apply for loans with supporting documents
- Loan request workflow with three statuses: Pending, Approved, Rejected
- Admin dashboard for reviewing and approving loan requests
- Loan limits per member
- Admin comments on loan decisions
- Document upload for loan applications

### Financial Transactions
- Track multiple transaction types:
  - Deposits
  - Loan Disbursements
  - Loan Repayments
- Transaction status tracking (Pending/Completed)
- Payment reference tracking
- Mobile money (M-Pesa) integration for payments

### Admin Features
- Admin login and authentication
- Loan approval dashboard
- Member analytics dashboard
- Transaction monitoring
- Payment processing via STK push (M-Pesa)

## Technology Stack

**Backend Framework:**
- Django 6.0.2 - Python web framework

**Database:**
- SQLite (development)

**Payment Integration:**
- django-daraja 1.3.0 - M-Pesa integration

**Key Dependencies:**
- asgiref 3.11.1 - ASGI utilities
- requests 2.32.5 - HTTP client library
- python-decouple 3.8 - Environment variable management
- cryptography 46.0.5 - Cryptographic recipes and primitives
- django-extensions - Django extensions
- sqlparse 0.5.5 - SQL parser

See [requirements.txt](requirements.txt) for complete dependencies list.

## Project Structure

```
communitysacco/
├── Authapp/                    # Authentication & Member Management
│   ├── models.py              # MemberProfile model
│   ├── views.py               # Authentication & member views
│   ├── forms.py               # Registration & login forms
│   ├── urls.py                # URL routing
│   ├── templates/Authapp/     # Registration, login, profile templates
│   └── static/Authapp/        # CSS and images
│
├── FinanceApp/                # Finance Management
│   ├── models.py              # Savings, Loan, Transaction models
│   ├── views.py               # Finance views & admin dashboards
│   ├── forms.py               # Loan & savings forms
│   ├── urls.py                # Finance URL routing
│   └── templates/FinanceApp/  # Loan, savings, transaction templates
│
├── communitysacco/            # Project settings
│   ├── settings.py            # Django settings
│   ├── urls.py                # Project URL configuration
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
│
├── templates/                 # Base templates
│   ├── main.html              # Base template
│   └── navbar.html            # Navigation template
│
├── media/                     # User uploaded files
│   └── loan_documents/        # Loan document uploads
│
├── static/                    # Static files (CSS, JS, images)
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
└── db.sqlite3                # SQLite database
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd communitysacco
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/Scripts/activate  # On Windows
   # or
   source env/bin/activate      # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root (if needed):
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ```
   Use python-decouple to load these variables in settings.py

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files (for production)**
   ```bash
   python manage.py collectstatic
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```
   The application will be available at `http://localhost:8000/`

## Usage

### For Members
1. **Register** - Create a new account on the registration page
2. **Login** - Access your member dashboard
3. **View Profile** - Check your membership details
4. **Contribute Savings** - Add money to your savings account
5. **Apply for Loan** - Submit a loan request with required documents
6. **Track Transactions** - View all your financial transactions

### For Admins
1. **Login as Admin** - Use admin credentials
2. **Loan Approval Dashboard** - Review pending loan applications
3. **Analytics Dashboard** - View member and financial analytics
4. **Process Payments** - Use STK push to initiate M-Pesa payments
5. **Manage Members** - View and manage member information

## API Endpoints

The application uses Django URLs configured in:
- `Authapp/urls.py` - Authentication endpoints
- `FinanceApp/urls.py` - Finance endpoints
- `communitysacco/urls.py` - Project root URLs

## Database Models

### MemberProfile
- Linked to Django User model
- Stores member-specific information
- Tracks membership numbers and join dates

### SavingsRecord
- Records member savings contributions
- Timestamped entries
- Linked to user accounts

### LoanRequest
- Manages loan applications
- Tracks loan status and decisions
- Stores loan documents
- Admin review and comments

### Transaction
- Core financial transaction records
- Multiple transaction types support
- Payment status tracking
- M-Pesa integration support

### UserLoanLimit
- Defines borrowing limits per member
- One-to-one relationship with users
- Configurable loan amount limits

## Payment Integration (M-Pesa)

The application uses django-daraja for M-Pesa integration:
- STK push for initiating payments
- Payment confirmation handling
- Transaction reference tracking

Configuration is handled in FinanceApp views and requires:
- M-Pesa business account credentials
- Consumer key and secret
- Pass key for STK push

## Development Notes

- Database: SQLite for development (configure PostgreSQL/MySQL for production)
- Static files: Use `collectstatic` command for production
- Media files: User uploads stored in `media/loan_documents/`
- ASGI support for async operations
- Comprehensive admin interface via Django admin

## Security Considerations

- Use environment variables for sensitive configuration
- Set `DEBUG=False` in production
- Use strong SECRET_KEY
- Enable CSRF protection (enabled by default)
- Validate all file uploads (loan documents)
- Hash passwords using Django's password hashing
- Use HTTPS in production
- Configure ALLOWED_HOSTS in settings.py

## Testing

Run tests using:
```bash
python manage.py test
```

Test files are located in `tests.py` within each app.

## Admin Panel

Access Django admin at: `http://localhost:8000/admin/`

Manage:
- Users and member profiles
- Loan requests and approvals
- Savings records
- Transactions
- User loan limits

## Troubleshooting

### Migration Issues
```bash
python manage.py migrate --fake-initial  # If migrations fail on first install
```

### Database Issues
```bash
python manage.py flush  # Clear database (development only)
python manage.py migrate  # Reapply migrations
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## License

[Specify your project license here]

## Support

For issues, questions, or suggestions, please open an issue on the repository or contact the development team.

---

**Last Updated:** February 2026
