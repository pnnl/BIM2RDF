
def config():
    import os.path 
    from project import root
    _= root / 'speckle' / 'secret.json'
    if os.path.isfile(_) == False: 
        import json
        input_data = input("enter your token: ")
        json_object = {"speckl_token": input_data}
        with open("secret.json","w") as f:
            json.dump(json_object,f)
    else: 
        return None
    
if __name__ == '__main__':
    config()