

def has_parameter(obj,parameter):
    if hasattr(obj, parameter):
        return getattr(obj,parameter)
    else:
        return 0
