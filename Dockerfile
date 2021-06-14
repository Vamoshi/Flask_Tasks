# init base image
FROM python:3.9.5
# the working directory, app
WORKDIR /FLASK_GITHUB_TASK
# copy the contents into the working directory
COPY . /FLASK_GITHUB_TASK
# install dependencies from requiremnts.txt
RUN pip install -r requirements.txt
# ENV PORT=PORT
# define the command to start the container
CMD ["python", "app.py"]