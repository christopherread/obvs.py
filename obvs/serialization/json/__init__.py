import json
from importlib import import_module

from obvs.serialization.typing import MessageSerializer, MessageDeserializer


def convert_to_dict(obj):
    obj_dict = {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__
    }
    obj_dict.update(obj.__dict__)
    return obj_dict


def dict_to_obj(our_dict):
    """
    Function that takes in a dict and returns a custom object associated with the dict.
    This function makes use of the "__module__" and "__class__" metadata in the dictionary
    to know which object type to create.
    """
    if "__class__" in our_dict:
        class_name = our_dict.pop("__class__")
        module_name = our_dict.pop("__module__")
        module = import_module(module_name)
        class_ = getattr(module, class_name)
        obj = class_(**our_dict)
    else:
        obj = our_dict
    return obj


class JsonMessageSerializer(MessageSerializer):
    def serialize(self, message: object):
        return json.dumps(message, default=convert_to_dict, indent=4, sort_keys=True)


class JsonMessageDeserializer(MessageDeserializer):
    def deserialize(self, data: object):
        return dict_to_obj(json.loads(data))

