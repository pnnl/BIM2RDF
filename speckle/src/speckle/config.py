
def config(dev = True):
    from project import root
    _ = root / 'speckle' / 'secret.json'
    if dev:
        if not _.exists():
            import json
            input_data = input("enter your Speckle API token: ")
            json_object = {"speckl_token": input_data}
            with open(_,"w") as f:
                json.dump(json_object,f)
        else: 
            return _
    else:
        # TODO: use systemized config
        from project_azure.secret import get
        with open(_, "w") as f:
            import json
            json.dump({"speckl_token": get('gitlab-speckle')}, f)
        return _


if __name__ == '__main__':
    from fire import Fire
    Fire(config)
