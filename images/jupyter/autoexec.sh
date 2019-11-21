rm -rf genesis-client .ipython/genesis
git clone https://github.com/dirac-institute/genesis-client
ln -s ../genesis-client/genesis .ipython/genesis
gitpuller https://github.com/dirac-institute/genesis-streaming-demo master genesis-streaming-demo
