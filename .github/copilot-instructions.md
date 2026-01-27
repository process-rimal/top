# AI Coding Instructions - Django Shop Management System

## Architecture & app boundaries
- Django apps are split by domain: accounts, inventory, vendors, customers, sales, reports; routing is centralized in [shop_management/urls.py](shop_management/urls.py).
- Shared templates live under templates/ with the base layout in [templates/base.html](templates/base.html).
- POS flow: [templates/sales/pos.html](templates/sales/pos.html) calls JSON endpoints in [sales/urls.py](sales/urls.py); `create_sale_api()` in [sales/views.py](sales/views.py) creates `Sale` + `SaleItem`, decrements `Inventory.quantity_in_stock`, and adds `CreditTransaction` for credit sales.
- Receipts: PDF rendering is in [sales/utils.py](sales/utils.py) (ReportLab), and served by `receipt_pdf()` in [sales/views.py](sales/views.py).
- Barcode generation uses python-barcode in [inventory/views.py](inventory/views.py) and helpers in [sales/utils.py](sales/utils.py).

## Data model conventions
- User roles are `admin`, `staff`, `manager` in [accounts/models.py](accounts/models.py); `UserProfile` is auto-created in [accounts/views.py](accounts/views.py).
- Monetary values are DecimalFields; VAT is fixed at 13% via `VAT_PERCENT` in [shop_management/settings.py](shop_management/settings.py).
- `Sale` auto-generates `sale_number` and `receipt_number` in [sales/models.py](sales/models.py).
- Stock is driven by `Inventory.quantity_in_stock` in [inventory/models.py](inventory/models.py); sale creation decrements stock and sale deletion restores it in [sales/views.py](sales/views.py).

## API & view patterns
- JSON APIs use `json.loads(request.body)` + `JsonResponse` (no DRF), see [sales/views.py](sales/views.py).
- Most business views are `@login_required`; auth endpoints (login/register) are open in [accounts/views.py](accounts/views.py).

## Runtime/config
- .env is loaded via python-dotenv in [shop_management/settings.py](shop_management/settings.py); set `USE_MYSQL=True` to use mysql-connector, otherwise SQLite is default.
- Static files are served with WhiteNoise; `collectstatic` outputs to staticfiles/ (see [shop_management/settings.py](shop_management/settings.py)).
- Logs are written to logs/django.log via the logging config in [shop_management/settings.py](shop_management/settings.py).

## Common developer workflows
- `python manage.py makemigrations` → `migrate` after model changes.
- `python manage.py createsuperuser` for admin login.
- `python manage.py runserver` for local dev (POS at /sales/pos/).
