# BUPT-Computer-Networking-SMTP-Proxy

## Before you start

```sh
git clone git@github.com:Nova-Noir/BUPT-Computer-Networking-SMTP-Proxy.git
git checkout -b <YOUR_BRANCH_NAME> dev
```



## Workflow

```sh
# Make sure you're working under your own branch
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



## 