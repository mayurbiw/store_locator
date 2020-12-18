# store_locator

Instructions to run the project. 

# Install all the packages required for the project.
pip3 install -r  requirments.txt 

# clone the repository.
git clone https://github.com/mayurbiw/store_locator.git

# make .env file to keep secret keys and smtp credentials. 

# Run Django
python3 manage.py runserver

# Run Celery
Run Celery-
celery -A store_locator worker  -l info