class Component(object):
    """
    Abstract base class of composite design pattern.

    New classes should not inherit from this class but from
    the Leaf or Composite classes instead.

    Attributes:
        parent (Component): The parent component.
        Is None if this is a root component.
        component_type (string): The component_type, a composite can only
        have one active child of a given component_type.
        tags (Set of strings): Tags can be used as a second
        means of identifying a component.
    """
    def __init__(self, *args, **kw):
        self._parent = None
        self.component_type = None
        self.tags = set()
        self.to_be_removed = False

    @property
    def parent(self):
        if self._parent is None:
            raise LookupError("Tried to get parent of {0}, "
                              "but parent was not set".format(str(self)))
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        self.on_parent_changed()

    def has_parent(self):
        return not self._parent is None

    @property
    def next(self):
        """
        Gets the next sibling of the same type,
        allows components to decorate components of the same type.
        """
        if(self.parent.get_original_child(self.component_type) is self):
            return None
        siblings =\
            self.parent.get_spoofed_children_of_type(self.component_type)
        next_index = siblings.index(self) + 1
        if(len(siblings) > next_index):
            return siblings[next_index]
        return self.parent.get_original_child(self.component_type)

    def on_parent_changed(self):
        """
        A method hook called when the parent changes.
        """
        pass

    def precondition(self, *args, **kw):
        """
        A method hook for checking if it's valid to update all components.
        """
        return True

    def update(self, *args, **kw):
        """
        A method hook for updating the component tree.
        """
        pass

    def before_tick(self, time):
        """
        A method hook for updating the component tree before tick.
        """
        pass

    def on_tick(self, time):
        """
        A method hook for updating the component tree on tick.
        """
        pass

    def after_tick(self, time):
        """
        A method hook for updating the component tree after tick.
        """
        pass

    def message(self, message):
        """
        A method hook for broadcasting a message down the component tree.
        """
        pass

    def has_sibling(self, component_type):
        """
        Returns true if this components parent has a child of the given type.

        False otherwise.
        """
        if(self._parent is None):
            raise Exception("ERROR: Tries to find sibling {0} "
                            "of component {1} but it "
                            "has no parent!".format(str(component_type),
                                                    str(self)))
        return self.parent.has_child(component_type)


class Leaf(Component):
    """
    Abstract leaf class of composite design pattern.

    Component classes of leaf type should inherit from this class.
    """
    def __init__(self, *args, **kw):
        super(Leaf, self).__init__(*args, **kw)


class Composite(Component):
    """
    Abstract composite class of composite design pattern.

    Component classes of composite type should inherit from this class.
    Composite objects may hold other Components.
    """
    def __init__(self, *args, **kw):
        super(Composite, self).__init__(*args, **kw)
        self._spoofed_children = {}
        self._children = {}

    def add_child(self, child):
        """
        Adds a child component to this component.
        If the child already has a parent an exception is thrown.
        """
        if child.tags is None:
            raise Exception("Component {0} tried ta add_child"
                            "component: {1} to its children."
                            "But tags"
                            "was not set.".format(str(self), str(child)))
        if child.component_type is None:
            raise Exception("Component {0} tried ta add_child"
                            "component: {1} to its children."
                            "But component_type"
                            "was not set.".format(str(self), str(child)))
        if(not child._parent is None):
            raise Exception("Component {0} tried ta add_child"
                            "component: {1} to its children."
                            "But it already"
                            "had parent: {2}.".format(str(self),
                                                      str(child),
                                                      str(child.parent)))
        self._children[child.component_type] = child
        child.parent = self

    def add_spoof_child(self, child):
        """
        Adds a spoofed child component to this composite.
        If the child already has a parent an exception is thrown.
        """
        if child.tags is None:
            raise Exception("Component {0} tried to add_child "
                            "component: {1} to its children. "
                            "But tags "
                            "was not set.".format(str(self), str(child)))
        if child.component_type is None:
            raise Exception("Component {0} tried to add_child "
                            "component: {1} to its children. "
                            "But component_type "
                            "was not set.".format(str(self), str(child)))
        if(not child._parent is None):
            raise Exception("Component {0} tried to add_child "
                            "component: {1} to its children. "
                            "But it already "
                            "had parent: {2}.".format(str(self),
                                                      str(child),
                                                      str(child.parent)))
        if(not child.component_type in self._children):
            raise Exception("Component {0} tried to add_spoof_child"
                            "component: {1} to its spoofed_children."
                            "But there was no real "
                            "child of that type.".format(str(self),
                                                         str(child)))
        if(not child.component_type in self._spoofed_children):
            self._spoofed_children[child.component_type] = []
        self._spoofed_children[child.component_type].append(child)
        child.parent = self

    def reset_spoofed_children(self):
        """
        Removes all spoofed children.
        """
        self._spoofed_children = {}

    def remove_component(self, component):
        """
        Removes a child component to this component.
        """
        if(component.component_type in self._children and
           component is self._children[component.component_type]):
            del self._children[component.component_type]
            component.parent = None
        return component

    def update(self):
        """
        Runs update on all child components.
        """
        map(lambda x: x.update(), self._children.values())

    def before_tick(self, time):
        """
        Runs before_tick on all child components.
        """
        map(lambda x: x.before_tick(time), self._children.values())

    def on_tick(self, time):
        """
        Runs on_tick on all child components.
        """
        map(lambda x: x.on_tick(time), self._children.values())

    def after_tick(self, time):
        """
        Runs after_tick on all child components.

        It also resets all spoofed children.
        """
        self.reset_spoofed_children()
        map(lambda x: x.after_tick(time), self._children.values())

    def message(self, message):
        """
        Sends message to all child components.
        """
        map(lambda x: x.message(message), self._children.values())

    def __getattr__(self, component_type):
        try:
            if(component_type in self._spoofed_children and
               len(self._spoofed_children[component_type]) > 0):
                return self._spoofed_children[component_type][0]
            return self._children[component_type]
        except KeyError:
            raise Exception("Tried to access component {0} from composite {1} "
                            "But it doesn't exist.".format(str(component_type),
                                                           str(self)))

    def get_original_child(self, component_type):
        """
        Gets the "real" child of the composite.
        """
        return self._children[component_type]

    def get_spoofed_children_of_type(self, component_type):
        try:
            return self._spoofed_children[component_type]
        except KeyError:
            raise Exception("Tried to access components of type"
                            " {0} from composite {1} "
                            "But it doesn't exist.".format(str(component_type),
                                                           str(self)))

    def has_child(self, component_type):
        """
        Returns true if this component has a child of the given type.

        False otherwise.
        """
        return component_type in self._children

    def get_children_with_tag(self, tag):
        """
        Gets the list of all children with the given tag.
        """
        return [self.__getattr__(component_type)
                for component_type in self._children.keys()
                if tag in self.__getattr__(component_type).tags]


class CompositeMessage(object):
    """
    Enumerator defining class. Defines all messages that may be sent.
    """
    DUNGEON_LEVEL_CHANGED = 0
    POSITION_CHANGED = 1

    def __init__(self):
        """
        Should not be initiated.
        """
        raise
