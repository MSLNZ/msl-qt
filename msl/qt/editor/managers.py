import inspect
import logging

from .types import Mode, Panel

logger = logging.getLogger(__name__)


class Manager(object):

    def __init__(self, editor, typ):
        self._editor = editor
        self._type = typ
        self._children = dict()

    def __repr__(self):
        return '<{} children=[{}]>'.format(
            self.__class__.__name__, ', '.join(self._children.keys()))

    @property
    def editor(self):
        return self._editor

    @property
    def children(self):
        """:class:`dict`: The children (i.e., instances of :class:`Mode` or :class:`Panel`)
        that are associated with this :class:`Manager`."""
        return self._children

    def get(self, child):
        if not inspect.isclass(child) or not issubclass(child, (Mode, Panel)):
            raise TypeError('Must pass in a Mode or a Panel object. Received a {}'.format(type(child)))

        for obj in self._children.values():
            if isinstance(obj, child):
                return obj

        return None

    def add(self, child):
        """Add the child to the :class:`Manager` and to the :class:`BaseEditor`.

        Parameters
        ----------
        child : :class:`Mode` or :class:`Panel`
            The child to add.
        """
        if not isinstance(child, self._type):
            raise TypeError('The child is of type {}, it must be a {}'.format(type(child), self._type))

        if child.name in self._children:
            logger.warning('{} already has a {}'.format(self._editor, child.name))
            return

        self._children[child.name] = child  # add the child to the Manager
        child.add()  # add the child to the BaseEditor
        logger.debug('added ' + str(child))

    def remove(self, child):
        """Remove the child from the :class:`Manager` and from the :class:`BaseEditor`.

        Parameters
        ----------
        child : :class:`str`, :class:`Mode` or :class:`Panel`
            The child to remove. If :class:`str` then the name of the :class:`Mode` or :class:`Panel`.
        """
        if not child:
            logger.error('you did not specify a child to remove')
            return

        if isinstance(child, str):
            try:
                child = self._children[child]
            except KeyError:
                logger.error('a child with name "{}" is not in {}'.format(child, self))
                return

        try:
            del self._children[child.name]  # remove the child from the Manager
        except KeyError:
            logger.error('{} is not in {}'.format(child, self))
        except AttributeError:
            logger.error('{} is not of type {}'.format(child, self._type))
        else:
            child.remove()  # remove the child from the BaseEditor
            logger.debug('removed ' + str(child))


class ModeManager(Manager):

    def __init__(self, editor):
        super(ModeManager, self).__init__(editor, Mode)


class PanelManager(Manager):

    def __init__(self, editor):
        super(PanelManager, self).__init__(editor, Panel)
