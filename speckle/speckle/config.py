
def config():
    import os.path 
    import shutil
    from project import root
    _= root / 'speckle' / 'secret.json'
    bdir = root / 'speckle'
    if os.path.isfile(_) == False: 
        import json
        input_data = input("enter your token: ")
        json_object = {"speckl_token": input_data}
        with open(os.path.join(bdir,"secret.json"),"w") as f:
            json.dump(json_object,f)
    else: 
        return None
    
if __name__ == '__main__':
    config()
  
