rm -rf genesis-client .ipython/genesis
git clone https://github.com/dirac-institute/genesis-client
mkdir -p .ipython
test -L .ipython/genesis || ln -s ../genesis-client/genesis .ipython/genesis
gitpuller https://github.com/dirac-institute/genesis-streaming-demo master genesis-streaming-demo
