#%%
import json
import scaleapi
from scaleapi.tasks import TaskType,TaskReviewStatus, TaskStatus
from scaleapi.exceptions import ScaleDuplicateResource

#%%
# create api object
client = scaleapi.ScaleClient("scaleint_b8649eb1809e438c97f60c4b914b05de|5c7633ec64c093003791762f")

# name of target project
project_name = "NextGenUnifiedSceneTags_V100_PVM_Road" # name of the project of the images
video_project_name = "dev | Single Frame to Video Frame Test" # name of the project of the new video Tasks

#%%
# get the tasks in the image annotation project
task_ids = [
    "62466762fa0bf8002cb13efe",
    "62466803001511002c381db4",
    "62466714505f430011e98af3",
    "6246781e6892ac003302bb62",
    "62466cb82efa670017d93937",
    "622b87934b025b0033530178",
    "622b70a08b3807002b4a74a2",
    "6246741ccffc3600252b360a",
    "62465929bc8a520039df5706",
    "6246765fcffc3600252b3bcd",
]

tasks = []
for task in task_ids:
    task_res = client.get_task(task)
    tasks.append(task_res)
print("Downloaded all tasks")

#%% create and upload hypothesis of original labels
hypothesis_data = [task.as_dict()["response"] for task in tasks]
hypothesis_path = "./hypothesis_video_task_real.json"
with open(hypothesis_path, 'w', encoding='utf8') as f:
    json.dump(hypothesis_data, f, ensure_ascii=False)
    f.close()
# * upload the json file to a url accessible by the Scale API
hypothesis = {"annotations": {
    "url": "https://raw.githubusercontent.com/scaleJunyuLiu/test_files/main/hypothesis_number.json"}
}

#%% create layers information and upload layers

# in this instance, the frames will be labeled left and right sequentially
# we can define the layer information freely
camera_list = ["left", "right"]
layers_data = [{
            "boxes": [
                {
                    "label": camera_list[i%2],
                    "height": 1,
                    "width": 1,
                    "top": 1,
                    "left": 1
                }
            ],
        } for i in range(len(tasks))]
layers_path = "./layers_video_task_real.json"
with open(layers_path, 'w', encoding='utf8') as f:
    json.dump(layers_data, f, ensure_ascii=False)
    f.close()
# * upload the layer information to a URL accessible by Scale API

layers = {
    "url": "https://raw.githubusercontent.com/scaleJunyuLiu/test_files/main/layers_video_task_info.json"
} # the URL of the layers json file

#%% create payload
payload = dict(
    project=video_project_name,
    instruction=tasks[0].as_dict()["instruction"],
    attachment_type="image",
    attachments=[task.as_dict()["params"]["attachment"] for task in tasks],
    attachment="",
    geometries=tasks[0].as_dict()["params"]["geometries"],
    annotation_attributes=tasks[0].as_dict(
    )["params"]["annotation_attributes"],
    layers=layers, #! add the layers
    hypothesis=hypothesis, # keep the hypothesis
)

# create the video annotation task
try:
    task = client.create_task(TaskType.VideoAnnotation, **payload)
    print(task)
except ScaleDuplicateResource as err:
    print(err.message)  # If unique_id is already used for a different task

# %%
