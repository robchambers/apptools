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
from enthought.traits.api import Bool, Interface


class IUserDatabase(Interface):
    """The interface to be implemented by a user database for the default user
    manager."""

    # Set if the implementation supports adding users.
    can_add_user = Bool(False)

    # Set if the implementation supports modifying users.
    can_modify_user = Bool(False)

    # Set if the implementation supports deleting users.
    can_delete_user = Bool(False)

    def add_user(self):
        """Add a user account to the database.  This only needs to be
        reimplemented if 'can_add_user' is True."""

    def modify_user(self):
        """Modify a user account in the database.  This only needs to be
        reimplemented if 'can_modify_user' is True."""

    def delete_user(self):
        """Delete a user account from the database.  This only needs to be
        reimplemented if 'can_delete_user' is True."""