from typing import Optional


def get_notebook_json_name(save_dir: Optional[str] = None) -> Optional[str]:
    """Gets the current Jupyter notebook name and returns it with .json extension.
    Args:
        save_dir (str, optional): Directory where the JSON file should be saved.
                                 Defaults to current working directory.
    Returns:
        str: The full path to the JSON file.
    """
    try:
        import os
        from notebook import notebookapp
        from IPython import get_ipython
        import requests

        # Set the save directory to the current working directory if not provided
        if save_dir is None:
            save_dir = os.getcwd()

        # Get the IPython instance
        ipython = get_ipython()
        if ipython is None:
            raise RuntimeError("Not running in a Jupyter notebook")

        # Get the connection file and kernel ID from the IPython instance
        connection_file = ipython.config["IPKernelApp"]["connection_file"]
        kernel_id = os.path.basename(connection_file).split("-", 1)[1].split(".")[0]

        # Iterate over all running Jupyter notebook servers
        for srv in notebookapp.list_running_servers():
            # Construct the URL to get the sessions from the server
            response_url = srv["url"] + "api/sessions"
            token = srv.get("token", "")
            if token:
                response_url += f"?token={token}"

            try:
                # Get the list of sessions from the server
                response = requests.get(response_url)

                # Check if the response is successful
                if response.status_code != 200:
                    print(
                        f"Error: Failed to retrieve sessions, status code: {response.status_code}"
                    )
                    continue

                sessions = response.json()

                # Ensure sessions is a list
                if not isinstance(sessions, list):
                    print(f"Error: Expected list of sessions, got: {type(sessions)}")
                    continue

                # Iterate over the sessions to find the one with the matching kernel ID
                for sess in sessions:
                    if sess["kernel"]["id"] == kernel_id:
                        # Get the notebook path and name
                        notebook_path = sess["notebook"]["path"]
                        notebook_name = os.path.basename(notebook_path)
                        # Replace the .ipynb extension with .json
                        json_name = notebook_name.replace(".ipynb", ".json")
                        # Create the full path to the JSON file
                        full_json_path = os.path.join(save_dir, json_name)
                        # Print information about the file for the user
                        print(f"Found notebook: {notebook_name}")
                        print(f"JSON file will be saved as: {full_json_path}")
                        # Return the full path to the JSON file
                        return full_json_path
            except requests.RequestException as e:
                print(f"Error getting notebook server information: {e}")
            except (KeyError, TypeError) as e:
                print(f"Error parsing session information: {e}")

        raise RuntimeError("Could not determine active notebook name")

    except Exception as e:
        print(f"Error getting notebook name: {e}")
        return None
