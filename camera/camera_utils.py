

def get_video_binary(save_path:str, video_output:str):
    with open(save_path + '/' + video_output, 'rb') as v:
        return v.read()
    