# Abarrotes Yamessi - Inventario (FastAPI)

Simple inventory management app using FastAPI, Jinja2 templates and SQLite.

Requirements (install into a venv):

```
pip install -r requirements.txt
```

Run the app locally (host on all interfaces so you can access from phone):

```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then open in a browser on your PC: http://localhost:8000
From a phone on the same Wi-Fi, find your PC IP (e.g. 192.168.1.10) and open: http://192.168.1.10:8000

Notes:
- Stock is only changed via inventory movements (entry, sale, adjustment).
- Database file `inventory.db` will be created in the same folder.
