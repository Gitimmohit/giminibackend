
# Get the code
git clone  
cd gimini

# Virtualenv modules installation (Unix based systems) (One time installation)

virtualenv --no-site-packages .gimini
source env/bin/activate
source .gimini/bin/activate

# For Ubuntu or Debian based distros
sudo apt-get install python3-venv
python -m venv .gimini


# Virtualenv modules installation (Windows based systems) (One time installation)
pip install virtualenv

networksetup -getinfo Wi-Fi #for ipconfig

python -m virtualenv .gimini

#to activate virtualenv
.gimini/Scripts/activate

# For Ubuntu or Debian based distros
sudo apt-get install python3-venv
<!-- for mac only do this  -->
python3 -m venv .gimini


# Install modules
pip install -r requirements.txt

# rm -r **/migrations
# rm -r **/__pycache__
# pip freeze > requirements.txt

# Create tables, user and collect statics
python manage.py makemigrations ems cards


python manage.py migrate


# Create super user and masters
python manage.py createsuperuser

# OR just run loaddata sub-command to load initial masters data with superuser created
# python manage.py loaddata fixture\dump-including-superuser.json

# Load masters initial data if you created super user by command
python manage.py loaddata fixture\dump-masters-only.json

# Collect static contents into workspace
python manage.py collectstatic

# Start the application (development mode)
python manage.py runserver 7000

```

Congratulations! You made it! You should've superuser credentials to login. If you've used the command [python manage.py loaddata fixture\dump-including-superuser.json](https://www.coderedcorp.com/blog/how-to-dump-your-django-database-and-load-it-into-/) and loaded the data use Admin as superuser and India@123 as your password.


############################################################### 
# For Installation of Celery and Redis
# Run the requirement.txt file

# For Windows Download Redis Installation
https://www.youtube.com/watch?v=pdkmHa9n2SI&list=PLS1QulWo1RIYZZxQdap7Sd0ARKFI-XVsd&index=3

# For Ubuntu checkout this video
https://www.youtube.com/watch?v=r2zYjT4ILm0&list=PLS1QulWo1RIYZZxQdap7Sd0ARKFI-XVsd&index=3

