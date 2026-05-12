"""This resource interact with data.mit.edu through API,
and requires authorization to get temporary credentials following the official doc
http://dsg-datahub-apidoc.s3-website-us-east-1.amazonaws.com/
"""

from io import BytesIO, IOBase, StringIO

import pandas as pd
import requests
from dagster import ConfigurableResource, get_dagster_logger
from pydantic import PrivateAttr
from requests.exceptions import SSLError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

logger = get_dagster_logger()
default_timeout = 30


@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(SSLError),
)
def upload_data_to_dhub(url: str, data: IOBase, ext: str = "csv"):
    """Upload data to datahub using the given url with retries for SSL error.
    Args:
        url: An AWS presigned URL to upload the data.
        data: StringIO or BytesIO object containing the data to be uploaded.
        ext: file extension of the data to be uploaded, default to "csv".
    """
    if ext == "csv":
        payload = {
            "data": data.getvalue().encode("utf-8"),
            "headers": {"Content-Type": "text/csv"},
        }
    elif ext == "parquet":
        payload = {
            "data": data,
            "headers": {"Content-Type": "application/gzip"},
        }
    else:
        logger.error("Unsupported file extension")
        return

    res = requests.put(url, timeout=1000, **payload)
    if res.status_code == 200:
        print("Upload Successful")
    else:
        logger.error(f"Failed to upload. Status code: {res.status_code}")


def data_hub_authorize(auth_token):
    """This function will return a temporary token to access datahub"""
    url = "https://data.mit.edu/api/auth"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"token": auth_token}
    res = requests.post(url, headers=headers, json=data, timeout=10)
    if res.status_code == 200:
        return res.json()["data"]["jwt"]
    else:
        logger.error("Fail to authorize on Data Hub")
        return


class DataHubResource(ConfigurableResource):
    """This resource contains methods interacting with MIT Data Hub API"""

    auth_token: str

    _jwt: str | None = PrivateAttr(default=None)
    _headers: dict = PrivateAttr(default_factory=lambda: {"accept": "application/json"})
    _api_endpoint: str = PrivateAttr(default="https://data.mit.edu/api")

    def _ensure_authorized(self):
        if self._jwt:
            return
        self._jwt = data_hub_authorize(self.auth_token)
        self._headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self._jwt}",
        }

    def list_projects(self):
        """Return a list of projects the user has access to."""
        self._ensure_authorized()
        url = f"{self._api_endpoint}/user"
        res = requests.get(url, headers=self._headers, timeout=default_timeout)
        if res.status_code == 200:
            logger.info("Successfully connected to Data Hub")
            return res.json()["data"]["projects"]
        logger.error("Fail to list projects.")
        return None

    def get_project_id(self, project_name):
        """Return the project_id for the project with the given name."""
        projects = self.list_projects()
        if not projects:
            logger.error("Unable to retrieve projects from Data Hub; cannot resolve project_id.")
            return None
        for project in projects:
            if project.get("display_name") == project_name:
                return project.get("project_id")

    def get_download_link(self, file_id):
        """Return a download link for the file"""
        self._ensure_authorized()
        url = f"{self._api_endpoint}/file/{file_id}"
        res = requests.get(url, headers=self._headers, timeout=default_timeout)
        if res.status_code == 200:
            return res.json()["data"]["temporarily_download_url"]
        return None

    def search_files_from_project(
        self,
        project_id: str,
        search_term: str,
        tags: list[str] | None = None,
        **kwargs,
    ):
        """Return a list of file download links matching the search term in the project"""
        self._ensure_authorized()
        url = f"{self._api_endpoint}/search"
        data: dict = {
            "term": search_term,
            "projects": [project_id],
            "paging": {"start": 0, "size": 50},
        }
        if tags:
            data["tags"] = tags
        # Allow advance search with additional parameters
        data.update(kwargs)
        res = requests.post(url, headers=self._headers, json=data, timeout=default_timeout)
        if res.status_code != 200:
            logger.error(
                f"Fail to find the file with name {search_term} in project {project_id} "
                f"(status_code={res.status_code})."
            )
            return None

        files = res.json()["data"]
        if not files:
            logger.info(f"No files found for search term {search_term} in project {project_id}.")
            return []

        logger.info(f"Successfully found files: {files}")
        download_links = [self.get_download_link(file["hash_id"]) for file in files]
        logger.info(f"Successfully obtained {len(download_links)} download links.")
        return download_links

    def get_upload_link(self, meta):
        """Get upload link to datahub"""
        self._ensure_authorized()
        url = f"{self._api_endpoint}/file"
        res = requests.post(url, headers=self._headers, json=meta, timeout=default_timeout)
        if res.status_code == 200:
            return res.json()["data"]["temporarily_upload_url"]

    def sync_dataframe(self, df: pd.DataFrame, meta: dict, ext: str):
        """Sync the dataframe to target csv on datahub
        Args:
            df: dataframe to be uploaded.
            meta: datahub file configuration, including project, title, and filenames.
            ext: file extension of the data to be uploaded.

        """
        upload_link = self.get_upload_link(meta)
        if ext == "csv":
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            upload_data_to_dhub(upload_link, csv_buffer)
        else:
            out_buffer = BytesIO()
            df.to_parquet(out_buffer, index=False, compression="gzip")
            out_buffer.seek(0)
            upload_data_to_dhub(upload_link, out_buffer, ext=ext)
