from .exceptions import OSFException
from .models import OSFCore
from .models import Project
from json import dumps

class OSF(OSFCore):
    """Interact with the Open Science Framework.

    This is the main point of contact for interactions with the
    OSF. Use the methods of this class to find projects, login
    to the OSF, etc.
    """
    def __init__(self, username=None, password=None, token=None, *args, **kwargs):
        super(OSF, self).__init__({}, *args, **kwargs)
        try:
            self.login(username, password, token)
        except OSFException:
            pass

    def login(self, username=None, password=None, token=None):
        """Login user for protected API calls."""
        if token is not None:
            self.session.token_auth(token)
        elif username is not None and password is not None:
            self.session.basic_auth(username, password)
        else:
            raise OSFException("No login details provided.")

    def projects(self):
        projects = []

        url = self._build_url("users", "me")
        user = self._json(self._get(url), 200)
        nodes_url = user['data']['relationships']['nodes']['links']['related']['href']

        data = self._json(self._get(nodes_url), 200)['data']
        for proj in data:
            projects.append(Project(proj, self.session))

        return projects


    def project(self, project_id):
        """Fetch project `project_id`."""
        type_ = self.guid(project_id)
        url = self._build_url(type_, project_id)
        if type_ in Project._types:
            return Project(self._json(self._get(url), 200), self.session)
        raise OSFException('{} is unrecognized type {}. Clone supports projects and registrations'.format(project_id, type_))

    def create_project(self, title, category, description="", tags=None):
        """Create new project with title, category, description (optional), tags (optional)."""

        if tags is None:
            tags = []

        type_ = "nodes"
        url = self._build_url(type_)
        data = dumps({"data": {"type": type_, "attributes": {
            "title": title,
            "category": category,
            "description": description,
            "tags": tags
        }}})

        return Project(self._json(self._post(url, data=data), 200), self.session)

    @property
    def username(self):
        if self.session.auth is not None:
            return self.session.auth[0]

    @property
    def password(self):
        if self.session.auth is not None:
            return self.session.auth[1]
