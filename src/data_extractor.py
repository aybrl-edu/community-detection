import requests
import string
import time

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Example of a search of depth = 2                                                          #
#                                                                                           #
# Start_repo -> Contributors                                                                #
#                   |-> repos -> Contributors                                               #
#                                      |-> repos -> Contributors                            #
#                                                        |-> repos -> Contributors          #
#                                                                          |-> repos        #
#                                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Globals
SEARCH_DEPTH = 3
MIN_REPOS_TO_VISIT = 10000
MAX_REPOS_TO_VISIT = 60000
nodes_file = open("data/nodes_data.json", "w")
edges_file = open("data/edges_data.json", "w")

api_helper = {
    "base_url": "https://api.github.com",
    "start_point": {
        "repo_name": "node",
        "repo_owner": "nodejs"
    },
    "token": "FILTERED"
}


globals_vars = {
    "repos_visited": 0
}

network_data_structure = {
    "nodes": [],
    "links": []
}

contributors_visited = {}
repositories_visited = {}


def launch(launches):
    s_depth = 0
    start_repo_name = api_helper.get("start_point").get("repo_name")
    start_repo_owner = api_helper.get("start_point").get("repo_owner")

    print("#### Data extraction has started... ####")

    status = False

    try:
        status = extract_data(s_depth, globals_vars.get("repos_visited"), start_repo_name, start_repo_owner, launches)

    except Exception:
        nodes_file.close()
        edges_file.close()

    if status:
        if globals_vars.get("repos_visited") < MIN_REPOS_TO_VISIT:
            # Move to the second page of the initial repo
            launch(launches + 1)

        print("#### Data has been successfully extracted. Please check the /data/ directory ####")

        nodes_file.close()
        edges_file.close()

        return True

    print("#### Something went wrong while extracting data! ####")

    nodes_file.close()
    edges_file.close()

    return False


def extract_data(s_depth, repos_visited, repo_name, repo_owner, page):
    if s_depth > SEARCH_DEPTH:
        return True

    contributors_list = get_repo_users(repo_name, repo_owner, page)

    for contributor in contributors_list:

        if contributors_visited.get(contributor['login']):
            continue

        contributors_visited[contributor['login']] = True
        cont_repos = get_user_repos(contributor['repos_url'], True)

        if not cont_repos:
            continue

        for repo in cont_repos:
            if repositories_visited.get(repo['name']):
                continue

            repositories_visited[repo['name']] = True
            repo_languages = get_repo_languages(repo["name"], contributor["login"])

            # Repo as node
            node = {
                "repo_name": repo["name"],
                "repo_owner": contributor["login"],
                "repo_languages": repo_languages
            }
            network_data_structure.get("nodes").append(node)
            nodes_file.write(str(node)+",\n")

            # Repo <-> Repo edge
            edge = {
                "source": repo_name,
                "target": repo["name"]
            }
            network_data_structure.get("links").append(edge)
            edges_file.write(str(edge)+",\n")

            repos_visited = repos_visited + 1
            globals_vars["repos_visited"] = repos_visited

            if repos_visited >= MAX_REPOS_TO_VISIT:
                print("#### Max number of repos has been reached! ####")
                return "end"

            if s_depth < SEARCH_DEPTH:
                s_depth = s_depth + 1
                extract_data(s_depth, repos_visited, repo["name"], contributor["login"], 1)

        # Sleep to avoid exceeding API limit
        time.sleep(1)

    return network_data_structure


def get_repo_users(repo, owner, page=1):
    endpoint = f"{api_helper.get('base_url')}/repos/{owner}/{repo}/contributors?per_page=20&page={page}"
    return make_request(endpoint)


def get_repo_languages(repo, owner):
    endpoint = f"{api_helper.get('base_url')}/repos/{owner}/{repo}/languages"
    return make_request(endpoint)


def get_user_repos(username_endpoint, is_endpoint):
    if is_endpoint:
        return make_request(username_endpoint)

    endpoint = f"{api_helper.get('base_url')}/users/{username_endpoint}/repos"
    return make_request(endpoint)


# Helpers
def make_request(endpoint):
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {api_helper.get("token")}',
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        return response.json()

    if "API rate limit exceeded" in response.text:
        while True:
            time.sleep(10)

            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                return response.json()

    print(response.text)
    return False


def stop_extraction():
    print("#### API rate limit exceeded, extraction has been stopped for 1 hour... ####")
    time.sleep(4000)
    print("#### Extraction will be resumed shortly! ####")