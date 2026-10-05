# SUHAASA — In-App Admin Notifications

This patch wires the notification bell in the SUHAASA Store Admin into a persistent, backend-backed notification system.

## Included
- Persistent `Notification` model with unread/read state.
- Admin-only notification API.
- Notification dropdown opened by the bell icon.
- Unread red dot only when unread notifications exist.
- Mark individual notification read.
- Mark all notifications read.
- Automatic state-based alerts for recent orders, paid orders, low-stock variants and out-of-stock variants.
- Automatic polling every 30 seconds so new store alerts appear without refreshing.
- SUHAASA light/dusk styling matching the existing admin dashboard.

## Files to add/replace
Add:
```text
backend/notifications/
```
Replace:
```text
backend/config/settings.py
backend/config/urls.py
backend/templates/admin/base_site.html
```

Do NOT replace `db.sqlite3`, `.env`, `media/`, the frontend, or the dashboard template.

## Apply
From the existing integrated project:

```powershell
cd C:\Users\OMEN\Desktop\suhaasa-build-integrated\backend
.\.venv\Scripts\Activate.ps1

python manage.py check
python manage.py migrate
python manage.py test notifications
python manage.py test
```

Expected notification tests:
```text
Found 3 test(s).
...
OK
```

Then restart Django:
```powershell
python manage.py runserver
```

## Acceptance test
1. Open `/admin/`.
2. The bell icon beside the owner profile is now clickable.
3. A dropdown should open with current store alerts.
4. The red dot should appear when unread alerts exist.
5. Click an alert: it becomes read and opens its relevant admin page.
6. Click **Mark all as read**: the red dot disappears.
7. Create a new order or change inventory into a low-stock state. Within the next polling cycle, a new alert should appear.
8. Refresh the admin page; read state must persist.

The notification system is intentionally in-app only. No email is added.
