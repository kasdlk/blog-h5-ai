sudo yum groupinstall -y "Development Tools"
sudo yum install -y gcc gcc-c++ make wget tar \
    bzip2 bzip2-devel zlib-devel readline-devel \
    sqlite sqlite-devel openssl-devel libffi-devel xz-devel

cd /usr/src
sudo wget https://www.python.org/ftp/python/3.11.2/Python-3.11.2.tgz
sudo tar xzf Python-3.11.2.tgz
cd Python-3.11.2

sudo ./configure --enable-optimizations
sudo make -j $(nproc)
sudo make altinstall

pip3.11 install openai