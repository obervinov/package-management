import os
import re
import subprocess
from logger import log


class PACKAGES:

    def __init__(self, DB=None) -> None:
        self.db_conenction = DB

    # Function for comparing package versions in yum repositories and database
    def version_comparison(self, env):
        log.info(
            f"PACKAGES.version_comparison(): "
            f"comparison of versions for the {env} environment"
        )
        records = self.db_conenction.select_db_all(f"packages_{env}")
        green_color_items = []
        for item in records:

            if (item[2] != item[3] and item[3] != "not_found"):
                green_color_items.append(item[0])
                log.info(
                    f"PACKAGES.version_comparison(): "
                    f"version {item[2]} is less than version {item[3]} for package {item[1]}"
                )

        GREEN = green_color_items

        return GREEN

    # Function for adding repositories from the database to /etc/yum.repos.d/
    def mount_yum_repos(self):
        log.info(
            "PACKAGES.mount_yum_repos(): "
            "extracting yum repositories from the database to the file system"
        )
        data = self.db_conenction.select_db_all("yum_repos_d")
        for item in data:
            repo_name = item[1]
            repo_content = item[2]
            f = open(f"/etc/yum.repos.d/{repo_name}.repo", "w")
            f.write('{}'.format(repo_content))
            f.close()

        return data

    # Function for adding repositories from the database to /etc/yum.d via rpm
    def mount_rpm_repos(self):
        log.info(
            "PACKAGES.mount_rpm_repos(): "
            "extracting rpm repositories from the database to the file system"
        )
        data = self.db_conenction.select_db_all('rpm_list')
        for item in data:
            rpm_url = item[2]
            try:
                os.system(f"rpm -Uvh {rpm_url}")
            except Exception as ex:
                log.error(
                    "PACKAGES.mount_rpm_repos(): "
                    f"exception: {ex}"
                )

        return data

    # A function for searching and extracting the latest version of a package from yum repositories
    def check_version_in_repo(self, package_name):
        log.info(
            f"PACKAGES.check_version_in_repo(): "
            f"search for the latest versions of the package {package_name} in the yum repository"
        )
        try:
            cmd = f"yum info {package_name} -y| grep Version|head -1|sed 's/ //g'"
            output = subprocess.check_output(
                            cmd,
                            stderr=subprocess.STDOUT,
                            shell=True,
                            universal_newlines=True
                        )
            log.info(
                f"PACKAGES.check_version_in_repo(): "
                f"output yum info about {package_name}: {output}"
            )
        except subprocess.CalledProcessError as exc:
            pkg_version = str(exc)
            log.error(
                f"PACKAGES.check_version_in_repo(): "
                f"subprocess CalledProcessError for package {package_name}: {exc}"
            )
        else:
            pkg = any(char.isdigit() for char in output)
            if pkg is True:
                pkg_version = re.sub('[^0-9.]', '', output)
                log.info(
                    f"PACKAGES.check_version_in_repo(): "
                    f"package {package_name} founded version: {pkg_version}"
                )
            else:
                pkg_version = "not_found"
                log.warning(
                    "PACKAGES.check_version_in_repo(): "
                    f" info package {package_name} not found"
                )

        return pkg_version

    # Function for extracting repositories from the database to the file system
    # and initializing yum update
    def update_yum_cache(self):
        log.info(
            "PACKAGES.update_yum_cache(): "
            "updating yum cache..."
        )
        self.mount_yum_repos()
        self.mount_rpm_repos()
        os.system('yum update -y')
        log.info(
            "PACKAGES.update_yum_cache(): "
            "yum cache has been updated"
        )
