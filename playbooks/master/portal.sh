
git clone https://superspandan@bitbucket.org/saeedare/blade.git
cd blade
git checkout vino_local

sudo pip install django isodate

mysql -uroot -pvinopass -e "CREATE DATABASE blade"

#modify ~/blade/core/settings.py, L87-88

python manage.py migrate
