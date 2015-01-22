#!/bin/bash
# Run this script to update the local repositories for CIS and the CEDA DI tool
tag="origin/devel"

if [ -n "$1" ]
then
  tag=$1
fi

export http_proxy="http://wwwcache.rl.ac.uk:8080"
export https_proxy="http://wwwcache.rl.ac.uk:8080"
main_dir=`pwd`
cd $main_dir # cd to this dir
echo "Activating virtualenv"
source venv/bin/activate
cd jasmin_cis
echo "Updating CIS: Fetching latest source from $tag"
git fetch --all
git reset --hard "$tag"
echo "Installing CIS"
python setup.py install

cd $main_dir/ceda-di
echo "Updating CEDA DI to latest source on branch origin/cis_integration"
git fetch --all
git reset --hard origin/cis_integration
sed -i -r 's|("input-path":\s)(".*")|\1"/group_workspaces/jasmin/cis/p3_testing/ceda_di_test/in"|' python/config/ceda_di.json
sed -i -r 's|("output-path":\s)(".*")|\1"/group_workspaces/jasmin/cis/p3_testing/ceda_di_test/out"|' python/config/ceda_di.json
sed -i -r 's|("es_index":\s)(".*")|\1"cis_test"|' python/config/ceda_di.json
cd python
pip install -r pip_requirements.txt || exit
python setup.py install
chgrp -R gws_cis $main_dir
chmod -R g+w $main_dir
echo "DONE"
