This documents how to prepare a personal DataStore instance for use whilst in development.

Firstly, you have to create a new gcloud project. https://cloud.google.com/resource-manager/docs/creating-managing-projects. Next, you should get a prompt that asks you whether the project should be in Native or DataStore mode. You'll have to select the DataStore mode. Once that is complete, you need to run and follow through the following commands:

1. `gcloud auth login`
2. `gcloud auth application-default login`

With that done, you should update your `instance/config.py` file to have a matching project id with the gcloud project you just created