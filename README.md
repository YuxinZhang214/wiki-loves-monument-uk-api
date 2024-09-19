# Wiki Loves Monuments - UK API

## Project Description

This is the backend application for the Wiki Loves Monuments UK Visualisation tool, hosted on Toolforge at https://toolhub.wikimedia.org/tools/toolforge-wiki-loves-monument-uk. The project aims to support the visualisation of monuments data across the UK in collaboration with Wikimedia. 

Wiki Loves Monuments UK is a web-based platform designed to showcase the community's contributions to UK heritage through the Wiki Loves Monuments competition. This project provides the data and API support for an intuitive interface where users can explore a vast dataset of monuments and image submissions, highlighting the importance of cultural heritage preservation.

You can view the frontend visualisation application at https://wiki-loves-monument-uk-visualisation.vercel.app/

**Data Accuracy Notice:** The dataset currently being served by this backend application is undergoing active corrections and updates. As a result, the data provided may not be entirely accurate at this time. We are working diligently to improve the quality and reliability of the information.

## Features

- API Endpoints: Serve data for monuments, images, and contributor information.
- Data Processing: Handle and prepare data from 12 years of the Wiki Loves Monument UK competition.
- Database Management: Store and manage the vast dataset of monuments and submissions.

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

## Contact

For any queries about the project, please contact the project supervisor at ksrh1@st-andrews.ac.uk.

## Acknowledgements

- University of St Andrews, School of Computer Science: For providing academic support and resources.
- Wiki Loves Monuments Community: For their invaluable contributions to cultural heritage.
- Wikimedia Foundation: For their support and collaboration in this project.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
