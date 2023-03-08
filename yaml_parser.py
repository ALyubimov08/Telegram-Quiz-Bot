import yaml
from yaml.loader import SafeLoader

def load_yaml() -> list:
    with open('questions.yaml') as f:
        data = yaml.load(f, Loader=SafeLoader)
        return data
    
def get_correct(data, id: int) -> chr:
    return data[id-1]['correct']