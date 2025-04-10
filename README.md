# Hive Auto Check

## TL;DR

Here before you is a simple auto-checking infrasturcture for Hive.<br>
For examples on how to use it please jump forward to [the examples](#some-examples)


## Important Notes

1. If some responses are marked as segel-only and some aren't then 2 responses would be posted - one for all the student facing responses and one for segel facing
1. In the same category (segel only or student facing) there is a difference between the result (AutoCheck, Done or Redo) the most decisive is the one chosen (Redo, then Done and finaly AutoCheck).
1. Same goes on hide checker name - if even one test chose to hide it it will be hidden
1. Both segel-only and hide-checker-name default to True


## The Longer Version

Hello, happy to have you here.

This project was written after a little pain I experienced after being part of a course with insufficient auto checking and with the acknowledgement that Hive may provide a solid foundation to write auto checks but it has a long way to go to be intuitive, and that every course has a different view on creating an auto checking infrastructure.<br>


## Technologies Chosen

To integrate into hive's autochecks the obvious part was packing the whole system into a docker container.<br>
And to make your lives easier in integrating this system into your course I chose to write it using python 3.12 and pytest (that looks at any python file not just the ones starting with test) with a bunch of prewritten fixtures. Also the entire thing is built as a wheel for easy development :)<br>
So all you need to do is write your tests in a gitlab repository, setup metadata files for the exercises you want to test and write a Dockerfile that inherits from this project's image and sets a few environemnt variables.

> Wait... A bunch of fixtures?

Yes, and a decorator! Here they are:


### Decorator

Each test needs to be marked with the `@autocheck()` decorator - that handles all the logic for posing comments.

Signature: `@autocheck(test_title=None)`

`test_title` is used as a title in the comment posted from this test on the exercise (whether it's segel only or not). if it's equal to None then the test function name is used.


### Fixtures

|Fixture| Type            | Purpose                                                                                                                                                    |Scope|
|-------|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|-----|
|`autocheck_input`|`AutocheckInput`|Get an AutocheckInput dataclass built from the json given by Hive|Session|
|`hive_client`|`HiveClient`|A Hive API client|Session|
|`exercise`|`Exercise`|Use Hive's API to get info about the exercise|Session|
|`exercise_test_metadata`|`ExerciseTestMetadata`|Get the exercise's configured metadata from the configured segel git repo|Session|
|`assignment`|`Assignment`|Use Hive's API to get info about the assignment|Session|
|`original_file_path`|`Path \| None`|The path where the file, as submitted by the student, is saved - None if no file was submitted|Session|
|`hanich_repository_url`|`str \| None`|Attempts to find the hanich's Git clone URL of the current assignment. First from assignemnt service' (or anything like it) message to the student in the description, then a configurable input field from the student (default `repository_url`). If both do not exist returns None|Session|
|`hanich_gitlab_client`|`GitlabClient`|An api client against the haniches gitlab instance|Session|
|`temp_directory`|`Path`|returns a temp directory path, this is used for the cloned repository fixture|Session|
|`hanich_repository_branch`|`str`|Get the configured branch name, either from on_creation_data, environment variable or overriding exercise metadata. default dev|Session|
|`cloned_repository`|`Path`|Clones the haniches repo and returns the path on disk|Session|
|`make_compiled_executable`|`Path`|Compiles the makefile project in the haniches repository and returns the executable's path on disk|Session|
|`cmake_compiled_executable`|`Path`|Compiles the cmake project in the haniches repository and returns the executable's path on disk|Session|
|`blackbox_test_configs`|`list[BlackboxTestConfig]`|Parses the exercise's blackbox tests configurations from disk and returns them|Session|
|`submitted_file`|`bytes \| None`|The contents of the file submitted by the student - None is no file was submitted|Session|
|`extracted_path`|`Path \| None`|The path to which the contents of the file submitted by the student is extracted to - None if no file was submitted or the file submitted is not a archive|Session|

Those are all existing fixtures at the time of writing these lines, more fixtures may be defined in [fixtures.py](autocheck/fixtures.py)


## Tell me more about the tests themselves

So as mentioned you have to use the `@autocheck()` decorator.

In addition, you need to return __either__ an `AutocheckResponse` object that is defined in [autocheck.py](autocheck/autocheck.py) __or__ a boolean value specifying if the test was a success.

The test title (either a given title or the test name by default) __MUST__ be unique as it's used as a dictionary key.

Anything beyond that is up to your imagination - go wild!

If any test throws you'd be noticed by a `segel_only` response by the infrastructure.


## Examples

### autocheck.Dockerfile

> Note there is no entrypoint - __DO NOT__ override the entrypoint:

```Dockerfile
FROM autocheck:latest

ENV HIVE_URL=https://<user>:<password>:<host>

ENV HANICH_GITLAB_HOST=https://<hanich-gitlab-host>
ENV HANICH_GITLAB_TOKEN=<hanich-gitlab-token>

ENV SEGEL_GITLAB_HOST=https://<segel-gitlab-host>
ENV SEGEL_GITLAB_TOKEN=<segel-gitlab-token>
ENV TESTS_REPOSITORY_URL=<repository-url>
ENV TESTS_REPOSITORY_REF=<repository-ref/branch-name>
```

### Tests

```python
import os
from pathlib import Path
from typing import Optional

from autocheck.autocheck import AutocheckResponse, ResponseType, ContentDescriptor, autocheck
from autocheck.exercise import Exercise

# This is a test that does stuff with the info from the submitted exercise
@autocheck()
def test_exercise(exercise: Exercise):
    exercise_string_id = f"{exercise.subject_letter}_{exercise.subject_name}/{exercise.module_name}/{exercise.name}"
    return AutocheckResponse([ ContentDescriptor(exercise_string_id, "Comment") ], ResponseType.AutoCheck, False)


# This is a test that does stuff with th file the student submitted and the files that could be extracted from it, also the title of it's response would be "File Check"
@autocheck(test_title="File Check")
def test_files(submitted_file: Optional[bytes], original_file_path: Optional[Path], extracted_path: Optional[Path]):
    if original_file_path:
        with original_file_path.open('rb') as orig:
            content = orig.read()
        
        string = ['good job, the files match' if submitted_file == content else 'What just happened?']

        if extracted_path:
            for root, _, files in os.walk(extracted_path):
                string += [str(Path(root) / file) for file in files]
    else:
        string = ['No file submitted']
        
    return AutocheckResponse([ ContentDescriptor('\n'.join(string), "Comment") ], ResponseType.AutoCheck if string[0] != 'What just happened?' else ResponseType.Redo)
```

## And Where Do I Put My Tests?

Place your tests in a gitlab repository in a file (or files) under a directory in the root of the project called `tests`. Under the project's root there should also be a `metadata` folder, in which you should create subfolders according to the path of the exercise in Hive (`<subject>/<module>`) and create a file called `exercises.json` which will contain metadata for each exercise.

> An exercise metadata can include:
> - `tests` - array of files or tests to run for that test
> - `hanich_repository_branch_name` - override the default branch name


### Example `exercises.json`

```json
{
  "Foo": {
    "tests": [
      "foo.py",
      "bar.py::test_baz"
    ],
    "hanich_repository_branch_name": "main"
  },
  "Oof": {
    "tests": [
      "oof.py::test_oof"
    ]
  }
}
```

### Example Repository Layout
```
> /
>   tests/
>     foo.py
>     bar.py
>   metadata/
>     C/
>       pointers/
>         exercises.json
>       io/
>         exercises.json
```