
def config(dev = True):
    from project import root
    _ = root / 'speckle' / 'secret.json'
    if _.exists() == False: 
        import json
        input_data = input("enter your token: ")
        json_object = {"speckl_token": input_data}
        with open(_,"w") as f:
            json.dump(json_object,f)
    else: 
        return None
    
if __name__ == '__main__':
    config()