#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought permissions package component>
#------------------------------------------------------------------------------


# Enthought library imports.
from enthought.traits.api import Dict, HasTraits, implements, Instance, Unicode

# Local imports.
from i_user_database import IUserDatabase
from persistent import Persistent


class _UserAccount(HasTraits):
    """This represents a single account in the user database."""

    # The name the user uses to identify themselves.
    name = Unicode

    # A description of the user (typically their full name).
    description = Unicode

    # The user's password.
    password = Unicode


class _UserDb(Persistent):
    """This is the persisted user database."""

    # The dictionary of user accounts.
    users = Dict


class UserDatabase(HasTraits):
    """This is the default implementation of a user database.  It is good
    enough to be used in a cooperative environment (ie. where real access
    control is not required).  In an enterprise environment the user database
    should be replaced with one that interacts with some secure directory
    service."""

    implements(IUserDatabase)

    #### 'IUserDatabase' interface ############################################

    can_add_user = True

    can_modify_user = True

    can_delete_user = True

    #### Private interface ###################################################

    # The persisted database.
    _db = Instance(_UserDb)

    ###########################################################################
    # 'IUserDatabase' interface.
    ###########################################################################

    def authenticate_user(self, user):
        """TODO"""

        # Always authenticate for the moment.
        return True

    def unauthenticate_user(self, user):

        # There is nothing to do to authenticate so it is always successful.
        return True

    def add_user(self):
        """TODO"""

        from enthought.pyface.api import information

        information(None, "This will eventually implement a TraitsUI based GUI for adding users.")

    def modify_user(self):
        """TODO"""

        from enthought.pyface.api import information

        information(None, "This will eventually implement a TraitsUI based GUI for modifying users.")

    def delete_user(self):
        """TODO"""

        from enthought.pyface.api import information

        information(None, "This will eventually implement a TraitsUI based GUI for deleting users.")

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def __db_default(self):
        """Return the default persisted data."""

        return _UserDb('ets_perms_userdb', 'ETS_PERMS_USERDB')
