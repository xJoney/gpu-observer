# Alert manager doesnt natively support .env files so using this script to replace variables in the alert_manager template instead

#!/bin/sh
sed "s/\$EMAIL_TO/$EMAIL_TO/g; s/\$EMAIL_FROM/$EMAIL_FROM/g; s/\$EMAIL_USER/$EMAIL_USER/g; s/\$EMAIL_PASS/$EMAIL_PASS/g" \
  /etc/alertmanager/alertmanager.yml.template > /etc/alertmanager/alertmanager.yml

# Start AlertManager
/bin/alertmanager --config.file=/etc/alertmanager/alertmanager.yml --storage.path=/alertmanager