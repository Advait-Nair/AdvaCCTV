def create_path_if_not_exists(path:str):
    import os
    if not os.path.exists(path):
        os.makedirs(path)