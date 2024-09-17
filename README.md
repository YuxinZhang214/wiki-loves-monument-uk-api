## Run the backend

```bash
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py runserver
```

Deactivate Virtual Environment

```bash
    deactivate
```

```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
```

## Deployment on Toolforge

1. SSH into your Toolforge account:
   ```
   ssh username@login.toolforge.org
   ```

2. Clone the repository:
   ```
   git clone https://github.com/your-repo/wlm-uk.git
   ```

3. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Copy the `toolforge.yaml` file to `/data/project/wlm-uk/`:
   ```
   cp toolforge.yaml /data/project/wlm-uk/
   ```

6. Set up the web service:
   ```
   webservice --backend=kubernetes python3.9 shell
   webservice --backend=kubernetes python3.9 start
   ```

7. Run migrations:
   ```
   python manage.py migrate
   ```

8. Collect static files:
   ```
   python manage.py collectstatic
   ```

9. Your application should now be accessible at `https://wlm-uk.toolforge.org`