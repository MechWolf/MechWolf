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
        import json
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
        
        # Get Jupyter server information from the connection file
        with open(connection_file, 'r') as f:
            connection_info = json.load(f)
        
        # Try different methods to get the notebook path
        # Method 1: Using Jupyter Server REST API
        base_url = os.environ.get('JUPYTER_SERVER_URL', 'http://localhost:8888')
        
        # Make sure base_url ends with a slash
        if not base_url.endswith('/'):
            base_url += '/'
            
        # Get the token from the environment or from the user's jupyter config
        token = os.environ.get('JUPYTER_TOKEN', '')
        if not token:
            # Try to get token from jupyter config
            try:
                jupyter_config_dir = os.path.expanduser('~/.jupyter')
                config_file = os.path.join(jupyter_config_dir, 'jupyter_server_config.json')
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                        token = config.get('ServerApp', {}).get('token', '')
            except:
                pass
        
        # Construct API URL with token
        api_url = f"{base_url}api/sessions"
        if token:
            api_url += f"?token={token}"
            
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                sessions = response.json()
                for session in sessions:
                    if session.get('kernel', {}).get('id') == kernel_id:
                        if 'path' in session.get('notebook', {}):
                            notebook_path = session['notebook']['path']
                        elif 'path' in session:
                            notebook_path = session['path']
                        else:
                            continue
                            
                        notebook_name = os.path.basename(notebook_path)
                        json_name = notebook_name.replace('.ipynb', '.json')
                        full_path = os.path.join(save_dir, json_name)
                        print(f"Using JSON file: {full_path}")
                        return full_path
        except requests.RequestException as e:
            print(f"Error accessing Jupyter server API: {e}")
        
        # Method 2: Using IPython user namespace (if we're in a notebook)
        if hasattr(ipython, 'kernel') and hasattr(ipython.kernel, 'do_one_iteration'):
            try:
                # Get the path via JavaScript execution (works in classic notebook)
                js_code = "window.document.getElementById('notebook_name').innerHTML"
                notebook_name = ipython.run_cell_magic('javascript', '-o', js_code)
                if notebook_name:
                    notebook_name = notebook_name.strip()
                    json_name = notebook_name.replace('.ipynb', '.json')
                    full_path = os.path.join(save_dir, json_name)
                    print(f"Using JSON file: {full_path}")
                    return full_path
            except:
                pass
        
        # Method 3: Last resort, check environment variables
        notebook_path = os.environ.get('NOTEBOOK_PATH')
        if notebook_path:
            notebook_name = os.path.basename(notebook_path)
            json_name = notebook_name.replace('.ipynb', '.json')
            full_path = os.path.join(save_dir, json_name)
            print(f"Using JSON file: {full_path}")
            return full_path
        
        raise RuntimeError("Could not determine active notebook name")
        
    except Exception as e:
        print(f"Error getting notebook name: {e}")
        return None
