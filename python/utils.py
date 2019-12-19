# from config import DeployConfig
import os
import yaml
import importlib
from pathlib import Path
import argparse
import subprocess

def call(cmd, silent=False):
    ps = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    lines = []
    while True:
        out = ps.stdout.readline()
        if out == b'' and ps.poll() is not None:
            break
        if out:
            lines.append(out)
            if not silent:
                print(out.decode("utf-8"), end="")
            
    exit_code = ps.wait()
    if exit_code == 0:
        return (b"\n".join(lines)).decode("utf-8")
    else:
        print("Command", "'" +  " ".join(cmd) + "'", "returned exit code", str(exit_code))
        print(ps.stderr.read().decode("utf-8"))
        exit(-1)    

def default_if_included(arg, defaults, *args):
    parser = argparse.ArgumentParser()
    parser.add_argument(arg)

    if arg[0:2] == '--':
        arg = arg[2:]
    elif arg[0] == '-':
        arg = arg[1:]
    
    args, _ = parser.parse_known_args()
    if getattr(args, arg, None):
        return defaults
    else:
        return None

def default_if_equals(arg, deafult_values, *args):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(arg)

    if arg[0:2] == '--':
        arg = arg[2:]
    elif arg[0] == '-':
        arg = arg[1:]
    
    args, _ = parser.parse_known_args()
    for key, defaults in deafult_values.items():
        if getattr(args, arg, None) == key:
            return defaults
    return None


def create_handler(_handler):
    _handler_split = _handler.split(".")
    _handler_module = _handler_split[0]
    _handler_class_name = _handler_split[1]

    handler_module = importlib.import_module(_handler_module)
    handler_class = getattr(handler_module, _handler_class_name)
    handler = handler_class()
    return handler

class Initializer(object):
    directory = {
        "deploy.yaml" : {
            "type" : "file"
        },
        "cluster/" : {
            "type" : "dir",
            "items" : []
        },
        "components/" : {
            "type" : "dir",
            "items" : [],
        }, 
        "hub/" : {
            "type" : "dir",
            "items" : [
                { 
                    "scripts/" : {
                        "type" : "dir",
                        "items" : []
                    }
                }
            ]
        }
    }

    def __init__(self, deployment_directory):
        self.deployment_directory = deployment_directory

    def init(self):
        def make_directory_structure(structure, basepath):
            for key, value in structure.items():
                if value['type'] == 'file':
                    file_path = os.path.join(basepath, key)
                    print("creating file:", file_path)
                    Path(file_path).touch()
                elif value['type'] == 'dir':
                    dir_path = os.path.join(basepath, key)
                    if not os.path.exists(dir_path):
                        print("creating directory:", dir_path)
                        os.makedirs(dir_path)
                        for item in value['items']:
                            make_directory_structure(item, dir_path)

        make_directory_structure(self.directory, self.deployment_directory)


class AutomatorItem(object):
    def init(self, *args, **kwargs):
        pass

    # wrapper over init to allow for configuration of __init__
    def __init__(self, *args, **kwargs):
        self.init(args, kwargs)

    def _register_deployment(self, config_path):
        self.deployment_directory = os.path.dirname(config_path)
        self.config_path = config_path
        if os.path.exists(self.config_path) and os.path.isfile(self.config_path):
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f)

    # wrapper to allow easy configuration of register_deployment
    def register_deployment(self, config_path):
        self._register_deployment(config_path)

    def create(self, *args, **kwargs):
        raise Exception(f"create not implemented in {self.__class__.__name__}")
    
    def validate(self, *args, **kwargs):
        raise Exception(f"validate not implemented in {self.__class__.__name__}")

    def delete(self, *args, **kwargs):
        raise Exception(f"delete not implemented in {self.__class__.__name__}")