# Core
This is a reposity for graphql application core code.

# Requirements

- Python 3.10
- Docker 
- docker-compose

# Install and Run Project

docker and docker-compose have to be installed. If not installed you can install Docker via [this link](https://docs.docker.com/engine/install/ubuntu/).

After installing docker, you need to add your current user to docker group. It can be done with [this link](https://docs.docker.com/engine/install/linux-postinstall/)

Build 

```
docker-compose build --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)"
```
After build, you can run ```make up``` command and API service will be run at port 8000, also mongodb service run at port 27018.

Create initial objects to use the system

```
make seed
```

Setup [pre-commit](https://pre-commit.com/) for code formatting etc

Install pre-commit

```
sudo apt install pre-commit
```

Install pre-commit dependencies

```
pre-commit install
```

# Documents

GraphQL endpoint `/graphql`
Rest APIs document `/docs`


# Open shell to run a script
Open bash
```
make bash
```

Activate env
``` 
pipenv shell
```

Enter interactive mode after running main file
```
python -i core/main.py
```

Import core and connect to DB
```
import sys
sys.path.append("/core")
connect("app", host="mongodb://mongo")
```
