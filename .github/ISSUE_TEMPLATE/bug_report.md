---
name: Bug report
about: Create a report to help us improve
title: ''
labels: type:bug
assignees: ''

---

### Checklist

*   [ ] I read [Contribution Guidelines](https://github.com/apragacz/django-rest-registration/blob/master/CONTRIBUTING.md#issues)
*   [ ] I searched existing issues before opening this one
*   [ ] This is not a major security issue
*   [ ] I reproduced the bug with the newest version

#### Optional checklist

*   [ ] I attached a PR with a test case reproducing the problem

### Describe the bug
(Provide here clear and concise description of what the bug is)

### Expected behavior
(Provide here clear and concise description of what you expected to happen)

### Actual behavior
(Provide here clear and concise description of what actually happens)

### Steps to reproduce
Steps to reproduce the behavior:
1. (provide first step)
2. (provide second step)
3. ...

### Diagnostic info

My `settings.py`:

```python
# (Please paste here contents of your Django settings.py file
# (after removing all sensitive information like secrets and domains),
# or at least provide specific settings mentioned below):

REST_REGISTRATION = {
...
}

REST_FRAMEWORK = {
...
}

INSTALLED_APPS = (
...
)
```

### Additional context
(Add any other context about the problem here)
