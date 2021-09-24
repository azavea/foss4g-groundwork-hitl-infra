import argparse
from copy import deepcopy
from itertools import zip_longest
import os
from os.path import join
from urllib.parse import quote

import requests

rf_api_refresh_token = os.getenv("RF_REFRESH_TOKEN")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

auth0_domain = "raster-foundry.auth0.com"


def get_auth0_bearer():
    resp = requests.post(
        f"https://{auth0_domain}/oauth/token",
        json={
            "client_id": client_id,
            "client_secret": client_secret,
            "audience": f"https://{auth0_domain}/api/v2/",
            "grant_type": "client_credentials",
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_rf_bearer():
    resp = requests.post(
        "https://app.rasterfoundry.com/api/tokens",
        json={"refresh_token": rf_api_refresh_token},
    )
    resp.raise_for_status()
    return resp.json()["id_token"]


def get_user_by_email(email, bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    query_string = f"name:{email} OR email:{email}"
    resp = requests.get(
        f"https://{auth0_domain}/api/v2/users",
        params={
            "q": query_string,
        },
        headers=headers,
    )
    try:
        resp.raise_for_status()
    except:
        print(resp.content)
        raise
    return resp.json()[0]


def get_campaign(campaign_id, bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    resp = requests.get(
        f"https://app.rasterfoundry.com/api/campaigns/{campaign_id}", headers=headers
    )
    resp.raise_for_status()
    return resp.json()


def clone_campaign(campaign, owner_id, bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    copied = deepcopy(campaign)
    copied["owner"] = owner_id
    copied["tags"] = ["FOSS4G 2021"]
    campaign_resp = requests.post(
        "https://app.rasterfoundry.com/api/campaigns", headers=headers, json=copied
    )
    campaign_resp.raise_for_status()
    new_campaign = campaign_resp.json()
    new_groups = [
        x | {"campaignId": new_campaign["id"], "classes": x["labelClasses"]}
        for x in copied["labelClassGroups"]
    ]
    for group in new_groups:
        label_class_group_resp = requests.post(
            f"https://app.rasterfoundry.com/api/campaigns/{new_campaign['id']}/label-class-groups",
            headers=headers,
            json=group,
        )
        label_class_group_resp.raise_for_status()
    return new_campaign["id"]


def get_project(project_id, bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    resp = requests.get(
        f"https://app.rasterfoundry.com/api/annotation-projects/{project_id}",
        headers=headers,
    )
    resp.raise_for_status()
    return resp.json()


def clone_project(project, campaign_id, owner_id, bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    copied = deepcopy(project)
    copied["owner"] = owner_id
    copied["tags"] = ["FOSS4G 2021"]
    copied["campaignId"] = campaign_id
    copied["projectId"] = None
    project_resp = requests.post(
        "https://app.rasterfoundry.com/api/annotation-projects",
        headers=headers,
        json=copied,
    )
    project_resp.raise_for_status()
    return project_resp.json()


def fetch_tasks(annotation_project_id, url_base, bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    template_project_tasks_url = join(
        url_base, "api/annotation-projects/", annotation_project_id, "tasks"
    )
    tasks = requests.get(template_project_tasks_url, headers=headers).json()
    has_next = tasks["hasNext"]
    next_page = 1
    while has_next:
        new_tasks_url = f"{template_project_tasks_url}?page={next_page}"
        next_tasks = requests.get(new_tasks_url, headers=headers).json()
        tasks["features"] += next_tasks["features"]
        has_next = next_tasks["hasNext"]
        next_page += 1
    return tasks


# break all tasks into manageable chunks
# modified from https://docs.python.org/3/library/itertools.html#itertools-recipes
def grouper(iterable, n):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    x = zip_longest(*args)
    # workaround to remove the fill values in the chunks
    return [[ii for ii in i if ii is not None] for i in x]


# POST the tasks to the new project in groups
def copy_tasks_to_project(source_tasks, project_id, bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    tasks_post_url = join(
        "https://app.rasterfoundry.com",
        "api",
        "annotation-projects",
        project_id,
        "tasks",
    )
    chunks = grouper(source_tasks["features"], 1250)
    out = {"type": "FeatureCollection", "features": []}
    for chunk in chunks:
        chunk_tasks = {"features": [], "type": "FeatureCollection"}
        for task in chunk:
            # set the status to unlabeled, no matter what it was before
            task["properties"]["status"] = "UNLABELED"
            # set the annotationProjectId to
            task["properties"]["annotationProjectId"] = project_id
            chunk_tasks["features"] += [task]

        chunk_tasks_response = requests.post(
            tasks_post_url, headers=headers, json=chunk_tasks
        )
        # make sure this post request doesn't fail silently
        chunk_tasks_response.raise_for_status()
        out["features"] += chunk_tasks_response.json()["features"]
    return out


# One-shot to grab all the tasks and do the copy
def clone_tasks(from_project_id, to_project_id, bearer_token):
    source_tasks = fetch_tasks(
        from_project_id, "https://app.rasterfoundry.com", bearer_token
    )
    return copy_tasks_to_project(source_tasks, to_project_id, bearer_token)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_project")
    parser.add_argument("email")
    args = parser.parse_args()
    auth0_bearer = get_auth0_bearer()
    rf_bearer = get_rf_bearer()
    auth0_user = get_user_by_email(args.email, auth0_bearer)
    source_project = get_project(args.source_project, rf_bearer)
    source_campaign_id = source_project["campaignId"]
    source_campaign = get_campaign(source_campaign_id, rf_bearer)
    new_campaign_id = clone_campaign(source_campaign, auth0_user["user_id"], rf_bearer)
    new_project = clone_project(
        source_project, new_campaign_id, auth0_user["user_id"], rf_bearer
    )
    clone_tasks(args.source_project, new_project["id"], rf_bearer)


if __name__ == "__main__":
    main()
