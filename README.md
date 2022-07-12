# POLLS API
____
This is a more complex implementation of the [polls api tutorial](https://www.agiliq.com/blog/2019/04/drf-polls/) introducing more complex permissions and class based viewws all `GET` operations do not require authorization

## Project Summary

* Custom request initilizer that allows object to be build from url arguments
* Custom owner permission class that allows class to specify owner field for verification
* Custom Nested Serilizers Implementation with initilizer

## Running this project

To get this project up and running you should start by having Python installed on your computer. It's advised you create a virtual environment to store your projects dependencies separately. You can install virtualenv with

```
pip install virtualenv
```

Clone or download this repository and open it in your editor of choice. In a terminal (mac/linux) or windows terminal, run the following command in the base directory of this project

```
virtualenv env
```

That will create a new folder `env` in your project directory. Next activate it with this command on mac/linux:

```
source env/bin/activate
```

Then install the project dependencies with

```
pip install -r requirements.txt

```
Now you can run the project with this command

```
python manage.py runserver

```

## Support

you can always contact me at [faradaydanfard@gmail.com](mailto:faradaydanfard@gmail.com)

## Conclusion

Thanks enjoy
