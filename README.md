# BUPT-Computer-Networking-SMTP-Proxy

## Before you start


We will use [PDM](https://pdm.fming.dev/latest/) for package management.
So there's little differences when running project or adding packages, check [Version Controlling](#version-control) for adding packages and [Run-the-project](#run-the-project) for running the project.

```sh
git clone git@github.com:Nova-Noir/BUPT-Computer-Networking-SMTP-Proxy.git
git checkout -b <YOUR_BRANCH_NAME> dev

cd BUPT-Computer-Networking-SMTP-Proxy

# Use pdm 
curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python -
pdm install
```



## Workflow

```sh
# Make sure you're working under your own branch
smtp_proxy\Scripts\activate.bat  # Windows
source  smtp_proxy/bin/activate  # Linux / macOS

... After some development
git add .
git commit -m 'Your commit message'  # if possible, follow https://gitmoji.dev/ for a prettier commit message.

# Update main branch
git checkout dev
git pull origin dev

# Rebase and fix conflicts
git checkout <YOUR_BRANCH_NAME>
git rebase dev
... Fix conflicts
# ( Optional ) Make your commit history prettier ( squash commits )
git rebase -i HEAD~3
# Ignore next line if there's no conflict
git rebase --continue

# Push
git push <YOUR_BRANCH_NAME>
```

! DO NOT MODIFY `main` or `dev` BRANCH DIRECTLY !


## Run the project
When using PDM, we're actually adding packages to the virtual env, thus, it is required to specify the interpreter.

```sh
pdm run start
# or
pdm run python main.py
# or
eval $(pdm venv activate in-project)
python main.py
```

## Version Control

If you add any package, make sure to export it using

```sh
pdm add <PACKAGE_NAME>
```

If updated, make sure to sync packages using 

```sh
pdm sync
# or
pdm install
```

If updated, make sure to sync packages using 

```sh
pdm sync
# or
pdm install
```
