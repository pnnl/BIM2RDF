
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
        raise ValueError('speckle not configured')


if __name__ == '__main__':
    config()
