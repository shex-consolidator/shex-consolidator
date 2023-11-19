from shex_consolidator.model import Shape


class Schema(object):

    def __init__(self, namespaces, shapes):
        self._namespaces = namespaces
        self._shapes = shapes

    @property
    def namespaces(self):
        return self._namespaces

    @property
    def shapes(self):
        return self._shapes

    @property
    def n_shapes(self):
        return len(self._shapes)

    def yield_shapes(self):
        for a_shape in self._shapes:
            yield a_shape

    def contains_shape(self, target_shape: Shape):
        for a_shape in self._shapes:
            if a_shape.label == target_shape.label:
                return True
        return False

    def get_shape_by_label(self, shape_label: str):
        for a_shape in self._shapes:
            if a_shape.label == shape_label:
                return a_shape
        return None
