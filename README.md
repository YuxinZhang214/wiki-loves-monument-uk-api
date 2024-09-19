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

## Deployment

The application is currently not running on Toolforge. The planned URL `https://wiki-loves-monument-uk.toolforge.org/api/` is not active at this time.

For local development and testing, please refer to the "Run the backend" section above.

## API Endpoints

### Monuments

1. **List all monuments**
   - URL: `/monuments/`
   - Method: GET
   - Example: `GET /monuments/`

2. **Get monument locations**
   - URL: `/monuments/locations`
   - Method: GET
   - Example: `GET /monuments/locations`

3. **Get heritage destinations**
   - URL: `/monuments/destinations`
   - Method: GET
   - Example: `GET /monuments/destinations`

4. **Get monument inceptions by year**
   - URL: `/monuments/inceptions`
   - Method: GET
   - Example: `GET /monuments/inceptions`

5. **Get monument images**
   - URL: `/monuments/images`
   - Method: GET
   - Example: `GET /monuments/images`

6. **Get monument details**
   - URL: `/monuments/<str:label>`
   - Method: GET
   - Example: `GET /monuments/eiffel_tower`

### Participants

7. **List all participants**
   - URL: `/participants/`
   - Method: GET
   - Example: `GET /participants/`

8. **Get participant submissions**
   - URL: `/participants/submissions`
   - Method: GET
   - Example: `GET /participants/submissions`

9. **Get participant details**
   - URL: `/participants/<str:authorname>/`
   - Method: GET
   - Example: `GET /participants/john_doe/`

### Submissions

10. **List all submissions**
    - URL: `/submissions/`
    - Method: GET
    - Example: `GET /submissions/`

11. **Get daily submissions**
    - URL: `/submissions/daily`
    - Method: GET
    - Example: `GET /submissions/daily`

12. **Get yearly submissions**
    - URL: `/submissions/yearly`
    - Method: GET
    - Example: `GET /submissions/yearly`

13. **Get total yearly submissions**
    - URL: `/submissions/yearly/total`
    - Method: GET
    - Example: `GET /submissions/yearly/total`

14. **Get yearly submissions by author**
    - URL: `/submissions/yearly/<str:authorname>`
    - Method: GET
    - Example: `GET /submissions/yearly/john_doe`

15. **Get total yearly submissions by author**
    - URL: `/submissions/yearly/total/<str:authorname>/`
    - Method: GET
    - Example: `GET /submissions/yearly/total/john_doe/`

16. **Get submission images**
    - URL: `/submissions/images`
    - Method: GET
    - Example: `GET /submissions/images`

17. **Get submission details**
    - URL: `/submissions/<str:label>`
    - Method: GET
    - Example: `GET /submissions/eiffel_tower_photo`

### Competition Statistics

18. **Get competition statistics**
    - URL: `/competition/statistics/`
    - Method: GET
    - Example: `GET /competition/statistics/`
    - Working Toolforge URL: `https://wiki-loves-monument-uk.toolforge.org/api/competition/statistics/`
    - Curl Example:
      ```bash
      curl -X GET "https://wiki-loves-monument-uk.toolforge.org/api/competition/statistics/" -H "Accept: application/json"
      ```

## Contributing

We welcome contributions! Please submit a pull request or open an issue for bug reports, feature requests, or any questions.

## Contact

For any queries about the project, please contact the project supervisor at ksrh1@st-andrews.ac.uk.

## Acknowledgements

- University of St Andrews, School of Computer Science: For providing academic support and resources.
- Wiki Loves Monuments Community: For their invaluable contributions to cultural heritage.
- Wikimedia Foundatiodasn: For their support and collaboration in this project.

## License

This project is licensed under the MIT License. See the LICENSE file for details.