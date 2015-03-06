#!/usr/bin/env python
import argparse
import os
from datetime import datetime

from jinja2 import Template


parser = argparse.ArgumentParser(
    description='Python app project setup'
)

parser.add_argument(
    '--author-name', '-a',
    dest='author_name',
    type=str,
    required=True,
    help='Your full name (in quotes)'
)
parser.add_argument(
    '--author-email', '-e',
    dest='author_email',
    type=str,
    required=True,
    help='Your email',
)
parser.add_argument(
    '--author-github', '-g',
    dest='author_github',
    type=str,
    required=True,
    help='Your github username',
)
parser.add_argument(
    '--pypi-name', '-p',
    dest='pypi_name',
    type=str,
    required=True,
    help='Name for the package on pypi'
)
parser.add_argument(
    '--repo-name', '-r',
    dest='repo_name',
    type=str,
    required=True,
    help='Name of the repository on GitHub'
)
parser.add_argument(
    '--project-name', '-n',
    dest='project_name',
    type=str,
    required=True,
    help='python importable name of the project'
)
parser.add_argument(
    '--rtd-subdomain', '-d',
    dest='rtd_subdomain',
    type=str,
    required=True,
    help='ReadTheDocs subdomain'
)
parser.add_argument(
    '--extension', '-x',
    dest='extensions',
    action='append',
    default=['py', 'md', 'rst', 'yml', 'cfg', 'LICENSE'],
    required=False,
    help='The file extension(s) to render (default: "py,rst,md,yml,cfg,LICENSE").'
         'Use -e multiple times. for multiple extensions'
)


class ProjectSetup(object):
    def __init__(self, args):
        self.args = args

        self.extensions = tuple(args.extensions)
        self.excluded_files = ['new_project.py']

        self.template_context = {
            'author_name': self.args.author_name,
            'author_email': self.args.author_email,
            'author_github': self.args.author_github,
            'current_year': datetime.utcnow().year,
            'project_name': self.args.project_name,
            'pypi_name': self.args.pypi_name,
            'repo_name': self.args.repo_name,
            'rtd_subdomain': self.args.rtd_subdomain,
        }

    ignored_extensions = ('.pyo', '.pyc', '.py.class', '.swp')

    def print(self, output):
        print(output)

    def can_render_file(self, filename):
        if filename.endswith(self.ignored_extensions):
            return False
        if filename in self.excluded_files:
            return False
        elif filename.endswith(self.extensions):
            return True

    def render_new_file_content(self, file_path):
        t = Template(open(file_path, 'r').read())
        return t.render(self.template_context) + '\n'

    def rename_file(self, root, filename):
        base_filename = filename.split('.')[0]
        extension = filename.split('.')[-1]
        old_path = '{}/{}'.format(root, filename)
        new_path = '{}/{}.{}'.format(root, self.template_context[base_filename], extension)
        os.rename(old_path, new_path)

        self.print('Renamed file {0} to {1}'.format(old_path, new_path))

    def run(self):
        """
        Setup the project
        """
        root_dir = os.getcwd()

        self.print(
            'Rendering files with extensions {0}\n'.format(', '.join(self.extensions))
        )

        # Render all files with valid extensions
        for root, dirs, files in os.walk(root_dir):
            for dirname in dirs[:]:
                if dirname.startswith('.') or dirname == '__pycache__':
                    dirs.remove(dirname)
            if '/env' not in root and '.git' not in root:
                for filename in files:
                    if self.can_render_file(filename):
                        new_path = '{root}/{filename}'.format(
                            root=root,
                            filename=filename
                        )
                        rendered_content = self.render_new_file_content(new_path)

                        with open(new_path, 'wb') as new_file:
                            new_file.write(rendered_content.encode('utf-8'))

                        self.print('Rendered file {0}'.format(new_path))

        # Rename any files named 'project_name'
        for root, dirs, files in os.walk(root_dir):
            if '/env' not in root and '.git' not in root:
                for filename in files:
                    base_filename = filename.split('.')[0]
                    if base_filename == 'project_name':
                        self.rename_file(root, filename)

        # Rename any directories named 'project_name'
        for root, dirs, files in os.walk(root_dir):
            if '/env' not in root and '.git' not in root:
                dirname = root.split('/')[-1]

                if dirname == 'project_name':
                    path_parent = '/'.join(root.split('/')[:-1])

                    new_path_name = '{0}/{1}'.format(
                        path_parent,
                        self.template_context[dirname]
                    )
                    os.rename(root, new_path_name)
                    self.print('Renamed directory {0} to {1}'.format(
                        root,
                        new_path_name
                    ))


if __name__ == '__main__':  # pragma: no coverage
    args = parser.parse_args()
    status = ProjectSetup(args)
    status.run()
