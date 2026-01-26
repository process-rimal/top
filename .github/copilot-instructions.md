# AI Coding Instructions - Django Shop Management System

## Project Overview
This is a complete Django 4.2 shop management system for a stationery store in Nepal, featuring POS, inventory tracking, customer/vendor management, and credit tracking. Built for MySQL backend with Nepal-specific configurations (timezone: Asia/Kathmandu, VAT: 13%, currency: NPR).

## Architecture

### App Structure (Django Apps)
- **accounts/** - User authentication, UserProfile with role-based access (admin/manager/cashier/inventory)
- **inventory/** - Product, Category, Inventory models with low stock tracking
- **sales/** - Sale, SaleItem models; POS system with JSON API endpoints
- **customers/** - Customer model with credit_limit, CustomerContact
- **vendors/** - Vendor model with VendorContact for supplier management
- **reports/** - Dashboard and analytics views (no models)

### Key Design Patterns
1. **ForeignKey protection**: Use `on_delete=models.PROTECT` for critical relations (Product, Vendor) to prevent accidental deletion
2. **Inventory transactions**: Sale creation automatically decrements `Inventory.quantity` in atomic operations (see [sales/views.py](sales/views.py#L47-L50))
3. **Related names**: All FK relationships use explicit `related_name` (e.g., `Sale.items`, `Customer.contacts`)
4. **JSON APIs**: POS endpoints use `JsonResponse` with `json.loads(request.body)` pattern (no DRF)

## Development Workflow

### Environment Setup
```bash
# Always activate virtual environment first
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Environment variables via .env (see .env.example)
# Uses python-dotenv loaded in settings.py
```

### Database Commands
```bash
# After model changes
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Backup MySQL database
mysqldump -u shop_user -p shop_management > backup.sql
```

### Running the Server
```bash
python manage.py runserver
# Access at http://localhost:8000
# Admin panel: http://localhost:8000/admin/
# POS system: http://localhost:8000/sales/pos/
```

## Code Conventions

### Authentication
- **All views** use `@login_required` decorator - no exceptions
- Login redirect configured: `LOGIN_URL = 'login'`, `LOGIN_REDIRECT_URL = 'dashboard'`
- User roles stored in `UserProfile.role` but permissions not enforced in views yet

### Models
- Use `auto_now_add=True` for created_at, `auto_now=True` for updated_at
- Decimal fields for money: `DecimalField(max_digits=12, decimal_places=2)`
- Phone/email fields: CharField(max_length=20) and EmailField(unique=True) respectively
- All models have `__str__()` methods returning meaningful names

### Admin Configuration
- Register models with `@admin.register(Model)` decorator
- Admin classes are minimal (pass only) - relies on Django auto-generation
- No custom list_display or search_fields configured currently

### Templates
- Base template: [templates/base.html](templates/base.html) with Bootstrap 5.3
- Gradient navbar: `#667eea` to `#764ba2`
- No template inheritance beyond base.html
- Static files served via WhiteNoise in production

### URL Patterns
- Main URLs in [shop_management/urls.py](shop_management/urls.py) use `include()` for app URLs
- App-specific URLs in `app_name/urls.py` with named patterns (e.g., `name='pos_system'`)
- No API versioning or namespaces used

## Critical Integration Points

### POS System Workflow
1. Frontend ([templates/sales/pos.html](templates/sales/pos.html)) sends JSON to `/sales/create/`
2. Backend creates Sale, SaleItems, updates Inventory atomically
3. Returns `{'sale_id': int, 'total': Decimal}` for receipt generation
4. Receipt accessible at `/sales/<sale_id>/receipt/`

### Inventory Management
- **Stock updates**: Only via Sale creation (automatic decrement) or manual admin edits
- **Low stock alerts**: Compare `Inventory.quantity` vs `Inventory.reorder_level` (default: 10)
- **No StockAdjustment model**: Previous migration removed it ([inventory/migrations/0002](inventory/migrations/0002_remove_stockadjustment_adjusted_by_and_more.py))

### Third-Party Dependencies
- **crispy-forms + crispy-bootstrap5**: Form rendering (configured in settings)
- **django-filter**: Filtering in list views
- **WhiteNoise**: Static file serving
- **WeasyPrint, reportlab**: PDF generation (receipt printing)
- **python-barcode, qrcode**: Barcode generation
- **MySQL connector**: `mysql-connector-python==9.1.0` (NOT mysqlclient)

## Common Patterns

### Creating new features
1. Add model to `app/models.py`, run `makemigrations` + `migrate`
2. Register in `app/admin.py` with `@admin.register(Model)`
3. Create view in `app/views.py` with `@login_required`
4. Add URL pattern to `app/urls.py` with descriptive name
5. Create template in `templates/app_name/template.html` extending `base.html`

### Query Optimization
- Use `select_related()` for forward FK lookups
- Use `prefetch_related()` for reverse FK/M2M (e.g., `Sale.items.all()`)
- Aggregate with `Sum`, `Count`, `Avg` from `django.db.models` (see [reports/views.py](reports/views.py))

## Documentation Files
- **README.md**: Quick start guide for end users
- **START_HERE.md**: Installation roadmap
- **COMPLETE_INSTALL_GUIDE.md**: Detailed setup instructions
- **QUICK_REFERENCE.md**: Command cheat sheet for daily operations
