import logging
from pathlib import Path
from typing import Tuple

import gitlab
import urllib.parse


class GitlabClient:
    def __init__(self, host: str, private_token: str):
        self.__client = gitlab.Gitlab(host, private_token=private_token, ssl_verify=False)
    
    def find_group(self, group_name: str):
        groups = self.__client.groups.list(search=group_name)
        return groups[0] if len(groups) > 0 else None
    
    def find_user(self, user_name: str):
        users = self.__client.users.list(search=user_name)
        return users[0] if len(users) > 0 else None
    
    def clone(self, url: str, dir_path: Path, branch_name: str) -> None:
        group_name, project_name = GitlabClient.__parse_url(url)
        logging.debug(f"cloning {url}, using ({group_name=}, {project_name=})")

        group = self.find_group(group_name) or self.find_user(group_name)

        if group is None:
            logging.error(f"unable to get group from {url}")
            raise Exception(f"Could not find group, non-Recoverable! {url=}")
        
        project_id = self.find_project(group, project_name).id
        project = self.__client.projects.get(project_id)

        self.__get_files(project, branch_name, dir_path)

    @staticmethod
    def find_project(group, project_name: str):
        projects = group.projects.list(search=project_name)
        project = projects[0] if len(projects) > 0 else None
        if not project:
            raise Exception(f"Could not find project from {group=}. Non-Recoverable!!!")
        return project

    @staticmethod
    def __parse_url(url: str) -> Tuple[str, str]:
        __URL_PATH_SEPARATOR = '/'
        url_path_quoted_parts = urllib.parse.parseurl(url).path.split(__URL_PATH_SEPARATOR)
        url_path = [urllib.parse.unquote(part) for part in url_path_quoted_parts]
        group_name = __URL_PATH_SEPARATOR.join(url_path[1:-1])
        project_name = url_path[-1].split('.')[0]

        return group_name, project_name
    
    @staticmethod
    def __get_files(project, branch_name: str, dir_path: Path) -> None:
        for file_details in project.repository_tree(recursive=True, ref=branch_name):
            file_type = file_details['type']
            file_path = file_details['path']
            out_file_path: Path = dir_path / file_path

            if file_type == 'tree' and not out_file_path.exists():
                out_file_path.mkdir(parents=True)
            
            if file_type != 'tree':
                with open(out_file_path.as_posix(), 'wb') as f:
                    project.files.raw(file_path, ref=branch_name, streamed=True, action=f.write)
