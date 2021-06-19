# Notes to self:
## Setting up:
1. source venv/bin
2. export FLASK_APP=fitbit_flask.py
3. export FLASK_ENV=development
4. flask run

## For Docker:
- docker build -t *name_of_image* .
- docker run -p 5000:5000 *name_of_image*

### SQL_DATABASE_URL host should be changed from localhost to postgres container name so that it will work
### ^took me a few hours to figure this out