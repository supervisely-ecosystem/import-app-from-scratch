import os

import supervisely as sly
from dotenv import load_dotenv

from tqdm import tqdm


# Load ENV variables for debug, has no effect in production
IS_PRODUCTION = sly.is_production()
if IS_PRODUCTION is True:
    load_dotenv("advanced.env")
    STORAGE_DIR = sly.app.get_data_dir()
else:
    load_dotenv("local.env")

load_dotenv(os.path.expanduser("~/supervisely.env"))

# Get ENV variables
TEAM_ID = sly.env.team_id()
WORKSPACE_ID = sly.env.workspace_id()
PATH_TO_FOLDER = sly.env.folder()

# Create api object to communicate with Supervisely Server
api = sly.Api.from_env()

# Initialize application
app = sly.Application()

# Create project and dataset on Supervisely server
project = api.project.create(WORKSPACE_ID, "My Project", change_name_if_conflict=True)
dataset = api.dataset.create(project.id, "ds0", change_name_if_conflict=True)

# Download folder from Supervisely server
if IS_PRODUCTION is True:
    api.file.download_directory(TEAM_ID, PATH_TO_FOLDER, STORAGE_DIR)
    # Set path to folder with images
    PATH_TO_FOLDER = STORAGE_DIR

images_names = []
images_paths = []
for file in os.listdir(PATH_TO_FOLDER):
    file_path = os.path.join(PATH_TO_FOLDER, file)
    images_names.append(file)
    images_paths.append(file_path)

# Process folder with images and upload them to Supervisely server
with tqdm(total=len(images_paths)) as pbar:
    for img_name, img_path in zip(images_names, images_paths):
        try:
            # Upload image into dataset on Supervisely server
            info = api.image.upload_path(dataset_id=dataset.id, name=img_name, path=img_path)
            sly.logger.trace(f"Image has been uploaded: id={info.id}, name={info.name}")
        except Exception as e:
            sly.logger.warn("Skip image", extra={"name": img_name, "reason": repr(e)})
        finally:
            # Update progress bar
            pbar.update(1)

sly.logger.info(f"Result project: id={project.id}, name={project.name}")
