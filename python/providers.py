import utils
from utils import AutomatorItem
import argparse
import bash
import os
import subprocess
import json

class AWSProvider(AutomatorItem):
    def __init__(self):
        parser = argparse.ArgumentParser()

        args, extra_args = parser.parse_known_args()
        args = vars(args)
        print("in __init__")
        print("args:", args)
        print("extra args:", extra_args)

        self.init()

    def validate(self):
        cluster_name = self.config.get("k8s").get("cluster_name")
        self.cluster_config_file_path = os.path.join(self.deployment_directory, self.config.get("eksctl").get("file"))
        cmd = ["eksctl", "get", "cluster", "-o", "json"]
        result = utils.call(cmd, silent=True)
        if result:
            clusters = json.loads(result)
            self.cluster_exists = any([cluster_name == cluster['name'] for cluster in clusters])
            if self.cluster_exists:
                print(f"Found cluster {cluster_name}")
            else:
                print(f"Did not find cluster {cluster_name}")
            return self.cluster_exists
        else:
            return False

    def create(self):
        print("in create")
        self.cluster_config_file_path = os.path.join(self.deployment_directory, self.config.get("eksctl").get("file"))
        cmd = ["eksctl", "create", "cluster", "-f", self.cluster_config_file_path]
        print(" ".join(cmd))
        # utils.call(cmd)

    def add_nodegroup(self):
        parser = argparse.ArgumentParser()
        # nodegroup arguments
        parser.add_argument("--size", 
                            default="m5.xlarge"
        )
        parser.add_argument("--nodes", default=3)
        parser.add_argument("--name", default="genesis-nodes")
        parser.add_argument("--availability-zones", nargs="+", 
                            default=["us-west-2a"]
        )        
        args, extra_args = parser.parse_known_args()
        args = vars(args)
        print("in add_nodegroup")
        print("args:", args)
