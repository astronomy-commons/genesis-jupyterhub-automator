import argparse
import os
import shutil
import sys
from config import DeployConfig
import importlib
import yaml
from utils import create_handler, Initializer, default_if_included, default_if_equals

class Automator(object):
    parser = None
    subparsers = None
    init_parser = None
    deploy_parser = None
    edit_parser = None
    delete_parser = None

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='JupyterHub on Kubernetes Automator',
        )
        self.parser = parser
        subparsers = parser.add_subparsers(dest='command')
        self.subparsers = subparsers
        self.init_parser = subparsers.add_parser("init", help="Initialize a deployment")
        self.deploy_parser = subparsers.add_parser("deploy", help="Deploy a deployment")
        self.edit_parser = subparsers.add_parser("edit", help="Edit a part of a deployment")
        self.delete_parser = subparsers.add_parser("delete", help="Delete a deployment in whole or in part")

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not args.command or not hasattr(self, args.command):
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        sys.argv.remove(args.command)
        getattr(self, args.command)()

    def init(self):
        parser = self.init_parser
        parser.add_argument("deployment", help="The deployment directory.")
        parser.add_argument("--provider", required=True)

        # k8s arguments
        parser.add_argument("--k8s-version",
                            default=default_if_equals(
                                "--provider", {
                                    "aws" : "1.14",
                                    "do" : "1.16.2-do.1",
                                }
                            ),
                            help="The Kubernetes Version to use."
        )
        parser.add_argument("--cluster-name", default="genesis")
        parser.add_argument("--region",
                            default=default_if_equals(
                                "--provider", {
                                    "aws" : "us-west-2",
                                    "do" : "sfo2",
                                }
                            )
        )
        parser.add_argument("--availability-zones", 
                            nargs="+", 
                            default=default_if_equals(
                                "--provider", {
                                    "aws" : [
                                        "us-west-2a", 
                                        "us-west-2b",
                                    ]
                                }
                            )
        )

        # nodegroup arguments
        parser.add_argument("--size", 
                            default=default_if_equals(
                                "--provider", {
                                    "aws" : "m5.xlarge",
                                    "do" : "s-4vcpu-8gb"
                                }
                            )
        )
        parser.add_argument("--nodes", default=3)
        parser.add_argument("--nodegroup-name", default="genesis-nodes")
        parser.add_argument("--nodegroup-availability-zones", nargs="+", 
                            default=default_if_equals(
                                "--provider", {
                                    "aws" : [
                                        "us-west-2a", 
                                    ]
                                }
                            )
        )

        # hub
        parser.add_argument("--hub-chart-repository", default="jupyterhub")
        parser.add_argument("--hub-chart-name", default="jupyterhub")
        parser.add_argument("--hub-chart-version", default="0.9.0-alpha.1.090.1810aa5")
        parser.add_argument("--hub-image", default=None)
        parser.add_argument("--hub-namespace", default="genesis-hub")
        parser.add_argument("--hub-release-name", default="genesis-hub")
        parser.add_argument("--hub-values", nargs="+", default=None)
        parser.add_argument("--hub-admin-user", default=None)
        
        # singluser
        parser.add_argument("--cpu", default=0.5)
        parser.add_argument("--memory", default=1)
        parser.add_argument("--storage", default=1)
        parser.add_argument("--notebook-image", default=None)
        parser.add_argument("--notebook-start-scripts", nargs="+", default=None)

        # dns
        parser.add_argument("--domain-name")
        parser.add_argument("--dns-provider", 
                            default=default_if_equals(
                                "--provider", {
                                    "aws" : "aws",
                                    "do" : "do",
                                }
                            )
        )        

        # eksctl
        parser.add_argument("--eksctl-api-version", 
                            default=default_if_equals(
                                "--provider", {
                                    "aws" : "eksctl.io/v1alpha5"
                                }
                            )
        )

        parser.add_argument("--dashboard-version", default="v2.0.0-beta6")

        args, extra_args = parser.parse_known_args()
        args = vars(args)
        print(args)
        sys.argv.remove(args['deployment'])

        deployment_dir = args['deployment']
        print(deployment_dir)
        if os.path.exists(deployment_dir):
            print(deployment_dir, "already exists! automator init may not work with an existing directory.")
            # exit(-1)
        else:
            os.makedirs(deployment_dir)

        initializer = Initializer(deployment_dir)
        initializer.init()

        config = {}
        config['provider'] = args['provider']

        # k8s configuration
        k8s = {}
        k8s['k8s_version'] = args['k8s_version']
        k8s['cluster_name'] = args['cluster_name']
        k8s['region'] = args['region']

        config['k8s'] = k8s

        # provider-specific configuration
        if args['provider'] == 'aws':
            eksctl = {}
            eksctl['file'] = "cluster/config.yaml"
            
            config['eksctl'] = eksctl

            eksctl_file_contents = {}    
            eksctl_file_contents['apiVersion'] = args['eksctl_api_version']
            eksctl_file_contents['availabilityZones'] = args['availability_zones']
            eksctl_file_contents['kind'] = "ClusterConfig"

            metadata = {}
            metadata['name'] = args['cluster_name']
            metadata['region'] = args['region']
            eksctl_file_contents['metadata'] = metadata

            nodegroup = {}
            nodegroup['availabilityZones'] = args['nodegroup_availability_zones']
            nodegroup['desiredCapacity'] = args['nodes']
            nodegroup['name'] = args['nodegroup_name']
            nodegroup['instanceType'] = args['size']
            eksctl_file_contents['nodeGroups'] = [nodegroup]
            
            eksctl_file_path = os.path.join(deployment_dir, "cluster", "config.yaml")
            with open(eksctl_file_path, "w") as f:
                f.write(yaml.safe_dump(eksctl_file_contents))
        elif args['provider'] == 'do':
            doks = {}
            doks['name'] = args['nodegroup_name']
            doks['size'] = args['size']
            doks['nodes'] = args['nodes']
            config['doks'] = doks
        else:
            print(f"Provider {args['provider']} is not supported by the automator")
            exit(-1)

        # hub
        hub = {}
        hub['release'] = args['hub_release_name']
        hub['namespace'] = args['hub_namespace']
        hub['repository'] = args['hub_chart_repository']
        hub['chart'] = args['hub_chart_name']
        hub['version'] = args['hub_chart_version']
        hub['hub_admin_user'] = args['hub_admin_user']

        if args['hub_image']:
            hub['image'] = args['hub_image']
        
        if args['hub_values']:
            hub['extra_values'] = args['hub_values']

        hub['cpu'] = args['cpu']
        hub['memory'] = args['memory']
        hub['storage'] = args['storage']
        if args['notebook_image']:
            hub['notebook_image'] = args['notebook_image']
        if args['notebook_start_scripts']:
            hub['notebook_start_scripts'] = args['notebook_start_scripts']
            for script in args['notebook_start_scripts']:
                # copy script to deployment location
                if os.path.exists(script) and os.path.isfile(script):
                    shutil.copyfile(script, os.path.join(deployment_dir, "scripts", script))
                else:
                    print(f"Could not locate script {script}")
                    exit(-1)

        config['hub'] = hub

        # dashboard
        dashboard = {}
        dashboard['version'] = args['dashboard_version']
        config['dashboard'] = dashboard

        # plans

        plans = {}
        deploy = [
            {
                "description" : "Create Kubernetes Cluster",
                "handler" : "providers.AWSProvider",
            }, 
            {
                "description" : "Create Helm Deployment",
                "handler" : "components.Helm",
            },
            {
                "description" : "Create JupyterHub Deployment",
                "handler" : "components.JupyterHub",
            },
            {
                "description" : "Create A Records for DNS Routing",
                "handler" : "dns.AWSDNSProvider",
            },
        ]
        plans['deploy'] = deploy
        
        config['plans'] = plans

        config_file_path = os.path.join(deployment_dir, "deploy.yaml")
        with open(config_file_path, "w") as f:
            f.write(yaml.safe_dump(config))

    def deploy(self):
        parser = self.deploy_parser
        parser.add_argument("deployment")

        args, extra_args = parser.parse_known_args()
        args = vars(args)
        sys.argv.remove(args['deployment'])

        deploy_config_path = os.path.join(args['deployment'], "deploy.yaml")
        self.config = DeployConfig(deploy_config_path)

        deploy_steps = self.config.get('plans.deploy')
        for step in deploy_steps:
            description = step['description']
            print(description)
            _handler = step['handler']
            handler = create_handler(_handler)

            handler.register_deployment(deploy_config_path)

            if not handler.validate():
                handler.create()

    def edit(self):
        parser = self.edit_parser
        parser.add_argument("deployment")
        parser.add_argument("action")

        args, extra_args = parser.parse_known_args()
        args = vars(args)
        sys.argv.remove(args['deployment'])
        sys.argv.remove(args['action'])

        deploy_config_path = os.path.join(args['deployment'], "deploy.yaml")

        self.config = DeployConfig(deploy_config_path)

        edit_actions = self.config.get("plans.edit")
        if not args['action'] in edit_actions.keys():
            print(args['action'], "not supported with automator edit")
        else:
            action = edit_actions[args['action']]
            description = action['description']
            _handler = action['handler']
            function = action['function']

            handler = create_handler(_handler)
            handler.register_deployment(deploy_config_path)

            handler_function = getattr(handler, function, None)
            if handler_function:
                handler_function()
            else:
                print(f"function {function} not implemented by {handler.__class__.__name__}")

    def delete(self):
        parser = self.delete_parser
        parser.add_argument("deployment")
        parser.add_argument("--component")

        args, extra_args = parser.parse_known_args()
        args = vars(args)
        sys.argv.remove(args['deployment'])

        deploy_config_path = os.path.join(args['deployment'], "deploy.yaml")



def main():
    Automator()

if __name__ == "__main__":
    main()

