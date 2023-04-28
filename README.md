## gve_devnet_securex_tile_visualisation
This sample script allows users to select SecureX Dashboard Tiles associated to multiple tenants which are saved as a configuration and then can be loaded for visualisation in a dashboard. To do this, the user simply provides the client ID and secret that are associated to each SecureX Dashboard that they have.

## Contacts
* Jordan Coaten

## Solution Components
* Python
* Flask
* SecureX Dashboard
* SecureX Dashboard API's

# Workflow of PoV
![Overview of PoV](/IMAGES/workflow.png)


# High Level Design

![High level design of PoV](/IMAGES/high_level_design.png)


## Installation
1. Log in to [https://securex.us.security.cisco.com/settings/apiClients](https://securex.us.security.cisco.com/settings/apiClients) with your Cisco Security credentials.

2. Create new API keys clicking on **Add API Credentials**.

3. Give the API Credentials a name (e.g., *Dashboard Tiles Sample Script*).

4. Select **Select All**.

5. Add an optional description if needed.

6. Click on **Add New Client**.

7. The **Client ID** and **Client Secret** are now shown to you. Do NOT click on **close** until you have copy-pasted these credentials later to the config.json file in the repository.

8. Make sure Python 3 and Git is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/) and Git [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).


9.	(Optional) Create and activate a virtual environment - once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).  
    ```
    #MacOS and Linux: 
    python3 -m venv [add name of virtual environment here] 
    source [add name of virtual environment here]/bin/activate
    
    #Windows: 
    python -m venv [add name of virtual environment here] 
    [add name of virtual environment here]/Scripts/activate
    ```
    
  * Access the created virtual environment folder
    ```
    cd [add name of virtual environment here] 
    ```

10. Clone this Github repository:  
```
git clone [add github link here]
```
        
  * For Github link: 
      In Github, click on the **Clone or download** button in the upper part of the page > click the **copy icon**  
      ![/IMAGES/giturl.png](/IMAGES/giturl.png)
  * Or simply download the repository as zip file using 'Download ZIP' button and extract it

11. Install all dependencies:  
```
pip install -r requirements.txt
```

12. Make sure that the config.json file looks like this (with the right keys and IDs filled in between the quotes):
```
{
  "clients": [
    {
      "client_name": "<name-of-your-org/tenant/client>",
      "client_id": "<associated-client-id>",
      "client_secret": "<associated-client-secret>"
    },
    {
      "client_name": "<name-of-your-org/tenant/client>",
      "client_id": "<associated-client-id>",
      "client_secret": "<associated-client-secret>"
    }
  ]
}
```

## Usage

13. Run the script:   
```
python3 app.py
```

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
