import os
import yaml

class DeployConfig(object):
    def __init__(self, full_path):
        self.config_path = full_path
        self.refresh()
        
        good, errors = self.validate()
        if not good:
            raise ValueError("\n  ".join(errors))
    
    def refresh(self):
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)
    
    def save(self):
        with open(self.config_path, "w") as f:
            f.write(yaml.safe_dump(self.config))

    def validate_keys(self, keys_to_check):
        good = True
        errors = []
        for key in keys_to_check:
            if not self.get(key):
                good = False
                errors.append(f"{key} missing from deployment config at {self.config_path}")
        return good, errors

    def validate_aws(self):
        keys_to_check = []
        return self.validate_keys(keys_to_check)

    def validate(self):
        good, errors = self.validate_keys(["provider"])
        if good:
            provider = self.get("provider")
            if provider == "aws":
                return self.validate_aws()
        else:
            return False, errors

    def get(self, key):
        if "." in key:
            keys = key.split(".")
            d = self.config
            for i, _key in enumerate(keys):
                print(f"trying key {_key}")
                _value = d.get(_key, None)
                # value is good and we've reached the last key
                if _value and i == len(keys) - 1:
                    value = _value
                    break
                # value is good, and the next level is a dictionary
                elif _value and type(_value) is dict:
                    d = _value
                    continue
                # value is good, but the next level isn't a dictionary
                elif _value and not (type(_value) is dict):
                    print(f"object found with {' '.join(keys[:i])} is not a dictionary, cannot process {key}")
                    value = None
                    break
                # value is not good
                else:
                    value = None
                    break
        else:
            value = self.config.get(key, None)

        if value:
            return value
        else:
            print(f"{key} not found in deployment config at {self.config_path}")
            return None
        