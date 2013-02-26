git clone http://proj.badc.rl.ac.uk/git/jasmin_cis.git
git checkout V0R3M1
export http_proxy=wwwcache.rl.ac.uk:8080
export https_proxy=wwwcache.rl.ac.uk:8080
virtualenv CISENV -p /usr/bin/python2.7 --system-site-packages
source CISENV/bin/activate #deactivate
cd jasmin_cis
python setup.py install



