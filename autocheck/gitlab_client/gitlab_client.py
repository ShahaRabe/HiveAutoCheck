import logging
import urllib.parse
from pathlib import Path

import gitlab
from gitlab.v4.objects import Group, GroupProject, Project, User

_URL_PATH_SEPARATOR = "/"

logger = logging.getLogger(__name__)

class GitlabClient:
    def __init__(self, host: str, private_token: str) -> None:
        self.__client = gitlab.Gitlab(
            host,
            private_token=private_token,
            ssl_verify=False,
        )

    def find_group(self, group_name: str) -> Group | None:
        groups = self.__client.groups.list(search=group_name)
        if len(groups) == 0:
            # Gitlab sucks
            possible_group_name = group_name.split(_URL_PATH_SEPARATOR)[-1]
            groups = self.__client.groups.list(search=possible_group_name)

        return groups[0] if len(groups) > 0 else None  # type: ignore

    def find_user(self, user_name: str) -> User | None:
        users = self.__client.users.list(search=user_name)
        return users[0] if len(users) > 0 else None  # type: ignore

    def clone(self, url: str, dir_path: Path, branch_name: str) -> None:
        group_name, project_name = GitlabClient.__parse_url(url)
        logger.debug(f"Cloning {url}, using ({group_name=}, {project_name=})")

        group = self.find_group(group_name) or self.find_user(group_name)

        if group is None:
            logger.error(f"Unable to get group from {url}")
            raise ValueError(
                f"Could not find group, non-Recoverable! {url=}, {group_name=}",
            )

        project_id = self.find_project(group, project_name).id
        project = self.__client.projects.get(project_id)

        self.__get_files(project, branch_name, dir_path)

    @staticmethod
    def find_project(group: Group | User, project_name: str) -> GroupProject:
        projects = group.projects.list(search=project_name)
        project = projects[0] if len(projects) > 0 else None
        if not project:
            raise ValueError(f"Could not find project from group "
                             f"`{group}`. Non-Recoverable!")
        return project  # type: ignore

    @staticmethod
    def __parse_url(url: str) -> tuple[str, str]:
        url_path_quoted_parts = urllib.parse.urlparse(url).path.split(
            _URL_PATH_SEPARATOR,
        )
        url_path = [urllib.parse.unquote(part) for part in url_path_quoted_parts]
        group_name = _URL_PATH_SEPARATOR.join(url_path[1:-1])
        project_name = url_path[-1].split(".")[0]

        return group_name, project_name

    @staticmethod
    def __get_files(project: Project, branch_name: str, dir_path: Path) -> None:
        for file_details in project.repository_tree(
            recursive=True,
            ref=branch_name,
            all=True,
        ):  # type: ignore
            file_type = file_details["type"]
            file_path = file_details["path"]
            out_file_path: Path = dir_path / file_path

            if file_type == "tree" and not out_file_path.exists():
                out_file_path.mkdir(parents=True)

            if file_type != "tree":
                with out_file_path.open("wb") as f:
                    project.files.raw(
                        file_path,
                        ref=branch_name,
                        streamed=True,
                        action=f.write,
                    )
