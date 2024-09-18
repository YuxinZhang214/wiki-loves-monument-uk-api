# Wiki Loves Monuments - UK

## Project Description

This is the backend application for the Wiki Loves Monuments tool, hosted on Toolforge. The project aims to support the visualisation of monuments data across the UK in collaboration with Wikimedia. You can view the visualisation application You can view the visualisation application at https://wiki-loves-monument-uk-visualisation.vercel.app/

## Running the project

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

## Contributing

We welcome contributions! Please submit a pull request or open an issue for bug reports, feature requests, or any questions.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
