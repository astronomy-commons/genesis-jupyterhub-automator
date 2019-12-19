from utils import AutomatorItem
import shutil
from utils import call
import json

class Helm(AutomatorItem):
    def __init__(self):
        result = call(["helm", "version", "--short", "--client"])

        if result:
            self.helm_version = int(result.split(" ")[1][1])

        self.init()

    def validate(self):
        # confirm tiller deployed
        result = call(["kubectl", "get", "deployment", "-n", "kube-system", "-o", "json"])
        if result:
            deployments = json.loads(result)
            deployment_names = [item['metadata']['name'] for item in deployments['items']]
            
            tiller_deployed = "tiller-deploy" in deployment_names
            if not tiller_deployed:
                return False
        
        # confirm versions are same between client and server
        result = call(["helm", "version", "--short", "--server"])
        if result:
            tiller_version = result.split(" ")[1]
        
        result = call(["helm", "version", "--short", "--client"])
        if result:
            helm_version = result.split(" ")[1]

        if tiller_version != helm_version:
            print("Error: Client and Server versions of Helm are not the same!")
            print("Client:", helm_version)
            print("Server:", tiller_version)
            exit(-1)

    def create(self):
        print(self.__class__.__name__, "create()")

        result = call(["kubectl", "--namespace", "kube-system", "create", "serviceaccount", "tiller"])
        if not result:
            exit(-1)
        result = call(["kubectl", "create", "clusterrolebinding", "tiller", "--clusterrole", "--serviceaccount=kube-system:tiller"])
        if not result:
            exit(-1)
        result = call(["helm", "init", "--service-account", "tiller", "--wait"])
        if not result:
            exit(-1)
        result = call(["kubectl", "patch", "deployment", "tiller-deploy", "--namespace=kube-system", "--type=json", '--patch=[{"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["/tiller", "--listen=localhost:44134"]}]'])
        if not result:
            exit(-1)

        pass

class Dashboard(AutomatorItem):
    def create(self):
        print(self.__class__.__name__, "create()")
        pass

class JupyterHub(AutomatorItem):
    def __init__(self):
        result = call(["helm", "version", "--short", "-c"])

        if result:
            self.helm_version = int(result.split(" ")[1][1])

    def validate(self):
        hub_release = self.config.get("hub").get("release")

        if self.helm_version == 2:
            result = call(["helm", "list", "--output", "json"])
            if result:
                helm_releases = json.loads(result)
                release_exists = any([hub_release == release['Name'] for release in helm_releases['Releases']])
                print(release_exists)
            print()

    def create(self):
        print(self.__class__.__name__, "create()")
        pass