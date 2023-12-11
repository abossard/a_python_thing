# A Python Thing 🐍

Welcome to A Python Thing! This project is a combination of a webapp, two background jobs, and some Azure infrastructure. It's all about embracing the power of Python and having some fun along the way! 😄

## Getting Started

To create and update a best practice Python setup with Poetry, follow these steps:

1. Install Poetry by running the following command:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Create a new Python project with Poetry:
   ```bash
   poetry new my_project
   ```

3. Navigate to your project directory:
   ```bash
   cd my_project
   ```

4. Install project dependencies:
   ```bash
   poetry install
   ```

5. Start coding and enjoy the magic of Python and Poetry! ✨

## Documentation

For more information on Poetry, check out the official documentation [here](https://python-poetry.org/docs/). It's a great resource to explore all the features and best practices for managing your Python projects.

Happy coding! 🚀



poetry config virtualenvs.in-project true


```shell
mkdir data
docker run -v $PWD/data:/data -e ZO_DATA_DIR="/data" -p 5080:5080 \
    -e ZO_ROOT_USER_EMAIL="root@example.com" -e ZO_ROOT_USER_PASSWORD="Complexpass#123" \
    public.ecr.aws/zinclabs/openobserve:latest

```


## Todo
[ ] Minimal Console Logging (Exceptions, Warnings)