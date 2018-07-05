import flask_graphql
from flask_graphql.graphqlview import HttpError
import json
from werkzeug.exceptions import BadRequest


class GraphQLView(flask_graphql.GraphQLView):

    def parse_body(self, request):
        content_type = self.get_content_type(request)

        if content_type == 'application/graphql':
            return {'query': request.data.decode()}

        if content_type == 'application/json':
            try:
                request_json = json.loads(request.data.decode('utf8'))
                if self.batch:
                    assert isinstance(request_json, list)
                else:
                    assert isinstance(request_json, dict)
                return request_json
            except Exception:
                # TODO: do we actually need to wrap in HttpError?
                raise HttpError(BadRequest('POST body sent invalid JSON.'))

        if content_type == 'application/x-www-form-urlencoded':
            return request.form

        if content_type == 'multipart/form-data':
            operations = json.loads(request.form['operations'])
            files_map = json.loads(request.form['map'])
            return place_files_in_operations(
                operations, files_map, request.files)

        return {}


def place_files_in_operations(operations, files_map, files):
    # operations: dict or list
    # files_map: {filename: [path, path, ...]}
    # files: {filename: FileStorage}

    fmap = []
    for key, values in files_map.items():
        for val in values:
            path = val.split('.')
            fmap.append((path, key))

    return _place_files_in_operations(operations, fmap, files)


def _place_files_in_operations(ops, fmap, fobjs):
    for path, fkey in fmap:
        ops = _place_file_in_operations(ops, path, fobjs[fkey])
    return ops


def _place_file_in_operations(ops, path, obj):

    if len(path) == 0:
        return obj

    if isinstance(ops, list):
        key = int(path[0])
        sub = _place_file_in_operations(ops[key], path[1:], obj)
        return _insert_in_list(ops, key, sub)

    if isinstance(ops, dict):
        key = path[0]
        sub = _place_file_in_operations(ops[key], path[1:], obj)
        return _insert_in_dict(ops, key, sub)

    raise TypeError('Expected ops to be list or dict')


def _insert_in_dict(dct, key, val):
    return {**dct, key: val}


def _insert_in_list(lst, key, val):
    return [*lst[:key], val, *lst[key+1:]]
