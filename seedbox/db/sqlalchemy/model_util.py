"""
Provides utilities for managing models
"""
import logging

from seedbox.db import models as api_model
from seedbox.db.sqlalchemy import models as db_model

LOG = logging.getLogger(__name__)


def from_db(db_item):
    """
    Handles the conversion from the database model object to the
    corresponding public facing api model object. If an item has
    a reference to another model object then the call is recursive.

    :param db_item: an instance of a database model object
    :returns: an instance of an api model object
    """
    # if the input was None then return back what was provided
    if db_item is None:
        return db_item

    # determine which object model we are converting to based
    # on the model provided. Assumes that the name of the models
    # at the database and api are the same.
    _model = getattr(api_model, db_item.__class__.__name__)

    # now start the conversion process
    instance = _model.make_empty()
    for k in instance:
        # the public api model has a named primary key vs. the
        # default database primary key field of id for better
        # readability.
        if k == instance.PK_NAME:
            instance[k] = db_item.get('id')
        else:
            # need to inspect each attribute of the incoming object
            # to determine if it is holding an instance to another
            # object or potentially a list of another object.
            _attr = db_item.get(k)
            if isinstance(_attr, db_model.Base):
                instance[k] = from_db(_attr)
            # if it is a list with values and the values are of type
            # defined within the database models then we handle the
            # conversion for the entire list. The more items in the
            # list the higher chance of impacting performance.
            elif (isinstance(_attr, list) and _attr and
                    isinstance(_attr[0], db_model.Base)):
                instance[k] = [from_db(v) for v in _attr]
            else:
                instance[k] = _attr
    return instance


def to_db(api_item, db_item=None):
    """
    Handles the conversion from the api model object to the
    corresponding database model object. If an item has
    a reference to another model object then the call is recursive.

    :param api_item: an instance of a api model object
    :param db_item: an instance of a database model object that
                    is to be updated. (optional)
    :returns: an instance of an database model object
    """
    # if the input was None then return back what was provided
    if api_item is None:
        return api_item

    row = db_item
    # if the optional row not provided then we assumed a new row
    # and initialize instance
    if row is None:
        # determine which object model we are converting to based
        # on the model provided. Assumes that the name of the models
        # at the database and api are the same.
        _model = getattr(db_model, api_item.__class__.__name__)

        # initialize the new db row object with the primary key
        # value within the api object.
        row = _model(id=getattr(api_item, api_item.PK_NAME))

    # start conversion by taking the values within the api and
    # setting onto the db row object (treating it as a dict)
    for k, v in api_item.items():

        # because of the relationship to another object exists
        # then we need to check for values that are of the type
        # of an api object or a list of an api object.
        if isinstance(v, api_model.Model):
            v = to_db(v)
        elif isinstance(v, list) and v and isinstance(v[0], api_model.Model):
            v = [to_db(elm) for elm in v]

        # after all the converting just set the value onto
        # the db row object.
        row[k] = v

    return row
