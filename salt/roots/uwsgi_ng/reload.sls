# fetch app (optional)

# unpack app in separate dir

# create new virtualenv

# install app in a separate dir

# update uwsgi configuration to point to new virtualenv

# gracefully reload uwsgi
echo r > .uwsgi/master-fifo

# cleanup old virtualenvs
