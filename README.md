# Projekt serwisu "Projekty Kół Naukowych"

Serwis ma służyć do obsługi zgłoszeń projetków studentów będących członkami kół naukowych


To setup and run your server:







Run migrations:
  - python manage.py makemigrations
  - python manage.py migrate
  (if the first command doesn't make migrations for all the apps run migrations for each app individually:
    - python manage.py makemigrations <appname>
    - python manage.py migrate <appname>
    where <appname> is the name of the app. List of your apps you can get by running python manage.py migrate.)
Load fixtures to database:
  - python manage.py loaddata announcement grades groups notificationperiod studentclub
Run server:
  - python manage.py runserver
